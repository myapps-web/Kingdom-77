"""
Kingdom-77 Bot - Command Parser
Handles variable replacement, embed parsing, and condition checking
"""

import discord
import random
import re
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
import json


class CommandParser:
    """Parser for custom commands with variables and embeds"""
    
    def __init__(self):
        self.variable_pattern = re.compile(r'\{([^}]+)\}')
    
    # ==================== Variable Replacement ====================
    
    async def parse_variables(
        self,
        content: str,
        ctx: discord.ApplicationContext,
        args: Optional[str] = None
    ) -> str:
        """Parse and replace all variables in content"""
        if not content:
            return content
        
        # Find all variables
        variables = self.variable_pattern.findall(content)
        
        for var in variables:
            value = await self._get_variable_value(var, ctx, args)
            if value is not None:
                content = content.replace(f"{{{var}}}", str(value))
        
        return content
    
    async def _get_variable_value(
        self,
        variable: str,
        ctx: discord.ApplicationContext,
        args: Optional[str]
    ) -> Optional[str]:
        """Get the value of a specific variable"""
        var_lower = variable.lower()
        
        # User variables
        if var_lower == "user":
            return ctx.author.mention
        elif var_lower == "user.name":
            return ctx.author.name
        elif var_lower == "user.id":
            return str(ctx.author.id)
        elif var_lower == "user.discriminator":
            return ctx.author.discriminator
        elif var_lower == "user.avatar":
            return ctx.author.display_avatar.url
        elif var_lower == "user.created":
            return discord.utils.format_dt(ctx.author.created_at, style='R')
        elif var_lower == "user.joined":
            if isinstance(ctx.author, discord.Member):
                return discord.utils.format_dt(ctx.author.joined_at, style='R')
        
        # Server variables
        elif var_lower == "server":
            return ctx.guild.name
        elif var_lower == "server.id":
            return str(ctx.guild.id)
        elif var_lower == "server.members":
            return str(ctx.guild.member_count)
        elif var_lower == "server.icon":
            return ctx.guild.icon.url if ctx.guild.icon else ""
        elif var_lower == "server.owner":
            return ctx.guild.owner.mention if ctx.guild.owner else "Unknown"
        elif var_lower == "server.created":
            return discord.utils.format_dt(ctx.guild.created_at, style='R')
        elif var_lower == "server.boosts":
            return str(ctx.guild.premium_subscription_count)
        elif var_lower == "server.boost_level":
            return str(ctx.guild.premium_tier)
        
        # Channel variables
        elif var_lower == "channel":
            return ctx.channel.mention
        elif var_lower == "channel.name":
            return ctx.channel.name
        elif var_lower == "channel.id":
            return str(ctx.channel.id)
        elif var_lower == "channel.topic":
            if hasattr(ctx.channel, 'topic'):
                return ctx.channel.topic or "No topic"
        
        # Date/Time variables
        elif var_lower == "date":
            return datetime.utcnow().strftime("%Y-%m-%d")
        elif var_lower == "time":
            return datetime.utcnow().strftime("%H:%M:%S UTC")
        elif var_lower == "timestamp":
            return discord.utils.format_dt(datetime.utcnow(), style='f')
        elif var_lower == "unix":
            return str(int(datetime.utcnow().timestamp()))
        
        # Arguments
        elif var_lower == "args":
            return args or ""
        elif var_lower.startswith("args["):
            # {args[0]}, {args[1]}, etc.
            match = re.match(r'args\[(\d+)\]', var_lower)
            if match and args:
                index = int(match.group(1))
                arg_list = args.split()
                if 0 <= index < len(arg_list):
                    return arg_list[index]
        
        # Random variables
        elif var_lower.startswith("random"):
            # {random:1-100}
            match = re.match(r'random:(\d+)-(\d+)', var_lower)
            if match:
                min_val = int(match.group(1))
                max_val = int(match.group(2))
                return str(random.randint(min_val, max_val))
        
        # Math variables
        elif var_lower.startswith("math:"):
            # {math:2+2}
            expression = variable[5:]
            try:
                # Safe evaluation (only basic math)
                result = eval(expression, {"__builtins__": {}}, {})
                return str(result)
            except:
                return f"[Invalid Math: {expression}]"
        
        # Choice variables
        elif var_lower.startswith("choose:"):
            # {choose:option1|option2|option3}
            choices = variable[7:].split('|')
            return random.choice(choices)
        
        return f"[Unknown Variable: {variable}]"
    
    def get_available_variables(self) -> Dict[str, str]:
        """Get list of all available variables with descriptions"""
        return {
            # User variables
            "{user}": "Mention the user",
            "{user.name}": "User's display name",
            "{user.id}": "User's ID",
            "{user.discriminator}": "User's discriminator",
            "{user.avatar}": "User's avatar URL",
            "{user.created}": "When user created their account",
            "{user.joined}": "When user joined the server",
            
            # Server variables
            "{server}": "Server name",
            "{server.id}": "Server ID",
            "{server.members}": "Member count",
            "{server.icon}": "Server icon URL",
            "{server.owner}": "Server owner mention",
            "{server.created}": "When server was created",
            "{server.boosts}": "Server boost count",
            "{server.boost_level}": "Server boost level",
            
            # Channel variables
            "{channel}": "Mention current channel",
            "{channel.name}": "Channel name",
            "{channel.id}": "Channel ID",
            "{channel.topic}": "Channel topic",
            
            # Date/Time variables
            "{date}": "Current date (YYYY-MM-DD)",
            "{time}": "Current time (HH:MM:SS UTC)",
            "{timestamp}": "Discord timestamp",
            "{unix}": "Unix timestamp",
            
            # Arguments
            "{args}": "All command arguments",
            "{args[0]}": "First argument",
            "{args[1]}": "Second argument",
            
            # Random/Utility
            "{random:1-100}": "Random number between 1-100",
            "{math:2+2}": "Evaluate math expression",
            "{choose:a|b|c}": "Choose random option"
        }
    
    # ==================== Embed Parsing ====================
    
    def parse_embed(self, embed_data: Dict[str, Any]) -> Optional[discord.Embed]:
        """Parse embed data dictionary into discord.Embed"""
        try:
            # Create embed with basic properties
            embed = discord.Embed()
            
            # Title
            if "title" in embed_data and embed_data["title"]:
                embed.title = embed_data["title"][:256]
            
            # Description
            if "description" in embed_data and embed_data["description"]:
                embed.description = embed_data["description"][:4096]
            
            # Color
            if "color" in embed_data:
                color_value = embed_data["color"]
                if isinstance(color_value, str):
                    # Remove # if present
                    color_value = color_value.lstrip('#')
                    # Convert hex to int
                    embed.color = discord.Color(int(color_value, 16))
                elif isinstance(color_value, int):
                    embed.color = discord.Color(color_value)
            
            # URL
            if "url" in embed_data and embed_data["url"]:
                embed.url = embed_data["url"]
            
            # Timestamp
            if embed_data.get("timestamp", False):
                embed.timestamp = datetime.utcnow()
            
            # Footer
            if "footer" in embed_data:
                footer = embed_data["footer"]
                if isinstance(footer, dict):
                    footer_text = footer.get("text", "")[:2048]
                    footer_icon = footer.get("icon_url")
                    if footer_text:
                        embed.set_footer(text=footer_text, icon_url=footer_icon)
                elif isinstance(footer, str) and footer:
                    embed.set_footer(text=footer[:2048])
            
            # Image
            if "image" in embed_data and embed_data["image"]:
                embed.set_image(url=embed_data["image"])
            
            # Thumbnail
            if "thumbnail" in embed_data and embed_data["thumbnail"]:
                embed.set_thumbnail(url=embed_data["thumbnail"])
            
            # Author
            if "author" in embed_data:
                author = embed_data["author"]
                if isinstance(author, dict):
                    author_name = author.get("name", "")[:256]
                    author_url = author.get("url")
                    author_icon = author.get("icon_url")
                    if author_name:
                        embed.set_author(
                            name=author_name,
                            url=author_url,
                            icon_url=author_icon
                        )
            
            # Fields
            if "fields" in embed_data and isinstance(embed_data["fields"], list):
                for field in embed_data["fields"][:25]:  # Max 25 fields
                    if isinstance(field, dict):
                        name = field.get("name", "")[:256]
                        value = field.get("value", "")[:1024]
                        inline = field.get("inline", False)
                        if name and value:
                            embed.add_field(name=name, value=value, inline=inline)
            
            return embed
            
        except Exception as e:
            print(f"Error parsing embed: {e}")
            return None
    
    async def parse_embed_with_variables(
        self,
        embed_data: Dict[str, Any],
        ctx: discord.ApplicationContext,
        args: Optional[str] = None
    ) -> Optional[discord.Embed]:
        """Parse embed and replace variables in all text fields"""
        try:
            # Deep copy to avoid modifying original
            embed_data = json.loads(json.dumps(embed_data))
            
            # Replace variables in title
            if "title" in embed_data:
                embed_data["title"] = await self.parse_variables(
                    embed_data["title"], ctx, args
                )
            
            # Replace variables in description
            if "description" in embed_data:
                embed_data["description"] = await self.parse_variables(
                    embed_data["description"], ctx, args
                )
            
            # Replace variables in footer
            if "footer" in embed_data:
                if isinstance(embed_data["footer"], dict):
                    if "text" in embed_data["footer"]:
                        embed_data["footer"]["text"] = await self.parse_variables(
                            embed_data["footer"]["text"], ctx, args
                        )
                elif isinstance(embed_data["footer"], str):
                    embed_data["footer"] = await self.parse_variables(
                        embed_data["footer"], ctx, args
                    )
            
            # Replace variables in author
            if "author" in embed_data and isinstance(embed_data["author"], dict):
                if "name" in embed_data["author"]:
                    embed_data["author"]["name"] = await self.parse_variables(
                        embed_data["author"]["name"], ctx, args
                    )
            
            # Replace variables in fields
            if "fields" in embed_data and isinstance(embed_data["fields"], list):
                for field in embed_data["fields"]:
                    if isinstance(field, dict):
                        if "name" in field:
                            field["name"] = await self.parse_variables(
                                field["name"], ctx, args
                            )
                        if "value" in field:
                            field["value"] = await self.parse_variables(
                                field["value"], ctx, args
                            )
            
            # Parse to embed
            return self.parse_embed(embed_data)
            
        except Exception as e:
            print(f"Error parsing embed with variables: {e}")
            return None
    
    def validate_embed_data(self, embed_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate embed data structure"""
        # Check if at least one field is present
        required_fields = ["title", "description", "fields"]
        has_content = any(embed_data.get(field) for field in required_fields)
        
        if not has_content:
            return False, "Embed must have at least a title, description, or fields"
        
        # Validate color format
        if "color" in embed_data:
            color = embed_data["color"]
            if isinstance(color, str):
                # Must be valid hex color
                if not re.match(r'^#?[0-9A-Fa-f]{6}$', color):
                    return False, "Color must be a valid hex color (e.g., #FF0000)"
            elif not isinstance(color, int):
                return False, "Color must be hex string or integer"
        
        # Validate URLs
        url_fields = ["url", "image", "thumbnail"]
        for field in url_fields:
            if field in embed_data and embed_data[field]:
                url = embed_data[field]
                if not url.startswith(("http://", "https://")):
                    return False, f"{field.capitalize()} must be a valid URL"
        
        # Validate fields array
        if "fields" in embed_data:
            if not isinstance(embed_data["fields"], list):
                return False, "Fields must be an array"
            
            if len(embed_data["fields"]) > 25:
                return False, "Maximum 25 fields allowed"
            
            for i, field in enumerate(embed_data["fields"]):
                if not isinstance(field, dict):
                    return False, f"Field {i+1} must be an object"
                if "name" not in field or "value" not in field:
                    return False, f"Field {i+1} must have 'name' and 'value'"
        
        return True, None
    
    # ==================== Condition Checking ====================
    
    async def check_conditions(
        self,
        ctx: discord.ApplicationContext,
        required_roles: List[int],
        allowed_channels: List[int]
    ) -> Tuple[bool, Optional[str]]:
        """Check if user meets command conditions"""
        # Check channel restriction
        if allowed_channels and ctx.channel.id not in allowed_channels:
            return False, "This command is not available in this channel"
        
        # Check role requirements
        if required_roles:
            if not isinstance(ctx.author, discord.Member):
                return False, "This command requires server membership"
            
            user_role_ids = [role.id for role in ctx.author.roles]
            has_required_role = any(role_id in user_role_ids for role_id in required_roles)
            
            if not has_required_role:
                return False, "You don't have the required roles for this command"
        
        return True, None
    
    def check_cooldown(
        self,
        last_used: Optional[datetime],
        cooldown_seconds: int
    ) -> Tuple[bool, Optional[int]]:
        """Check if command is on cooldown"""
        if cooldown_seconds == 0 or last_used is None:
            return True, None
        
        now = datetime.utcnow()
        time_passed = (now - last_used).total_seconds()
        
        if time_passed < cooldown_seconds:
            remaining = int(cooldown_seconds - time_passed)
            return False, remaining
        
        return True, None
    
    # ==================== Content Validation ====================
    
    def validate_command_name(self, name: str) -> Tuple[bool, Optional[str]]:
        """Validate command name"""
        if not name:
            return False, "Command name cannot be empty"
        
        if len(name) > 32:
            return False, "Command name must be 32 characters or less"
        
        if not re.match(r'^[a-z0-9_-]+$', name.lower()):
            return False, "Command name can only contain letters, numbers, hyphens, and underscores"
        
        # Reserved names
        reserved = ["help", "ping", "info", "setup", "config"]
        if name.lower() in reserved:
            return False, f"'{name}' is a reserved command name"
        
        return True, None
    
    def validate_content(self, content: str, max_length: int = 2000) -> Tuple[bool, Optional[str]]:
        """Validate command content"""
        if not content:
            return False, "Content cannot be empty"
        
        if len(content) > max_length:
            return False, f"Content must be {max_length} characters or less"
        
        return True, None
    
    def sanitize_content(self, content: str) -> str:
        """Sanitize content to prevent exploits"""
        # Remove @everyone and @here mentions
        content = content.replace("@everyone", "@\u200beveryone")
        content = content.replace("@here", "@\u200bhere")
        
        return content
    
    # ==================== Helper Methods ====================
    
    def format_variable_list(self) -> str:
        """Format variable list for display"""
        variables = self.get_available_variables()
        
        output = "**Available Variables:**\n\n"
        
        categories = {
            "👤 User Variables": [k for k in variables.keys() if k.startswith("{user")],
            "🏰 Server Variables": [k for k in variables.keys() if k.startswith("{server")],
            "📝 Channel Variables": [k for k in variables.keys() if k.startswith("{channel")],
            "⏰ Date/Time Variables": [k for k in variables.keys() if k.startswith(("{date", "{time", "{timestamp", "{unix"))],
            "🎲 Random/Utility": [k for k in variables.keys() if k.startswith(("{random", "{math", "{choose", "{args"))]
        }
        
        for category, vars in categories.items():
            if vars:
                output += f"\n**{category}**\n"
                for var in vars:
                    output += f"`{var}` - {variables[var]}\n"
        
        return output
    
    def preview_command(
        self,
        name: str,
        response_type: str,
        content: Optional[str],
        embed_data: Optional[Dict[str, Any]]
    ) -> str:
        """Generate preview of command output"""
        preview = f"**Command Preview: `{name}`**\n\n"
        preview += f"**Type:** {response_type}\n\n"
        
        if response_type in ["text", "both"] and content:
            preview += f"**Text Response:**\n{content[:500]}\n\n"
        
        if response_type in ["embed", "both"] and embed_data:
            preview += "**Embed Response:**\n"
            preview += f"Title: {embed_data.get('title', 'N/A')}\n"
            preview += f"Description: {embed_data.get('description', 'N/A')[:100]}...\n"
            if embed_data.get('fields'):
                preview += f"Fields: {len(embed_data['fields'])}\n"
        
        return preview
