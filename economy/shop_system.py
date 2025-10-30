"""
Kingdom-77 Bot v3.8 - Shop System

This module manages the shop and inventory system including:
- Shop items (frames, badges, banners, themes)
- Item purchases with credits
- Inventory management
- Equip/unequip system
- Item previews

Author: Kingdom-77 Team
Date: 2024
"""

import discord
from discord.ext import commands
from typing import Optional, Dict, Any, List
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


class ShopSystem:
    """
    Main system for managing the shop and inventory.
    
    Features:
    - Browse shop items by category
    - Purchase items with credits
    - Inventory management
    - Equip/unequip items
    - Item previews
    """
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.item_cache = {}  # Cache for shop items
        self.cache_timestamp = None
        self.cache_ttl = 300  # 5 minutes
    
    # ============================================================
    # SHOP ITEMS
    # ============================================================
    
    async def get_shop_items(
        self,
        item_type: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get shop items, optionally filtered by type.
        
        Args:
            item_type: Filter by type (frame, badge, banner, theme)
            user_id: If provided, includes ownership status
            
        Returns:
            List of shop items with metadata
        """
        items = await ShopItem.get_all_items(item_type=item_type, enabled_only=True)
        
        # Get user inventory if user_id provided
        user_inventory = []
        equipped_items = {}
        if user_id:
            inventory = await UserInventory.get_user_inventory(user_id)
            user_inventory = [inv['item_id'] for inv in inventory]
            equipped_items = {inv['item_id']: inv['equipped'] for inv in inventory}
        
        # Add metadata
        result = []
        for item in items:
            result.append({
                **item,
                'rarity_emoji': get_rarity_emoji(item['rarity']),
                'rarity_color': get_rarity_color(item['rarity']),
                'owned': item['item_id'] in user_inventory if user_id else False,
                'equipped': equipped_items.get(item['item_id'], False) if user_id else False
            })
        
        return result
    
    async def get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Get specific item by ID.
        
        Args:
            item_id: Item ID
            
        Returns:
            Item data or None
        """
        item = await ShopItem.get_item(item_id)
        if item:
            item['rarity_emoji'] = get_rarity_emoji(item['rarity'])
            item['rarity_color'] = get_rarity_color(item['rarity'])
        return item
    
    async def get_items_by_category(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all items organized by category.
        
        Returns:
            Dictionary with categories as keys
        """
        all_items = await self.get_shop_items()
        
        categories = {
            'frames': [],
            'badges': [],
            'banners': [],
            'themes': []
        }
        
        for item in all_items:
            item_type = item.get('type')
            if item_type in categories:
                categories[item_type].append(item)
        
        return categories
    
    # ============================================================
    # PURCHASE SYSTEM
    # ============================================================
    
    async def purchase_item(
        self,
        user_id: int,
        username: str,
        item_id: str,
        credits_system
    ) -> Dict[str, Any]:
        """
        Purchase an item from the shop.
        
        Args:
            user_id: Discord user ID
            username: Discord username
            item_id: Item ID to purchase
            credits_system: CreditsSystem instance
            
        Returns:
            Dictionary with purchase result
        """
        # Get item
        item = await ShopItem.get_item(item_id)
        if not item:
            return {
                'success': False,
                'error': 'item_not_found',
                'message': 'Item not found'
            }
        
        if not item.get('enabled', False):
            return {
                'success': False,
                'error': 'item_unavailable',
                'message': 'Item is not available for purchase'
            }
        
        # Check if already owned
        has_item = await UserInventory.has_item(user_id, item_id)
        if has_item:
            return {
                'success': False,
                'error': 'already_owned',
                'message': 'You already own this item'
            }
        
        # Check balance
        price = item['price']
        if not await credits_system.has_sufficient_balance(user_id, price):
            user = await UserCredits.get_user(user_id)
            balance = user['balance'] if user else 0
            return {
                'success': False,
                'error': 'insufficient_credits',
                'message': f'Insufficient credits. You have {balance} ❄️, need {price} ❄️'
            }
        
        # Deduct credits
        success = await credits_system.spend_credits(
            user_id=user_id,
            amount=price,
            description=f"Purchased {item['name']} {item['emoji']}",
            transaction_type="shop_purchase",
            metadata={
                'item_id': item['item_id'],
                'item_type': item['type'],
                'item_rarity': item['rarity']
            }
        )
        
        if not success:
            return {
                'success': False,
                'error': 'purchase_failed',
                'message': 'Failed to complete purchase'
            }
        
        # Add to inventory
        await UserInventory.add_item(user_id, item_id, item)
        
        # Increment sales
        await ShopItem.increment_sales(item_id)
        
        # Get updated balance
        user = await UserCredits.get_user(user_id)
        
        return {
            'success': True,
            'item': {
                'item_id': item['item_id'],
                'name': item['name'],
                'type': item['type'],
                'emoji': item['emoji'],
                'rarity': item['rarity']
            },
            'price': price,
            'new_balance': user['balance']
        }
    
    # ============================================================
    # INVENTORY SYSTEM
    # ============================================================
    
    async def get_user_inventory(
        self,
        user_id: int,
        item_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get user's inventory.
        
        Args:
            user_id: Discord user ID
            item_type: Filter by type
            
        Returns:
            List of inventory items
        """
        return await UserInventory.get_user_inventory(user_id, item_type)
    
    async def has_item(self, user_id: int, item_id: str) -> bool:
        """
        Check if user owns an item.
        
        Args:
            user_id: Discord user ID
            item_id: Item ID
            
        Returns:
            True if user owns the item
        """
        return await UserInventory.has_item(user_id, item_id)
    
    async def get_equipped_items(self, user_id: int) -> Dict[str, Dict[str, Any]]:
        """
        Get all equipped items by type.
        
        Args:
            user_id: Discord user ID
            
        Returns:
            Dictionary with item types as keys
        """
        return await UserInventory.get_equipped_items(user_id)
    
    # ============================================================
    # EQUIP SYSTEM
    # ============================================================
    
    async def equip_item(self, user_id: int, item_id: str) -> Dict[str, Any]:
        """
        Equip an item from inventory.
        
        Args:
            user_id: Discord user ID
            item_id: Item ID to equip
            
        Returns:
            Dictionary with equip result
        """
        # Check if user owns item
        if not await self.has_item(user_id, item_id):
            return {
                'success': False,
                'error': 'not_owned',
                'message': 'You do not own this item'
            }
        
        # Get item details
        inventory = await self.get_user_inventory(user_id)
        item_data = next((inv for inv in inventory if inv['item_id'] == item_id), None)
        
        if not item_data:
            return {
                'success': False,
                'error': 'not_found',
                'message': 'Item not found in inventory'
            }
        
        # Check if already equipped
        if item_data.get('equipped', False):
            return {
                'success': False,
                'error': 'already_equipped',
                'message': 'Item is already equipped'
            }
        
        # Equip item (auto-unequip others of same type)
        success = await UserInventory.equip_item(
            user_id,
            item_id,
            item_data['item_type']
        )
        
        if success:
            return {
                'success': True,
                'item_id': item_id,
                'item_name': item_data['item_name'],
                'item_type': item_data['item_type']
            }
        
        return {
            'success': False,
            'error': 'equip_failed',
            'message': 'Failed to equip item'
        }
    
    async def unequip_item(self, user_id: int, item_type: str) -> Dict[str, Any]:
        """
        Unequip all items of a specific type.
        
        Args:
            user_id: Discord user ID
            item_type: Type of item to unequip
            
        Returns:
            Dictionary with unequip result
        """
        # Get equipped item of this type
        equipped = await self.get_equipped_items(user_id)
        
        if item_type not in equipped:
            return {
                'success': False,
                'error': 'not_equipped',
                'message': f'No {item_type} is currently equipped'
            }
        
        # Unequip by equipping nothing (handled by database)
        # For now, we'll update directly
        from database.credits_schema import user_inventory_collection
        
        result = await user_inventory_collection.update_many(
            {"user_id": user_id, "item_type": item_type},
            {"$set": {"equipped": False}}
        )
        
        return {
            'success': result.modified_count > 0,
            'item_type': item_type
        }
    
    # ============================================================
    # EMBED HELPERS
    # ============================================================
    
    def create_shop_embed(
        self,
        items: List[Dict[str, Any]],
        category: str = "All Items",
        page: int = 1,
        per_page: int = 10
    ) -> discord.Embed:
        """Create shop items display embed."""
        embed = discord.Embed(
            title=f"🛍️ K77 Credits Shop - {category}",
            description="Purchase items to customize your profile!",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        # Pagination
        start = (page - 1) * per_page
        end = start + per_page
        page_items = items[start:end]
        
        if not page_items:
            embed.description = "No items found in this category."
            return embed
        
        for item in page_items:
            value_lines = [
                f"{item['rarity_emoji']} **{item['rarity'].title()}**",
                f"💰 **{item['price']} ❄️**",
                f"📊 Sales: {item.get('total_sales', 0)}"
            ]
            
            if item.get('owned', False):
                status = "✓ Equipped" if item.get('equipped', False) else "✓ Owned"
                value_lines.append(f"**{status}**")
            
            embed.add_field(
                name=f"{item['emoji']} {item['name']}",
                value="\n".join(value_lines),
                inline=True
            )
        
        total_pages = (len(items) + per_page - 1) // per_page
        embed.set_footer(text=f"Page {page}/{total_pages} • Use /shop buy <item> to purchase")
        
        return embed
    
    def create_item_embed(self, item: Dict[str, Any], owned: bool = False, equipped: bool = False) -> discord.Embed:
        """Create individual item display embed."""
        embed = discord.Embed(
            title=f"{item['emoji']} {item['name']}",
            description=item['description'],
            color=get_rarity_color(item['rarity']),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="Rarity",
            value=f"{get_rarity_emoji(item['rarity'])} **{item['rarity'].title()}**",
            inline=True
        )
        
        embed.add_field(
            name="Price",
            value=f"**{item['price']} ❄️**",
            inline=True
        )
        
        embed.add_field(
            name="Type",
            value=f"**{item['type'].title()}**",
            inline=True
        )
        
        embed.add_field(
            name="Total Sales",
            value=f"**{item.get('total_sales', 0)}**",
            inline=True
        )
        
        if owned:
            status = "✓ Equipped" if equipped else "✓ Owned"
            embed.add_field(
                name="Status",
                value=f"**{status}**",
                inline=True
            )
        
        if item.get('preview_url'):
            embed.set_image(url=item['preview_url'])
        
        return embed
    
    def create_inventory_embed(
        self,
        inventory: List[Dict[str, Any]],
        category: str = "All Items"
    ) -> discord.Embed:
        """Create inventory display embed."""
        embed = discord.Embed(
            title=f"🎒 Your Inventory - {category}",
            description="Your owned items",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        
        if not inventory:
            embed.description = "Your inventory is empty. Visit the shop to purchase items!"
            return embed
        
        # Group by type
        by_type = {}
        for item in inventory:
            item_type = item['item_type']
            if item_type not in by_type:
                by_type[item_type] = []
            by_type[item_type].append(item)
        
        for item_type, items in by_type.items():
            items_text = []
            for item in items:
                status = "✓ Equipped" if item.get('equipped', False) else "Owned"
                items_text.append(f"• {item['item_name']} - *{status}*")
            
            embed.add_field(
                name=f"{item_type.title()}s ({len(items)})",
                value="\n".join(items_text) or "None",
                inline=False
            )
        
        total_items = len(inventory)
        embed.set_footer(text=f"Total Items: {total_items} • Use /shop equip <item> to equip")
        
        return embed


# Export
__all__ = ['ShopSystem']
