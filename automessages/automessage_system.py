"""
Auto-Message System Core Logic

Handles automatic message responses with various triggers and interaction types.
"""

import discord
from discord import ui
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import re


class AutoMessageSystem:
    """Core system for automatic message responses"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.messages_collection = db.auto_messages
        self.settings_collection = db.auto_messages_settings
        
        # Cache for active messages (guild_id -> list of messages)
        self.message_cache: Dict[str, List[Dict]] = {}
        
        # Cooldown tracking (user_id:message_id -> timestamp)
        self.cooldowns: Dict[str, datetime] = {}
    
    # ==================== CREATE & MANAGE ====================
    
    async def create_message(
        self,
        guild_id: str,
        name: str,
        trigger_type: str,
        trigger_value: str,
        response_type: str,
        response_content: Optional[str] = None,
        embed_data: Optional[Dict] = None,
        buttons: Optional[List[Dict]] = None,
        dropdowns: Optional[List[Dict]] = None,
        settings: Optional[Dict] = None
    ) -> Dict:
        """
        Create a new auto-message
        
        Args:
            guild_id: Guild ID
            name: Message name (identifier)
            trigger_type: keyword, button, dropdown, slash_command
            trigger_value: The trigger value (keyword text, button custom_id, etc.)
            response_type: text, embed, buttons, dropdowns
            response_content: Plain text response (optional)
            embed_data: Embed configuration (optional)
            buttons: List of button configurations (optional)
            dropdowns: List of dropdown configurations (optional)
            settings: Additional settings (permissions, channels, cooldown, etc.)
        
        Returns:
            Created message document
        """
        message_data = {
            "guild_id": guild_id,
            "name": name,
            "trigger": {
                "type": trigger_type,
                "value": trigger_value,
                "case_sensitive": settings.get("case_sensitive", False) if settings else False,
                "exact_match": settings.get("exact_match", False) if settings else False,
            },
            "response": {
                "type": response_type,
                "content": response_content,
                "embed": embed_data,
                "buttons": buttons or [],
                "dropdowns": dropdowns or [],
            },
            "settings": {
                "enabled": True,
                "allowed_roles": settings.get("allowed_roles", []) if settings else [],
                "allowed_channels": settings.get("allowed_channels", []) if settings else [],
                "cooldown_seconds": settings.get("cooldown_seconds", 0) if settings else 0,
                "auto_delete_after": settings.get("auto_delete_after", 0) if settings else 0,
                "dm_response": settings.get("dm_response", False) if settings else False,
            },
            "statistics": {
                "total_triggers": 0,
                "last_triggered": None,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        }
        
        result = await self.messages_collection.insert_one(message_data)
        message_data["_id"] = result.inserted_id
        
        # Invalidate cache
        if guild_id in self.message_cache:
            del self.message_cache[guild_id]
        
        return message_data
    
    async def update_message(
        self,
        guild_id: str,
        message_name: str,
        updates: Dict
    ) -> bool:
        """Update an existing auto-message"""
        updates["statistics.updated_at"] = datetime.utcnow()
        
        result = await self.messages_collection.update_one(
            {"guild_id": guild_id, "name": message_name},
            {"$set": updates}
        )
        
        # Invalidate cache
        if guild_id in self.message_cache:
            del self.message_cache[guild_id]
        
        return result.modified_count > 0
    
    async def delete_message(self, guild_id: str, message_name: str) -> bool:
        """Delete an auto-message"""
        result = await self.messages_collection.delete_one(
            {"guild_id": guild_id, "name": message_name}
        )
        
        # Invalidate cache
        if guild_id in self.message_cache:
            del self.message_cache[guild_id]
        
        return result.deleted_count > 0
    
    async def toggle_message(self, guild_id: str, message_name: str) -> Tuple[bool, bool]:
        """
        Toggle message enabled/disabled
        
        Returns:
            (success, new_enabled_state)
        """
        message = await self.get_message(guild_id, message_name)
        if not message:
            return False, False
        
        new_state = not message["settings"]["enabled"]
        success = await self.update_message(
            guild_id,
            message_name,
            {"settings.enabled": new_state}
        )
        
        return success, new_state
    
    # ==================== QUERY ====================
    
    async def get_message(self, guild_id: str, message_name: str) -> Optional[Dict]:
        """Get a specific auto-message"""
        return await self.messages_collection.find_one(
            {"guild_id": guild_id, "name": message_name}
        )
    
    async def get_all_messages(
        self,
        guild_id: str,
        enabled_only: bool = False
    ) -> List[Dict]:
        """Get all auto-messages for a guild"""
        query = {"guild_id": guild_id}
        if enabled_only:
            query["settings.enabled"] = True
        
        messages = await self.messages_collection.find(query).to_list(length=None)
        return messages
    
    async def get_active_messages(self, guild_id: str) -> List[Dict]:
        """Get all enabled messages for a guild (with caching)"""
        if guild_id in self.message_cache:
            return self.message_cache[guild_id]
        
        messages = await self.get_all_messages(guild_id, enabled_only=True)
        self.message_cache[guild_id] = messages
        return messages
    
    # ==================== TRIGGER MATCHING ====================
    
    async def find_matching_keyword(
        self,
        guild_id: str,
        content: str
    ) -> Optional[Dict]:
        """Find auto-message matching keyword in content"""
        messages = await self.get_active_messages(guild_id)
        
        for message in messages:
            if message["trigger"]["type"] != "keyword":
                continue
            
            trigger_value = message["trigger"]["value"]
            case_sensitive = message["trigger"]["case_sensitive"]
            exact_match = message["trigger"]["exact_match"]
            
            # Prepare strings for comparison
            search_in = content if case_sensitive else content.lower()
            search_for = trigger_value if case_sensitive else trigger_value.lower()
            
            # Check match
            if exact_match:
                if search_in == search_for:
                    return message
            else:
                if search_for in search_in:
                    return message
        
        return None
    
    async def find_matching_button(
        self,
        guild_id: str,
        custom_id: str
    ) -> Optional[Dict]:
        """Find auto-message for button custom_id"""
        messages = await self.get_active_messages(guild_id)
        
        for message in messages:
            if message["trigger"]["type"] == "button":
                if message["trigger"]["value"] == custom_id:
                    return message
        
        return None
    
    async def find_matching_dropdown(
        self,
        guild_id: str,
        custom_id: str,
        selected_value: str
    ) -> Optional[Dict]:
        """Find auto-message for dropdown selection"""
        messages = await self.get_active_messages(guild_id)
        
        for message in messages:
            if message["trigger"]["type"] == "dropdown":
                # Format: "dropdown_id:option_value"
                trigger = message["trigger"]["value"]
                if trigger == f"{custom_id}:{selected_value}":
                    return message
        
        return None
    
    # ==================== PERMISSIONS & CHECKS ====================
    
    def check_permissions(
        self,
        message: Dict,
        member: discord.Member,
        channel: discord.TextChannel
    ) -> bool:
        """Check if user/channel can trigger this message"""
        settings = message["settings"]
        
        # Check allowed roles
        allowed_roles = settings.get("allowed_roles", [])
        if allowed_roles:
            member_role_ids = [str(role.id) for role in member.roles]
            if not any(role_id in member_role_ids for role_id in allowed_roles):
                return False
        
        # Check allowed channels
        allowed_channels = settings.get("allowed_channels", [])
        if allowed_channels:
            if str(channel.id) not in allowed_channels:
                return False
        
        return True
    
    def check_cooldown(self, user_id: str, message_name: str, cooldown_seconds: int) -> bool:
        """
        Check if user is on cooldown for this message
        
        Returns:
            True if can trigger, False if on cooldown
        """
        if cooldown_seconds <= 0:
            return True
        
        key = f"{user_id}:{message_name}"
        
        if key in self.cooldowns:
            time_since = (datetime.utcnow() - self.cooldowns[key]).total_seconds()
            if time_since < cooldown_seconds:
                return False
        
        # Update cooldown
        self.cooldowns[key] = datetime.utcnow()
        return True
    
    # ==================== RESPONSE BUILDING ====================
    
    def build_embed(self, embed_data: Dict) -> discord.Embed:
        """Build Discord embed from data"""
        embed = discord.Embed(
            title=embed_data.get("title"),
            description=embed_data.get("description"),
            color=discord.Color(int(embed_data.get("color", "0x5865F2").replace("#", ""), 16))
        )
        
        # Author
        if embed_data.get("author"):
            author = embed_data["author"]
            embed.set_author(
                name=author.get("name"),
                icon_url=author.get("icon_url"),
                url=author.get("url")
            )
        
        # Fields
        for field in embed_data.get("fields", []):
            embed.add_field(
                name=field.get("name", "Field"),
                value=field.get("value", "Value"),
                inline=field.get("inline", True)
            )
        
        # Footer
        if embed_data.get("footer"):
            footer = embed_data["footer"]
            embed.set_footer(
                text=footer.get("text"),
                icon_url=footer.get("icon_url")
            )
        
        # Images
        if embed_data.get("thumbnail"):
            embed.set_thumbnail(url=embed_data["thumbnail"])
        
        if embed_data.get("image"):
            embed.set_image(url=embed_data["image"])
        
        # Timestamp
        if embed_data.get("timestamp"):
            embed.timestamp = datetime.utcnow()
        
        return embed
    
    def build_buttons(self, buttons_data: List[Dict]) -> List[discord.ui.Button]:
        """Build Discord buttons from data"""
        buttons = []
        
        for btn_data in buttons_data:
            style_map = {
                "primary": discord.ButtonStyle.primary,
                "secondary": discord.ButtonStyle.secondary,
                "success": discord.ButtonStyle.success,
                "danger": discord.ButtonStyle.danger,
                "link": discord.ButtonStyle.link,
            }
            
            style = style_map.get(btn_data.get("style", "secondary"), discord.ButtonStyle.secondary)
            
            button = discord.ui.Button(
                label=btn_data.get("label", "Button"),
                style=style,
                custom_id=btn_data.get("custom_id") if style != discord.ButtonStyle.link else None,
                url=btn_data.get("url") if style == discord.ButtonStyle.link else None,
                emoji=btn_data.get("emoji"),
                disabled=btn_data.get("disabled", False)
            )
            
            buttons.append(button)
        
        return buttons
    
    def build_dropdown(self, dropdown_data: Dict) -> discord.ui.Select:
        """Build Discord select menu from data"""
        options = []
        
        for opt_data in dropdown_data.get("options", []):
            option = discord.SelectOption(
                label=opt_data.get("label", "Option"),
                value=opt_data.get("value", "value"),
                description=opt_data.get("description"),
                emoji=opt_data.get("emoji"),
                default=opt_data.get("default", False)
            )
            options.append(option)
        
        select = discord.ui.Select(
            placeholder=dropdown_data.get("placeholder", "Select an option"),
            custom_id=dropdown_data.get("custom_id", "select"),
            min_values=dropdown_data.get("min_values", 1),
            max_values=dropdown_data.get("max_values", 1),
            options=options
        )
        
        return select
    
    def build_view(self, message_data: Dict) -> Optional[discord.ui.View]:
        """Build Discord view with buttons and/or dropdowns"""
        response = message_data["response"]
        buttons_data = response.get("buttons", [])
        dropdowns_data = response.get("dropdowns", [])
        
        if not buttons_data and not dropdowns_data:
            return None
        
        view = discord.ui.View(timeout=None)
        
        # Add buttons
        for btn_data in buttons_data:
            button = self.build_buttons([btn_data])[0]
            view.add_item(button)
        
        # Add dropdowns
        for dd_data in dropdowns_data:
            select = self.build_dropdown(dd_data)
            view.add_item(select)
        
        return view
    
    # ==================== SEND RESPONSE ====================
    
    async def send_auto_response(
        self,
        message_data: Dict,
        target: discord.abc.Messageable,
        user: Optional[discord.User] = None
    ) -> Optional[discord.Message]:
        """
        Send auto-message response
        
        Args:
            message_data: The auto-message document
            target: Where to send (channel or user DM)
            user: User who triggered (for statistics)
        
        Returns:
            Sent message or None
        """
        response = message_data["response"]
        settings = message_data["settings"]
        
        # Build components
        content = response.get("content")
        embed = self.build_embed(response["embed"]) if response.get("embed") else None
        view = self.build_view(message_data)
        
        # Send message
        try:
            sent_message = await target.send(
                content=content,
                embed=embed,
                view=view
            )
            
            # Update statistics
            await self.messages_collection.update_one(
                {"_id": message_data["_id"]},
                {
                    "$inc": {"statistics.total_triggers": 1},
                    "$set": {"statistics.last_triggered": datetime.utcnow()}
                }
            )
            
            # Auto-delete if configured
            auto_delete = settings.get("auto_delete_after", 0)
            if auto_delete > 0:
                await sent_message.delete(delay=auto_delete)
            
            return sent_message
        
        except discord.Forbidden:
            return None
        except Exception as e:
            print(f"Error sending auto-response: {e}")
            return None
    
    async def handle_keyword_trigger(
        self,
        guild_id: str,
        content: str,
        channel: discord.TextChannel,
        member: discord.Member
    ) -> bool:
        """
        Handle keyword-based trigger
        
        Returns:
            True if message was sent, False otherwise
        """
        message = await self.find_matching_keyword(guild_id, content)
        if not message:
            return False
        
        # Check permissions
        if not self.check_permissions(message, member, channel):
            return False
        
        # Check cooldown
        cooldown = message["settings"].get("cooldown_seconds", 0)
        if not self.check_cooldown(str(member.id), message["name"], cooldown):
            return False
        
        # Send response
        dm_response = message["settings"].get("dm_response", False)
        target = member if dm_response else channel
        
        sent = await self.send_auto_response(message, target, member)
        return sent is not None
    
    async def handle_button_trigger(
        self,
        guild_id: str,
        custom_id: str,
        interaction: discord.Interaction
    ) -> bool:
        """Handle button click trigger"""
        message = await self.find_matching_button(guild_id, custom_id)
        if not message:
            return False
        
        # Check permissions
        if not self.check_permissions(message, interaction.user, interaction.channel):
            await interaction.response.send_message(
                "❌ ليس لديك صلاحية لاستخدام هذا الزر!",
                ephemeral=True
            )
            return False
        
        # Check cooldown
        cooldown = message["settings"].get("cooldown_seconds", 0)
        if not self.check_cooldown(str(interaction.user.id), message["name"], cooldown):
            await interaction.response.send_message(
                f"⏰ عليك الانتظار قبل استخدام هذا مرة أخرى!",
                ephemeral=True
            )
            return False
        
        # Send response
        dm_response = message["settings"].get("dm_response", False)
        
        if dm_response:
            await interaction.response.send_message("✅ تم الإرسال في الرسائل الخاصة!", ephemeral=True)
            await self.send_auto_response(message, interaction.user, interaction.user)
        else:
            # Build response
            response = message["response"]
            content = response.get("content")
            embed = self.build_embed(response["embed"]) if response.get("embed") else None
            view = self.build_view(message)
            
            await interaction.response.send_message(
                content=content,
                embed=embed,
                view=view,
                ephemeral=False
            )
            
            # Update statistics
            await self.messages_collection.update_one(
                {"_id": message["_id"]},
                {
                    "$inc": {"statistics.total_triggers": 1},
                    "$set": {"statistics.last_triggered": datetime.utcnow()}
                }
            )
        
        return True
    
    async def handle_dropdown_trigger(
        self,
        guild_id: str,
        custom_id: str,
        selected_value: str,
        interaction: discord.Interaction
    ) -> bool:
        """Handle dropdown selection trigger"""
        message = await self.find_matching_dropdown(guild_id, custom_id, selected_value)
        if not message:
            return False
        
        # Check permissions
        if not self.check_permissions(message, interaction.user, interaction.channel):
            await interaction.response.send_message(
                "❌ ليس لديك صلاحية لاستخدام هذا!",
                ephemeral=True
            )
            return False
        
        # Check cooldown
        cooldown = message["settings"].get("cooldown_seconds", 0)
        if not self.check_cooldown(str(interaction.user.id), message["name"], cooldown):
            await interaction.response.send_message(
                f"⏰ عليك الانتظار قبل استخدام هذا مرة أخرى!",
                ephemeral=True
            )
            return False
        
        # Send response (similar to button)
        dm_response = message["settings"].get("dm_response", False)
        
        if dm_response:
            await interaction.response.send_message("✅ تم الإرسال في الرسائل الخاصة!", ephemeral=True)
            await self.send_auto_response(message, interaction.user, interaction.user)
        else:
            response = message["response"]
            content = response.get("content")
            embed = self.build_embed(response["embed"]) if response.get("embed") else None
            view = self.build_view(message)
            
            await interaction.response.send_message(
                content=content,
                embed=embed,
                view=view,
                ephemeral=False
            )
            
            # Update statistics
            await self.messages_collection.update_one(
                {"_id": message["_id"]},
                {
                    "$inc": {"statistics.total_triggers": 1},
                    "$set": {"statistics.last_triggered": datetime.utcnow()}
                }
            )
        
        return True
    
    # ==================== STATISTICS ====================
    
    async def get_statistics(self, guild_id: str) -> Dict:
        """Get guild auto-messages statistics"""
        messages = await self.get_all_messages(guild_id)
        
        total_messages = len(messages)
        enabled_messages = sum(1 for m in messages if m["settings"]["enabled"])
        total_triggers = sum(m["statistics"]["total_triggers"] for m in messages)
        
        # By type
        type_counts = {}
        for message in messages:
            msg_type = message["trigger"]["type"]
            type_counts[msg_type] = type_counts.get(msg_type, 0) + 1
        
        # Most used
        most_used = sorted(
            messages,
            key=lambda m: m["statistics"]["total_triggers"],
            reverse=True
        )[:5]
        
        return {
            "total_messages": total_messages,
            "enabled_messages": enabled_messages,
            "disabled_messages": total_messages - enabled_messages,
            "total_triggers": total_triggers,
            "by_type": type_counts,
            "most_used": [
                {
                    "name": m["name"],
                    "triggers": m["statistics"]["total_triggers"],
                    "type": m["trigger"]["type"]
                }
                for m in most_used
            ]
        }
