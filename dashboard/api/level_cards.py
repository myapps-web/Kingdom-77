"""
Level Cards API Endpoints
Handles custom level card designs and previews
"""

from fastapi import APIRouter, HTTPException, Depends, Response
from pydantic import BaseModel, Field
from typing import Optional
import logging
from io import BytesIO

from ..auth import get_current_user
from database.mongodb import db
from database.level_cards_schema import LevelCardsSchema, DEFAULT_TEMPLATES

logger = logging.getLogger(__name__)
router = APIRouter()

# ==================== Pydantic Models ====================

class CardDesignUpdate(BaseModel):
    """Model for updating card design"""
    template: Optional[str] = None
    background_color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    background_image: Optional[str] = None
    progress_bar_color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    progress_bar_bg_color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    text_color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    accent_color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    font: Optional[str] = None
    avatar_border_color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    avatar_border_width: Optional[int] = Field(None, ge=0, le=15)
    show_rank: Optional[bool] = None
    show_progress_percentage: Optional[bool] = None


class CardPreviewRequest(BaseModel):
    """Model for card preview request"""
    username: str = "TestUser"
    discriminator: str = "0"
    level: int = 50
    current_xp: int = 750
    required_xp: int = 1000
    rank: int = 5
    total_users: int = 1234
    avatar_url: Optional[str] = None
    background_color: str = "#2C2F33"
    progress_bar_color: str = "#5865F2"
    progress_bar_bg_color: str = "#99AAB5"
    text_color: str = "#FFFFFF"
    accent_color: str = "#5865F2"
    avatar_border_color: str = "#5865F2"
    avatar_border_width: int = 5
    show_rank: bool = True
    show_progress_percentage: bool = True


# ==================== Helper Functions ====================

async def check_premium_access(guild_id: str, user_id: str) -> bool:
    """Check if guild has premium access for custom cards"""
    try:
        from database.premium_schema import PremiumSchema
        
        premium_schema = PremiumSchema(db)
        subscription = await premium_schema.get_subscription(guild_id)
        
        if not subscription:
            return False
        
        return subscription.get('status') == 'active' and subscription.get('tier') == 'premium'
    except Exception as e:
        logger.error(f"Error checking premium access: {e}")
        return False


# ==================== API Endpoints ====================

