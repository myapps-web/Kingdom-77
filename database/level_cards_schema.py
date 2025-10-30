"""
Level Cards Schema
Database collections for custom level card designs
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase

# Collection names
CARD_DESIGNS = "guild_card_designs"
CARD_TEMPLATES = "card_templates"

# Default templates
DEFAULT_TEMPLATES = {
    "classic": {
        "name": "Classic",
        "description": "Clean and simple design",
        "background_color": "#2C2F33",
        "progress_bar_color": "#5865F2",
        "text_color": "#FFFFFF",
        "accent_color": "#5865F2",
        "font": "arial",
        "avatar_border_color": "#5865F2"
    },
    "dark": {
        "name": "Dark",
        "description": "Modern dark theme",
        "background_color": "#1A1A1A",
        "progress_bar_color": "#00D9FF",
        "text_color": "#FFFFFF",
        "accent_color": "#00D9FF",
        "font": "arial",
        "avatar_border_color": "#00D9FF"
    },
    "light": {
        "name": "Light",
        "description": "Bright and clean",
        "background_color": "#FFFFFF",
        "progress_bar_color": "#5865F2",
        "text_color": "#2C2F33",
        "accent_color": "#5865F2",
        "font": "arial",
        "avatar_border_color": "#5865F2"
    },
    "purple": {
        "name": "Purple Dream",
        "description": "Purple gradient theme",
        "background_color": "#6B46C1",
        "progress_bar_color": "#D946EF",
        "text_color": "#FFFFFF",
        "accent_color": "#D946EF",
        "font": "arial",
        "avatar_border_color": "#D946EF"
    },
    "ocean": {
        "name": "Ocean Blue",
        "description": "Cool ocean theme",
        "background_color": "#0EA5E9",
        "progress_bar_color": "#38BDF8",
        "text_color": "#FFFFFF",
        "accent_color": "#38BDF8",
        "font": "arial",
        "avatar_border_color": "#38BDF8"
    },
    "forest": {
        "name": "Forest Green",
        "description": "Natural green theme",
        "background_color": "#10B981",
        "progress_bar_color": "#34D399",
        "text_color": "#FFFFFF",
        "accent_color": "#34D399",
        "font": "arial",
        "avatar_border_color": "#34D399"
    },
    "sunset": {
        "name": "Sunset",
        "description": "Warm sunset colors",
        "background_color": "#F97316",
        "progress_bar_color": "#FB923C",
        "text_color": "#FFFFFF",
        "accent_color": "#FB923C",
        "font": "arial",
        "avatar_border_color": "#FB923C"
    },
    "cyber": {
        "name": "Cyberpunk",
        "description": "Neon cyberpunk style",
        "background_color": "#1E1B4B",
        "progress_bar_color": "#F0ABFC",
        "text_color": "#E0E7FF",
        "accent_color": "#F0ABFC",
        "font": "arial",
        "avatar_border_color": "#F0ABFC"
    }
}

# Card design schema
CARD_DESIGN_SCHEMA = {
    "guild_id": str,
    "template": str,  # Template name or "custom"
    "background_color": str,  # Hex color
    "background_image": Optional[str],  # URL to background image
    "progress_bar_color": str,
    "progress_bar_bg_color": Optional[str],
    "text_color": str,
    "accent_color": str,
    "font": str,  # Font name
    "avatar_border_color": str,
    "avatar_border_width": int,
    "show_rank": bool,
    "show_progress_percentage": bool,
    "custom_settings": Dict[str, Any],
    "created_at": datetime,
    "updated_at": datetime
}

class LevelCardsSchema:
    """Level cards database operations"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.card_designs = db[CARD_DESIGNS]
        self.card_templates = db[CARD_TEMPLATES]
    
    async def initialize(self):
        """Initialize collections and indexes"""
        # Create indexes
        await self.card_designs.create_index("guild_id", unique=True)
        
        # Insert default templates if not exists
        for template_id, template_data in DEFAULT_TEMPLATES.items():
            await self.card_templates.update_one(
                {"template_id": template_id},
                {
                    "$set": {
                        "template_id": template_id,
                        **template_data,
                        "updated_at": datetime.utcnow()
                    }
                },
                upsert=True
            )
    
    async def get_card_design(self, guild_id: str) -> Optional[Dict[str, Any]]:
        """Get card design for a guild"""
        design = await self.card_designs.find_one({"guild_id": guild_id})
        
        if not design:
            # Return default template
            return {
                "guild_id": guild_id,
                "template": "classic",
                **DEFAULT_TEMPLATES["classic"],
                "background_image": None,
                "progress_bar_bg_color": "#99AAB5",
                "avatar_border_width": 5,
                "show_rank": True,
                "show_progress_percentage": True,
                "custom_settings": {}
            }
        
        return design
    
    async def save_card_design(
        self,
        guild_id: str,
        template: str = "custom",
        background_color: str = "#2C2F33",
        background_image: Optional[str] = None,
        progress_bar_color: str = "#5865F2",
        progress_bar_bg_color: str = "#99AAB5",
        text_color: str = "#FFFFFF",
        accent_color: str = "#5865F2",
        font: str = "arial",
        avatar_border_color: str = "#5865F2",
        avatar_border_width: int = 5,
        show_rank: bool = True,
        show_progress_percentage: bool = True,
        custom_settings: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Save or update card design for a guild"""
        try:
            design = {
                "guild_id": guild_id,
                "template": template,
                "background_color": background_color,
                "background_image": background_image,
                "progress_bar_color": progress_bar_color,
                "progress_bar_bg_color": progress_bar_bg_color,
                "text_color": text_color,
                "accent_color": accent_color,
                "font": font,
                "avatar_border_color": avatar_border_color,
                "avatar_border_width": avatar_border_width,
                "show_rank": show_rank,
                "show_progress_percentage": show_progress_percentage,
                "custom_settings": custom_settings or {},
                "updated_at": datetime.utcnow()
            }
            
            result = await self.card_designs.update_one(
                {"guild_id": guild_id},
                {
                    "$set": design,
                    "$setOnInsert": {"created_at": datetime.utcnow()}
                },
                upsert=True
            )
            
            return result.acknowledged
        except Exception as e:
            print(f"Error saving card design: {e}")
            return False
    
    async def delete_card_design(self, guild_id: str) -> bool:
        """Delete card design (reset to default)"""
        try:
            result = await self.card_designs.delete_one({"guild_id": guild_id})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting card design: {e}")
            return False
    
    async def get_all_templates(self) -> List[Dict[str, Any]]:
        """Get all available templates"""
        templates = []
        async for template in self.card_templates.find():
            templates.append(template)
        
        # If no templates in DB, return defaults
        if not templates:
            return [
                {"template_id": tid, **data}
                for tid, data in DEFAULT_TEMPLATES.items()
            ]
        
        return templates
    
    async def apply_template(self, guild_id: str, template_id: str) -> bool:
        """Apply a template to a guild"""
        if template_id not in DEFAULT_TEMPLATES:
            return False
        
        template_data = DEFAULT_TEMPLATES[template_id]
        
        return await self.save_card_design(
            guild_id=guild_id,
            template=template_id,
            background_color=template_data["background_color"],
            progress_bar_color=template_data["progress_bar_color"],
            text_color=template_data["text_color"],
            accent_color=template_data["accent_color"],
            font=template_data["font"],
            avatar_border_color=template_data["avatar_border_color"]
        )
    
    async def get_guild_stats(self, guild_id: str) -> Dict[str, Any]:
        """Get card usage statistics for a guild"""
        design = await self.get_card_design(guild_id)
        
        return {
            "guild_id": guild_id,
            "has_custom_design": design.get("template") == "custom",
            "template": design.get("template", "classic"),
            "has_background_image": bool(design.get("background_image")),
            "last_updated": design.get("updated_at")
        }

# Helper functions
async def initialize_level_cards_schema(db: AsyncIOMotorDatabase):
    """Initialize level cards schema"""
    schema = LevelCardsSchema(db)
    await schema.initialize()
    print("✅ Level cards schema initialized")

async def get_card_design(db: AsyncIOMotorDatabase, guild_id: str) -> Dict[str, Any]:
    """Get card design for a guild"""
    schema = LevelCardsSchema(db)
    return await schema.get_card_design(guild_id)

async def save_card_design(db: AsyncIOMotorDatabase, guild_id: str, **kwargs) -> bool:
    """Save card design"""
    schema = LevelCardsSchema(db)
    return await schema.save_card_design(guild_id, **kwargs)

async def get_all_templates(db: AsyncIOMotorDatabase) -> List[Dict[str, Any]]:
    """Get all templates"""
    schema = LevelCardsSchema(db)
    return await schema.get_all_templates()

async def apply_template(db: AsyncIOMotorDatabase, guild_id: str, template_id: str) -> bool:
    """Apply template"""
    schema = LevelCardsSchema(db)
    return await schema.apply_template(guild_id, template_id)
