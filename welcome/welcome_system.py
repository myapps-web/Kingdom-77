"""
Welcome System Core - Kingdom-77 Bot
Advanced welcome system with card generation, captcha, and auto-role.
"""

import discord
from discord import Member, Guild, TextChannel
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import random
import string
import asyncio
try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
except ImportError:
    Image = ImageDraw = ImageFont = ImageFilter = None
import io
import aiohttp

from database.welcome_schema import WelcomeSchema


class WelcomeSystem:
    """Advanced Welcome System"""
    
    def __init__(self, db):
        self.db = db
        self.schema = WelcomeSchema(db)
        
        # Card dimensions
        self.card_width = 800
        self.card_height = 400
        
        # Captcha dimensions
        self.captcha_width = 300
        self.captcha_height = 100
    
    async def on_member_join(self, member: Member) -> None:
        """Handle member join event"""
        try:
            settings = await self.schema.get_settings(member.guild.id)
            if not settings or not settings.get("enabled", False):
                return
            
            # Check anti-raid
            if await self._check_anti_raid(member.guild.id):
                # Raid detected, don't send welcome
                return
            
            # Record join in history
            await self.schema.add_join_history(
                member.guild.id,
                member.id,
                "join"
            )
            
            # Check if captcha is required
            if settings.get("captcha_enabled", False):
                await self._send_captcha(member, settings)
                return
            
            # Auto-role
            if settings.get("auto_role_enabled", False):
                await self._assign_auto_role(member, settings)
            
            # Send welcome message
            await self._send_welcome(member, settings)
            
            # Send DM
            if settings.get("dm_enabled", False):
                await self._send_dm_welcome(member, settings)
                
        except Exception as e:
            print(f"Error in on_member_join: {e}")
    
    async def on_member_remove(self, member: Member) -> None:
        """Handle member leave event"""
        try:
            settings = await self.schema.get_settings(member.guild.id)
            if not settings or not settings.get("enabled", False):
                return
            
            # Record leave in history
            await self.schema.add_join_history(
                member.guild.id,
                member.id,
                "leave"
            )
            
            # Send goodbye message
            if settings.get("goodbye_enabled", False):
                await self._send_goodbye(member, settings)
                
        except Exception as e:
            print(f"Error in on_member_remove: {e}")
    
    async def _send_welcome(self, member: Member, settings: Dict[str, Any]) -> None:
        """Send welcome message"""
        try:
            # Get welcome channels
            channel_ids = settings.get("welcome_channels", [])
            if not channel_ids:
                return
            
            # Get message type
            message_type = settings.get("welcome_type", "text")
            
            for channel_id in channel_ids:
                channel = member.guild.get_channel(channel_id)
                if not channel:
                    continue
                
                if message_type == "text":
                    content = self._replace_variables(
                        settings.get("welcome_message", "Welcome {user} to {server}!"),
                        member
                    )
                    await channel.send(content)
                    
                elif message_type == "embed":
                    embed = await self._create_welcome_embed(member, settings)
                    await channel.send(embed=embed)
                    
                elif message_type == "card":
                    card = await self._generate_welcome_card(member, settings)
                    await channel.send(file=card)
                    
        except Exception as e:
            print(f"Error sending welcome: {e}")
    
    async def _send_goodbye(self, member: Member, settings: Dict[str, Any]) -> None:
        """Send goodbye message"""
        try:
            channel_id = settings.get("goodbye_channel")
            if not channel_id:
                return
            
            channel = member.guild.get_channel(channel_id)
            if not channel:
                return
            
            message_type = settings.get("goodbye_type", "text")
            
            if message_type == "text":
                content = self._replace_variables(
                    settings.get("goodbye_message", "Goodbye {user}!"),
                    member
                )
                await channel.send(content)
                
            elif message_type == "embed":
                embed = await self._create_goodbye_embed(member, settings)
                await channel.send(embed=embed)
                
        except Exception as e:
            print(f"Error sending goodbye: {e}")
    
    async def _send_dm_welcome(self, member: Member, settings: Dict[str, Any]) -> None:
        """Send DM welcome message"""
        try:
            dm_message = settings.get("dm_message")
            if not dm_message:
                return
            
            content = self._replace_variables(dm_message, member)
            await member.send(content)
            
        except discord.Forbidden:
            # User has DMs disabled
            pass
        except Exception as e:
            print(f"Error sending DM: {e}")
    
    def _replace_variables(self, text: str, member: Member) -> str:
        """Replace variables in text"""
        guild = member.guild
        
        variables = {
            "{user}": member.mention,
            "{user.name}": member.name,
            "{user.id}": str(member.id),
            "{server}": guild.name,
            "{server.name}": guild.name,
            "{server.members}": str(guild.member_count),
            "{count}": str(guild.member_count),
            "{date}": datetime.now().strftime("%Y-%m-%d"),
            "{time}": datetime.now().strftime("%H:%M:%S"),
        }
        
        for var, value in variables.items():
            text = text.replace(var, value)
        
        return text
    
    async def _create_welcome_embed(self, member: Member, settings: Dict[str, Any]) -> discord.Embed:
        """Create welcome embed"""
        title = self._replace_variables(
            settings.get("embed_title", "Welcome!"),
            member
        )
        description = self._replace_variables(
            settings.get("embed_description", "Welcome {user} to {server}!"),
            member
        )
        
        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Member #{member.guild.member_count}")
        
        # Add custom fields
        fields = settings.get("embed_fields", [])
        for field in fields:
            embed.add_field(
                name=self._replace_variables(field.get("name", ""), member),
                value=self._replace_variables(field.get("value", ""), member),
                inline=field.get("inline", True)
            )
        
        return embed
    
    async def _create_goodbye_embed(self, member: Member, settings: Dict[str, Any]) -> discord.Embed:
        """Create goodbye embed"""
        title = self._replace_variables(
            settings.get("goodbye_embed_title", "Goodbye!"),
            member
        )
        description = self._replace_variables(
            settings.get("goodbye_embed_description", "Goodbye {user.name}!"),
            member
        )
        
        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        
        embed.set_thumbnail(url=member.display_avatar.url)
        
        return embed
    
    async def _generate_welcome_card(self, member: Member, settings: Dict[str, Any]) -> discord.File:
        """Generate welcome card image"""
        try:
            # Get card design
            card_id = settings.get("card_id")
            card_design = None
            
            if card_id:
                card_design = await self.schema.get_card_design(member.guild.id, card_id)
            
            if not card_design:
                # Use default template
                card_design = {
                    "template": "classic",
                    "background_color": "#2C2F33",
                    "text_color": "#FFFFFF",
                    "accent_color": "#7289DA"
                }
            
            # Create image
            template = card_design.get("template", "classic")
            
            if template == "classic":
                image = await self._generate_classic_card(member, card_design)
            elif template == "modern":
                image = await self._generate_modern_card(member, card_design)
            elif template == "minimal":
                image = await self._generate_minimal_card(member, card_design)
            elif template == "fancy":
                image = await self._generate_fancy_card(member, card_design)
            else:
                image = await self._generate_classic_card(member, card_design)
            
            # Save to bytes
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            buffer.seek(0)
            
            return discord.File(buffer, filename="welcome.png")
            
        except Exception as e:
            print(f"Error generating card: {e}")
            # Return None if failed
            return None
    
    async def _generate_classic_card(self, member: Member, design: Dict[str, Any]) -> Image.Image:
        """Generate classic style card"""
        # Create base image
        bg_color = design.get("background_color", "#2C2F33")
        image = Image.new("RGB", (self.card_width, self.card_height), bg_color)
        draw = ImageDraw.Draw(image)
        
        # Download avatar
        avatar = await self._get_avatar(member)
        if avatar:
            # Resize and make circular
            avatar = avatar.resize((150, 150))
            mask = Image.new("L", (150, 150), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, 150, 150), fill=255)
            
            # Paste avatar
            image.paste(avatar, (50, 125), mask)
        
        # Draw text
        text_color = design.get("text_color", "#FFFFFF")
        accent_color = design.get("accent_color", "#7289DA")
        
        try:
            # Try to load custom font
            title_font = ImageFont.truetype("arial.ttf", 40)
            text_font = ImageFont.truetype("arial.ttf", 25)
        except:
            # Fallback to default
            title_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
        
        # Welcome text
        draw.text((250, 100), "WELCOME!", fill=accent_color, font=title_font)
        
        # Member name
        name = member.name
        if len(name) > 20:
            name = name[:20] + "..."
        draw.text((250, 160), name, fill=text_color, font=text_font)
        
        # Server info
        draw.text((250, 220), f"Member #{member.guild.member_count}", fill=text_color, font=text_font)
        draw.text((250, 270), member.guild.name, fill=text_color, font=text_font)
        
        return image
    
    async def _generate_modern_card(self, member: Member, design: Dict[str, Any]) -> Image.Image:
        """Generate modern style card"""
        # Create gradient background
        image = Image.new("RGB", (self.card_width, self.card_height), "#23272A")
        draw = ImageDraw.Draw(image)
        
        # Create gradient effect
        accent_color = design.get("accent_color", "#7289DA")
        for i in range(self.card_height):
            opacity = int(255 * (1 - i / self.card_height))
            color = self._hex_to_rgb(accent_color)
            draw.rectangle([(0, i), (self.card_width, i+1)], 
                         fill=(*color, opacity))
        
        # Download and process avatar
        avatar = await self._get_avatar(member)
        if avatar:
            avatar = avatar.resize((180, 180))
            # Add border
            bordered = Image.new("RGB", (200, 200), accent_color)
            bordered.paste(avatar, (10, 10))
            image.paste(bordered, (300, 110))
        
        # Draw text
        text_color = design.get("text_color", "#FFFFFF")
        
        try:
            title_font = ImageFont.truetype("arial.ttf", 45)
            text_font = ImageFont.truetype("arial.ttf", 30)
        except:
            title_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
        
        draw.text((50, 50), "WELCOME TO", fill=text_color, font=text_font)
        draw.text((50, 100), member.guild.name.upper(), fill=accent_color, font=title_font)
        
        return image
    
    async def _generate_minimal_card(self, member: Member, design: Dict[str, Any]) -> Image.Image:
        """Generate minimal style card"""
        bg_color = design.get("background_color", "#FFFFFF")
        image = Image.new("RGB", (self.card_width, self.card_height), bg_color)
        draw = ImageDraw.Draw(image)
        
        # Simple design
        avatar = await self._get_avatar(member)
        if avatar:
            avatar = avatar.resize((120, 120))
            image.paste(avatar, (340, 50))
        
        text_color = design.get("text_color", "#000000")
        
        try:
            font = ImageFont.truetype("arial.ttf", 35)
        except:
            font = ImageFont.load_default()
        
        # Center text
        welcome_text = f"Welcome, {member.name}!"
        draw.text((400, 200), welcome_text, fill=text_color, font=font, anchor="mm")
        
        return image
    
    async def _generate_fancy_card(self, member: Member, design: Dict[str, Any]) -> Image.Image:
        """Generate fancy style card with effects"""
        # Create base with gradient
        image = Image.new("RGB", (self.card_width, self.card_height), "#1E1E1E")
        draw = ImageDraw.Draw(image)
        
        # Add decorative elements
        accent_color = self._hex_to_rgb(design.get("accent_color", "#FFD700"))
        
        # Draw decorative corners
        for i in range(0, 100, 2):
            color_val = int(255 * (1 - i / 100))
            draw.arc([(i, i), (200-i, 200-i)], 0, 90, fill=(*accent_color, color_val), width=2)
        
        # Avatar with glow effect
        avatar = await self._get_avatar(member)
        if avatar:
            avatar = avatar.resize((160, 160))
            # Create glow
            glow = avatar.filter(ImageFilter.GaussianBlur(10))
            image.paste(glow, (315, 115))
            image.paste(avatar, (320, 120))
        
        # Fancy text
        text_color = design.get("text_color", "#FFFFFF")
        
        try:
            title_font = ImageFont.truetype("arial.ttf", 50)
            text_font = ImageFont.truetype("arial.ttf", 28)
        except:
            title_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
        
        draw.text((400, 50), "✨ WELCOME ✨", fill=accent_color, font=title_font, anchor="mm")
        draw.text((400, 320), member.name, fill=text_color, font=text_font, anchor="mm")
        draw.text((400, 360), f"You are member #{member.guild.member_count}", 
                 fill=text_color, font=text_font, anchor="mm")
        
        return image
    
    async def _get_avatar(self, member: Member) -> Optional[Image.Image]:
        """Download and return member avatar"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(str(member.display_avatar.url)) as resp:
                    if resp.status == 200:
                        data = await resp.read()
                        return Image.open(io.BytesIO(data))
        except Exception as e:
            print(f"Error downloading avatar: {e}")
        return None
    
    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    async def _send_captcha(self, member: Member, settings: Dict[str, Any]) -> None:
        """Send captcha verification to member"""
        try:
            # Generate captcha code
            difficulty = settings.get("captcha_difficulty", "medium")
            code = self._generate_captcha_code(difficulty)
            
            # Create captcha image
            captcha_image = self._generate_captcha_image(code, settings)
            
            # Save verification
            timeout = settings.get("captcha_timeout", 300)  # 5 minutes
            await self.schema.create_captcha_verification(
                member.guild.id,
                member.id,
                code,
                timeout
            )
            
            # Send to member
            embed = discord.Embed(
                title="🛡️ Verification Required",
                description=f"Please solve the captcha below and send the code in this DM.\n"
                           f"You have {timeout // 60} minutes to verify.",
                color=discord.Color.blue()
            )
            
            buffer = io.BytesIO()
            captcha_image.save(buffer, format="PNG")
            buffer.seek(0)
            
            file = discord.File(buffer, filename="captcha.png")
            embed.set_image(url="attachment://captcha.png")
            
            await member.send(embed=embed, file=file)
            
            # Assign unverified role if configured
            unverified_role_id = settings.get("unverified_role")
            if unverified_role_id:
                role = member.guild.get_role(unverified_role_id)
                if role:
                    await member.add_roles(role)
                    
        except discord.Forbidden:
            # User has DMs disabled, can't verify
            pass
        except Exception as e:
            print(f"Error sending captcha: {e}")
    
    def _generate_captcha_code(self, difficulty: str) -> str:
        """Generate captcha code based on difficulty"""
        if difficulty == "easy":
            # 4 digits
            return ''.join(random.choices(string.digits, k=4))
        elif difficulty == "hard":
            # 6 alphanumeric
            return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        else:
            # medium: 5 alphanumeric
            return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    
    def _generate_captcha_image(self, code: str, settings: Dict[str, Any]) -> Image.Image:
        """Generate captcha image"""
        # Create image
        image = Image.new("RGB", (self.captcha_width, self.captcha_height), "#FFFFFF")
        draw = ImageDraw.Draw(image)
        
        # Add noise
        for _ in range(100):
            x = random.randint(0, self.captcha_width)
            y = random.randint(0, self.captcha_height)
            draw.point((x, y), fill="#CCCCCC")
        
        # Draw lines
        for _ in range(3):
            x1 = random.randint(0, self.captcha_width)
            y1 = random.randint(0, self.captcha_height)
            x2 = random.randint(0, self.captcha_width)
            y2 = random.randint(0, self.captcha_height)
            draw.line([(x1, y1), (x2, y2)], fill="#DDDDDD", width=2)
        
        # Draw code
        try:
            font = ImageFont.truetype("arial.ttf", 48)
        except:
            font = ImageFont.load_default()
        
        # Calculate text position
        bbox = draw.textbbox((0, 0), code, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (self.captcha_width - text_width) // 2
        y = (self.captcha_height - text_height) // 2
        
        # Draw with slight distortion
        for i, char in enumerate(code):
            offset_x = random.randint(-5, 5)
            offset_y = random.randint(-5, 5)
            draw.text((x + i * 40 + offset_x, y + offset_y), char, fill="#000000", font=font)
        
        return image
    
    async def verify_captcha(self, guild_id: int, user_id: int, code: str) -> bool:
        """Verify captcha code"""
        result = await self.schema.verify_captcha(guild_id, user_id, code)
        
        if result:
            # Get settings for post-verification actions
            settings = await self.schema.get_settings(guild_id)
            
            # Get member
            guild = discord.utils.get(self.db.guilds, id=guild_id)
            if guild:
                member = guild.get_member(user_id)
                if member:
                    # Remove unverified role
                    unverified_role_id = settings.get("unverified_role")
                    if unverified_role_id:
                        role = guild.get_role(unverified_role_id)
                        if role and role in member.roles:
                            await member.remove_roles(role)
                    
                    # Assign auto-role
                    if settings.get("auto_role_enabled", False):
                        await self._assign_auto_role(member, settings)
                    
                    # Send welcome
                    await self._send_welcome(member, settings)
                    
                    # Send success DM
                    try:
                        await member.send("✅ Verification successful! Welcome to the server!")
                    except:
                        pass
        
        return result
    
    async def _assign_auto_role(self, member: Member, settings: Dict[str, Any]) -> None:
        """Assign auto-role to member"""
        try:
            role_ids = settings.get("auto_roles", [])
            delay = settings.get("auto_role_delay", 0)
            
            if delay > 0:
                # Wait before assigning
                await asyncio.sleep(delay)
            
            for role_id in role_ids:
                role = member.guild.get_role(role_id)
                if role and role not in member.roles:
                    await member.add_roles(role)
                    
        except Exception as e:
            print(f"Error assigning auto-role: {e}")
    
    async def _check_anti_raid(self, guild_id: int) -> bool:
        """Check if raid is detected"""
        settings = await self.schema.get_settings(guild_id)
        if not settings or not settings.get("anti_raid_enabled", False):
            return False
        
        threshold = settings.get("anti_raid_threshold", 10)
        return await self.schema.is_raid_detected(guild_id, threshold)
    
    async def test_welcome(self, member: Member) -> None:
        """Test welcome message"""
        settings = await self.schema.get_settings(member.guild.id)
        if not settings:
            return
        
        await self._send_welcome(member, settings)