@router.get("/{guild_id}/card-design")
async def get_card_design(
    guild_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Get current card design for a guild
    
    Returns the current card design settings, or default if none set.
    """
    try:
        schema = LevelCardsSchema(db)
        design = await schema.get_card_design(guild_id)
        
        if not design:
            # Return default design
            default_template = DEFAULT_TEMPLATES['classic']
            design = {
                'guild_id': guild_id,
                'template': 'classic',
                **default_template
            }
        
        return design
        
    except Exception as e:
        logger.error(f"Error getting card design for guild {guild_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{guild_id}/card-design")
async def update_card_design(
    guild_id: str,
    design: CardDesignUpdate,
    user_id: str = Depends(get_current_user)
):
    """
    Update card design for a guild
    
    Templates are free, custom colors require Premium.
    """
    try:
        schema = LevelCardsSchema(db)
        
        # If applying a template, allow without premium
        if design.template and all(
            getattr(design, field) is None 
            for field in design.model_fields 
            if field != 'template'
        ):
            # Just applying a template
            success = await schema.apply_template(guild_id, design.template)
            if not success:
                raise HTTPException(status_code=400, detail="Invalid template")
            
            # Return updated design
            updated_design = await schema.get_card_design(guild_id)
            return updated_design
        
        # For custom colors, check premium
        has_premium = await check_premium_access(guild_id, user_id)
        if not has_premium:
            raise HTTPException(
                status_code=403,
                detail="Custom card colors require Premium subscription"
            )
        
        # Update design with provided fields
        update_data = design.model_dump(exclude_none=True)
        
        success = await schema.save_card_design(guild_id, **update_data)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to update design")
        
        # Return updated design
        updated_design = await schema.get_card_design(guild_id)
        return updated_design
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating card design for guild {guild_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{guild_id}/card-design")
async def reset_card_design(
    guild_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Reset card design to default
    """
    try:
        schema = LevelCardsSchema(db)
        success = await schema.delete_card_design(guild_id)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to reset design")
        
        return {
            'success': True,
            'message': 'Card design reset to default'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting card design for guild {guild_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{guild_id}/templates")
async def get_templates(
    guild_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Get all available card templates
    
    Returns list of all preset templates with their details.
    """
    try:
        schema = LevelCardsSchema(db)
        templates = await schema.get_all_templates()
        
        # Convert to list format for frontend
        template_list = [
            {
                'id': template_id,
                **template_data
            }
            for template_id, template_data in templates.items()
        ]
        
        return template_list
        
    except Exception as e:
        logger.error(f"Error getting templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{guild_id}/preview-card")
async def preview_card(
    guild_id: str,
    preview_data: CardPreviewRequest,
    user_id: str = Depends(get_current_user)
):
    """
    Generate a preview of a level card
    
    Returns a PNG image of the level card with the provided settings.
    """
    try:
        from leveling.card_generator import generate_level_card
        
        # Generate card with provided settings
        card_buffer = await generate_level_card(
            username=preview_data.username,
            discriminator=preview_data.discriminator,
            level=preview_data.level,
            current_xp=preview_data.current_xp,
            required_xp=preview_data.required_xp,
            rank=preview_data.rank,
            total_users=preview_data.total_users,
            avatar_url=preview_data.avatar_url,
            background_color=preview_data.background_color,
            progress_bar_color=preview_data.progress_bar_color,
            progress_bar_bg_color=preview_data.progress_bar_bg_color,
            text_color=preview_data.text_color,
            accent_color=preview_data.accent_color,
            avatar_border_color=preview_data.avatar_border_color,
            avatar_border_width=preview_data.avatar_border_width,
            show_rank=preview_data.show_rank,
            show_progress_percentage=preview_data.show_progress_percentage
        )
        
        # Return image as response
        return Response(
            content=card_buffer.getvalue(),
            media_type="image/png",
            headers={
                'Content-Disposition': 'inline; filename="levelcard_preview.png"'
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating card preview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{guild_id}/card-stats")
async def get_card_stats(
    guild_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Get statistics about card usage
    
    Returns info about current design and available features.
    """
    try:
        schema = LevelCardsSchema(db)
        design = await schema.get_card_design(guild_id)
        
        has_premium = await check_premium_access(guild_id, user_id)
        
        stats = {
            'current_template': design.get('template', 'classic') if design else 'classic',
            'is_custom': design is not None,
            'has_premium': has_premium,
            'available_templates': len(DEFAULT_TEMPLATES),
            'features': {
                'templates': True,  # Always available
                'custom_colors': has_premium,
                'background_images': has_premium,
                'advanced_options': has_premium
            }
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting card stats for guild {guild_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Admin Endpoints ====================

@router.get("/admin/all-designs")
async def get_all_designs(
    user_id: str = Depends(get_current_user),
    limit: int = 100
):
    """
    Admin: Get all custom card designs
    
    Returns list of all guilds with custom designs (for admin monitoring).
    """
    try:
        # TODO: Add admin permission check
        
        designs = await db['guild_card_designs'].find().limit(limit).to_list(limit)
        
        return {
            'total': len(designs),
            'designs': designs
        }
        
    except Exception as e:
        logger.error(f"Error getting all designs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/template-usage")
async def get_template_usage(
    user_id: str = Depends(get_current_user)
):
    """
    Admin: Get template usage statistics
    
    Returns count of how many guilds use each template.
    """
    try:
        # TODO: Add admin permission check
        
        pipeline = [
            {
                '$group': {
                    '_id': '$template',
                    'count': {'$sum': 1}
                }
            },
            {
                '$sort': {'count': -1}
            }
        ]
        
        results = await db['guild_card_designs'].aggregate(pipeline).to_list(100)
        
        # Format results
        usage = {
            result['_id']: result['count']
            for result in results
        }
        
        # Add templates with 0 usage
        for template_id in DEFAULT_TEMPLATES.keys():
            if template_id not in usage:
                usage[template_id] = 0
        
        return {
            'template_usage': usage,
            'total_custom_designs': sum(usage.values())
        }
        
    except Exception as e:
        logger.error(f"Error getting template usage: {e}")
        raise HTTPException(status_code=500, detail=str(e))
