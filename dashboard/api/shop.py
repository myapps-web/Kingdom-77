"""
Kingdom-77 Bot v3.8 - Shop API Endpoints

FastAPI endpoints for shop items and user inventory management.

Endpoints:
- GET /api/shop/items - Get all shop items
- GET /api/shop/items/{item_type} - Get items by type
- GET /api/shop/{user_id}/inventory - Get user inventory
- POST /api/shop/{user_id}/purchase - Purchase item
- POST /api/shop/{user_id}/equip - Equip item

Author: Kingdom-77 Team
Date: 2024
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Import database
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.credits_schema import (
    ShopItem,
    UserInventory,
    UserCredits,
    CreditTransaction,
    get_rarity_emoji,
    get_rarity_color
)

router = APIRouter(prefix="/api/shop", tags=["Shop"])


# ============================================================
# PYDANTIC MODELS
# ============================================================

class ShopItemResponse(BaseModel):
    item_id: str
    name: str
    name_ar: str
    description: str
    description_ar: str
    type: str
    price: int
    rarity: str
    rarity_emoji: str
    rarity_color: int
    preview_url: Optional[str]
    color: Optional[str]
    emoji: str
    total_sales: int
    owned: bool = False
    equipped: bool = False


class InventoryItemResponse(BaseModel):
    item_id: str
    item_name: str
    item_type: str
    equipped: bool
    acquired_at: datetime


class PurchaseItemRequest(BaseModel):
    user_id: int
    username: str
    item_id: str


class PurchaseItemResponse(BaseModel):
    success: bool
    item: Dict[str, Any]
    new_balance: int
    message: str


class EquipItemRequest(BaseModel):
    user_id: int
    item_id: str


class EquipItemResponse(BaseModel):
    success: bool
    item_id: str
    item_type: str
    message: str


# ============================================================
# ENDPOINTS
# ============================================================

@router.get("/items", response_model=List[ShopItemResponse])
async def get_shop_items(
    item_type: Optional[str] = None,
    user_id: Optional[int] = None
):
    """
    Get all shop items, optionally filtered by type.
    
    Query Parameters:
    - item_type: Filter by type (frame, badge, banner, theme)
    - user_id: If provided, includes ownership status
    
    Types:
    - frame: Level card borders
    - badge: Profile badges
    - banner: Level card backgrounds
    - theme: Complete level card themes
    """
    try:
        items = await ShopItem.get_all_items(item_type=item_type, enabled_only=True)
        
        # Get user inventory if user_id provided
        user_inventory = []
        equipped_items = {}
        if user_id:
            user_inventory_items = await UserInventory.get_user_inventory(user_id)
            user_inventory = [inv['item_id'] for inv in user_inventory_items]
            equipped_items = {inv['item_id']: inv['equipped'] for inv in user_inventory_items}
        
        return [
            ShopItemResponse(
                item_id=item['item_id'],
                name=item['name'],
                name_ar=item['name_ar'],
                description=item['description'],
                description_ar=item['description_ar'],
                type=item['type'],
                price=item['price'],
                rarity=item['rarity'],
                rarity_emoji=get_rarity_emoji(item['rarity']),
                rarity_color=get_rarity_color(item['rarity']),
                preview_url=item.get('preview_url'),
                color=item.get('color'),
                emoji=item['emoji'],
                total_sales=item.get('total_sales', 0),
                owned=item['item_id'] in user_inventory,
                equipped=equipped_items.get(item['item_id'], False)
            )
            for item in items
        ]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get shop items: {str(e)}"
        )


@router.get("/items/{item_type}", response_model=List[ShopItemResponse])
async def get_shop_items_by_type(
    item_type: str,
    user_id: Optional[int] = None
):
    """
    Get shop items filtered by type.
    
    Path Parameters:
    - item_type: frames, badges, banners, or themes
    """
    return await get_shop_items(item_type=item_type, user_id=user_id)


@router.get("/{user_id}/inventory", response_model=List[InventoryItemResponse])
async def get_user_inventory(
    user_id: int,
    item_type: Optional[str] = None
):
    """
    Get user's inventory.
    
    Query Parameters:
    - item_type: Filter by type (frame, badge, banner, theme)
    """
    try:
        inventory = await UserInventory.get_user_inventory(
            user_id=user_id,
            item_type=item_type
        )
        
        return [
            InventoryItemResponse(
                item_id=inv['item_id'],
                item_name=inv['item_name'],
                item_type=inv['item_type'],
                equipped=inv['equipped'],
                acquired_at=inv['acquired_at']
            )
            for inv in inventory
        ]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get inventory: {str(e)}"
        )


@router.post("/{user_id}/purchase", response_model=PurchaseItemResponse)
async def purchase_item(request: PurchaseItemRequest):
    """
    Purchase an item from the shop.
    
    Rules:
    - Must have sufficient credits
    - Cannot purchase owned items
    - Item must exist and be enabled
    """
    try:
        # Get item
        item = await ShopItem.get_item(request.item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
        
        if not item.get('enabled', False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Item is not available for purchase"
            )
        
        # Check if user already owns it
        has_item = await UserInventory.has_item(request.user_id, request.item_id)
        if has_item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You already own this item"
            )
        
        # Get user balance
        user = await UserCredits.get_or_create_user(request.user_id, request.username)
        
        if user['balance'] < item['price']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient credits. You have {user['balance']} ❄️, need {item['price']} ❄️"
            )
        
        # Deduct credits
        await UserCredits.update_balance(request.user_id, -item['price'])
        
        # Add to inventory
        await UserInventory.add_item(request.user_id, request.item_id, item)
        
        # Increment sales
        await ShopItem.increment_sales(request.item_id)
        
        # Create transaction
        await CreditTransaction.create_transaction(
            user_id=request.user_id,
            transaction_type="shop_purchase",
            amount=-item['price'],
            description=f"Purchased {item['name']} {item['emoji']}",
            metadata={
                "item_id": item['item_id'],
                "item_type": item['type'],
                "item_rarity": item['rarity']
            }
        )
        
        # Get updated balance
        updated_user = await UserCredits.get_user(request.user_id)
        
        return PurchaseItemResponse(
            success=True,
            item={
                "item_id": item['item_id'],
                "name": item['name'],
                "type": item['type'],
                "emoji": item['emoji']
            },
            new_balance=updated_user['balance'],
            message=f"Successfully purchased {item['name']} {item['emoji']}!"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to purchase item: {str(e)}"
        )


@router.post("/{user_id}/equip", response_model=EquipItemResponse)
async def equip_item(request: EquipItemRequest):
    """
    Equip an item from inventory.
    
    Rules:
    - Must own the item
    - Automatically unequips other items of same type
    """
    try:
        # Check if user owns item
        has_item = await UserInventory.has_item(request.user_id, request.item_id)
        if not has_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found in inventory"
            )
        
        # Get item details
        inventory_item = await UserInventory.get_user_inventory(request.user_id)
        item_data = next((inv for inv in inventory_item if inv['item_id'] == request.item_id), None)
        
        if not item_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found in inventory"
            )
        
        # Equip item (will auto-unequip others of same type)
        success = await UserInventory.equip_item(
            request.user_id,
            request.item_id,
            item_data['item_type']
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to equip item"
            )
        
        return EquipItemResponse(
            success=True,
            item_id=request.item_id,
            item_type=item_data['item_type'],
            message=f"Successfully equipped {item_data['item_name']}!"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to equip item: {str(e)}"
        )


@router.get("/{user_id}/equipped", response_model=Dict[str, InventoryItemResponse])
async def get_equipped_items(user_id: int):
    """
    Get all currently equipped items by type.
    
    Returns a dictionary with item types as keys.
    """
    try:
        equipped = await UserInventory.get_equipped_items(user_id)
        
        return {
            item_type: InventoryItemResponse(
                item_id=item['item_id'],
                item_name=item['item_name'],
                item_type=item['item_type'],
                equipped=item['equipped'],
                acquired_at=item['acquired_at']
            )
            for item_type, item in equipped.items()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get equipped items: {str(e)}"
        )


# Export router
__all__ = ['router']
