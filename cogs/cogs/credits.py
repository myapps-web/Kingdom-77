"""
Kingdom-77 Bot v3.8 - Credits Commands

Discord commands for managing K77 Credits.

Commands:
- /credits balance - View your credit balance
- /credits daily - Claim daily credits
- /credits transfer - Transfer credits to another user
- /credits history - View transaction history

Author: Kingdom-77 Team
Date: 2024
"""

import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
from datetime import datetime

# Import systems
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from economy.credits_system import CreditsSystem


class CreditsCog(commands.Cog, name="Credits"):
    """Commands for managing K77 Credits."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.credits_system = CreditsSystem(bot)
    
    async def cog_unload(self):
        """Clean up when cog is unloaded."""
        self.credits_system.cleanup_expired_cooldowns.cancel()
    
    # ============================================================
    # CREDITS GROUP
    # ============================================================
    
    credits_group = app_commands.Group(
        name="credits",
        description="❄️ Manage your K77 Credits"
    )
    
    # ============================================================
    # BALANCE COMMAND
    # ============================================================
    
    @credits_group.command(
        name="balance",
        description="View your K77 Credits balance"
    )
    async def credits_balance(self, interaction: discord.Interaction):
        """View your credit balance and stats."""
        await interaction.response.defer()
        
        try:
            # Get balance
            balance_data = await self.credits_system.get_balance(
                user_id=interaction.user.id,
                username=interaction.user.name
            )
            
            # Create embed
            embed = self.credits_system.create_balance_embed(balance_data)
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
    # DAILY CLAIM COMMAND
    # ============================================================
    
    @credits_group.command(
        name="daily",
        description="Claim your daily K77 Credits (5-10 ❄️)"
    )
    async def credits_daily(self, interaction: discord.Interaction):
        """Claim daily credits."""
        await interaction.response.defer()
        
        try:
            # Attempt claim
            result = await self.credits_system.claim_daily_credits(
                user_id=interaction.user.id,
                username=interaction.user.name
            )
            
            if result['success']:
                # Success embed
                embed = discord.Embed(
                    title="🎁 Daily Credits Claimed!",
                    description=f"You claimed **{result['amount']} ❄️**!",
                    color=discord.Color.green(),
                    timestamp=datetime.utcnow()
                )
                
                embed.add_field(
                    name="💰 New Balance",
                    value=f"**{result['new_balance']} ❄️**",
                    inline=True
                )
                
                embed.add_field(
                    name="🔥 Streak",
                    value=f"**{result['streak']} days**",
                    inline=True
                )
                
                next_claim_timestamp = int(result['next_claim_time'].timestamp())
                embed.add_field(
                    name="⏳ Next Claim",
                    value=f"<t:{next_claim_timestamp}:R>",
                    inline=False
                )
                
                embed.set_footer(text="Come back tomorrow to continue your streak!")
                
                await interaction.followup.send(embed=embed)
            
            else:
                # On cooldown
                if result['error'] == 'on_cooldown':
                    next_claim = result['next_claim_time']
                    timestamp = int(next_claim.timestamp())
                    
                    embed = discord.Embed(
                        title="⏳ Daily Claim On Cooldown",
                        description=f"You can claim again <t:{timestamp}:R>",
                        color=discord.Color.orange(),
                        timestamp=datetime.utcnow()
                    )
                    
                    embed.add_field(
                        name="Next Available",
                        value=f"<t:{timestamp}:F>",
                        inline=False
                    )
                    
                    embed.set_footer(text="Check back later to claim your daily credits!")
                    
                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send(
                        "❌ Failed to claim daily credits. Please try again later.",
                        ephemeral=True
                    )
        
        except Exception as e:
            await interaction.followup.send(
                f"❌ An error occurred: {str(e)}",
                ephemeral=True
            )
    
    # ============================================================
    # TRANSFER COMMAND
    # ============================================================
    
    @credits_group.command(
        name="transfer",
        description="Transfer credits to another user (minimum 10 ❄️)"
    )
    @app_commands.describe(
        user="The user to transfer credits to",
        amount="Amount of credits to transfer (minimum 10)",
        note="Optional note for the transfer"
    )
    async def credits_transfer(
        self,
        interaction: discord.Interaction,
        user: discord.User,
        amount: int,
        note: Optional[str] = None
    ):
        """Transfer credits to another user."""
        await interaction.response.defer()
        
        try:
            # Perform transfer
            result = await self.credits_system.transfer_credits(
                from_user_id=interaction.user.id,
                to_user_id=user.id,
                to_username=user.name,
                amount=amount,
                note=note
            )
            
            if result['success']:
                # Success embed
                embed = discord.Embed(
                    title="💸 Credits Transferred!",
                    description=f"You transferred **{amount} ❄️** to {user.mention}",
                    color=discord.Color.green(),
                    timestamp=datetime.utcnow()
                )
                
                embed.add_field(
                    name="Your New Balance",
                    value=f"**{result['from_balance']} ❄️**",
                    inline=True
                )
                
                embed.add_field(
                    name=f"{user.name}'s New Balance",
                    value=f"**{result['to_balance']} ❄️**",
                    inline=True
                )
                
                if note:
                    embed.add_field(
                        name="Note",
                        value=note,
                        inline=False
                    )
                
                embed.set_footer(text="Thank you for sharing!")
                
                await interaction.followup.send(embed=embed)
            
            else:
                # Error handling
                error_messages = {
                    'minimum_amount': "❌ Minimum transfer amount is 10 credits.",
                    'same_user': "❌ You cannot transfer credits to yourself.",
                    'insufficient_balance': "❌ You don't have enough credits for this transfer."
                }
                
                message = error_messages.get(result['error'], result.get('message', 'Transfer failed.'))
                await interaction.followup.send(message, ephemeral=True)
        
        except Exception as e:
            await interaction.followup.send(
                f"❌ An error occurred: {str(e)}",
                ephemeral=True
            )
    
    # ============================================================
    # HISTORY COMMAND
    # ============================================================
    
    @credits_group.command(
        name="history",
        description="View your credit transaction history"
    )
    @app_commands.describe(
        limit="Number of transactions to show (default: 10)",
        type="Filter by transaction type"
    )
    @app_commands.choices(type=[
        app_commands.Choice(name="All Transactions", value="all"),
        app_commands.Choice(name="Daily Claims", value="daily_claim"),
        app_commands.Choice(name="Purchases", value="purchase"),
        app_commands.Choice(name="Shop Purchases", value="shop_purchase"),
        app_commands.Choice(name="Transfers Sent", value="transfer_sent"),
        app_commands.Choice(name="Transfers Received", value="transfer_received"),
        app_commands.Choice(name="Premium Purchases", value="premium_purchase")
    ])
    async def credits_history(
        self,
        interaction: discord.Interaction,
        limit: Optional[int] = 10,
        type: Optional[str] = "all"
    ):
        """View transaction history."""
        await interaction.response.defer()
        
        try:
            # Validate limit
            if limit < 1 or limit > 50:
                await interaction.followup.send(
                    "❌ Limit must be between 1 and 50.",
                    ephemeral=True
                )
                return
            
            # Get transaction history
            transaction_type = None if type == "all" else type
            transactions = await self.credits_system.get_transaction_history(
                user_id=interaction.user.id,
                limit=limit,
                transaction_type=transaction_type
            )
            
            if not transactions:
                embed = discord.Embed(
                    title="📊 Transaction History",
                    description="No transactions found.",
                    color=discord.Color.blue(),
                    timestamp=datetime.utcnow()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Create embed
            embed = discord.Embed(
                title="📊 Transaction History",
                description=f"Showing {len(transactions)} recent transactions",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )
            
            for txn in transactions:
                amount = txn['amount']
                emoji = "➕" if amount > 0 else "➖"
                timestamp = int(txn['created_at'].timestamp())
                
                embed.add_field(
                    name=f"{emoji} {txn['description']}",
                    value=(
                        f"**Amount:** {abs(amount)} ❄️\n"
                        f"**Type:** {txn['transaction_type']}\n"
                        f"**Date:** <t:{timestamp}:R>"
                    ),
                    inline=False
                )
            
            embed.set_author(
                name=interaction.user.name,
                icon_url=interaction.user.display_avatar.url
            )
            embed.set_footer(text=f"Use /credits balance to see your current balance")
            
            await interaction.followup.send(embed=embed)
        
        except Exception as e:
            await interaction.followup.send(
                f"❌ An error occurred: {str(e)}",
                ephemeral=True
            )
    
    # ============================================================
    # PACKAGES COMMAND (View available packages)
    # ============================================================
    
    @credits_group.command(
        name="packages",
        description="View available credit packages for purchase"
    )
    async def credits_packages(self, interaction: discord.Interaction):
        """View available credit packages."""
        await interaction.response.defer()
        
        try:
            packages = await self.credits_system.get_credit_packages()
            
            embed = discord.Embed(
                title="💰 K77 Credits Packages",
                description="Purchase credits with bonus amounts!",
                color=discord.Color.gold(),
                timestamp=datetime.utcnow()
            )
            
            for pkg in packages:
                bonus_percent = int((pkg['bonus_credits'] / pkg['base_credits']) * 100)
                
                value_lines = [
                    f"**{pkg['emoji']} {pkg['total_credits']} ❄️**",
                    f"({pkg['base_credits']} + {pkg['bonus_credits']} bonus)",
                    f"💵 ${pkg['price_usd']} USD / {pkg['price_sar']} SAR",
                    f"🎁 **+{bonus_percent}% Bonus**"
                ]
                
                if pkg.get('badge'):
                    value_lines.append(f"⭐ **{pkg['badge']}**")
                
                if pkg.get('popular'):
                    value_lines.append("🔥 **POPULAR**")
                
                embed.add_field(
                    name=pkg['name'],
                    value="\n".join(value_lines),
                    inline=True
                )
            
            embed.add_field(
                name="💡 How to Purchase",
                value=(
                    "Visit the **Dashboard Shop** to purchase credits:\n"
                    f"`https://kingdom77.com/shop`\n\n"
                    "Credits can be used to:\n"
                    "• 🛍️ Buy shop items\n"
                    "• 💎 Activate Premium\n"
                    "• 🎁 Gift to friends"
                ),
                inline=False
            )
            
            embed.set_footer(text="All packages include bonus credits!")
            
            await interaction.followup.send(embed=embed)
        
        except Exception as e:
            await interaction.followup.send(
                f"❌ An error occurred: {str(e)}",
                ephemeral=True
            )


async def setup(bot: commands.Bot):
    """Load the Credits cog."""
    await bot.add_cog(CreditsCog(bot))
