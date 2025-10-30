"""
Kingdom-77 Bot v3.8 - Shop Commands

Discord commands for the K77 Credits shop.

Commands:
- /shop browse - Browse shop items by category
- /shop buy - Purchase an item from the shop
- /shop inventory - View your owned items
- /shop equip - Equip an item from your inventory
- /shop view - View details of a specific item

Author: Kingdom-77 Team
Date: 2024
"""

import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, List
from datetime import datetime

# Import systems
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from economy.credits_system import CreditsSystem
from economy.shop_system import ShopSystem


class ShopCog(commands.Cog, name="Shop"):
    """Commands for the K77 Credits shop."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.credits_system = CreditsSystem(bot)
        self.shop_system = ShopSystem(bot)
    
    # ============================================================
    # SHOP GROUP
    # ============================================================
    
    shop_group = app_commands.Group(
        name="shop",
        description="🛍️ Browse and purchase items with K77 Credits"
    )
    
    # ============================================================
    # BROWSE COMMAND
    # ============================================================
    
    @shop_group.command(
        name="browse",
        description="Browse shop items by category"
    )
    @app_commands.describe(
        category="Category to browse"
    )
    @app_commands.choices(category=[
        app_commands.Choice(name="🖼️ All Items", value="all"),
        app_commands.Choice(name="🖼️ Frames", value="frames"),
        app_commands.Choice(name="⭐ Badges", value="badges"),
        app_commands.Choice(name="🌅 Banners", value="banners"),
        app_commands.Choice(name="🎨 Themes", value="themes")
    ])
    async def shop_browse(
        self,
        interaction: discord.Interaction,
        category: Optional[str] = "all"
    ):
        """Browse shop items."""
        await interaction.response.defer()
        
        try:
            # Get items
            item_type = None if category == "all" else category
            items = await self.shop_system.get_shop_items(
                item_type=item_type,
                user_id=interaction.user.id
            )
            
            if not items:
                await interaction.followup.send(
                    f"❌ No items found in category: {category}",
                    ephemeral=True
                )
                return
            
            # Create embed
            category_name = category.title() if category != "all" else "All Items"
            embed = self.shop_system.create_shop_embed(
                items=items,
                category=category_name,
                page=1,
                per_page=10
            )
            
            embed.set_author(
                name="K77 Credits Shop",
                icon_url=self.bot.user.display_avatar.url
            )
            
            await interaction.followup.send(embed=embed)
        
        except Exception as e:
            await interaction.followup.send(
                f"❌ An error occurred: {str(e)}",
                ephemeral=True
            )
    
    # ============================================================
    # VIEW COMMAND
    # ============================================================
    
    @shop_group.command(
        name="view",
        description="View details of a specific shop item"
    )
    @app_commands.describe(
        item_id="Item ID to view (e.g., frame_gold)"
    )
    async def shop_view(
        self,
        interaction: discord.Interaction,
        item_id: str
    ):
        """View item details."""
        await interaction.response.defer()
        
        try:
            # Get item
            item = await self.shop_system.get_item(item_id)
            
            if not item:
                await interaction.followup.send(
                    f"❌ Item not found: {item_id}",
                    ephemeral=True
                )
                return
            
            # Check ownership
            owned = await self.shop_system.has_item(interaction.user.id, item_id)
            equipped = False
            
            if owned:
                equipped_items = await self.shop_system.get_equipped_items(interaction.user.id)
                equipped = item_id in [i['item_id'] for i in equipped_items.values()]
            
            # Create embed
            embed = self.shop_system.create_item_embed(
                item=item,
                owned=owned,
                equipped=equipped
            )
            
            embed.set_author(
                name=interaction.user.name,
                icon_url=interaction.user.display_avatar.url
            )
            
            # Add purchase button if not owned
            if not owned:
                # Get balance
                balance = await self.credits_system.get_balance(
                    interaction.user.id,
                    interaction.user.name
                )
                
                can_afford = balance['balance'] >= item['price']
                embed.add_field(
                    name="💰 Your Balance",
                    value=f"**{balance['balance']} ❄️** {'✅' if can_afford else '❌'}",
                    inline=True
                )
            
            await interaction.followup.send(embed=embed)
        
        except Exception as e:
            await interaction.followup.send(
                f"❌ An error occurred: {str(e)}",
                ephemeral=True
            )
    
    # ============================================================
    # BUY COMMAND
    # ============================================================
    
    @shop_group.command(
        name="buy",
        description="Purchase an item from the shop"
    )
    @app_commands.describe(
        item_id="Item ID to purchase (e.g., frame_gold)"
    )
    async def shop_buy(
        self,
        interaction: discord.Interaction,
        item_id: str
    ):
        """Purchase an item."""
        await interaction.response.defer()
        
        try:
            # Attempt purchase
            result = await self.shop_system.purchase_item(
                user_id=interaction.user.id,
                username=interaction.user.name,
                item_id=item_id,
                credits_system=self.credits_system
            )
            
            if result['success']:
                # Success embed
                item = result['item']
                embed = discord.Embed(
                    title="✅ Purchase Successful!",
                    description=f"You purchased **{item['name']} {item['emoji']}**!",
                    color=discord.Color.green(),
                    timestamp=datetime.utcnow()
                )
                
                embed.add_field(
                    name="💰 Price",
                    value=f"**{result['price']} ❄️**",
                    inline=True
                )
                
                embed.add_field(
                    name="💳 New Balance",
                    value=f"**{result['new_balance']} ❄️**",
                    inline=True
                )
                
                embed.add_field(
                    name="📦 Item Details",
                    value=(
                        f"**Type:** {item['type'].title()}\n"
                        f"**Rarity:** {item['rarity'].title()}"
                    ),
                    inline=False
                )
                
                embed.set_footer(text=f"Use /shop equip {item_id} to equip this item!")
                
                await interaction.followup.send(embed=embed)
            
            else:
                # Error handling
                error_messages = {
                    'item_not_found': f"❌ Item not found: {item_id}",
                    'item_unavailable': "❌ This item is currently unavailable.",
                    'already_owned': "❌ You already own this item!",
                    'insufficient_credits': result.get('message', '❌ Insufficient credits.'),
                    'purchase_failed': "❌ Failed to complete purchase. Please try again."
                }
                
                message = error_messages.get(result['error'], result.get('message', 'Purchase failed.'))
                await interaction.followup.send(message, ephemeral=True)
        
        except Exception as e:
            await interaction.followup.send(
                f"❌ An error occurred: {str(e)}",
                ephemeral=True
            )
    
    # ============================================================
    # INVENTORY COMMAND
    # ============================================================
    
    @shop_group.command(
        name="inventory",
        description="View your owned items"
    )
    @app_commands.describe(
        category="Filter by category"
    )
    @app_commands.choices(category=[
        app_commands.Choice(name="All Items", value="all"),
        app_commands.Choice(name="Frames", value="frames"),
        app_commands.Choice(name="Badges", value="badges"),
        app_commands.Choice(name="Banners", value="banners"),
        app_commands.Choice(name="Themes", value="themes")
    ])
    async def shop_inventory(
        self,
        interaction: discord.Interaction,
        category: Optional[str] = "all"
    ):
        """View your inventory."""
        await interaction.response.defer()
        
        try:
            # Get inventory
            item_type = None if category == "all" else category
            inventory = await self.shop_system.get_user_inventory(
                user_id=interaction.user.id,
                item_type=item_type
            )
            
            # Create embed
            category_name = category.title() if category != "all" else "All Items"
            embed = self.shop_system.create_inventory_embed(
                inventory=inventory,
                category=category_name
            )
            
            embed.set_author(
                name=interaction.user.name,
                icon_url=interaction.user.display_avatar.url
            )
            
            await interaction.followup.send(embed=embed)
        
        except Exception as e:
            await interaction.followup.send(
                f"❌ An error occurred: {str(e)}",
                ephemeral=True
            )
    
    # ============================================================
    # EQUIP COMMAND
    # ============================================================
    
    @shop_group.command(
        name="equip",
        description="Equip an item from your inventory"
    )
    @app_commands.describe(
        item_id="Item ID to equip (e.g., frame_gold)"
    )
    async def shop_equip(
        self,
        interaction: discord.Interaction,
        item_id: str
    ):
        """Equip an item."""
        await interaction.response.defer()
        
        try:
            # Attempt equip
            result = await self.shop_system.equip_item(
                user_id=interaction.user.id,
                item_id=item_id
            )
            
            if result['success']:
                # Success embed
                embed = discord.Embed(
                    title="✅ Item Equipped!",
                    description=f"You equipped **{result['item_name']}**!",
                    color=discord.Color.green(),
                    timestamp=datetime.utcnow()
                )
                
                embed.add_field(
                    name="📦 Item Type",
                    value=result['item_type'].title(),
                    inline=True
                )
                
                embed.add_field(
                    name="ℹ️ Note",
                    value=f"Other {result['item_type']}s have been unequipped.",
                    inline=False
                )
                
                embed.set_footer(text="Your profile will now display this item!")
                
                await interaction.followup.send(embed=embed)
            
            else:
                # Error handling
                error_messages = {
                    'not_owned': "❌ You don't own this item. Use /shop buy to purchase it!",
                    'not_found': f"❌ Item not found in your inventory: {item_id}",
                    'already_equipped': "❌ This item is already equipped!",
                    'equip_failed': "❌ Failed to equip item. Please try again."
                }
                
                message = error_messages.get(result['error'], result.get('message', 'Equip failed.'))
                await interaction.followup.send(message, ephemeral=True)
        
        except Exception as e:
            await interaction.followup.send(
                f"❌ An error occurred: {str(e)}",
                ephemeral=True
            )
    
    # ============================================================
    # UNEQUIP COMMAND
    # ============================================================
    
    @shop_group.command(
        name="unequip",
        description="Unequip items of a specific type"
    )
    @app_commands.describe(
        item_type="Type of item to unequip"
    )
    @app_commands.choices(item_type=[
        app_commands.Choice(name="Frame", value="frame"),
        app_commands.Choice(name="Badge", value="badge"),
        app_commands.Choice(name="Banner", value="banner"),
        app_commands.Choice(name="Theme", value="theme")
    ])
    async def shop_unequip(
        self,
        interaction: discord.Interaction,
        item_type: str
    ):
        """Unequip items of a type."""
        await interaction.response.defer()
        
        try:
            # Attempt unequip
            result = await self.shop_system.unequip_item(
                user_id=interaction.user.id,
                item_type=item_type
            )
            
            if result['success']:
                # Success embed
                embed = discord.Embed(
                    title="✅ Item Unequipped!",
                    description=f"You unequipped your {item_type}.",
                    color=discord.Color.green(),
                    timestamp=datetime.utcnow()
                )
                
                embed.set_footer(text="Use /shop equip to equip another item!")
                
                await interaction.followup.send(embed=embed)
            
            else:
                # Error handling
                error_messages = {
                    'not_equipped': f"❌ No {item_type} is currently equipped."
                }
                
                message = error_messages.get(result['error'], result.get('message', 'Unequip failed.'))
                await interaction.followup.send(message, ephemeral=True)
        
        except Exception as e:
            await interaction.followup.send(
                f"❌ An error occurred: {str(e)}",
                ephemeral=True
            )
    
    # ============================================================
    # EQUIPPED COMMAND
    # ============================================================
    
    @shop_group.command(
        name="equipped",
        description="View your currently equipped items"
    )
    async def shop_equipped(self, interaction: discord.Interaction):
        """View equipped items."""
        await interaction.response.defer()
        
        try:
            # Get equipped items
            equipped = await self.shop_system.get_equipped_items(interaction.user.id)
            
            if not equipped:
                embed = discord.Embed(
                    title="📦 Equipped Items",
                    description="You don't have any items equipped.",
                    color=discord.Color.blue(),
                    timestamp=datetime.utcnow()
                )
                embed.set_footer(text="Use /shop browse to find items!")
                await interaction.followup.send(embed=embed)
                return
            
            # Create embed
            embed = discord.Embed(
                title="📦 Equipped Items",
                description="Your currently equipped items",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )
            
            for item_type, item in equipped.items():
                timestamp = int(item['acquired_at'].timestamp())
                embed.add_field(
                    name=f"{item_type.title()}",
                    value=(
                        f"**{item['item_name']}**\n"
                        f"Acquired: <t:{timestamp}:R>"
                    ),
                    inline=True
                )
            
            embed.set_author(
                name=interaction.user.name,
                icon_url=interaction.user.display_avatar.url
            )
            embed.set_footer(text="These items are displayed on your profile!")
            
            await interaction.followup.send(embed=embed)
        
        except Exception as e:
            await interaction.followup.send(
                f"❌ An error occurred: {str(e)}",
                ephemeral=True
            )


async def setup(bot: commands.Bot):
    """Load the Shop cog."""
    await bot.add_cog(ShopCog(bot))
