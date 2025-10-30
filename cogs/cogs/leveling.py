"""
Leveling Cog for Kingdom-77 Bot v3.0
=====================================
Slash commands for leveling system (Nova-style)
"""

import discord
from discord import app_commands
from discord.ext import commands
import logging
from typing import Optional
from datetime import datetime
from io import BytesIO

from leveling.level_system import get_leveling_system
from database import db

logger = logging.getLogger(__name__)


class LevelingCog(commands.Cog):
    """Leveling commands for XP and ranks."""
    
    def __init__(self, bot):
        self.bot = bot
        self.leveling = None
        
    async def cog_load(self):
        """Initialize leveling system when cog loads."""
        if db and db.client:
            self.leveling = get_leveling_system(db.db)
            logger.info("✅ Leveling system initialized")
        else:
            logger.warning("⚠️ MongoDB not available, leveling disabled")
    
    def make_embed(self, title: str, description: str, color: discord.Color) -> discord.Embed:
        """Create a standard embed."""
        embed = discord.Embed(title=title, description=description, color=color)
        embed.set_footer(text=f"Kingdom-77 Bot v3.9 • {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
        return embed
    
    def create_progress_bar(self, percentage: float, length: int = 10) -> str:
        """Create a progress bar (Nova style).
        
        Args:
            percentage: Progress percentage (0-100)
            length: Bar length
            
        Returns:
            Progress bar string
        """
        filled = int(length * (percentage / 100))
        empty = length - filled
        
        # Nova style: ▰▰▰▰▰▱▱▱▱▱
        bar = "▰" * filled + "▱" * empty
        return bar
    
    # ========================================================================
    # RANK COMMAND
    # ========================================================================
    
    @app_commands.command(name="rank", description="📊 عرض بطاقة رتبتك أو رتبة عضو آخر")
    @app_commands.describe(user="العضو المراد عرض رتبته (اختياري)")
    async def rank(
        self,
        interaction: discord.Interaction,
        user: Optional[discord.Member] = None
    ):
        """Display user's rank card."""
        if not self.leveling:
            embed = self.make_embed(
                title='❌ خطأ',
                description='نظام المستويات غير متاح حالياً.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Default to command user
        target = user or interaction.user
        
        # Don't show ranks for bots
        if target.bot:
            embed = self.make_embed(
                title='❌ خطأ',
                description='لا يمكن عرض رتبة البوتات.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # Get user data
            user_data = await self.leveling.get_user_level(
                str(interaction.guild.id),
                str(target.id)
            )
            
            # Get rank
            rank = await self.leveling.get_user_rank(
                str(interaction.guild.id),
                str(target.id)
            )
            
            # Calculate progress
            xp = user_data.get("xp", 0)
            level = user_data.get("level", 0)
            messages = user_data.get("messages", 0)
            
            progress = self.leveling.calculate_progress(xp, level)
            progress_bar = self.create_progress_bar(progress["percentage"])
            
            # Create embed (Nova style)
            embed = discord.Embed(
                title=f"📊 بطاقة الرتبة",
                color=discord.Color.from_str(user_data.get("rank_card_color", "#5865F2"))
            )
            
            # User info
            embed.set_author(
                name=target.display_name,
                icon_url=target.display_avatar.url
            )
            
            # Stats
            embed.add_field(
                name="📈 المستوى",
                value=f"**{level}**",
                inline=True
            )
            
            embed.add_field(
                name="🏆 الترتيب",
                value=f"**#{rank}**",
                inline=True
            )
            
            embed.add_field(
                name="💬 الرسائل",
                value=f"**{messages:,}**",
                inline=True
            )
            
            # Progress to next level
            embed.add_field(
                name=f"⚡ التقدم إلى المستوى {level + 1}",
                value=f"{progress_bar} **{progress['current_xp']}/{progress['needed_xp']} XP** ({progress['percentage']:.1f}%)",
                inline=False
            )
            
            # Total XP
            embed.add_field(
                name="✨ إجمالي XP",
                value=f"**{xp:,}**",
                inline=True
            )
            
            # Next level XP
            next_level_total = self.leveling.calculate_xp_for_next_level(level)
            embed.add_field(
                name="🎯 XP للمستوى التالي",
                value=f"**{next_level_total:,}**",
                inline=True
            )
            
            embed.set_thumbnail(url=target.display_avatar.url)
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in rank command: {e}")
            embed = self.make_embed(
                title='❌ خطأ',
                description=f'حدث خطأ: {str(e)}',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # ========================================================================
    # LEADERBOARD COMMAND
    # ========================================================================
    
    @app_commands.command(name="leaderboard", description="🏆 عرض قائمة المتصدرين")
    @app_commands.describe(page="رقم الصفحة (اختياري)")
    async def leaderboard(
        self,
        interaction: discord.Interaction,
        page: Optional[int] = 1
    ):
        """Display server leaderboard."""
        if not self.leveling:
            embed = self.make_embed(
                title='❌ خطأ',
                description='نظام المستويات غير متاح حالياً.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Validate page
        page = max(1, page)
        per_page = 10
        offset = (page - 1) * per_page
        
        try:
            # Get leaderboard
            leaderboard = await self.leveling.get_leaderboard(
                str(interaction.guild.id),
                limit=per_page,
                offset=offset
            )
            
            if not leaderboard:
                embed = self.make_embed(
                    title='ℹ️ لا توجد بيانات',
                    description='لا يوجد أعضاء في قائمة المتصدرين بعد.',
                    color=discord.Color.blue()
                )
                await interaction.response.send_message(embed=embed)
                return
            
            # Create embed
            embed = discord.Embed(
                title=f"🏆 قائمة المتصدرين - صفحة {page}",
                description=f"أفضل {per_page} عضو في **{interaction.guild.name}**",
                color=discord.Color.gold()
            )
            
            # Add users to leaderboard
            for i, user_data in enumerate(leaderboard, start=offset + 1):
                user_id = user_data.get("user_id")
                level = user_data.get("level", 0)
                xp = user_data.get("xp", 0)
                messages = user_data.get("messages", 0)
                
                # Try to get user
                try:
                    member = interaction.guild.get_member(int(user_id))
                    user_name = member.mention if member else f"<@{user_id}>"
                except:
                    user_name = f"User {user_id}"
                
                # Medal for top 3
                medal = ""
                if i == 1:
                    medal = "🥇 "
                elif i == 2:
                    medal = "🥈 "
                elif i == 3:
                    medal = "🥉 "
                
                embed.add_field(
                    name=f"{medal}#{i} • {user_name}",
                    value=f"**المستوى:** {level} • **XP:** {xp:,} • **الرسائل:** {messages:,}",
                    inline=False
                )
            
            embed.set_footer(text=f"الصفحة {page} • استخدم /leaderboard page:{page + 1} للصفحة التالية")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in leaderboard command: {e}")
            embed = self.make_embed(
                title='❌ خطأ',
                description=f'حدث خطأ: {str(e)}',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # ========================================================================
    # ADMIN COMMANDS
    # ========================================================================
    
    @app_commands.command(name="addxp", description="➕ إضافة XP لعضو (إداري)")
    @app_commands.describe(
        user="العضو",
        amount="كمية XP"
    )
    async def addxp(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        amount: int
    ):
        """Add XP to a user (admin only)."""
        # Check permissions
        if not interaction.user.guild_permissions.administrator:
            embed = self.make_embed(
                title='❌ صلاحية مرفوضة',
                description='تحتاج صلاحية **Administrator** لاستخدام هذا الأمر.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if not self.leveling:
            embed = self.make_embed(
                title='❌ خطأ',
                description='نظام المستويات غير متاح حالياً.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if user.bot:
            embed = self.make_embed(
                title='❌ خطأ',
                description='لا يمكن إضافة XP للبوتات.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if amount <= 0:
            embed = self.make_embed(
                title='❌ خطأ',
                description='الكمية يجب أن تكون أكبر من 0.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # Add XP
            leveled_up, new_level, user_data = await self.leveling.add_xp(
                str(interaction.guild.id),
                str(user.id),
                amount,
                reason="admin_add",
                bot=self.bot
            )
            
            # Create response
            embed = self.make_embed(
                title='✅ تمت الإضافة',
                description=f'تمت إضافة **{amount} XP** إلى {user.mention}',
                color=discord.Color.green()
            )
            
            embed.add_field(name="XP الجديد", value=f"{user_data.get('xp', 0):,}", inline=True)
            embed.add_field(name="المستوى", value=f"{user_data.get('level', 0)}", inline=True)
            
            if leveled_up:
                embed.add_field(
                    name="🎉 ترقية!",
                    value=f"وصل إلى المستوى **{new_level}**!",
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in addxp command: {e}")
            embed = self.make_embed(
                title='❌ خطأ',
                description=f'حدث خطأ: {str(e)}',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="removexp", description="➖ إزالة XP من عضو (إداري)")
    @app_commands.describe(
        user="العضو",
        amount="كمية XP"
    )
    async def removexp(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        amount: int
    ):
        """Remove XP from a user (admin only)."""
        # Check permissions
        if not interaction.user.guild_permissions.administrator:
            embed = self.make_embed(
                title='❌ صلاحية مرفوضة',
                description='تحتاج صلاحية **Administrator** لاستخدام هذا الأمر.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if not self.leveling:
            embed = self.make_embed(
                title='❌ خطأ',
                description='نظام المستويات غير متاح حالياً.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if user.bot or amount <= 0:
            embed = self.make_embed(
                title='❌ خطأ',
                description='معاملات غير صحيحة.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # Remove XP
            user_data = await self.leveling.remove_xp(
                str(interaction.guild.id),
                str(user.id),
                amount
            )
            
            # Create response
            embed = self.make_embed(
                title='✅ تمت الإزالة',
                description=f'تمت إزالة **{amount} XP** من {user.mention}',
                color=discord.Color.green()
            )
            
            embed.add_field(name="XP الجديد", value=f"{user_data.get('xp', 0):,}", inline=True)
            embed.add_field(name="المستوى", value=f"{user_data.get('level', 0)}", inline=True)
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in removexp command: {e}")
            embed = self.make_embed(
                title='❌ خطأ',
                description=f'حدث خطأ: {str(e)}',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="resetxp", description="🔄 إعادة تعيين XP لعضو (إداري)")
    @app_commands.describe(user="العضو")
    async def resetxp(
        self,
        interaction: discord.Interaction,
        user: discord.Member
    ):
        """Reset user's XP (admin only)."""
        # Check permissions
        if not interaction.user.guild_permissions.administrator:
            embed = self.make_embed(
                title='❌ صلاحية مرفوضة',
                description='تحتاج صلاحية **Administrator** لاستخدام هذا الأمر.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if not self.leveling:
            embed = self.make_embed(
                title='❌ خطأ',
                description='نظام المستويات غير متاح حالياً.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if user.bot:
            embed = self.make_embed(
                title='❌ خطأ',
                description='لا يمكن إعادة تعيين XP للبوتات.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # Reset XP
            success = await self.leveling.reset_user_xp(
                str(interaction.guild.id),
                str(user.id)
            )
            
            if success:
                embed = self.make_embed(
                    title='✅ تمت إعادة التعيين',
                    description=f'تمت إعادة تعيين XP لـ {user.mention} إلى 0.',
                    color=discord.Color.green()
                )
            else:
                embed = self.make_embed(
                    title='ℹ️ لا توجد بيانات',
                    description=f'{user.mention} ليس لديه بيانات XP.',
                    color=discord.Color.blue()
                )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in resetxp command: {e}")
            embed = self.make_embed(
                title='❌ خطأ',
                description=f'حدث خطأ: {str(e)}',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # ==================== Level Card Commands ====================
    
    @app_commands.command(name="levelcard", description="🎨 Customize your server's level up cards (Premium)")
    @app_commands.describe(
        action="Choose an action",
        template="Select a template (for 'template' action)"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="Preview - Preview your current card", value="preview"),
        app_commands.Choice(name="Templates - View available templates", value="templates"),
        app_commands.Choice(name="Customize - Open customization (Premium)", value="customize"),
        app_commands.Choice(name="Reset - Reset to default", value="reset")
    ])
    @app_commands.choices(template=[
        app_commands.Choice(name="Classic - Clean and simple", value="classic"),
        app_commands.Choice(name="Dark - Modern dark theme", value="dark"),
        app_commands.Choice(name="Light - Bright and clean", value="light"),
        app_commands.Choice(name="Purple Dream - Purple gradient", value="purple"),
        app_commands.Choice(name="Ocean Blue - Cool ocean theme", value="ocean"),
        app_commands.Choice(name="Forest Green - Natural green", value="forest"),
        app_commands.Choice(name="Sunset - Warm sunset colors", value="sunset"),
        app_commands.Choice(name="Cyberpunk - Neon cyberpunk", value="cyber")
    ])
    async def levelcard(
        self, 
        interaction: discord.Interaction, 
        action: str,
        template: Optional[str] = None
    ):
        """Customize level cards (Premium feature)"""
        if not self.leveling:
            embed = self.make_embed(
                title='❌ خطأ',
                description='النظام غير متاح حالياً.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Check permissions
        if not interaction.user.guild_permissions.administrator:
            embed = self.make_embed(
                title='❌ خطأ',
                description='يجب أن تكون مسؤولاً لاستخدام هذا الأمر.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            if action == "preview":
                await self._preview_card(interaction)
            elif action == "templates":
                await self._show_templates(interaction)
            elif action == "customize":
                await self._customize_card(interaction)
            elif action == "reset":
                await self._reset_card(interaction)
            elif action == "template" and template:
                await self._apply_template(interaction, template)
        except Exception as e:
            logger.error(f"Error in levelcard command: {e}")
            embed = self.make_embed(
                title='❌ خطأ',
                description=f'حدث خطأ: {str(e)}',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    async def _preview_card(self, interaction: discord.Interaction):
        """Preview current card design"""
        await interaction.response.defer()
        
        try:
            from database.level_cards_schema import get_card_design
            from leveling.card_generator import generate_level_card
            
            # Get current card design
            design = await get_card_design(db.db, str(interaction.guild.id))
            
            # Get user's level data
            user_data = await self.leveling.get_user_level(
                str(interaction.guild.id),
                str(interaction.user.id)
            )
            
            current_xp = user_data.get('current_xp', 0)
            level = user_data.get('level', 1)
            required_xp = self.leveling.calculate_required_xp(level)
            
            # Get rank
            leaderboard = await self.leveling.get_leaderboard(str(interaction.guild.id), limit=1000)
            rank = next((i + 1 for i, u in enumerate(leaderboard) if u['user_id'] == str(interaction.user.id)), 0)
            
            # Generate card
            avatar_url = interaction.user.display_avatar.url
            card_buffer = await generate_level_card(
                username=interaction.user.name,
                discriminator=interaction.user.discriminator,
                level=level,
                current_xp=current_xp,
                required_xp=required_xp,
                rank=rank,
                total_users=len(leaderboard),
                avatar_url=avatar_url,
                background_color=design.get('background_color', '#2C2F33'),
                progress_bar_color=design.get('progress_bar_color', '#5865F2'),
                progress_bar_bg_color=design.get('progress_bar_bg_color', '#99AAB5'),
                text_color=design.get('text_color', '#FFFFFF'),
                accent_color=design.get('accent_color', '#5865F2'),
                avatar_border_color=design.get('avatar_border_color', '#5865F2'),
                avatar_border_width=design.get('avatar_border_width', 5),
                show_rank=design.get('show_rank', True),
                show_progress_percentage=design.get('show_progress_percentage', True)
            )
            
            file = discord.File(fp=card_buffer, filename="levelcard_preview.png")
            
            template_name = design.get('template', 'classic').title()
            embed = self.make_embed(
                title='🎨 Level Card Preview',
                description=f'**Current Template:** {template_name}\n\nThis is how your level cards look!',
                color=discord.Color.blue()
            )
            embed.set_image(url="attachment://levelcard_preview.png")
            
            await interaction.followup.send(embed=embed, file=file)
            
        except Exception as e:
            logger.error(f"Error previewing card: {e}")
            embed = self.make_embed(
                title='❌ خطأ',
                description=f'فشل في إنشاء المعاينة: {str(e)}',
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
    
    async def _show_templates(self, interaction: discord.Interaction):
        """Show available templates"""
        from database.level_cards_schema import DEFAULT_TEMPLATES
        
        embed = self.make_embed(
            title='🎨 Available Card Templates',
            description='Choose from these beautiful templates!\n\n**How to apply:**\nUse `/levelcard` and select a template',
            color=discord.Color.blue()
        )
        
        for template_id, template_data in DEFAULT_TEMPLATES.items():
            embed.add_field(
                name=f"{template_data['name']}",
                value=f"{template_data['description']}\nColors: `{template_data['background_color']}` `{template_data['progress_bar_color']}`",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
    
    async def _customize_card(self, interaction: discord.Interaction):
        """Open card customization (Premium feature)"""
        # Check if guild has premium
        if hasattr(self.bot, 'premium_system'):
            has_premium = await self.bot.premium_system.has_feature(
                str(interaction.guild.id),
                "custom_level_cards"
            )
            
            if not has_premium:
                embed = self.make_embed(
                    title='💎 Premium Feature',
                    description='Custom level card design is a **Premium** feature!\n\n'
                                'Upgrade to Premium to unlock:\n'
                                '✨ Full card customization\n'
                                '🎨 Custom colors\n'
                                '🖼️ Background images\n'
                                '🔤 Custom fonts\n\n'
                                'Use `/premium info` to learn more!',
                    color=discord.Color.gold()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        
        # Show customization info
        embed = self.make_embed(
            title='🎨 Card Customization',
            description='**For advanced customization, visit the Dashboard!**\n\n'
                        f'🌐 Dashboard: {self.bot.config.get("dashboard_url", "https://dashboard.kingdom77.com")}\n\n'
                        '**Available Options:**\n'
                        '• Background color\n'
                        '• Progress bar colors\n'
                        '• Text colors\n'
                        '• Avatar border\n'
                        '• Background images\n'
                        '• Show/hide elements\n\n'
                        '**Quick Apply Template:**\n'
                        'Use `/levelcard` and select a template!',
            color=discord.Color.blue()
        )
        
        await interaction.response.send_message(embed=embed)
    
    async def _reset_card(self, interaction: discord.Interaction):
        """Reset card to default"""
        await interaction.response.defer()
        
        try:
            from database.level_cards_schema import LevelCardsSchema
            
            schema = LevelCardsSchema(db.db)
            success = await schema.delete_card_design(str(interaction.guild.id))
            
            embed = self.make_embed(
                title='✅ تمت إعادة التعيين',
                description='تمت إعادة تعيين تصميم البطاقات إلى الإعداد الافتراضي (Classic).',
                color=discord.Color.green()
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error resetting card: {e}")
            embed = self.make_embed(
                title='❌ خطأ',
                description=f'فشل في إعادة التعيين: {str(e)}',
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
    
    async def _apply_template(self, interaction: discord.Interaction, template_id: str):
        """Apply a template"""
        await interaction.response.defer()
        
        try:
            from database.level_cards_schema import apply_template
            
            success = await apply_template(db.db, str(interaction.guild.id), template_id)
            
            if success:
                from database.level_cards_schema import DEFAULT_TEMPLATES
                template_name = DEFAULT_TEMPLATES[template_id]['name']
                
                embed = self.make_embed(
                    title='✅ تم تطبيق Template',
                    description=f'تم تطبيق template **{template_name}** بنجاح!\n\n'
                                f'استخدم `/levelcard preview` لمعاينة التصميم الجديد.',
                    color=discord.Color.green()
                )
            else:
                embed = self.make_embed(
                    title='❌ خطأ',
                    description='فشل في تطبيق template.',
                    color=discord.Color.red()
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error applying template: {e}")
            embed = self.make_embed(
                title='❌ خطأ',
                description=f'فشل في تطبيق template: {str(e)}',
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot):
    """Setup function to add cog to bot."""
    await bot.add_cog(LevelingCog(bot))
    logger.info("✅ Leveling cog loaded")
