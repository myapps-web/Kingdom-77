"""
Kingdom-77 Bot - Advanced Logging System Core
Comprehensive event tracking for all Discord server activities
"""

import discord
from discord.ext import commands
from typing import Optional, Dict, Any
from datetime import datetime
from database.logging_schema import LoggingSchema


class LoggingSystem:
    """Core logging system with event handlers"""
    
    def __init__(self, bot: commands.Bot, db_schema: LoggingSchema):
        self.bot = bot
        self.db = db_schema
        self.message_cache = {}  # In-memory cache for quick lookups
        
    async def initialize(self):
        """Initialize the logging system"""
        await self.db.create_indexes()
        print("✅ Logging System initialized successfully")
    
    # ==================== Settings Helpers ====================
    
    async def _get_settings(self, guild_id: int) -> Optional[Dict[str, Any]]:
        """Get logging settings for a guild"""
        settings = await self.db.get_server_settings(guild_id)
        if not settings:
            settings = await self.db.create_default_settings(guild_id)
        return settings
    
    async def _is_log_enabled(self, guild_id: int, log_type: str) -> bool:
        """Check if a specific log type is enabled"""
        settings = await self._get_settings(guild_id)
        if not settings or not settings.get("enabled"):
            return False
        return settings.get("log_types", {}).get(log_type, False)
    
    async def _get_log_channel(self, guild_id: int, log_category: str) -> Optional[discord.TextChannel]:
        """Get the logging channel for a specific category"""
        settings = await self._get_settings(guild_id)
        if not settings:
            return None
        
        channel_id = settings.get("channels", {}).get(log_category)
        if not channel_id:
            return None
        
        guild = self.bot.get_guild(guild_id)
        if not guild:
            return None
        
        return guild.get_channel(channel_id)
    
    async def _should_ignore(self, guild_id: int, member: discord.Member = None, channel: discord.TextChannel = None) -> bool:
        """Check if event should be ignored"""
        settings = await self._get_settings(guild_id)
        if not settings:
            return True
        
        # Check if bots should be ignored
        if member and member.bot and not settings.get("settings", {}).get("log_bots", False):
            return True
        
        # Check ignored channels
        if channel and channel.id in settings.get("ignored_channels", []):
            return True
        
        # Check ignored roles
        if member:
            for role in member.roles:
                if role.id in settings.get("ignored_roles", []):
                    return True
        
        # Check ignored users
        if member and member.id in settings.get("ignored_users", []):
            return True
        
        return False
    
    # ==================== Message Events ====================
    
    async def on_message(self, message: discord.Message):
        """Cache message for potential deletion"""
        if not message.guild or message.author.bot:
            return
        
        settings = await self._get_settings(message.guild.id)
        if not settings or not settings.get("settings", {}).get("cache_messages", True):
            return
        
        # Cache message
        await self.db.cache_message(message)
        self.message_cache[message.id] = {
            "content": message.content,
            "embeds": [e.to_dict() for e in message.embeds],
            "attachments": [{"filename": a.filename, "url": a.url, "size": a.size} for a in message.attachments],
            "author_id": message.author.id
        }
    
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        """Handle message edit event"""
        if not after.guild or after.author.bot:
            return
        
        guild_id = after.guild.id
        
        # Check if logging is enabled
        if not await self._is_log_enabled(guild_id, "message_edit"):
            return
        
        # Check if should ignore
        if await self._should_ignore(guild_id, after.author, after.channel):
            return
        
        # Ignore if content is the same (embed update)
        if before.content == after.content:
            return
        
        # Log to database
        await self.db.log_message_edit(
            guild_id=guild_id,
            message_id=after.id,
            channel_id=after.channel.id,
            user_id=after.author.id,
            before_content=before.content,
            after_content=after.content,
            before_embeds=[e.to_dict() for e in before.embeds],
            after_embeds=[e.to_dict() for e in after.embeds]
        )
        
        # Send to log channel
        log_channel = await self._get_log_channel(guild_id, "message_logs")
        if log_channel:
            embed = discord.Embed(
                title="📝 Message Edited",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Author", value=after.author.mention, inline=True)
            embed.add_field(name="Channel", value=after.channel.mention, inline=True)
            embed.add_field(name="Message ID", value=f"`{after.id}`", inline=True)
            
            # Show before/after content (truncate if too long)
            before_text = before.content[:1024] if before.content else "*No content*"
            after_text = after.content[:1024] if after.content else "*No content*"
            
            embed.add_field(name="Before", value=before_text, inline=False)
            embed.add_field(name="After", value=after_text, inline=False)
            embed.add_field(name="Jump to Message", value=f"[Click here]({after.jump_url})", inline=False)
            
            embed.set_footer(text=f"User ID: {after.author.id}")
            
            try:
                await log_channel.send(embed=embed)
            except Exception as e:
                print(f"❌ Failed to send message edit log: {e}")
    
    async def on_message_delete(self, message: discord.Message):
        """Handle message delete event"""
        if not message.guild or message.author.bot:
            return
        
        guild_id = message.guild.id
        
        # Check if logging is enabled
        if not await self._is_log_enabled(guild_id, "message_delete"):
            return
        
        # Check if should ignore
        if await self._should_ignore(guild_id, message.author, message.channel):
            return
        
        # Get cached message content
        cached = await self.db.get_cached_message(message.id)
        content = cached["content"] if cached else message.content
        embeds = cached.get("embeds", []) if cached else [e.to_dict() for e in message.embeds]
        attachments = cached.get("attachments", []) if cached else [
            {"filename": a.filename, "url": a.url, "size": a.size} for a in message.attachments
        ]
        
        # Log to database
        await self.db.log_message_delete(
            guild_id=guild_id,
            message_id=message.id,
            channel_id=message.channel.id,
            user_id=message.author.id,
            content=content,
            embeds=embeds,
            attachments=attachments
        )
        
        # Send to log channel
        log_channel = await self._get_log_channel(guild_id, "message_logs")
        if log_channel:
            embed = discord.Embed(
                title="🗑️ Message Deleted",
                color=discord.Color.red(),
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Author", value=message.author.mention, inline=True)
            embed.add_field(name="Channel", value=message.channel.mention, inline=True)
            embed.add_field(name="Message ID", value=f"`{message.id}`", inline=True)
            
            # Show content (truncate if too long)
            content_text = content[:1024] if content else "*No content*"
            embed.add_field(name="Content", value=content_text, inline=False)
            
            # Show attachments
            if attachments:
                attachment_text = "\n".join([f"📎 {a['filename']} ({a['size']} bytes)" for a in attachments[:5]])
                embed.add_field(name="Attachments", value=attachment_text, inline=False)
            
            embed.set_footer(text=f"User ID: {message.author.id}")
            
            # Show author avatar
            embed.set_author(name=str(message.author), icon_url=message.author.display_avatar.url)
            
            try:
                await log_channel.send(embed=embed)
            except Exception as e:
                print(f"❌ Failed to send message delete log: {e}")
    
    async def on_bulk_message_delete(self, messages: list[discord.Message]):
        """Handle bulk message delete event"""
        if not messages or not messages[0].guild:
            return
        
        guild_id = messages[0].guild.id
        channel = messages[0].channel
        
        # Check if logging is enabled
        if not await self._is_log_enabled(guild_id, "message_delete"):
            return
        
        # Prepare messages data
        messages_data = []
        for msg in messages[:50]:  # Limit to 50 messages
            if not msg.author.bot:
                messages_data.append({
                    "message_id": msg.id,
                    "user_id": msg.author.id,
                    "username": str(msg.author),
                    "content": msg.content[:200],  # Truncate
                    "timestamp": msg.created_at
                })
        
        if not messages_data:
            return
        
        # Log to database
        await self.db.log_bulk_delete(
            guild_id=guild_id,
            channel_id=channel.id,
            messages_count=len(messages),
            deleted_by=0,  # Unknown who deleted
            messages_data=messages_data
        )
        
        # Send to log channel
        log_channel = await self._get_log_channel(guild_id, "message_logs")
        if log_channel:
            embed = discord.Embed(
                title="🗑️ Bulk Delete",
                description=f"{len(messages)} messages were deleted in {channel.mention}",
                color=discord.Color.dark_red(),
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Channel", value=channel.mention, inline=True)
            embed.add_field(name="Count", value=str(len(messages)), inline=True)
            
            # Show some message previews
            preview_text = ""
            for i, data in enumerate(messages_data[:10], 1):
                preview_text += f"{i}. **{data['username']}**: {data['content'][:50]}...\n"
            
            if preview_text:
                embed.add_field(name="Sample Messages", value=preview_text, inline=False)
            
            try:
                await log_channel.send(embed=embed)
            except Exception as e:
                print(f"❌ Failed to send bulk delete log: {e}")
    
    # ==================== Member Events ====================
    
    async def on_member_join(self, member: discord.Member):
        """Handle member join event"""
        guild_id = member.guild.id
        
        # Check if logging is enabled
        if not await self._is_log_enabled(guild_id, "member_join"):
            return
        
        # Calculate account age
        account_age = (datetime.utcnow() - member.created_at.replace(tzinfo=None)).days
        
        # Log to database
        await self.db.log_member_join(
            guild_id=guild_id,
            user_id=member.id,
            username=member.name,
            discriminator=member.discriminator,
            avatar_url=str(member.display_avatar.url),
            account_age_days=account_age,
            is_bot=member.bot
        )
        
        # Send to log channel
        log_channel = await self._get_log_channel(guild_id, "member_logs")
        if log_channel:
            embed = discord.Embed(
                title="📥 Member Joined",
                description=f"{member.mention} joined the server",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.add_field(name="Username", value=str(member), inline=True)
            embed.add_field(name="ID", value=f"`{member.id}`", inline=True)
            embed.add_field(name="Account Age", value=f"{account_age} days", inline=True)
            embed.add_field(name="Created At", value=f"<t:{int(member.created_at.timestamp())}:F>", inline=False)
            embed.add_field(name="Member Count", value=str(member.guild.member_count), inline=True)
            
            # Warning for new accounts
            if account_age < 7:
                embed.add_field(name="⚠️ Warning", value="This account is less than 7 days old", inline=False)
            
            embed.set_footer(text=f"User ID: {member.id}")
            
            try:
                await log_channel.send(embed=embed)
            except Exception as e:
                print(f"❌ Failed to send member join log: {e}")
    
    async def on_member_remove(self, member: discord.Member):
        """Handle member leave event"""
        guild_id = member.guild.id
        
        # Check if logging is enabled
        if not await self._is_log_enabled(guild_id, "member_leave"):
            return
        
        # Get roles
        roles = [role.id for role in member.roles if role.name != "@everyone"]
        
        # Log to database
        await self.db.log_member_leave(
            guild_id=guild_id,
            user_id=member.id,
            username=str(member),
            roles=roles,
            joined_at=member.joined_at,
            reason=None
        )
        
        # Send to log channel
        log_channel = await self._get_log_channel(guild_id, "member_logs")
        if log_channel:
            # Calculate time in server
            duration_days = (datetime.utcnow() - member.joined_at.replace(tzinfo=None)).days if member.joined_at else 0
            
            embed = discord.Embed(
                title="📤 Member Left",
                description=f"{member.mention} left the server",
                color=discord.Color.orange(),
                timestamp=datetime.utcnow()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.add_field(name="Username", value=str(member), inline=True)
            embed.add_field(name="ID", value=f"`{member.id}`", inline=True)
            embed.add_field(name="Time in Server", value=f"{duration_days} days", inline=True)
            
            # Show roles
            if roles:
                role_mentions = [f"<@&{r}>" for r in roles[:10]]
                embed.add_field(name="Roles", value=", ".join(role_mentions), inline=False)
            
            embed.add_field(name="Member Count", value=str(member.guild.member_count), inline=True)
            embed.set_footer(text=f"User ID: {member.id}")
            
            try:
                await log_channel.send(embed=embed)
            except Exception as e:
                print(f"❌ Failed to send member leave log: {e}")
    
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        """Handle member update event"""
        guild_id = after.guild.id
        
        # Check if logging is enabled
        if not await self._is_log_enabled(guild_id, "member_update"):
            return
        
        # Check if should ignore
        if await self._should_ignore(guild_id, after):
            return
        
        changes = []
        
        # Nickname change
        if before.nick != after.nick:
            await self.db.log_member_update(
                guild_id=guild_id,
                user_id=after.id,
                update_type="nickname",
                before=before.nick,
                after=after.nick
            )
            changes.append(("Nickname", before.nick or "None", after.nick or "None"))
        
        # Roles change
        before_roles = set(before.roles)
        after_roles = set(after.roles)
        if before_roles != after_roles:
            added = [r.name for r in after_roles - before_roles]
            removed = [r.name for r in before_roles - after_roles]
            
            if added or removed:
                await self.db.log_member_update(
                    guild_id=guild_id,
                    user_id=after.id,
                    update_type="roles",
                    before=[r.name for r in before_roles],
                    after=[r.name for r in after_roles]
                )
                
                if added:
                    changes.append(("Roles Added", None, ", ".join(added)))
                if removed:
                    changes.append(("Roles Removed", ", ".join(removed), None))
        
        # Timeout change
        if before.timed_out_until != after.timed_out_until:
            await self.db.log_member_update(
                guild_id=guild_id,
                user_id=after.id,
                update_type="timeout",
                before=before.timed_out_until,
                after=after.timed_out_until
            )
            
            if after.timed_out_until:
                changes.append(("Timeout", "None", f"Until <t:{int(after.timed_out_until.timestamp())}:F>"))
            else:
                changes.append(("Timeout", "Active", "Removed"))
        
        # Send to log channel if changes exist
        if changes:
            log_channel = await self._get_log_channel(guild_id, "member_logs")
            if log_channel:
                embed = discord.Embed(
                    title="📝 Member Updated",
                    description=f"{after.mention}'s profile was updated",
                    color=discord.Color.blue(),
                    timestamp=datetime.utcnow()
                )
                embed.set_thumbnail(url=after.display_avatar.url)
                embed.add_field(name="Member", value=after.mention, inline=True)
                embed.add_field(name="ID", value=f"`{after.id}`", inline=True)
                
                for change_type, before_val, after_val in changes:
                    if before_val and after_val:
                        embed.add_field(name=f"{change_type}", value=f"Before: {before_val}\nAfter: {after_val}", inline=False)
                    elif after_val:
                        embed.add_field(name=f"{change_type}", value=after_val, inline=False)
                    elif before_val:
                        embed.add_field(name=f"{change_type}", value=f"Removed: {before_val}", inline=False)
                
                embed.set_footer(text=f"User ID: {after.id}")
                
                try:
                    await log_channel.send(embed=embed)
                except Exception as e:
                    print(f"❌ Failed to send member update log: {e}")
    
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        """Handle member ban event"""
        guild_id = guild.id
        
        # Check if logging is enabled
        if not await self._is_log_enabled(guild_id, "member_ban"):
            return
        
        # Try to get ban reason from audit log
        reason = None
        banned_by = None
        try:
            async for entry in guild.audit_logs(action=discord.AuditLogAction.ban, limit=5):
                if entry.target.id == user.id:
                    reason = entry.reason
                    banned_by = entry.user.id
                    break
        except:
            pass
        
        # Log to database
        await self.db.log_member_ban(
            guild_id=guild_id,
            user_id=user.id,
            username=str(user),
            banned_by=banned_by,
            reason=reason
        )
        
        # Send to log channel
        log_channel = await self._get_log_channel(guild_id, "member_logs")
        if log_channel:
            embed = discord.Embed(
                title="🔨 Member Banned",
                description=f"{user.mention} was banned from the server",
                color=discord.Color.dark_red(),
                timestamp=datetime.utcnow()
            )
            embed.set_thumbnail(url=user.display_avatar.url)
            embed.add_field(name="Username", value=str(user), inline=True)
            embed.add_field(name="ID", value=f"`{user.id}`", inline=True)
            
            if banned_by:
                embed.add_field(name="Banned By", value=f"<@{banned_by}>", inline=True)
            
            if reason:
                embed.add_field(name="Reason", value=reason, inline=False)
            
            embed.set_footer(text=f"User ID: {user.id}")
            
            try:
                await log_channel.send(embed=embed)
            except Exception as e:
                print(f"❌ Failed to send ban log: {e}")
    
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        """Handle member unban event"""
        guild_id = guild.id
        
        # Check if logging is enabled
        if not await self._is_log_enabled(guild_id, "member_unban"):
            return
        
        # Try to get unban reason from audit log
        reason = None
        unbanned_by = None
        try:
            async for entry in guild.audit_logs(action=discord.AuditLogAction.unban, limit=5):
                if entry.target.id == user.id:
                    reason = entry.reason
                    unbanned_by = entry.user.id
                    break
        except:
            pass
        
        # Log to database
        await self.db.log_member_unban(
            guild_id=guild_id,
            user_id=user.id,
            username=str(user),
            unbanned_by=unbanned_by,
            reason=reason
        )
        
        # Send to log channel
        log_channel = await self._get_log_channel(guild_id, "member_logs")
        if log_channel:
            embed = discord.Embed(
                title="✅ Member Unbanned",
                description=f"{user.mention} was unbanned",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            embed.set_thumbnail(url=user.display_avatar.url)
            embed.add_field(name="Username", value=str(user), inline=True)
            embed.add_field(name="ID", value=f"`{user.id}`", inline=True)
            
            if unbanned_by:
                embed.add_field(name="Unbanned By", value=f"<@{unbanned_by}>", inline=True)
            
            if reason:
                embed.add_field(name="Reason", value=reason, inline=False)
            
            embed.set_footer(text=f"User ID: {user.id}")
            
            try:
                await log_channel.send(embed=embed)
            except Exception as e:
                print(f"❌ Failed to send unban log: {e}")
    
    # ==================== Channel Events ====================
    
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        """Handle channel create event"""
        guild_id = channel.guild.id
        
        # Check if logging is enabled
        if not await self._is_log_enabled(guild_id, "channel_create"):
            return
        
        # Try to get creator from audit log
        created_by = None
        try:
            async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_create, limit=5):
                if entry.target.id == channel.id:
                    created_by = entry.user.id
                    break
        except:
            pass
        
        # Log to database
        await self.db.log_channel_create(
            guild_id=guild_id,
            channel_id=channel.id,
            channel_name=channel.name,
            channel_type=str(channel.type),
            created_by=created_by,
            category=channel.category.id if channel.category else None
        )
        
        # Send to log channel
        log_channel = await self._get_log_channel(guild_id, "channel_logs")
        if log_channel:
            embed = discord.Embed(
                title="📢 Channel Created",
                description=f"Channel {channel.mention} was created",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Name", value=channel.name, inline=True)
            embed.add_field(name="Type", value=str(channel.type), inline=True)
            embed.add_field(name="ID", value=f"`{channel.id}`", inline=True)
            
            if channel.category:
                embed.add_field(name="Category", value=channel.category.name, inline=True)
            
            if created_by:
                embed.add_field(name="Created By", value=f"<@{created_by}>", inline=True)
            
            try:
                await log_channel.send(embed=embed)
            except Exception as e:
                print(f"❌ Failed to send channel create log: {e}")
    
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        """Handle channel delete event"""
        guild_id = channel.guild.id
        
        # Check if logging is enabled
        if not await self._is_log_enabled(guild_id, "channel_delete"):
            return
        
        # Try to get deleter from audit log
        deleted_by = None
        try:
            async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=5):
                if entry.target.id == channel.id:
                    deleted_by = entry.user.id
                    break
        except:
            pass
        
        # Log to database
        await self.db.log_channel_delete(
            guild_id=guild_id,
            channel_id=channel.id,
            channel_name=channel.name,
            channel_type=str(channel.type),
            deleted_by=deleted_by
        )
        
        # Send to log channel
        log_channel = await self._get_log_channel(guild_id, "channel_logs")
        if log_channel and log_channel.id != channel.id:  # Don't try to log to deleted channel
            embed = discord.Embed(
                title="🗑️ Channel Deleted",
                description=f"Channel `#{channel.name}` was deleted",
                color=discord.Color.red(),
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Name", value=channel.name, inline=True)
            embed.add_field(name="Type", value=str(channel.type), inline=True)
            embed.add_field(name="ID", value=f"`{channel.id}`", inline=True)
            
            if deleted_by:
                embed.add_field(name="Deleted By", value=f"<@{deleted_by}>", inline=True)
            
            try:
                await log_channel.send(embed=embed)
            except Exception as e:
                print(f"❌ Failed to send channel delete log: {e}")
    
    async def on_guild_channel_update(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel):
        """Handle channel update event"""
        guild_id = after.guild.id
        
        # Check if logging is enabled
        if not await self._is_log_enabled(guild_id, "channel_update"):
            return
        
        changes = []
        
        # Name change
        if before.name != after.name:
            await self.db.log_channel_update(
                guild_id=guild_id,
                channel_id=after.id,
                update_type="name",
                before=before.name,
                after=after.name
            )
            changes.append(("Name", before.name, after.name))
        
        # Topic change (text channels)
        if hasattr(before, 'topic') and hasattr(after, 'topic'):
            if before.topic != after.topic:
                await self.db.log_channel_update(
                    guild_id=guild_id,
                    channel_id=after.id,
                    update_type="topic",
                    before=before.topic,
                    after=after.topic
                )
                changes.append(("Topic", before.topic or "None", after.topic or "None"))
        
        # Slowmode change
        if hasattr(before, 'slowmode_delay') and hasattr(after, 'slowmode_delay'):
            if before.slowmode_delay != after.slowmode_delay:
                await self.db.log_channel_update(
                    guild_id=guild_id,
                    channel_id=after.id,
                    update_type="slowmode",
                    before=before.slowmode_delay,
                    after=after.slowmode_delay
                )
                changes.append(("Slowmode", f"{before.slowmode_delay}s", f"{after.slowmode_delay}s"))
        
        # NSFW change
        if hasattr(before, 'nsfw') and hasattr(after, 'nsfw'):
            if before.nsfw != after.nsfw:
                await self.db.log_channel_update(
                    guild_id=guild_id,
                    channel_id=after.id,
                    update_type="nsfw",
                    before=before.nsfw,
                    after=after.nsfw
                )
                changes.append(("NSFW", str(before.nsfw), str(after.nsfw)))
        
        # Send to log channel if changes exist
        if changes:
            log_channel = await self._get_log_channel(guild_id, "channel_logs")
            if log_channel:
                embed = discord.Embed(
                    title="📝 Channel Updated",
                    description=f"Channel {after.mention} was updated",
                    color=discord.Color.blue(),
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="Channel", value=after.mention, inline=True)
                embed.add_field(name="ID", value=f"`{after.id}`", inline=True)
                
                for change_type, before_val, after_val in changes:
                    embed.add_field(name=change_type, value=f"Before: {before_val}\nAfter: {after_val}", inline=False)
                
                try:
                    await log_channel.send(embed=embed)
                except Exception as e:
                    print(f"❌ Failed to send channel update log: {e}")
    
    # ==================== Role Events ====================
    
    async def on_guild_role_create(self, role: discord.Role):
        """Handle role create event"""
        guild_id = role.guild.id
        
        # Check if logging is enabled
        if not await self._is_log_enabled(guild_id, "role_create"):
            return
        
        # Try to get creator from audit log
        created_by = None
        try:
            async for entry in role.guild.audit_logs(action=discord.AuditLogAction.role_create, limit=5):
                if entry.target.id == role.id:
                    created_by = entry.user.id
                    break
        except:
            pass
        
        # Log to database
        await self.db.log_role_create(
            guild_id=guild_id,
            role_id=role.id,
            role_name=role.name,
            color=role.color.value,
            permissions=role.permissions.value,
            created_by=created_by
        )
        
        # Send to log channel
        log_channel = await self._get_log_channel(guild_id, "role_logs")
        if log_channel:
            embed = discord.Embed(
                title="🎭 Role Created",
                description=f"Role {role.mention} was created",
                color=role.color if role.color != discord.Color.default() else discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Name", value=role.name, inline=True)
            embed.add_field(name="Color", value=str(role.color), inline=True)
            embed.add_field(name="ID", value=f"`{role.id}`", inline=True)
            embed.add_field(name="Hoisted", value=str(role.hoist), inline=True)
            embed.add_field(name="Mentionable", value=str(role.mentionable), inline=True)
            
            if created_by:
                embed.add_field(name="Created By", value=f"<@{created_by}>", inline=True)
            
            try:
                await log_channel.send(embed=embed)
            except Exception as e:
                print(f"❌ Failed to send role create log: {e}")
    
    async def on_guild_role_delete(self, role: discord.Role):
        """Handle role delete event"""
        guild_id = role.guild.id
        
        # Check if logging is enabled
        if not await self._is_log_enabled(guild_id, "role_delete"):
            return
        
        # Try to get deleter from audit log
        deleted_by = None
        try:
            async for entry in role.guild.audit_logs(action=discord.AuditLogAction.role_delete, limit=5):
                if entry.target.id == role.id:
                    deleted_by = entry.user.id
                    break
        except:
            pass
        
        # Log to database
        await self.db.log_role_delete(
            guild_id=guild_id,
            role_id=role.id,
            role_name=role.name,
            deleted_by=deleted_by
        )
        
        # Send to log channel
        log_channel = await self._get_log_channel(guild_id, "role_logs")
        if log_channel:
            embed = discord.Embed(
                title="🗑️ Role Deleted",
                description=f"Role `@{role.name}` was deleted",
                color=discord.Color.red(),
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Name", value=role.name, inline=True)
            embed.add_field(name="Color", value=str(role.color), inline=True)
            embed.add_field(name="ID", value=f"`{role.id}`", inline=True)
            
            if deleted_by:
                embed.add_field(name="Deleted By", value=f"<@{deleted_by}>", inline=True)
            
            try:
                await log_channel.send(embed=embed)
            except Exception as e:
                print(f"❌ Failed to send role delete log: {e}")
    
    async def on_guild_role_update(self, before: discord.Role, after: discord.Role):
        """Handle role update event"""
        guild_id = after.guild.id
        
        # Check if logging is enabled
        if not await self._is_log_enabled(guild_id, "role_update"):
            return
        
        changes = []
        
        # Name change
        if before.name != after.name:
            await self.db.log_role_update(
                guild_id=guild_id,
                role_id=after.id,
                update_type="name",
                before=before.name,
                after=after.name
            )
            changes.append(("Name", before.name, after.name))
        
        # Color change
        if before.color != after.color:
            await self.db.log_role_update(
                guild_id=guild_id,
                role_id=after.id,
                update_type="color",
                before=str(before.color),
                after=str(after.color)
            )
            changes.append(("Color", str(before.color), str(after.color)))
        
        # Permissions change
        if before.permissions != after.permissions:
            await self.db.log_role_update(
                guild_id=guild_id,
                role_id=after.id,
                update_type="permissions",
                before=before.permissions.value,
                after=after.permissions.value
            )
            changes.append(("Permissions", "Changed", "See audit log"))
        
        # Send to log channel if changes exist
        if changes:
            log_channel = await self._get_log_channel(guild_id, "role_logs")
            if log_channel:
                embed = discord.Embed(
                    title="📝 Role Updated",
                    description=f"Role {after.mention} was updated",
                    color=after.color if after.color != discord.Color.default() else discord.Color.blue(),
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="Role", value=after.mention, inline=True)
                embed.add_field(name="ID", value=f"`{after.id}`", inline=True)
                
                for change_type, before_val, after_val in changes:
                    embed.add_field(name=change_type, value=f"Before: {before_val}\nAfter: {after_val}", inline=False)
                
                try:
                    await log_channel.send(embed=embed)
                except Exception as e:
                    print(f"❌ Failed to send role update log: {e}")
    
    # ==================== Voice Events ====================
    
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        """Handle voice state update event"""
        guild_id = member.guild.id
        
        # Check if should ignore
        if await self._should_ignore(guild_id, member):
            return
        
        # Join voice channel
        if before.channel is None and after.channel is not None:
            if await self._is_log_enabled(guild_id, "voice_join"):
                await self.db.log_voice_join(
                    guild_id=guild_id,
                    user_id=member.id,
                    channel_id=after.channel.id,
                    channel_name=after.channel.name
                )
                
                log_channel = await self._get_log_channel(guild_id, "voice_logs")
                if log_channel:
                    embed = discord.Embed(
                        title="🔊 Voice Join",
                        description=f"{member.mention} joined {after.channel.mention}",
                        color=discord.Color.green(),
                        timestamp=datetime.utcnow()
                    )
                    embed.set_thumbnail(url=member.display_avatar.url)
                    try:
                        await log_channel.send(embed=embed)
                    except Exception as e:
                        print(f"❌ Failed to send voice join log: {e}")
        
        # Leave voice channel
        elif before.channel is not None and after.channel is None:
            if await self._is_log_enabled(guild_id, "voice_leave"):
                # Calculate duration (approximate)
                duration_seconds = 0  # Would need to track join times
                
                await self.db.log_voice_leave(
                    guild_id=guild_id,
                    user_id=member.id,
                    channel_id=before.channel.id,
                    channel_name=before.channel.name,
                    duration_seconds=duration_seconds
                )
                
                log_channel = await self._get_log_channel(guild_id, "voice_logs")
                if log_channel:
                    embed = discord.Embed(
                        title="🔇 Voice Leave",
                        description=f"{member.mention} left {before.channel.mention}",
                        color=discord.Color.red(),
                        timestamp=datetime.utcnow()
                    )
                    embed.set_thumbnail(url=member.display_avatar.url)
                    try:
                        await log_channel.send(embed=embed)
                    except Exception as e:
                        print(f"❌ Failed to send voice leave log: {e}")
        
        # Move between voice channels
        elif before.channel != after.channel and before.channel is not None and after.channel is not None:
            if await self._is_log_enabled(guild_id, "voice_move"):
                await self.db.log_voice_move(
                    guild_id=guild_id,
                    user_id=member.id,
                    before_channel_id=before.channel.id,
                    after_channel_id=after.channel.id,
                    before_channel_name=before.channel.name,
                    after_channel_name=after.channel.name
                )
                
                log_channel = await self._get_log_channel(guild_id, "voice_logs")
                if log_channel:
                    embed = discord.Embed(
                        title="🔀 Voice Move",
                        description=f"{member.mention} moved from {before.channel.mention} to {after.channel.mention}",
                        color=discord.Color.blue(),
                        timestamp=datetime.utcnow()
                    )
                    embed.set_thumbnail(url=member.display_avatar.url)
                    try:
                        await log_channel.send(embed=embed)
                    except Exception as e:
                        print(f"❌ Failed to send voice move log: {e}")
    
    # ==================== Server Events ====================
    
    async def on_guild_update(self, before: discord.Guild, after: discord.Guild):
        """Handle server update event"""
        guild_id = after.id
        
        # Check if logging is enabled
        if not await self._is_log_enabled(guild_id, "server_update"):
            return
        
        changes = []
        
        # Name change
        if before.name != after.name:
            await self.db.log_server_update(
                guild_id=guild_id,
                update_type="name",
                before=before.name,
                after=after.name
            )
            changes.append(("Name", before.name, after.name))
        
        # Icon change
        if before.icon != after.icon:
            await self.db.log_server_update(
                guild_id=guild_id,
                update_type="icon",
                before=str(before.icon.url) if before.icon else None,
                after=str(after.icon.url) if after.icon else None
            )
            changes.append(("Icon", "Changed", "New icon uploaded"))
        
        # Verification level change
        if before.verification_level != after.verification_level:
            await self.db.log_server_update(
                guild_id=guild_id,
                update_type="verification_level",
                before=str(before.verification_level),
                after=str(after.verification_level)
            )
            changes.append(("Verification Level", str(before.verification_level), str(after.verification_level)))
        
        # Send to log channel if changes exist
        if changes:
            log_channel = await self._get_log_channel(guild_id, "server_logs")
            if log_channel:
                embed = discord.Embed(
                    title="⚙️ Server Updated",
                    description="Server settings were updated",
                    color=discord.Color.blue(),
                    timestamp=datetime.utcnow()
                )
                
                for change_type, before_val, after_val in changes:
                    embed.add_field(name=change_type, value=f"Before: {before_val}\nAfter: {after_val}", inline=False)
                
                if after.icon:
                    embed.set_thumbnail(url=after.icon.url)
                
                try:
                    await log_channel.send(embed=embed)
                except Exception as e:
                    print(f"❌ Failed to send server update log: {e}")
