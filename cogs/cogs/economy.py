"""
Economy Commands Cog
===================
Discord slash commands for economy system.
"""

import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, Literal
import logging

logger = logging.getLogger(__name__)


class ShopItemSelect(discord.ui.Select):
    """Shop item selection dropdown"""
    
    def __init__(self, items, economy_system, db):
        self.economy_system = economy_system
        self.db = db
        
        options = []
        for item in items[:25]:  # Discord limit
            emoji = item.get("emoji", "📦")
            label = item["name"][:100]
            description = f"{item['price']} 🪙 | {item['description'][:100]}"
            
            options.append(discord.SelectOption(
                label=label,
                description=description,
                value=item["item_id"],
                emoji=emoji
            ))
        
        super().__init__(
            placeholder="اختر عنصراً للشراء...",
            min_values=1,
            max_values=1,
            options=options
        )
    
    async def callback(self, interaction: discord.Interaction):
        item_id = self.values[0]
        
        # Buy item
        success, message = await self.economy_system.buy_item(
            interaction.guild.id,
            interaction.user.id,
            item_id,
            interaction.user
        )
        
        if success:
            await interaction.response.send_message(f"✅ {message}", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ {message}", ephemeral=True)


class ShopView(discord.ui.View):
    """Shop view with item selection"""
    
    def __init__(self, items, economy_system, db):
        super().__init__(timeout=180)
        self.add_item(ShopItemSelect(items, economy_system, db))


class EconomyCog(commands.Cog):
    """Economy system commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.economy_db
        self.economy = bot.economy_system
    
    economy_group = app_commands.Group(
        name="economy",
        description="أوامر النظام الاقتصادي"
    )
    
    # ==================== BALANCE ====================
    
    @app_commands.command(name="balance", description="عرض رصيدك")
    @app_commands.describe(member="العضو المراد عرض رصيده (اختياري)")
    async def balance(
        self,
        interaction: discord.Interaction,
        member: Optional[discord.Member] = None
    ):
        """Show balance"""
        target = member or interaction.user
        
        balance = await self.economy.get_balance(interaction.guild.id, target.id)
        
        embed = discord.Embed(
            title=f"💰 رصيد {target.display_name}",
            color=discord.Color.gold(),
            timestamp=discord.utils.utcnow()
        )
        
        embed.add_field(
            name="💵 النقد",
            value=f"**{balance['cash']:,}** 🪙",
            inline=True
        )
        
        embed.add_field(
            name="🏦 البنك",
            value=f"**{balance['bank']:,}** / {balance['bank_space']:,} 🪙",
            inline=True
        )
        
        embed.add_field(
            name="💎 الإجمالي",
            value=f"**{balance['total']:,}** 🪙",
            inline=True
        )
        
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.set_footer(text=f"مطلوب بواسطة {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)
    
    # ==================== DEPOSIT / WITHDRAW ====================
    
    @app_commands.command(name="deposit", description="إيداع المال في البنك")
    @app_commands.describe(amount="المبلغ المراد إيداعه (all للكل)")
    async def deposit(self, interaction: discord.Interaction, amount: str):
        """Deposit money to bank"""
        balance = await self.economy.get_balance(interaction.guild.id, interaction.user.id)
        
        if amount.lower() == "all":
            amount = balance["cash"]
        else:
            try:
                amount = int(amount)
            except ValueError:
                await interaction.response.send_message("❌ المبلغ يجب أن يكون رقماً!", ephemeral=True)
                return
        
        if amount <= 0:
            await interaction.response.send_message("❌ المبلغ يجب أن يكون أكبر من 0!", ephemeral=True)
            return
        
        if balance["cash"] < amount:
            await interaction.response.send_message(
                f"❌ ليس لديك ما يكفي من المال! لديك: {balance['cash']:,} 🪙",
                ephemeral=True
            )
            return
        
        if balance["bank"] + amount > balance["bank_space"]:
            await interaction.response.send_message(
                f"❌ البنك ممتلئ! المساحة المتبقية: {balance['bank_space'] - balance['bank']:,} 🪙",
                ephemeral=True
            )
            return
        
        success = await self.db.deposit(interaction.guild.id, interaction.user.id, amount)
        
        if success:
            await interaction.response.send_message(
                f"✅ تم إيداع **{amount:,}** 🪙 في البنك!",
                ephemeral=True
            )
        else:
            await interaction.response.send_message("❌ فشلت عملية الإيداع!", ephemeral=True)
    
    @app_commands.command(name="withdraw", description="سحب المال من البنك")
    @app_commands.describe(amount="المبلغ المراد سحبه (all للكل)")
    async def withdraw(self, interaction: discord.Interaction, amount: str):
        """Withdraw money from bank"""
        balance = await self.economy.get_balance(interaction.guild.id, interaction.user.id)
        
        if amount.lower() == "all":
            amount = balance["bank"]
        else:
            try:
                amount = int(amount)
            except ValueError:
                await interaction.response.send_message("❌ المبلغ يجب أن يكون رقماً!", ephemeral=True)
                return
        
        if amount <= 0:
            await interaction.response.send_message("❌ المبلغ يجب أن يكون أكبر من 0!", ephemeral=True)
            return
        
        if balance["bank"] < amount:
            await interaction.response.send_message(
                f"❌ ليس لديك ما يكفي في البنك! لديك: {balance['bank']:,} 🪙",
                ephemeral=True
            )
            return
        
        success = await self.db.withdraw(interaction.guild.id, interaction.user.id, amount)
        
        if success:
            await interaction.response.send_message(
                f"✅ تم سحب **{amount:,}** 🪙 من البنك!",
                ephemeral=True
            )
        else:
            await interaction.response.send_message("❌ فشلت عملية السحب!", ephemeral=True)
    
    # ==================== REWARDS ====================
    
    @app_commands.command(name="daily", description="استلام المكافأة اليومية")
    async def daily(self, interaction: discord.Interaction):
        """Claim daily reward"""
        success, message, amount = await self.economy.claim_daily(
            interaction.guild.id,
            interaction.user.id
        )
        
        if success:
            embed = discord.Embed(
                title="📅 مكافأة يومية",
                description=f"✅ {message}\n\nحصلت على **{amount:,}** 🪙",
                color=discord.Color.green(),
                timestamp=discord.utils.utcnow()
            )
        else:
            cooldown = await self.economy.get_daily_cooldown(interaction.guild.id, interaction.user.id)
            if cooldown:
                hours = int(cooldown.total_seconds() / 3600)
                minutes = int((cooldown.total_seconds() % 3600) / 60)
                embed = discord.Embed(
                    title="📅 مكافأة يومية",
                    description=f"❌ {message}\n\nالوقت المتبقي: **{hours}h {minutes}m**",
                    color=discord.Color.red()
                )
            else:
                embed = discord.Embed(
                    title="📅 مكافأة يومية",
                    description=f"❌ {message}",
                    color=discord.Color.red()
                )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="weekly", description="استلام المكافأة الأسبوعية")
    async def weekly(self, interaction: discord.Interaction):
        """Claim weekly reward"""
        success, message, amount = await self.economy.claim_weekly(
            interaction.guild.id,
            interaction.user.id
        )
        
        if success:
            embed = discord.Embed(
                title="📆 مكافأة أسبوعية",
                description=f"✅ {message}\n\nحصلت على **{amount:,}** 🪙",
                color=discord.Color.green(),
                timestamp=discord.utils.utcnow()
            )
        else:
            cooldown = await self.economy.get_weekly_cooldown(interaction.guild.id, interaction.user.id)
            if cooldown:
                days = cooldown.days
                hours = int(cooldown.seconds / 3600)
                embed = discord.Embed(
                    title="📆 مكافأة أسبوعية",
                    description=f"❌ {message}\n\nالوقت المتبقي: **{days}d {hours}h**",
                    color=discord.Color.red()
                )
            else:
                embed = discord.Embed(
                    title="📆 مكافأة أسبوعية",
                    description=f"❌ {message}",
                    color=discord.Color.red()
                )
        
        await interaction.response.send_message(embed=embed)
    
    # ==================== WORK & CRIME ====================
    
    @app_commands.command(name="work", description="اعمل لكسب المال")
    async def work(self, interaction: discord.Interaction):
        """Work to earn money"""
        success, message, amount, emoji = await self.economy.work(
            interaction.guild.id,
            interaction.user.id
        )
        
        if success:
            embed = discord.Embed(
                title=f"{emoji} عمل",
                description=message,
                color=discord.Color.green(),
                timestamp=discord.utils.utcnow()
            )
        else:
            embed = discord.Embed(
                title=f"{emoji} عمل",
                description=f"❌ {message}",
                color=discord.Color.red()
            )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="crime", description="ارتكب جريمة (مخاطرة)")
    async def crime(self, interaction: discord.Interaction):
        """Commit a crime"""
        success, message, amount, emoji = await self.economy.crime(
            interaction.guild.id,
            interaction.user.id
        )
        
        if success:
            color = discord.Color.green()
        else:
            if amount == 0:
                color = discord.Color.red()
            else:
                color = discord.Color.orange()
        
        embed = discord.Embed(
            title=f"{emoji} جريمة",
            description=message,
            color=color,
            timestamp=discord.utils.utcnow()
        )
        
        await interaction.response.send_message(embed=embed)
    
    # ==================== GAMBLING ====================
    
    @app_commands.command(name="slots", description="لعبة سلوتس (ماكينة القمار)")
    @app_commands.describe(bet="المبلغ المراد المراهنة به")
    async def slots(self, interaction: discord.Interaction, bet: int):
        """Play slots"""
        if bet <= 0:
            await interaction.response.send_message("❌ المراهنة يجب أن تكون أكبر من 0!", ephemeral=True)
            return
        
        won, symbols, payout, message = await self.economy.slots(
            interaction.guild.id,
            interaction.user.id,
            bet
        )
        
        embed = discord.Embed(
            title="🎰 سلوتس",
            description=f"**[ {' | '.join(symbols)} ]**\n\n{message}",
            color=discord.Color.green() if won else discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )
        
        if won:
            embed.add_field(name="💰 الربح", value=f"**{payout:,}** 🪙")
        else:
            embed.add_field(name="💸 الخسارة", value=f"**{bet:,}** 🪙")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="coinflip", description="رمي العملة")
    @app_commands.describe(
        bet="المبلغ المراد المراهنة به",
        choice="اختر صورة أو كتابة"
    )
    async def coinflip(
        self,
        interaction: discord.Interaction,
        bet: int,
        choice: Literal["heads", "tails"]
    ):
        """Coinflip game"""
        if bet <= 0:
            await interaction.response.send_message("❌ المراهنة يجب أن تكون أكبر من 0!", ephemeral=True)
            return
        
        won, result, payout, message = await self.economy.coinflip(
            interaction.guild.id,
            interaction.user.id,
            bet,
            choice
        )
        
        choice_ar = "صورة" if choice == "heads" else "كتابة"
        result_ar = "صورة" if result == "heads" else "كتابة"
        
        embed = discord.Embed(
            title="🪙 رمي العملة",
            description=f"اخترت: **{choice_ar}**\nالنتيجة: **{result_ar}**\n\n{message}",
            color=discord.Color.green() if won else discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )
        
        if won:
            embed.add_field(name="💰 الربح", value=f"**{payout:,}** 🪙")
        else:
            embed.add_field(name="💸 الخسارة", value=f"**{bet:,}** 🪙")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="dice", description="لعبة النرد")
    @app_commands.describe(bet="المبلغ المراد المراهنة به")
    async def dice(self, interaction: discord.Interaction, bet: int):
        """Dice game"""
        if bet <= 0:
            await interaction.response.send_message("❌ المراهنة يجب أن تكون أكبر من 0!", ephemeral=True)
            return
        
        won, user_roll, bot_roll, payout, message = await self.economy.dice(
            interaction.guild.id,
            interaction.user.id,
            bet
        )
        
        embed = discord.Embed(
            title="🎲 نرد",
            description=message,
            color=discord.Color.green() if won else (discord.Color.orange() if user_roll == bot_roll else discord.Color.red()),
            timestamp=discord.utils.utcnow()
        )
        
        if won:
            embed.add_field(name="💰 الربح", value=f"**{payout:,}** 🪙")
        elif user_roll != bot_roll:
            embed.add_field(name="💸 الخسارة", value=f"**{bet:,}** 🪙")
        
        await interaction.response.send_message(embed=embed)
    
    # ==================== SHOP ====================
    
    @app_commands.command(name="shop", description="عرض المتجر")
    @app_commands.describe(category="فئة العناصر")
    async def shop(
        self,
        interaction: discord.Interaction,
        category: Optional[Literal["role", "item", "boost", "other"]] = None
    ):
        """Show shop"""
        items = await self.db.get_shop_items(interaction.guild.id, category)
        
        if not items:
            await interaction.response.send_message(
                "❌ لا توجد عناصر في المتجر!",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="🛒 المتجر" + (f" - {category}" if category else ""),
            description="استخدم القائمة أدناه للشراء",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        
        for item in items[:10]:  # Show first 10
            emoji = item.get("emoji", "📦")
            stock_text = f"المخزون: {item['stock']}" if item["stock"] > 0 else "غير محدود"
            
            embed.add_field(
                name=f"{emoji} {item['name']}",
                value=f"{item['description']}\n**السعر:** {item['price']:,} 🪙 | {stock_text}",
                inline=False
            )
        
        view = ShopView(items, self.economy, self.db)
        await interaction.response.send_message(embed=embed, view=view)
    
    @app_commands.command(name="buy", description="شراء عنصر من المتجر")
    @app_commands.describe(item_id="معرف العنصر")
    async def buy(self, interaction: discord.Interaction, item_id: str):
        """Buy item"""
        success, message = await self.economy.buy_item(
            interaction.guild.id,
            interaction.user.id,
            item_id,
            interaction.user
        )
        
        if success:
            await interaction.response.send_message(f"✅ {message}")
        else:
            await interaction.response.send_message(f"❌ {message}", ephemeral=True)
    
    # ==================== INVENTORY ====================
    
    @app_commands.command(name="inventory", description="عرض مخزنك")
    @app_commands.describe(member="العضو المراد عرض مخزنه")
    async def inventory(
        self,
        interaction: discord.Interaction,
        member: Optional[discord.Member] = None
    ):
        """Show inventory"""
        target = member or interaction.user
        
        inventory = await self.db.get_inventory(interaction.guild.id, target.id)
        
        if not inventory:
            await interaction.response.send_message(
                f"❌ {'مخزنك' if target == interaction.user else f'مخزن {target.display_name}'} فارغ!",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title=f"🎒 مخزن {target.display_name}",
            color=discord.Color.purple(),
            timestamp=discord.utils.utcnow()
        )
        
        for inv_item in inventory[:25]:  # Discord limit
            item = await self.db.get_item(interaction.guild.id, inv_item["item_id"])
            if item:
                emoji = item.get("emoji", "📦")
                embed.add_field(
                    name=f"{emoji} {item['name']}",
                    value=f"الكمية: **{inv_item['quantity']}**",
                    inline=True
                )
        
        embed.set_thumbnail(url=target.display_avatar.url)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="sell", description="بيع عنصر من مخزنك")
    @app_commands.describe(
        item_id="معرف العنصر",
        quantity="الكمية (افتراضي: 1)"
    )
    async def sell(
        self,
        interaction: discord.Interaction,
        item_id: str,
        quantity: int = 1
    ):
        """Sell item"""
        if quantity <= 0:
            await interaction.response.send_message("❌ الكمية يجب أن تكون أكبر من 0!", ephemeral=True)
            return
        
        success, message, amount = await self.economy.sell_item(
            interaction.guild.id,
            interaction.user.id,
            item_id,
            quantity
        )
        
        if success:
            await interaction.response.send_message(f"✅ {message}")
        else:
            await interaction.response.send_message(f"❌ {message}", ephemeral=True)
    
    # ==================== TRANSFER ====================
    
    @app_commands.command(name="give", description="إهداء مال لعضو")
    @app_commands.describe(
        member="العضو المراد الإهداء له",
        amount="المبلغ"
    )
    async def give(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        amount: int
    ):
        """Give money to member"""
        if member == interaction.user:
            await interaction.response.send_message("❌ لا يمكنك إهداء نفسك!", ephemeral=True)
            return
        
        if member.bot:
            await interaction.response.send_message("❌ لا يمكنك إهداء البوتات!", ephemeral=True)
            return
        
        if amount <= 0:
            await interaction.response.send_message("❌ المبلغ يجب أن يكون أكبر من 0!", ephemeral=True)
            return
        
        success = await self.db.transfer_money(
            interaction.guild.id,
            interaction.user.id,
            member.id,
            amount
        )
        
        if success:
            await interaction.response.send_message(
                f"✅ تم إهداء **{amount:,}** 🪙 لـ {member.mention}!"
            )
        else:
            await interaction.response.send_message(
                "❌ فشلت العملية! تأكد من أن لديك ما يكفي من المال.",
                ephemeral=True
            )
    
    # ==================== LEADERBOARD ====================
    
    @app_commands.command(name="leaderboard", description="لوحة المتصدرين")
    @app_commands.describe(page="الصفحة (افتراضي: 1)")
    async def leaderboard(self, interaction: discord.Interaction, page: int = 1):
        """Economy leaderboard"""
        if page < 1:
            page = 1
        
        leaderboard = await self.economy.get_leaderboard(interaction.guild.id, limit=10)
        
        if not leaderboard:
            await interaction.response.send_message("❌ لا توجد بيانات!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🏆 لوحة المتصدرين - الاقتصاد",
            description="أغنى الأعضاء في السيرفر",
            color=discord.Color.gold(),
            timestamp=discord.utils.utcnow()
        )
        
        for idx, entry in enumerate(leaderboard, 1):
            user = interaction.guild.get_member(entry["user_id"])
            if user:
                medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"**{idx}.**"
                embed.add_field(
                    name=f"{medal} {user.display_name}",
                    value=f"💰 {entry['total']:,} 🪙",
                    inline=False
                )
        
        await interaction.response.send_message(embed=embed)
    
    # ==================== ADMIN COMMANDS ====================
    
    @economy_group.command(name="addmoney", description="إضافة مال لعضو (Admin)")
    @app_commands.describe(
        member="العضو",
        amount="المبلغ"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def addmoney(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        amount: int
    ):
        """Add money to member (Admin)"""
        success = await self.economy.add_money(interaction.guild.id, member.id, amount)
        
        if success:
            await interaction.response.send_message(
                f"✅ تم إضافة **{amount:,}** 🪙 لـ {member.mention}",
                ephemeral=True
            )
        else:
            await interaction.response.send_message("❌ فشلت العملية!", ephemeral=True)
    
    @economy_group.command(name="removemoney", description="إزالة مال من عضو (Admin)")
    @app_commands.describe(
        member="العضو",
        amount="المبلغ"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def removemoney(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        amount: int
    ):
        """Remove money from member (Admin)"""
        success = await self.economy.remove_money(interaction.guild.id, member.id, amount)
        
        if success:
            await interaction.response.send_message(
                f"✅ تم إزالة **{amount:,}** 🪙 من {member.mention}",
                ephemeral=True
            )
        else:
            await interaction.response.send_message("❌ فشلت العملية!", ephemeral=True)
    
    @economy_group.command(name="createitem", description="إنشاء عنصر في المتجر (Admin)")
    @app_commands.describe(
        item_id="معرف العنصر (فريد)",
        name="اسم العنصر",
        description="وصف العنصر",
        price="السعر",
        category="الفئة",
        role="الرتبة (للعناصر من نوع role)",
        stock="المخزون (-1 = غير محدود)",
        emoji="الإيموجي"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def createitem(
        self,
        interaction: discord.Interaction,
        item_id: str,
        name: str,
        description: str,
        price: int,
        category: Literal["role", "item", "boost", "other"],
        role: Optional[discord.Role] = None,
        stock: int = -1,
        emoji: Optional[str] = None
    ):
        """Create shop item (Admin)"""
        success = await self.db.create_item(
            guild_id=interaction.guild.id,
            item_id=item_id,
            name=name,
            description=description,
            price=price,
            category=category,
            role_id=role.id if role else None,
            stock=stock,
            emoji=emoji
        )
        
        if success:
            await interaction.response.send_message(
                f"✅ تم إنشاء العنصر **{name}** بنجاح!",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "❌ فشل إنشاء العنصر! تأكد من أن المعرف غير مستخدم.",
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(EconomyCog(bot))
