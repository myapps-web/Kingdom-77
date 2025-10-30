"""
Premium System Commands
Slash commands for premium subscription management

Commands:
- /premium - View premium plans and features
- /premium subscribe - Subscribe to premium
- /premium status - Check subscription status
- /premium features - View available features
- /premium trial - Start free trial
- /premium cancel - Cancel subscription
- /premium gift - Gift premium to another server
- /premium billing - View billing history
"""

import discord
from discord import option
from discord.ext import commands, tasks
from typing import Optional
from datetime import datetime

class PremiumCog(commands.Cog):
    """Premium subscription management commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.cleanup_task.start()
    
    def cog_unload(self):
        self.cleanup_task.cancel()
    
    @tasks.loop(hours=24)
    async def cleanup_task(self):
        """Daily cleanup of expired subscriptions"""
        try:
            count = await self.bot.premium_system.cleanup_expired()
            if count > 0:
                print(f"✅ Cleaned up {count} expired subscriptions")
        except Exception as e:
            print(f"❌ Error in premium cleanup: {e}")
    
    @cleanup_task.before_loop
    async def before_cleanup(self):
        await self.bot.wait_until_ready()
    
    # Premium Info Commands
    
    premium = discord.SlashCommandGroup(
        name="premium",
        description="Premium subscription commands"
    )
    
    @premium.command(
        name="info",
        description="View premium plans and features"
    )
    async def premium_info(self, ctx: discord.ApplicationContext):
        """Show premium plans and pricing"""
        from database.premium_schema import PREMIUM_TIERS
        
        embed = discord.Embed(
            title="👑 Kingdom-77 Premium",
            description="Unlock premium features for your server!",
            color=discord.Color.gold()
        )
        
        # Basic (Free) Plan
        basic = PREMIUM_TIERS["basic"]
        basic_features = "\n".join([
            f"✅ {feature.replace('_', ' ').title()}"
            for feature in basic["features"]
        ])
        
        embed.add_field(
            name="🆓 **Basic** - Free",
            value=basic_features + f"\n\n📊 Limits: {basic['limits']['max_custom_commands']} Commands | {basic['limits']['max_autoroles']} Auto-Roles",
            inline=False
        )
        
        # Premium (Paid) Plan
        premium = PREMIUM_TIERS["premium"]
        premium_features = "\n".join([
            f"✨ {feature.replace('_', ' ').title()}"
            for feature in premium["features"][:8]
        ])
        
        if len(premium["features"]) > 8:
            premium_features += f"\n✨ ...and {len(premium['features']) - 8} more!"
        
        embed.add_field(
            name=f"💎 **Premium** - ${premium['price_monthly']}/month or ${premium['price_yearly']}/year",
            value=premium_features + "\n\n♾️ Unlimited Commands & Auto-Roles",
            inline=False
        )
        
        embed.add_field(
            name="📝 How to Subscribe",
            value="Use `/premium subscribe premium` to upgrade!\nOr try `/premium trial` for a 7-day free trial!",
            inline=False
        )
        
        embed.set_footer(text="Kingdom-77 Bot v3.9 | Premium System")
        
        await ctx.respond(embed=embed)
    
    @premium.command(
        name="subscribe",
        description="Subscribe to premium with card or credits"
    )
    @option(
        "billing",
        description="Billing period",
        choices=["monthly", "yearly"],
        required=False,
        default="monthly"
    )
    @option(
        "payment_method",
        description="Payment method",
        choices=["card", "credits"],
        required=False,
        default="card"
    )
    @commands.has_permissions(administrator=True)
    async def premium_subscribe(
        self,
        ctx: discord.ApplicationContext,
        billing: str = "monthly",
        payment_method: str = "card"
    ):
        """Subscribe to premium"""
        guild_id = str(ctx.guild.id)
        user_id = str(ctx.author.id)
        tier = "premium"  # Only premium tier available for subscription
        
        # Check if already subscribed
        existing = await self.bot.premium_system.get_subscription(guild_id=guild_id)
        if existing and existing['tier'] == 'premium':
            await ctx.respond(
                "❌ This server already has an active Premium subscription!\n"
                f"Expires: <t:{int(existing['expires_at'].timestamp())}:R>",
                ephemeral=True
            )
            return
        
        # Handle Credits Payment
        if payment_method == "credits":
            await ctx.defer(ephemeral=True)
            
            try:
                # Get credits pricing
                pricing = await self.bot.premium_system.get_credits_pricing()
                credits_cost = pricing[billing]
                
                # Get user balance
                balance = await self.bot.premium_system.credits_system.get_balance(user_id)
                
                # Check if sufficient balance
                if balance < credits_cost:
                    embed = discord.Embed(
                        title="❌ Insufficient Credits",
                        description=f"You need **{credits_cost} ❄️** to purchase Premium ({billing}), but you only have **{balance} ❄️**.",
                        color=discord.Color.red()
                    )
                    embed.add_field(
                        name="💎 Purchase Credits",
                        value="Use `/credits packages` to buy more credits!",
                        inline=False
                    )
                    await ctx.followup.send(embed=embed, ephemeral=True)
                    return
                
                # Show confirmation view
                embed = discord.Embed(
                    title="🎫 Confirm Premium Purchase",
                    description=f"Are you sure you want to purchase **Premium ({billing})** for this server?",
                    color=discord.Color.blue()
                )
                embed.add_field(
                    name="💰 Cost",
                    value=f"{credits_cost} ❄️ credits",
                    inline=True
                )
                embed.add_field(
                    name="💎 Your Balance",
                    value=f"{balance} ❄️",
                    inline=True
                )
                embed.add_field(
                    name="⏱️ Duration",
                    value=f"{30 if billing == 'monthly' else 365} days",
                    inline=True
                )
                embed.add_field(
                    name="💵 Remaining After",
                    value=f"{balance - credits_cost} ❄️",
                    inline=False
                )
                
                view = ConfirmPurchaseView(self.bot, user_id, guild_id, tier, billing, credits_cost)
                await ctx.followup.send(embed=embed, view=view, ephemeral=True)
                return
            
            except Exception as e:
                await ctx.followup.send(
                    f"❌ An error occurred: {str(e)}",
                    ephemeral=True
                )
                return
        
        # Handle Card Payment (Stripe/Moyasar)
        success_url = f"{self.bot.config.get('FRONTEND_URL', 'http://localhost:3000')}/premium/success"
        cancel_url = f"{self.bot.config.get('FRONTEND_URL', 'http://localhost:3000')}/premium/cancel"
        
        checkout_url = await self.bot.premium_system.create_checkout_session(
            user_id=user_id,
            guild_id=guild_id,
            tier=tier,
            billing_period=billing,
            success_url=success_url,
            cancel_url=cancel_url
        )
        
        if not checkout_url:
            # Payment provider not configured - create subscription directly (for testing)
            from database.premium_schema import PREMIUM_TIERS
            tier_info = PREMIUM_TIERS[tier]
            
            duration = 30 if billing == "monthly" else 365
            subscription = await self.bot.premium_system.create_subscription(
                user_id=user_id,
                guild_id=guild_id,
                tier=tier,
                duration_days=duration
            )
            
            embed = discord.Embed(
                title="✅ Premium Activated!",
                description=f"**{tier_info['name']}** tier has been activated for this server!",
                color=discord.Color.green()
            )
            embed.add_field(
                name="Duration",
                value=f"{duration} days",
                inline=True
            )
            embed.add_field(
                name="Expires",
                value=f"<t:{int(subscription['expires_at'].timestamp())}:R>",
                inline=True
            )
            
            await ctx.respond(embed=embed)
        else:
            # Send checkout link
            from database.premium_schema import PREMIUM_TIERS
            tier_info = PREMIUM_TIERS[tier]
            price = tier_info[f'price_{billing}']
            
            embed = discord.Embed(
                title="💳 Complete Your Purchase",
                description=f"Click the button below to complete your **Premium** subscription!\n\n💰 **${price}** / {billing}",
                color=discord.Color.blue()
            )
            
            view = discord.ui.View()
            view.add_item(
                discord.ui.Button(
                    label="Complete Purchase",
                    url=checkout_url,
                    style=discord.ButtonStyle.link
                )
            )
            
            await ctx.respond(embed=embed, view=view, ephemeral=True)
    
    @premium.command(
        name="status",
        description="Check your premium subscription status"
    )
    async def premium_status(self, ctx: discord.ApplicationContext):
        """Check premium subscription status"""
        guild_id = str(ctx.guild.id)
        
        subscription = await self.bot.premium_system.get_subscription(guild_id=guild_id)
        
        if not subscription:
            embed = discord.Embed(
                title="📊 Premium Status",
                description="This server does not have an active premium subscription.",
                color=discord.Color.red()
            )
            embed.add_field(
                name="Get Premium",
                value="Use `/premium info` to view plans and `/premium trial` for a free trial!",
                inline=False
            )
        else:
            from database.premium_schema import PREMIUM_TIERS
            tier_info = PREMIUM_TIERS.get(subscription["tier"], {})
            
            embed = discord.Embed(
                title="👑 Premium Status",
                description=f"**{tier_info.get('name', subscription['tier'].title())}** Subscription",
                color=discord.Color.gold()
            )
            
            embed.add_field(
                name="Status",
                value=f"✅ {subscription['status'].title()}",
                inline=True
            )
            embed.add_field(
                name="Expires",
                value=f"<t:{int(subscription['expires_at'].timestamp())}:R>",
                inline=True
            )
            embed.add_field(
                name="Auto Renew",
                value="✅ Enabled" if subscription.get("auto_renew") else "❌ Disabled",
                inline=True
            )
            
            # Show features
            features = subscription.get("features", [])
            if features:
                features_text = "\n".join([
                    f"• {f.replace('_', ' ').title()}"
                    for f in features[:10]
                ])
                if len(features) > 10:
                    features_text += f"\n• ...and {len(features) - 10} more!"
                
                embed.add_field(
                    name=f"Features ({len(features)})",
                    value=features_text,
                    inline=False
                )
        
        embed.set_footer(text=f"Server ID: {guild_id}")
        await ctx.respond(embed=embed)
    
    @premium.command(
        name="features",
        description="View all available premium features"
    )
    async def premium_features(self, ctx: discord.ApplicationContext):
        """View all premium features"""
        features = await self.bot.premium_system.get_all_features()
        
        embed = discord.Embed(
            title="✨ Premium Features",
            description="All available premium features:",
            color=discord.Color.blue()
        )
        
        # Group by category
        categories = {}
        for feature in features:
            category = feature.get("category", "general")
            if category not in categories:
                categories[category] = []
            categories[category].append(feature)
        
        for category, cat_features in categories.items():
            features_text = "\n".join([
                f"**{f['name']}** ({f['tier']})\n{f['description']}"
                for f in cat_features[:3]
            ])
            
            embed.add_field(
                name=f"📂 {category.title()}",
                value=features_text,
                inline=False
            )
        
        embed.set_footer(text="Use /premium info to see tier pricing")
        await ctx.respond(embed=embed)
    
    @premium.command(
        name="trial",
        description="Start a 7-day free premium trial"
    )
    @commands.has_permissions(administrator=True)
    async def premium_trial(self, ctx: discord.ApplicationContext):
        """Start free trial"""
        guild_id = str(ctx.guild.id)
        user_id = str(ctx.author.id)
        
        # Check if already subscribed
        existing = await self.bot.premium_system.get_subscription(guild_id=guild_id)
        if existing:
            await ctx.respond(
                "❌ This server already has an active subscription!",
                ephemeral=True
            )
            return
        
        try:
            subscription = await self.bot.premium_system.start_trial(
                user_id=user_id,
                guild_id=guild_id,
                tier="premium",
                trial_days=7
            )
            
            embed = discord.Embed(
                title="🎉 Trial Started!",
                description="Your 7-day **Premium** trial has started!",
                color=discord.Color.green()
            )
            embed.add_field(
                name="Expires",
                value=f"<t:{int(subscription['expires_at'].timestamp())}:R>",
                inline=True
            )
            embed.add_field(
                name="What's Next?",
                value="Explore all premium features! Use `/premium subscribe` before the trial ends to keep them.",
                inline=False
            )
            
            await ctx.respond(embed=embed)
            
        except Exception as e:
            await ctx.respond(f"❌ Error: {str(e)}", ephemeral=True)
    
    @premium.command(
        name="cancel",
        description="Cancel your premium subscription"
    )
    @commands.has_permissions(administrator=True)
    async def premium_cancel(self, ctx: discord.ApplicationContext):
        """Cancel premium subscription"""
        guild_id = str(ctx.guild.id)
        
        subscription = await self.bot.premium_system.get_subscription(guild_id=guild_id)
        
        if not subscription:
            await ctx.respond(
                "❌ This server doesn't have an active subscription!",
                ephemeral=True
            )
            return
        
        # Confirmation
        view = ConfirmView(ctx.author.id)
        
        embed = discord.Embed(
            title="⚠️ Cancel Subscription",
            description=(
                "Are you sure you want to cancel your premium subscription?\n\n"
                f"Your subscription will remain active until <t:{int(subscription['expires_at'].timestamp())}:R>"
            ),
            color=discord.Color.orange()
        )
        
        await ctx.respond(embed=embed, view=view, ephemeral=True)
        await view.wait()
        
        if view.value:
            success = await self.bot.premium_system.cancel_subscription(
                str(subscription["_id"])
            )
            
            if success:
                await ctx.edit(
                    content="✅ Subscription cancelled. It will remain active until expiration.",
                    embed=None,
                    view=None
                )
            else:
                await ctx.edit(
                    content="❌ Failed to cancel subscription. Please try again.",
                    embed=None,
                    view=None
                )
        else:
            await ctx.edit(
                content="❌ Cancellation aborted.",
                embed=None,
                view=None
            )
    
    @premium.command(
        name="gift",
        description="Gift premium to another server"
    )
    @option("server_id", description="Server ID to gift to")
    @option("duration", description="Duration in days", min_value=7, max_value=365, default=30)
    @commands.has_permissions(administrator=True)
    async def premium_gift(
        self,
        ctx: discord.ApplicationContext,
        server_id: str,
        duration: int = 30
    ):
        """Gift premium to another server"""
        user_id = str(ctx.author.id)
        tier = "premium"  # Only premium can be gifted
        
        # Verify server exists and bot is in it
        try:
            guild = await self.bot.fetch_guild(int(server_id))
        except:
            await ctx.respond("❌ Invalid server ID or bot is not in that server!", ephemeral=True)
            return
        
        # Check if target server already has premium
        existing = await self.bot.premium_system.get_subscription(guild_id=server_id)
        if existing and existing['tier'] == 'premium':
            await ctx.respond("❌ That server already has an active Premium subscription!", ephemeral=True)
            return
        
        # Create gift subscription
        subscription = await self.bot.premium_system.gift_subscription(
            gifter_user_id=user_id,
            recipient_guild_id=server_id,
            tier=tier,
            duration_days=duration
        )
        
        embed = discord.Embed(
            title="🎁 Premium Gifted!",
            description=f"You've gifted **Premium** to **{guild.name}**!",
            color=discord.Color.green()
        )
        embed.add_field(
            name="Duration",
            value=f"{duration} days",
            inline=True
        )
        embed.add_field(
            name="Expires",
            value=f"<t:{int(subscription['expires_at'].timestamp())}:R>",
            inline=True
        )
        
        await ctx.respond(embed=embed)
        
        # Notify recipient server (if possible)
        try:
            system_channel = guild.system_channel
            if system_channel:
                notify_embed = discord.Embed(
                    title="🎁 Premium Gift Received!",
                    description=f"Your server has received a **Premium** gift!",
                    color=discord.Color.gold()
                )
                notify_embed.add_field(
                    name="Duration",
                    value=f"{duration} days",
                    inline=True
                )
                await system_channel.send(embed=notify_embed)
        except:
            pass
    
    @premium.command(
        name="billing",
        description="View billing history"
    )
    @commands.has_permissions(administrator=True)
    async def premium_billing(self, ctx: discord.ApplicationContext):
        """View billing history"""
        guild_id = str(ctx.guild.id)
        
        payments = await self.bot.premium_system.schema.get_payment_history(
            guild_id=guild_id,
            limit=10
        )
        
        if not payments:
            await ctx.respond("📄 No billing history found.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="💳 Billing History",
            description="Recent payments:",
            color=discord.Color.blue()
        )
        
        for payment in payments[:5]:
            created = payment.get("created_at", datetime.utcnow())
            embed.add_field(
                name=f"{payment['tier'].title()} - ${payment['amount']:.2f}",
                value=(
                    f"Status: {payment['status'].title()}\n"
                    f"Date: <t:{int(created.timestamp())}:D>"
                ),
                inline=False
            )
        
        if len(payments) > 5:
            embed.set_footer(text=f"Showing 5 of {len(payments)} payments")
        
        await ctx.respond(embed=embed, ephemeral=True)


class ConfirmView(discord.ui.View):
    """Confirmation view"""
    
    def __init__(self, author_id: int):
        super().__init__(timeout=30)
        self.author_id = author_id
        self.value = None
    
    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.danger)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("❌ Only the command author can confirm!", ephemeral=True)
            return
        self.value = True
        self.stop()
    
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("❌ Only the command author can cancel!", ephemeral=True)
            return
        self.value = False
        self.stop()


class ConfirmPurchaseView(discord.ui.View):
    """Confirmation view for credits purchase"""
    
    def __init__(self, bot, user_id: str, guild_id: str, tier: str, billing: str, credits_cost: int):
        super().__init__(timeout=60)
        self.bot = bot
        self.user_id = user_id
        self.guild_id = guild_id
        self.tier = tier
        self.billing = billing
        self.credits_cost = credits_cost
    
    @discord.ui.button(label="✅ Confirm Purchase", style=discord.ButtonStyle.success)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("❌ Only the command author can confirm!", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        try:
            # Purchase with credits
            result = await self.bot.premium_system.purchase_with_credits(
                user_id=self.user_id,
                guild_id=self.guild_id,
                tier=self.tier,
                billing_period=self.billing,
                user_email=None,  # Could be fetched from DB
                user_name=interaction.user.name,
                guild_name=interaction.guild.name
            )
            
            # Success
            subscription = result['subscription']
            embed = discord.Embed(
                title="✅ Premium Activated!",
                description=f"Successfully purchased **Premium ({self.billing})** with credits!",
                color=discord.Color.green()
            )
            embed.add_field(
                name="💰 Credits Spent",
                value=f"{result['credits_spent']} ❄️",
                inline=True
            )
            embed.add_field(
                name="💎 Remaining Balance",
                value=f"{result['new_balance']} ❄️",
                inline=True
            )
            embed.add_field(
                name="⏱️ Duration",
                value=f"{result['duration_days']} days",
                inline=True
            )
            embed.add_field(
                name="📅 Expires",
                value=f"<t:{int(subscription['expires_at'].timestamp())}:R>",
                inline=False
            )
            embed.set_footer(text="Thank you for supporting Kingdom-77! 👑")
            
            await interaction.followup.edit_message(
                message_id=interaction.message.id,
                embed=embed,
                view=None
            )
        
        except Exception as e:
            # Error
            embed = discord.Embed(
                title="❌ Purchase Failed",
                description=f"An error occurred: {str(e)}",
                color=discord.Color.red()
            )
            
            await interaction.followup.edit_message(
                message_id=interaction.message.id,
                embed=embed,
                view=None
            )
    
    @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("❌ Only the command author can cancel!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="❌ Purchase Cancelled",
            description="Premium purchase has been cancelled.",
            color=discord.Color.orange()
        )
        
        await interaction.response.edit_message(embed=embed, view=None)


def setup(bot):
    bot.add_cog(PremiumCog(bot))
