"""
AutoMod System - Automatic Moderation with Behavior Analysis
Handles spam detection, link filtering, trust scoring, and auto-actions.
"""

import re
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from collections import defaultdict, deque
import discord
from discord import Member, Message, Guild
from motor.motor_asyncio import AsyncIOMotorDatabase

from database.automod_schema import AutoModSchema

logger = logging.getLogger('automod_system')


class AutoModSystem:
    """
    Automatic Moderation System with Behavior Analysis.
    
    Features:
    - Spam Detection (duplicate messages)
    - Link Detection & Blacklist
    - Mention Spam Detection
    - Caps Lock Detection
    - Emoji Spam Detection
    - Message Rate Limiting
    - Blacklist Words/Phrases
    - Discord Invite Detection
    - Mass Ping Detection
    - User Trust Scoring
    - Progressive Penalties
    - Auto-Actions (Delete, Warn, Mute, Kick, Ban)
    """
    
    def __init__(self, bot: discord.Client, db: AsyncIOMotorDatabase, redis_client=None):
        self.bot = bot
        self.db = db
        self.schema = AutoModSchema(db)
        self.redis = redis_client
        
        # In-memory caches for performance
        self.guild_settings_cache = {}  # guild_id -> settings
        self.guild_rules_cache = {}  # guild_id -> {rule_type: [rules]}
        self.user_message_history = defaultdict(lambda: deque(maxlen=10))  # (guild_id, user_id) -> deque
        self.user_rate_limits = defaultdict(list)  # (guild_id, user_id) -> [(timestamp, ...)]
        
        # Regex patterns
        self.url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        self.invite_pattern = re.compile(
            r'(?:https?://)?(?:www\.)?(?:discord\.gg|discord\.com/invite)/([a-zA-Z0-9-]+)',
            re.IGNORECASE
        )
        
        logger.info("AutoMod System initialized")
    
    async def initialize(self):
        """Initialize the system (create indexes, load settings)"""
        await self.schema.ensure_indexes()
        logger.info("AutoMod System ready")
    
    # ==================== Settings Management ====================
    
    async def get_guild_settings(self, guild_id: int, force_refresh: bool = False) -> Dict[str, Any]:
        """Get guild AutoMod settings (with caching)"""
        if not force_refresh and guild_id in self.guild_settings_cache:
            return self.guild_settings_cache[guild_id]
        
        settings = await self.schema.get_settings(guild_id)
        if not settings:
            settings = await self.schema.create_settings(guild_id)
        
        self.guild_settings_cache[guild_id] = settings
        return settings
    
    async def update_guild_settings(self, guild_id: int, updates: Dict[str, Any]) -> bool:
        """Update guild settings"""
        success = await self.schema.update_settings(guild_id, updates)
        if success and guild_id in self.guild_settings_cache:
            del self.guild_settings_cache[guild_id]
        return success
    
    async def is_automod_enabled(self, guild_id: int) -> bool:
        """Check if AutoMod is enabled for guild"""
        settings = await self.get_guild_settings(guild_id)
        return settings.get("enabled", False)
    
    # ==================== Rules Management ====================
    
    async def get_guild_rules(self, guild_id: int, rule_type: Optional[str] = None, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """Get guild rules (with caching)"""
        cache_key = guild_id
        
        if not force_refresh and cache_key in self.guild_rules_cache:
            cached = self.guild_rules_cache[cache_key]
            if rule_type:
                return cached.get(rule_type, [])
            return [rule for rules in cached.values() for rule in rules]
        
        # Load from database
        all_rules = await self.schema.get_guild_rules(guild_id, enabled_only=True)
        
        # Organize by type
        rules_by_type = defaultdict(list)
        for rule in all_rules:
            rules_by_type[rule["rule_type"]].append(rule)
        
        self.guild_rules_cache[cache_key] = dict(rules_by_type)
        
        if rule_type:
            return rules_by_type.get(rule_type, [])
        return all_rules
    
    async def refresh_rules_cache(self, guild_id: int):
        """Refresh rules cache for guild"""
        if guild_id in self.guild_rules_cache:
            del self.guild_rules_cache[guild_id]
        await self.get_guild_rules(guild_id, force_refresh=True)
    
    # ==================== Permission Checks ====================
    
    async def is_whitelisted(self, member: Member, rule: Dict[str, Any]) -> bool:
        """Check if member is whitelisted for a rule"""
        # Check whitelist roles
        whitelist_roles = rule.get("whitelist_roles", [])
        if whitelist_roles:
            member_role_ids = [role.id for role in member.roles]
            if any(role_id in member_role_ids for role_id in whitelist_roles):
                return True
        
        # Check guild settings for immune roles
        settings = await self.get_guild_settings(member.guild.id)
        immune_roles = settings.get("immune_roles", [])
        if immune_roles:
            member_role_ids = [role.id for role in member.roles]
            if any(role_id in member_role_ids for role_id in immune_roles):
                return True
        
        # Check if admin/moderator
        if member.guild_permissions.administrator or member.guild_permissions.manage_guild:
            return True
        
        return False
    
    async def is_channel_ignored(self, channel_id: int, guild_id: int) -> bool:
        """Check if channel is ignored"""
        settings = await self.get_guild_settings(guild_id)
        ignored_channels = settings.get("ignored_channels", [])
        return channel_id in ignored_channels
    
    # ==================== Message Checks ====================
    
    async def check_message(self, message: Message) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Check a message against all AutoMod rules.
        
        Returns:
            (should_action, rule_type, reason)
        """
        if not message.guild or message.author.bot:
            return False, None, None
        
        guild_id = message.guild.id
        
        # Check if AutoMod is enabled
        if not await self.is_automod_enabled(guild_id):
            return False, None, None
        
        # Check if channel is ignored
        if await self.is_channel_ignored(message.channel.id, guild_id):
            return False, None, None
        
        # Get all rules
        rules = await self.get_guild_rules(guild_id)
        if not rules:
            return False, None, None
        
        # Check each rule type
        checks = [
            ("spam", self.check_spam),
            ("rate_limit", self.check_rate_limit),
            ("links", self.check_links),
            ("invites", self.check_invites),
            ("mentions", self.check_mentions),
            ("caps", self.check_caps),
            ("emojis", self.check_emojis),
            ("blacklist", self.check_blacklist),
        ]
        
        for rule_type, check_func in checks:
            type_rules = await self.get_guild_rules(guild_id, rule_type)
            if not type_rules:
                continue
            
            for rule in type_rules:
                # Check if member is whitelisted
                if await self.is_whitelisted(message.author, rule):
                    continue
                
                # Check if rule is triggered
                triggered, reason = await check_func(message, rule)
                if triggered:
                    return True, rule_type, reason
        
        return False, None, None
    
    async def check_spam(self, message: Message, rule: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Check for spam (duplicate messages)"""
        guild_id = message.guild.id
        user_id = message.author.id
        key = (guild_id, user_id)
        
        duplicate_count = rule.get("duplicate_count", 3)
        time_window = rule.get("time_window", 10)
        
        # Add message to history
        history = self.user_message_history[key]
        history.append({
            "content": message.content.lower().strip(),
            "timestamp": datetime.utcnow()
        })
        
        # Check for duplicates within time window
        cutoff = datetime.utcnow() - timedelta(seconds=time_window)
        recent_messages = [
            msg for msg in history
            if msg["timestamp"] > cutoff
        ]
        
        if len(recent_messages) < duplicate_count:
            return False, None
        
        # Count identical messages
        current_content = message.content.lower().strip()
        identical_count = sum(
            1 for msg in recent_messages
            if msg["content"] == current_content
        )
        
        if identical_count >= duplicate_count:
            return True, f"Spam detected: {identical_count} identical messages in {time_window}s"
        
        return False, None
    
    async def check_rate_limit(self, message: Message, rule: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Check message rate limiting"""
        guild_id = message.guild.id
        user_id = message.author.id
        key = (guild_id, user_id)
        
        messages_count = rule.get("messages_count", 5)
        time_window = rule.get("time_window", 5)
        
        # Add timestamp
        now = datetime.utcnow()
        self.user_rate_limits[key].append(now)
        
        # Remove old timestamps
        cutoff = now - timedelta(seconds=time_window)
        self.user_rate_limits[key] = [
            ts for ts in self.user_rate_limits[key]
            if ts > cutoff
        ]
        
        # Check if exceeded
        if len(self.user_rate_limits[key]) >= messages_count:
            return True, f"Rate limit exceeded: {len(self.user_rate_limits[key])} messages in {time_window}s"
        
        return False, None
    
    async def check_links(self, message: Message, rule: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Check for links"""
        urls = self.url_pattern.findall(message.content)
        if not urls:
            return False, None
        
        block_all = rule.get("block_all_links", False)
        whitelist = rule.get("allow_whitelist", [])
        
        if block_all:
            # Check if any URL is in whitelist
            if whitelist:
                for url in urls:
                    if not any(allowed in url for allowed in whitelist):
                        return True, f"Unauthorized link detected: {url}"
            else:
                return True, f"Links are not allowed ({len(urls)} found)"
        
        return False, None
    
    async def check_invites(self, message: Message, rule: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Check for Discord invite links"""
        invites = self.invite_pattern.findall(message.content)
        if invites:
            return True, f"Discord invite link detected: {len(invites)} invite(s)"
        return False, None
    
    async def check_mentions(self, message: Message, rule: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Check for mention spam"""
        max_mentions = rule.get("max_mentions", 5)
        include_roles = rule.get("include_roles", True)
        
        total_mentions = len(message.mentions)
        if include_roles:
            total_mentions += len(message.role_mentions)
        
        if total_mentions >= max_mentions:
            return True, f"Excessive mentions: {total_mentions} (max: {max_mentions})"
        
        return False, None
    
    async def check_caps(self, message: Message, rule: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Check for excessive caps lock"""
        percentage = rule.get("percentage", 70)
        min_length = rule.get("min_length", 10)
        
        content = message.content
        if len(content) < min_length:
            return False, None
        
        # Remove URLs and mentions
        clean_content = self.url_pattern.sub('', content)
        clean_content = re.sub(r'<@!?\d+>', '', clean_content)
        clean_content = re.sub(r'<@&\d+>', '', clean_content)
        
        # Count letters
        letters = [c for c in clean_content if c.isalpha()]
        if not letters:
            return False, None
        
        caps_count = sum(1 for c in letters if c.isupper())
        caps_percentage = (caps_count / len(letters)) * 100
        
        if caps_percentage >= percentage:
            return True, f"Excessive caps: {caps_percentage:.1f}% (max: {percentage}%)"
        
        return False, None
    
    async def check_emojis(self, message: Message, rule: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Check for emoji spam"""
        max_emojis = rule.get("max_emojis", 10)
        
        # Count custom emojis
        custom_emoji_pattern = re.compile(r'<a?:\w+:\d+>')
        custom_emojis = custom_emoji_pattern.findall(message.content)
        
        # Count unicode emojis (basic check)
        unicode_emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+", 
            flags=re.UNICODE
        )
        unicode_emojis = unicode_emoji_pattern.findall(message.content)
        
        total_emojis = len(custom_emojis) + len(unicode_emojis)
        
        if total_emojis >= max_emojis:
            return True, f"Excessive emojis: {total_emojis} (max: {max_emojis})"
        
        return False, None
    
    async def check_blacklist(self, message: Message, rule: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Check for blacklisted words/phrases"""
        words = rule.get("words", [])
        if not words:
            return False, None
        
        case_sensitive = rule.get("case_sensitive", False)
        content = message.content if case_sensitive else message.content.lower()
        
        for word in words:
            check_word = word if case_sensitive else word.lower()
            if check_word in content:
                return True, f"Blacklisted word detected: {word}"
        
        return False, None
    
    # ==================== Trust Score System ====================
    
    async def get_or_create_trust_score(self, guild_id: int, member: Member) -> Dict[str, Any]:
        """Get or create user trust score"""
        user_id = member.id
        
        score_doc = await self.schema.get_trust_score(guild_id, user_id)
        if score_doc:
            return score_doc
        
        # Calculate account age
        account_age = (datetime.utcnow() - member.created_at).days
        
        # Create new score
        return await self.schema.create_trust_score(guild_id, user_id, account_age)
    
    async def update_trust_score(
        self,
        guild_id: int,
        user_id: int,
        change: int,
        reason: str
    ) -> bool:
        """Update user trust score"""
        return await self.schema.update_trust_score(guild_id, user_id, change, reason)
    
    async def check_suspicious_user(self, member: Member) -> Tuple[bool, str]:
        """Check if user is suspicious based on trust score"""
        guild_id = member.guild.id
        score_doc = await self.get_or_create_trust_score(guild_id, member)
        
        score = score_doc["score"]
        
        if score < 20:
            return True, "Very low trust score (< 20)"
        elif score < 40:
            return True, "Low trust score (< 40)"
        
        return False, ""
    
    # ==================== Auto-Actions ====================
    
    async def execute_action(
        self,
        message: Message,
        rule: Dict[str, Any],
        rule_type: str,
        reason: str
    ) -> bool:
        """Execute the configured action for a rule violation"""
        action = rule.get("action", "delete")
        guild_id = message.guild.id
        user_id = message.author.id
        
        try:
            # Delete message
            if action in ["delete", "warn", "mute", "kick", "ban"]:
                try:
                    await message.delete()
                except discord.Forbidden:
                    logger.warning(f"Cannot delete message in {guild_id}: Missing permissions")
                except discord.NotFound:
                    pass  # Message already deleted
            
            # Execute action
            if action == "delete":
                await self._log_action(guild_id, user_id, "message_deleted", rule_type, reason, message)
            
            elif action == "warn":
                await self._warn_user(message, rule, rule_type, reason)
            
            elif action == "mute":
                await self._mute_user(message, rule, rule_type, reason)
            
            elif action == "kick":
                await self._kick_user(message, rule, rule_type, reason)
            
            elif action == "ban":
                await self._ban_user(message, rule, rule_type, reason)
            
            # Update trust score
            score_changes = {
                "delete": -2,
                "warn": -5,
                "mute": -10,
                "kick": -20,
                "ban": -30
            }
            change = score_changes.get(action, -2)
            await self.update_trust_score(guild_id, user_id, change, f"AutoMod: {action}")
            
            # Increment violations
            await self.schema.increment_violations(guild_id, user_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Error executing action {action}: {e}")
            return False
    
    async def _warn_user(self, message: Message, rule: Dict[str, Any], rule_type: str, reason: str):
        """Warn user"""
        # Log action
        await self._log_action(
            message.guild.id,
            message.author.id,
            "user_warned",
            rule_type,
            reason,
            message
        )
        
        # Send DM
        settings = await self.get_guild_settings(message.guild.id)
        if settings.get("dm_users", True):
            try:
                custom_message = rule.get("custom_message") or f"⚠️ You have been warned for: {reason}"
                await message.author.send(
                    f"**Warning from {message.guild.name}**\n{custom_message}"
                )
            except discord.Forbidden:
                pass
    
    async def _mute_user(self, message: Message, rule: Dict[str, Any], rule_type: str, reason: str):
        """Mute user (timeout)"""
        duration = rule.get("duration", 3600)  # seconds
        
        try:
            # Timeout user
            timeout_until = datetime.utcnow() + timedelta(seconds=duration)
            await message.author.timeout(timeout_until, reason=f"AutoMod: {reason}")
            
            # Log action
            await self._log_action(
                message.guild.id,
                message.author.id,
                "user_muted",
                rule_type,
                reason,
                message,
                duration=duration
            )
            
            # Send DM
            settings = await self.get_guild_settings(message.guild.id)
            if settings.get("dm_users", True):
                try:
                    custom_message = rule.get("custom_message") or f"🔇 You have been muted for {duration//60} minutes: {reason}"
                    await message.author.send(
                        f"**Muted in {message.guild.name}**\n{custom_message}"
                    )
                except discord.Forbidden:
                    pass
                    
        except discord.Forbidden:
            logger.warning(f"Cannot mute user in {message.guild.id}: Missing permissions")
    
    async def _kick_user(self, message: Message, rule: Dict[str, Any], rule_type: str, reason: str):
        """Kick user"""
        try:
            # Kick
            await message.author.kick(reason=f"AutoMod: {reason}")
            
            # Log action
            await self._log_action(
                message.guild.id,
                message.author.id,
                "user_kicked",
                rule_type,
                reason,
                message
            )
            
        except discord.Forbidden:
            logger.warning(f"Cannot kick user in {message.guild.id}: Missing permissions")
    
    async def _ban_user(self, message: Message, rule: Dict[str, Any], rule_type: str, reason: str):
        """Ban user"""
        try:
            # Ban
            await message.author.ban(reason=f"AutoMod: {reason}", delete_message_days=1)
            
            # Log action
            await self._log_action(
                message.guild.id,
                message.author.id,
                "user_banned",
                rule_type,
                reason,
                message
            )
            
        except discord.Forbidden:
            logger.warning(f"Cannot ban user in {message.guild.id}: Missing permissions")
    
    async def _log_action(
        self,
        guild_id: int,
        user_id: int,
        action: str,
        rule_type: str,
        reason: str,
        message: Optional[Message] = None,
        duration: Optional[int] = None
    ):
        """Log an AutoMod action"""
        log_data = {
            "guild_id": guild_id,
            "user_id": user_id,
            "moderator_id": self.bot.user.id,
            "action": action,
            "rule_type": rule_type,
            "reason": reason
        }
        
        if message:
            log_data["message_content"] = message.content[:1000]
            log_data["channel_id"] = message.channel.id
        
        if duration:
            log_data["duration"] = duration
        
        await self.schema.log_action(log_data)
        
        # Send to log channel
        settings = await self.get_guild_settings(guild_id)
        log_channel_id = settings.get("log_channel_id")
        
        if log_channel_id:
            try:
                channel = self.bot.get_channel(log_channel_id)
                if channel:
                    embed = discord.Embed(
                        title="🛡️ AutoMod Action",
                        description=f"**Action:** {action}\n**Rule:** {rule_type}\n**Reason:** {reason}",
                        color=discord.Color.orange(),
                        timestamp=datetime.utcnow()
                    )
                    embed.add_field(name="User", value=f"<@{user_id}>", inline=True)
                    if message:
                        embed.add_field(name="Channel", value=message.channel.mention, inline=True)
                    if duration:
                        embed.add_field(name="Duration", value=f"{duration//60} minutes", inline=True)
                    
                    await channel.send(embed=embed)
            except Exception as e:
                logger.error(f"Error sending to log channel: {e}")
    
    # ==================== Progressive Penalties ====================
    
    async def get_progressive_action(self, guild_id: int, user_id: int) -> str:
        """Get progressive action based on recent violations"""
        settings = await self.get_guild_settings(guild_id)
        if not settings.get("progressive_penalties", True):
            return "delete"
        
        # Get recent violations (last hour)
        violations = await self.schema.get_recent_violations(guild_id, user_id, minutes=60)
        violation_count = len(violations)
        
        # Progressive scale
        if violation_count <= 2:
            return "delete"
        elif violation_count <= 4:
            return "warn"
        elif violation_count <= 6:
            return "mute"
        elif violation_count <= 8:
            return "kick"
        else:
            return "ban"
    
    # ==================== Statistics ====================
    
    async def get_statistics(self, guild_id: int, days: int = 30) -> Dict[str, Any]:
        """Get AutoMod statistics"""
        return await self.schema.get_statistics(guild_id, days)
    
    async def get_user_violations(self, guild_id: int, user_id: int, days: int = 7) -> int:
        """Get user violation count"""
        return await self.schema.count_user_violations(guild_id, user_id, days)


# Export
__all__ = ["AutoModSystem"]
