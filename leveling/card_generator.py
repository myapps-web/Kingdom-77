"""
Level Card Generator
Generate custom level up cards using PIL/Pillow
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
import aiohttp
from typing import Optional, Tuple
import os

class CardGenerator:
    """Generate level cards with customization"""
    
    # Card dimensions
    WIDTH = 900
    HEIGHT = 250
    
    # Avatar settings
    AVATAR_SIZE = 180
    AVATAR_POS = (35, 35)
    
    # Text positions
    USERNAME_POS = (240, 40)
    LEVEL_POS = (240, 100)
    XP_POS = (240, 160)
    RANK_POS = (800, 40)
    
    # Progress bar
    PROGRESS_BAR_POS = (240, 200)
    PROGRESS_BAR_WIDTH = 620
    PROGRESS_BAR_HEIGHT = 30
    
    def __init__(self):
        """Initialize card generator"""
        self.fonts_loaded = False
        self.default_font = None
        self.load_fonts()
    
    def load_fonts(self):
        """Load fonts"""
        try:
            # Try to load Arial (available on most systems)
            self.username_font = ImageFont.truetype("arial.ttf", 40)
            self.level_font = ImageFont.truetype("arialbd.ttf", 36)
            self.xp_font = ImageFont.truetype("arial.ttf", 24)
            self.rank_font = ImageFont.truetype("arialbd.ttf", 32)
            self.fonts_loaded = True
        except:
            # Fallback to default font
            self.username_font = ImageFont.load_default()
            self.level_font = ImageFont.load_default()
            self.xp_font = ImageFont.load_default()
            self.rank_font = ImageFont.load_default()
            self.fonts_loaded = False
    
    def hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    async def download_avatar(self, avatar_url: str) -> Optional[Image.Image]:
        """Download user avatar"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(avatar_url) as response:
                    if response.status == 200:
                        avatar_bytes = await response.read()
                        avatar = Image.open(BytesIO(avatar_bytes))
                        return avatar.convert("RGBA")
        except Exception as e:
            print(f"Error downloading avatar: {e}")
        return None
    
    def create_circular_avatar(
        self, 
        avatar: Image.Image, 
        size: int, 
        border_color: Tuple[int, int, int], 
        border_width: int
    ) -> Image.Image:
        """Create circular avatar with border"""
        # Resize avatar
        avatar = avatar.resize((size, size), Image.Resampling.LANCZOS)
        
        # Create circular mask
        mask = Image.new('L', (size, size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, size, size), fill=255)
        
        # Apply mask to avatar
        circular_avatar = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        circular_avatar.paste(avatar, (0, 0))
        circular_avatar.putalpha(mask)
        
        # Add border
        if border_width > 0:
            total_size = size + (border_width * 2)
            bordered = Image.new('RGBA', (total_size, total_size), (0, 0, 0, 0))
            border_draw = ImageDraw.Draw(bordered)
            
            # Draw border circle
            border_draw.ellipse(
                (0, 0, total_size, total_size),
                fill=border_color,
                outline=border_color
            )
            
            # Paste avatar on top
            bordered.paste(circular_avatar, (border_width, border_width), circular_avatar)
            return bordered
        
        return circular_avatar
    
    def draw_progress_bar(
        self,
        draw: ImageDraw.ImageDraw,
        x: int,
        y: int,
        width: int,
        height: int,
        progress: float,
        bg_color: Tuple[int, int, int],
        fill_color: Tuple[int, int, int],
        border_radius: int = 15
    ):
        """Draw rounded progress bar"""
        # Background bar
        draw.rounded_rectangle(
            [x, y, x + width, y + height],
            radius=border_radius,
            fill=bg_color
        )
        
        # Progress fill
        if progress > 0:
            fill_width = int(width * min(progress, 1.0))
            if fill_width > 0:
                draw.rounded_rectangle(
                    [x, y, x + fill_width, y + height],
                    radius=border_radius,
                    fill=fill_color
                )
    
    async def generate_card(
        self,
        username: str,
        discriminator: str,
        level: int,
        current_xp: int,
        required_xp: int,
        rank: int,
        total_users: int,
        avatar_url: str,
        # Design options
        background_color: str = "#2C2F33",
        background_image: Optional[str] = None,
        progress_bar_color: str = "#5865F2",
        progress_bar_bg_color: str = "#99AAB5",
        text_color: str = "#FFFFFF",
        accent_color: str = "#5865F2",
        avatar_border_color: str = "#5865F2",
        avatar_border_width: int = 5,
        show_rank: bool = True,
        show_progress_percentage: bool = True
    ) -> BytesIO:
        """Generate a level card"""
        
        # Create base image
        if background_image:
            # TODO: Support background images
            img = Image.new('RGB', (self.WIDTH, self.HEIGHT), self.hex_to_rgb(background_color))
        else:
            img = Image.new('RGB', (self.WIDTH, self.HEIGHT), self.hex_to_rgb(background_color))
        
        # Download and process avatar
        avatar = await self.download_avatar(avatar_url)
        if avatar:
            circular_avatar = self.create_circular_avatar(
                avatar,
                self.AVATAR_SIZE,
                self.hex_to_rgb(avatar_border_color),
                avatar_border_width
            )
            
            # Paste avatar
            avatar_x = self.AVATAR_POS[0] - avatar_border_width
            avatar_y = self.AVATAR_POS[1] - avatar_border_width
            img.paste(circular_avatar, (avatar_x, avatar_y), circular_avatar)
        
        # Draw text
        draw = ImageDraw.Draw(img)
        text_rgb = self.hex_to_rgb(text_color)
        accent_rgb = self.hex_to_rgb(accent_color)
        
        # Username
        full_username = f"{username}#{discriminator}" if discriminator != "0" else username
        draw.text(self.USERNAME_POS, full_username, fill=text_rgb, font=self.username_font)
        
        # Level
        level_text = f"Level {level}"
        draw.text(self.LEVEL_POS, level_text, fill=accent_rgb, font=self.level_font)
        
        # XP
        xp_text = f"{current_xp:,} / {required_xp:,} XP"
        draw.text(self.XP_POS, xp_text, fill=text_rgb, font=self.xp_font)
        
        # Rank
        if show_rank:
            rank_text = f"#{rank}"
            # Right-align rank
            rank_bbox = draw.textbbox((0, 0), rank_text, font=self.rank_font)
            rank_width = rank_bbox[2] - rank_bbox[0]
            rank_x = self.WIDTH - rank_width - 40
            draw.text((rank_x, self.RANK_POS[1]), rank_text, fill=accent_rgb, font=self.rank_font)
            
            # Total users (small text below rank)
            total_text = f"of {total_users:,}"
            total_bbox = draw.textbbox((0, 0), total_text, font=self.xp_font)
            total_width = total_bbox[2] - total_bbox[0]
            total_x = self.WIDTH - total_width - 40
            draw.text((total_x, self.RANK_POS[1] + 40), total_text, fill=text_rgb, font=self.xp_font)
        
        # Progress bar
        progress = current_xp / required_xp if required_xp > 0 else 0
        self.draw_progress_bar(
            draw,
            self.PROGRESS_BAR_POS[0],
            self.PROGRESS_BAR_POS[1],
            self.PROGRESS_BAR_WIDTH,
            self.PROGRESS_BAR_HEIGHT,
            progress,
            self.hex_to_rgb(progress_bar_bg_color),
            self.hex_to_rgb(progress_bar_color)
        )
        
        # Progress percentage
        if show_progress_percentage:
            percentage_text = f"{int(progress * 100)}%"
            percentage_bbox = draw.textbbox((0, 0), percentage_text, font=self.xp_font)
            percentage_width = percentage_bbox[2] - percentage_bbox[0]
            percentage_x = self.PROGRESS_BAR_POS[0] + (self.PROGRESS_BAR_WIDTH // 2) - (percentage_width // 2)
            percentage_y = self.PROGRESS_BAR_POS[1] + 3
            draw.text((percentage_x, percentage_y), percentage_text, fill=text_rgb, font=self.xp_font)
        
        # Save to BytesIO
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return buffer

# Global instance
card_generator = CardGenerator()

async def generate_level_card(
    username: str,
    discriminator: str,
    level: int,
    current_xp: int,
    required_xp: int,
    rank: int,
    total_users: int,
    avatar_url: str,
    **design_options
) -> BytesIO:
    """Generate a level card (convenience function)"""
    return await card_generator.generate_card(
        username,
        discriminator,
        level,
        current_xp,
        required_xp,
        rank,
        total_users,
        avatar_url,
        **design_options
    )
