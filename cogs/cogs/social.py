"""
Social Media Integration Commands
Kingdom-77 Bot v4.0 - Phase 5.7

Discord commands for managing social media links and notifications.
Supports 7 platforms: YouTube, Twitch, Kick, Twitter, Instagram, TikTok, Snapchat
"""

import discord
from discord import app_commands
from discord.ext import commands
from typing import Literal, Optional
from datetime import datetime


class Social(commands.Cog):
    """Social Media Integration Commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.social_system = None
    
    async def cog_load(self):
        """Initialize social integration system"""
        self.social_system = self.bot.social_system
    
    # Group: /social
    social_group = app_commands.Group(
        name="social",
        description="إدارة روابط وسائل التواصل الاجتماعي"
    )
    
    # ==================== LINK MANAGEMENT ====================
    
    @social_group.command(name="link", description="ربط حساب من منصة اجتماعية")
    @app_commands.describe(
        platform="المنصة الاجتماعية",
        url="رابط القناة/الحساب",
        channel="قناة الإشعارات",
        role="رتبة للإشارة (اختياري)"
    )
    async def social_link(
        self,
        interaction: discord.Interaction,
        platform: Literal["youtube", "twitch", "kick", "twitter", "instagram", "tiktok", "snapchat"],
        url: str,
        channel: discord.TextChannel,
        role: Optional[discord.Role] = None
    ):
        """Link a social media account"""
        # Check permissions
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ تحتاج صلاحية **Manage Server** لاستخدام هذا الأمر!",
                ephemeral=True
            )
            return
        
        await interaction.response.defer(ephemeral=True)
        
        # Add link
        success, message = await self.social_system.add_link(
            guild_id=str(interaction.guild.id),
            user_id=str(interaction.user.id),
            platform=platform,
            channel_url=url,
            notification_channel_id=str(channel.id),
            mention_role_id=str(role.id) if role else None
        )
        
        if success:
            embed = discord.Embed(
                title="✅ تم إضافة الرابط",
                description=message,
                color=discord.Color.green()
            )
            
            # Get platform info
            platform_info = self.social_system.PLATFORMS[platform]
            
            embed.add_field(
                name="المنصة",
                value=f"{platform_info['emoji']} {platform_info['name']}",
                inline=True
            )
            
            embed.add_field(
                name="قناة الإشعارات",
                value=channel.mention,
                inline=True
            )
            
            if role:
                embed.add_field(
                    name="الإشارة",
                    value=role.mention,
                    inline=True
                )
            
            embed.set_footer(text="سيتم التحقق من المحتوى كل 5 دقائق")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.followup.send(message, ephemeral=True)
    
    @social_group.command(name="unlink", description="إلغاء ربط حساب")
    @app_commands.describe(
        link_id="معرف الرابط (من /social list)"
    )
    async def social_unlink(
        self,
        interaction: discord.Interaction,
        link_id: str
    ):
        """Unlink a social media account"""
        # Check permissions
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ تحتاج صلاحية **Manage Server**!",
                ephemeral=True
            )
            return
        
        await interaction.response.defer(ephemeral=True)
        
        success, message = await self.social_system.remove_link(
            guild_id=str(interaction.guild.id),
            link_id=link_id
        )
        
        await interaction.followup.send(message, ephemeral=True)
    
    @social_group.command(name="list", description="عرض جميع الروابط المضافة")
    async def social_list(self, interaction: discord.Interaction):
        """List all social media links"""
        await interaction.response.defer(ephemeral=True)
        
        links = await self.social_system.get_guild_links(str(interaction.guild.id))
        
        if not links:
            await interaction.followup.send(
                "📭 لا توجد روابط مضافة في هذا السيرفر!\n"
                "استخدم `/social link` لإضافة رابط",
                ephemeral=True
            )
            return
        
        # Build embed
        embed = discord.Embed(
            title="🔗 روابط وسائل التواصل الاجتماعي",
            description=f"السيرفر: **{interaction.guild.name}**\n"
                       f"الروابط: **{len(links)}**",
            color=discord.Color.blue()
        )
        
        for link in links[:10]:  # Limit to 10
            platform_info = self.social_system.PLATFORMS[link["platform"]]
            status = "✅" if link["enabled"] else "❌"
            
            channel = interaction.guild.get_channel(int(link["notification_channel_id"]))
            channel_mention = channel.mention if channel else "❌ محذوفة"
            
            value_text = (
                f"**الحالة:** {status}\n"
                f"**القناة:** {channel_mention}\n"
                f"**الإشعارات:** {link.get('statistics', {}).get('total_notifications', 0)}\n"
                f"**ID:** `{link['link_id'][:12]}...`"
            )
            
            embed.add_field(
                name=f"{platform_info['emoji']} {platform_info['name']}",
                value=value_text,
                inline=True
            )
        
        if len(links) > 10:
            embed.set_footer(text=f"يتم عرض 10 من أصل {len(links)} رابط")
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @social_group.command(name="toggle", description="تفعيل/تعطيل رابط")
    @app_commands.describe(
        link_id="معرف الرابط (من /social list)"
    )
    async def social_toggle(
        self,
        interaction: discord.Interaction,
        link_id: str
    ):
        """Toggle a social media link"""
        # Check permissions
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ تحتاج صلاحية **Manage Server**!",
                ephemeral=True
            )
            return
        
        await interaction.response.defer(ephemeral=True)
        
        success, message, new_state = await self.social_system.toggle_link(
            guild_id=str(interaction.guild.id),
            link_id=link_id
        )
        
        if success:
            status_emoji = "✅" if new_state else "❌"
            await interaction.followup.send(f"{status_emoji} {message}", ephemeral=True)
        else:
            await interaction.followup.send(message, ephemeral=True)
    
    @social_group.command(name="test", description="اختبار إشعار من رابط")
    @app_commands.describe(
        link_id="معرف الرابط (من /social list)"
    )
    async def social_test(
        self,
        interaction: discord.Interaction,
        link_id: str
    ):
        """Test notification for a link"""
        await interaction.response.defer(ephemeral=True)
        
        # Get link
        link = await self.social_system.get_link_by_id(
            str(interaction.guild.id),
            link_id
        )
        
        if not link:
            await interaction.followup.send("❌ الرابط غير موجود!", ephemeral=True)
            return
        
        # Create test post
        platform_info = self.social_system.PLATFORMS[link["platform"]]
        
        test_post = {
            "post_id": "test_" + datetime.utcnow().strftime("%Y%m%d%H%M%S"),
            "title": f"🧪 اختبار إشعار {platform_info['name']}",
            "url": link["channel_url"],
            "thumbnail": None,
            "author": "Test",
            "published_at": datetime.utcnow()
        }
        
        # Send test notification
        success = await self.social_system.send_notification(
            link,
            test_post,
            self.bot
        )
        
        if success:
            channel = interaction.guild.get_channel(int(link["notification_channel_id"]))
            await interaction.followup.send(
                f"✅ تم إرسال إشعار اختبار في {channel.mention}",
                ephemeral=True
            )
        else:
            await interaction.followup.send(
                "❌ فشل إرسال الإشعار! تحقق من صلاحيات البوت في القناة",
                ephemeral=True
            )
    
    @social_group.command(name="stats", description="إحصائيات الروابط")
    async def social_stats(self, interaction: discord.Interaction):
        """View social media statistics"""
        await interaction.response.defer(ephemeral=True)
        
        stats = await self.social_system.get_guild_statistics(str(interaction.guild.id))
        
        embed = discord.Embed(
            title="📊 إحصائيات وسائل التواصل الاجتماعي",
            description=f"السيرفر: **{interaction.guild.name}**",
            color=discord.Color.blue()
        )
        
        # Overall stats
        embed.add_field(
            name="📈 إجمالي",
            value=f"**الروابط:** {stats['total_links']}\n"
                  f"**النشطة:** {stats['active_links']}\n"
                  f"**الإشعارات:** {stats['total_notifications']}",
            inline=False
        )
        
        # By platform
        if stats.get("by_platform"):
            platform_text = ""
            for platform, data in stats["by_platform"].items():
                platform_info = self.social_system.PLATFORMS[platform]
                platform_text += (
                    f"{platform_info['emoji']} **{platform_info['name']}:** "
                    f"{data['count']} ({data['notifications']} إشعار)\n"
                )
            
            embed.add_field(
                name="📋 حسب المنصة",
                value=platform_text,
                inline=False
            )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @social_group.command(name="mylimits", description="عرض حدودك الحالية")
    async def social_mylimits(self, interaction: discord.Interaction):
        """View your current limits"""
        await interaction.response.defer(ephemeral=True)
        
        limits = await self.social_system.get_guild_limits(str(interaction.guild.id))
        
        embed = discord.Embed(
            title="📊 حدود الروابط",
            description=f"السيرفر: **{interaction.guild.name}**",
            color=discord.Color.blue()
        )
        
        # Free links
        free_used = limits["free_used"]
        free_max = limits["free_max"]
        free_remaining = free_max - free_used
        
        embed.add_field(
            name="🆓 الروابط المجانية",
            value=f"**المستخدمة:** {free_used}/{free_max}\n"
                  f"**المتبقية:** {free_remaining}",
            inline=True
        )
        
        # Purchased links
        purchased = limits["purchased"]
        embed.add_field(
            name="💎 الروابط المشتراة",
            value=f"**العدد:** {purchased}\n"
                  f"**السعر:** 200 ❄️ للرابط",
            inline=True
        )
        
        # Total
        embed.add_field(
            name="📊 الإجمالي",
            value=f"**الروابط:** {limits['total_links']}\n"
                  f"**يمكن الإضافة:** {'نعم ✅' if limits['can_add_free'] or purchased > 0 else 'لا ❌'}",
            inline=True
        )
        
        # By platform
        if limits.get("links_by_platform"):
            platform_text = ""
            for platform, count in limits["links_by_platform"].items():
                platform_info = self.social_system.PLATFORMS[platform]
                platform_text += f"{platform_info['emoji']} {platform_info['name']}: {count}\n"
            
            embed.add_field(
                name="📋 التوزيع حسب المنصة",
                value=platform_text,
                inline=False
            )
        
        if not limits["can_add_free"] and purchased == 0:
            embed.add_field(
                name="💡 نصيحة",
                value="وصلت إلى الحد الأقصى المجاني (2 روابط)!\n"
                      "يمكنك شراء روابط إضافية عبر `/social purchase-link`",
                inline=False
            )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @social_group.command(name="purchase-link", description="شراء رابط إضافي (200 ❄️)")
    async def social_purchase_link(self, interaction: discord.Interaction):
        """Purchase an additional link slot"""
        # Check permissions
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ تحتاج صلاحية **Manage Server**!",
                ephemeral=True
            )
            return
        
        await interaction.response.defer(ephemeral=True)
        
        # Check if already at limit
        limits = await self.social_system.get_guild_limits(str(interaction.guild.id))
        
        embed = discord.Embed(
            title="💎 شراء رابط إضافي",
            description="يمكنك شراء روابط إضافية دائمة للسيرفر!",
            color=discord.Color.gold()
        )
        
        embed.add_field(
            name="💰 السعر",
            value="**200 ❄️** (دائم)",
            inline=True
        )
        
        embed.add_field(
            name="📊 الحالة الحالية",
            value=f"**المجانية:** {limits['free_used']}/2\n"
                  f"**المشتراة:** {limits['purchased']}",
            inline=True
        )
        
        embed.add_field(
            name="✨ الميزات",
            value="• رابط دائم (لا يحتاج تجديد)\n"
                  "• دعم جميع المنصات السبعة\n"
                  "• إشعارات تلقائية كل 5 دقائق",
            inline=False
        )
        
        # Purchase button view
        view = PurchaseLinkView(
            self.social_system,
            str(interaction.guild.id),
            str(interaction.user.id),
            interaction.user
        )
        
        embed.set_footer(text="اضغط الزر أدناه للشراء")
        
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)
    
    @social_group.command(name="notifications", description="تعديل قناة الإشعارات")
    @app_commands.describe(
        link_id="معرف الرابط",
        channel="القناة الجديدة"
    )
    async def social_notifications(
        self,
        interaction: discord.Interaction,
        link_id: str,
        channel: discord.TextChannel
    ):
        """Change notification channel for a link"""
        # Check permissions
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ تحتاج صلاحية **Manage Server**!",
                ephemeral=True
            )
            return
        
        await interaction.response.defer(ephemeral=True)
        
        # Update link
        result = await self.social_system.links_collection.update_one(
            {
                "guild_id": str(interaction.guild.id),
                "link_id": link_id
            },
            {
                "$set": {
                    "notification_channel_id": str(channel.id)
                }
            }
        )
        
        if result.modified_count > 0:
            await interaction.followup.send(
                f"✅ تم تحديث قناة الإشعارات إلى {channel.mention}",
                ephemeral=True
            )
        else:
            await interaction.followup.send(
                "❌ الرابط غير موجود!",
                ephemeral=True
            )
    
    @social_group.command(name="role", description="تعديل رتبة الإشارة")
    @app_commands.describe(
        link_id="معرف الرابط",
        role="الرتبة (اختياري - اتركه فارغاً للإلغاء)"
    )
    async def social_role(
        self,
        interaction: discord.Interaction,
        link_id: str,
        role: Optional[discord.Role] = None
    ):
        """Change mention role for a link"""
        # Check permissions
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ تحتاج صلاحية **Manage Server**!",
                ephemeral=True
            )
            return
        
        await interaction.response.defer(ephemeral=True)
        
        # Update link
        result = await self.social_system.links_collection.update_one(
            {
                "guild_id": str(interaction.guild.id),
                "link_id": link_id
            },
            {
                "$set": {
                    "mention_role_id": str(role.id) if role else None
                }
            }
        )
        
        if result.modified_count > 0:
            if role:
                await interaction.followup.send(
                    f"✅ تم تحديث رتبة الإشارة إلى {role.mention}",
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    "✅ تم إلغاء الإشارة",
                    ephemeral=True
                )
        else:
            await interaction.followup.send(
                "❌ الرابط غير موجود!",
                ephemeral=True
            )


# ==================== UI COMPONENTS ====================

class PurchaseLinkView(discord.ui.View):
    """View for purchasing additional link slots"""
    
    def __init__(self, social_system, guild_id: str, user_id: str, user: discord.User):
        super().__init__(timeout=300)  # 5 minutes
        self.social_system = social_system
        self.guild_id = guild_id
        self.user_id = user_id
        self.user = user
    
    @discord.ui.button(label="💎 شراء رابط (200 ❄️)", style=discord.ButtonStyle.success)
    async def purchase_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(
                "❌ هذا الزر ليس لك!",
                ephemeral=True
            )
            return
        
        await interaction.response.defer(ephemeral=True)
        
        # Attempt purchase
        success, message = await self.social_system.purchase_link(
            self.guild_id,
            self.user_id
        )
        
        if success:
            embed = discord.Embed(
                title="✅ تم الشراء بنجاح",
                description=message,
                color=discord.Color.green()
            )
            
            # Disable button
            button.disabled = True
            button.label = "✅ تم الشراء"
            await interaction.edit_original_response(embed=embed, view=self)
        else:
            await interaction.followup.send(message, ephemeral=True)
    
    @discord.ui.button(label="❌ إلغاء", style=discord.ButtonStyle.secondary)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(
                "❌ هذا الزر ليس لك!",
                ephemeral=True
            )
            return
        
        await interaction.response.edit_message(
            content="❌ تم إلغاء الشراء",
            embed=None,
            view=None
        )


async def setup(bot):
    await bot.add_cog(Social(bot))
