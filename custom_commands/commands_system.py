"""
Kingdom-77 Bot - Custom Commands System
Core system for executing custom commands and auto-responses
"""

import discord
from discord.ext import commands
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta
import re

from database.custom_commands_schema import CustomCommandsSchema
from custom_commands.command_parser import CommandParser


class CommandsSystem(commands.Cog):
    """Core system for custom commands"""
    
    def __init__(self, bot: commands.Bot, db):
        self.bot = bot
        self.schema = CustomCommandsSchema(db)
        self.parser = CommandParser()
        
        # In-memory cooldown tracking
        self.cooldowns: Dict[str, datetime] = {}
    
    async def cog_load(self):
        """Setup indexes when cog loads"""
        await self.schema.setup_indexes()
    
    # ==================== Command Execution ====================
    
    async def execute_command(
        self,
        ctx: discord.ApplicationContext,
        command_name: str,
        args: Optional[str] = None
    ) -> bool:
        """Execute a custom command"""
        try:
            # Get command from database
            command = await self.schema.get_command(ctx.guild.id, command_name)
            
            if not command:
                return False
            
            # Check if command is enabled
            if not command.get("enabled", True):
                await ctx.respond(
                    embed=discord.Embed(
                        title="❌ Command Disabled",
                        description=f"The command `{command_name}` is currently disabled.",
                        color=discord.Color.red()
                    ),
                    ephemeral=True
                )
                return True
            
            # Check conditions
            can_use, error_msg = await self.parser.check_conditions(
                ctx,
                command.get("required_roles", []),
                command.get("allowed_channels", [])
            )
            
            if not can_use:
                await ctx.respond(
                    embed=discord.Embed(
                        title="❌ Cannot Use Command",
                        description=error_msg,
                        color=discord.Color.red()
                    ),
                    ephemeral=True
                )
                return True
            
            # Check cooldown
            cooldown_key = f"{ctx.guild.id}_{command['name']}_{ctx.author.id}"
            is_ready, remaining = self.parser.check_cooldown(
                self.cooldowns.get(cooldown_key),
                command.get("cooldown", 0)
            )
            
            if not is_ready:
                await ctx.respond(
                    embed=discord.Embed(
                        title="⏰ Command on Cooldown",
                        description=f"Please wait {remaining} seconds before using this command again.",
                        color=discord.Color.orange()
                    ),
                    ephemeral=True
                )
                return True
            
            # Execute command
            response_type = command.get("response_type", "text")
            
            if response_type == "text":
                # Text only response
                content = await self.parser.parse_variables(
                    command.get("response_content", ""),
                    ctx,
                    args
                )
                content = self.parser.sanitize_content(content)
                await ctx.respond(content)
            
            elif response_type == "embed":
                # Embed only response
                embed = await self.parser.parse_embed_with_variables(
                    command.get("embed_data", {}),
                    ctx,
                    args
                )
                if embed:
                    await ctx.respond(embed=embed)
                else:
                    await ctx.respond(
                        embed=discord.Embed(
                            title="❌ Error",
                            description="Failed to parse embed data.",
                            color=discord.Color.red()
                        ),
                        ephemeral=True
                    )
            
            elif response_type == "both":
                # Both text and embed
                content = await self.parser.parse_variables(
                    command.get("response_content", ""),
                    ctx,
                    args
                )
                content = self.parser.sanitize_content(content)
                
                embed = await self.parser.parse_embed_with_variables(
                    command.get("embed_data", {}),
                    ctx,
                    args
                )
                
                if embed:
                    await ctx.respond(content=content, embed=embed)
                else:
                    await ctx.respond(content)
            
            # Update cooldown
            self.cooldowns[cooldown_key] = datetime.utcnow()
            
            # Increment usage
            await self.schema.increment_usage(ctx.guild.id, command["name"])
            await self.schema.log_command_usage(
                ctx.guild.id,
                command["name"],
                ctx.author.id,
                ctx.channel.id,
                success=True
            )
            
            return True
            
        except Exception as e:
            print(f"Error executing command: {e}")
            await self.schema.log_command_usage(
                ctx.guild.id,
                command_name,
                ctx.author.id,
                ctx.channel.id,
                success=False,
                error_message=str(e)
            )
            return False
    
    # ==================== Auto-Response Detection ====================
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Check for auto-response triggers"""
        # Ignore bots and DMs
        if message.author.bot or not message.guild:
            return
        
        # Get all enabled auto-responses for guild
        auto_responses = await self.schema.get_all_auto_responses(
            message.guild.id,
            enabled_only=True
        )
        
        if not auto_responses:
            return
        
        # Check each auto-response
        for ar in auto_responses:
            if await self._matches_trigger(message.content, ar):
                # Check cooldown
                cooldown_key = f"{message.guild.id}_{ar['trigger']}_{message.author.id}"
                is_ready, _ = self.parser.check_cooldown(
                    self.cooldowns.get(cooldown_key),
                    ar.get("cooldown", 0)
                )
                
                if not is_ready:
                    continue
                
                # Delete trigger message if configured
                if ar.get("delete_trigger", False):
                    try:
                        await message.delete()
                    except:
                        pass
                
                # Parse response with variables
                # Create fake context for variable parsing
                class FakeContext:
                    def __init__(self, message):
                        self.author = message.author
                        self.guild = message.guild
                        self.channel = message.channel
                
                fake_ctx = FakeContext(message)
                response = await self.parser.parse_variables(
                    ar["response"],
                    fake_ctx,
                    None
                )
                response = self.parser.sanitize_content(response)
                
                # Send response
                await message.channel.send(response)
                
                # Update cooldown
                self.cooldowns[cooldown_key] = datetime.utcnow()
                
                # Increment usage
                await self.schema.increment_auto_response_usage(
                    message.guild.id,
                    ar["trigger"]
                )
                
                # Only trigger one auto-response per message
                break
    
    async def _matches_trigger(self, content: str, auto_response: Dict[str, Any]) -> bool:
        """Check if message content matches auto-response trigger"""
        trigger = auto_response["trigger"]
        match_type = auto_response.get("match_type", "exact")
        case_sensitive = auto_response.get("case_sensitive", False)
        
        if not case_sensitive:
            content = content.lower()
            trigger = trigger.lower()
        
        if match_type == "exact":
            return content == trigger
        elif match_type == "contains":
            return trigger in content
        elif match_type == "starts_with":
            return content.startswith(trigger)
        elif match_type == "ends_with":
            return content.endswith(trigger)
        elif match_type == "regex":
            try:
                return bool(re.search(trigger, content))
            except:
                return False
        
        return False
    
    # ==================== Command Management ====================
    
    async def create_command(
        self,
        guild_id: int,
        creator_id: int,
        name: str,
        response_type: str,
        response_content: Optional[str] = None,
        embed_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Tuple[bool, str]:
        """Create a new custom command"""
        # Validate name
        is_valid, error_msg = self.parser.validate_command_name(name)
        if not is_valid:
            return False, error_msg
        
        # Check if command already exists
        existing = await self.schema.get_command(guild_id, name)
        if existing:
            return False, f"Command `{name}` already exists"
        
        # Validate content
        if response_type in ["text", "both"]:
            if not response_content:
                return False, "Text response is required for this response type"
            is_valid, error_msg = self.parser.validate_content(response_content)
            if not is_valid:
                return False, error_msg
        
        # Validate embed
        if response_type in ["embed", "both"]:
            if not embed_data:
                return False, "Embed data is required for this response type"
            is_valid, error_msg = self.parser.validate_embed_data(embed_data)
            if not is_valid:
                return False, error_msg
        
        # Create command
        try:
            await self.schema.create_command(
                guild_id=guild_id,
                name=name,
                creator_id=creator_id,
                response_type=response_type,
                response_content=response_content,
                embed_data=embed_data,
                **kwargs
            )
            return True, f"Command `{name}` created successfully!"
        except Exception as e:
            return False, f"Failed to create command: {str(e)}"
    
    async def update_command(
        self,
        guild_id: int,
        name: str,
        updates: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """Update an existing command"""
        # Check if command exists
        existing = await self.schema.get_command(guild_id, name)
        if not existing:
            return False, f"Command `{name}` not found"
        
        # Validate updates
        if "response_content" in updates:
            is_valid, error_msg = self.parser.validate_content(updates["response_content"])
            if not is_valid:
                return False, error_msg
        
        if "embed_data" in updates:
            is_valid, error_msg = self.parser.validate_embed_data(updates["embed_data"])
            if not is_valid:
                return False, error_msg
        
        # Update command
        try:
            success = await self.schema.update_command(guild_id, name, updates)
            if success:
                return True, f"Command `{name}` updated successfully!"
            else:
                return False, "No changes were made"
        except Exception as e:
            return False, f"Failed to update command: {str(e)}"
    
    async def delete_command(
        self,
        guild_id: int,
        name: str
    ) -> Tuple[bool, str]:
        """Delete a custom command"""
        success = await self.schema.delete_command(guild_id, name)
        if success:
            return True, f"Command `{name}` deleted successfully!"
        else:
            return False, f"Command `{name}` not found"
    
    # ==================== Auto-Response Management ====================
    
    async def create_auto_response(
        self,
        guild_id: int,
        creator_id: int,
        trigger: str,
        response: str,
        **kwargs
    ) -> Tuple[bool, str]:
        """Create a new auto-response"""
        # Validate trigger
        if not trigger or len(trigger) > 100:
            return False, "Trigger must be 1-100 characters"
        
        # Validate response
        is_valid, error_msg = self.parser.validate_content(response)
        if not is_valid:
            return False, error_msg
        
        # Check if auto-response already exists
        existing = await self.schema.get_auto_response(guild_id, trigger)
        if existing:
            return False, f"Auto-response for `{trigger}` already exists"
        
        # Create auto-response
        try:
            await self.schema.create_auto_response(
                guild_id=guild_id,
                trigger=trigger,
                response=response,
                creator_id=creator_id,
                **kwargs
            )
            return True, f"Auto-response for `{trigger}` created successfully!"
        except Exception as e:
            return False, f"Failed to create auto-response: {str(e)}"
    
    # ==================== Statistics ====================
    
    async def get_guild_stats(self, guild_id: int, days: int = 7) -> Dict[str, Any]:
        """Get command statistics for a guild"""
        stats = await self.schema.get_command_stats(guild_id, days)
        command_count = await self.schema.get_command_count(guild_id)
        
        stats["total_commands"] = command_count
        return stats
    
    # ==================== Cooldown Cleanup ====================
    
    async def cleanup_cooldowns(self):
        """Remove expired cooldowns from memory"""
        now = datetime.utcnow()
        expired = []
        
        for key, timestamp in self.cooldowns.items():
            if (now - timestamp).total_seconds() > 3600:  # 1 hour
                expired.append(key)
        
        for key in expired:
            del self.cooldowns[key]


def setup(bot):
    bot.add_cog(CommandsSystem(bot, bot.db))
