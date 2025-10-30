"""
📝 Applications Cog - Kingdom-77 Bot v3.9
Discord Commands for Application System (مثل Appy Bot)

Commands:
- /application setup - إنشاء نموذج تقديم جديد
- /application add-question - إضافة سؤال للنموذج
- /application edit - تعديل نموذج
- /application delete - حذف نموذج
- /application list - عرض جميع النماذج
- /application toggle - تفعيل/تعطيل نموذج
- /application submit - تقديم طلب
- /application mystatus - حالة تقديماتك
- /application review - مراجعة تقديم
- /application stats - إحصائيات
- /application settings - إعدادات النظام
"""

import discord
from discord import option
from discord.ext import commands
from typing import Optional
import asyncio

from applications.application_system import ApplicationSystem


class FormSetupModal(discord.ui.Modal):
    """Modal لإنشاء نموذج جديد"""
    def __init__(self, application_system: ApplicationSystem, *args, **kwargs):
        super().__init__(*args, **kwargs, title="📝 إنشاء نموذج تقديم")
        self.app_system = application_system
        
        self.add_item(discord.ui.InputText(
            label="عنوان النموذج",
            placeholder="مثال: طلب انضمام للفريق",
            min_length=3,
            max_length=100,
            required=True
        ))
        
        self.add_item(discord.ui.InputText(
            label="الوصف",
            placeholder="وصف مختصر للنموذج",
            style=discord.InputTextStyle.long,
            max_length=500,
            required=False
        ))
        
        self.add_item(discord.ui.InputText(
            label="لون Embed (Hex)",
            placeholder="#5865F2",
            min_length=7,
            max_length=7,
            required=False
        ))
    
    async def callback(self, interaction: discord.Interaction):
        title = self.children[0].value
        description = self.children[1].value or ""
        color = self.children[2].value or "#5865F2"
        
        # Validate color
        if not color.startswith("#") or len(color) != 7:
            await interaction.response.send_message(
                "❌ لون غير صحيح! استخدم صيغة Hex مثل `#5865F2`",
                ephemeral=True
            )
            return
        
        # Create form
        form = await self.app_system.create_form(
            guild_id=str(interaction.guild.id),
            title=title,
            created_by=str(interaction.user.id),
            description=description,
            color=color
        )
        
        embed = discord.Embed(
            title="✅ تم إنشاء النموذج بنجاح!",
            description=f"**العنوان:** {title}\n**Form ID:** `{form['form_id']}`",
            color=int(color.replace("#", ""), 16)
        )
        embed.add_field(
            name="الخطوات التالية",
            value="1️⃣ أضف أسئلة باستخدام `/application add-question`\n"
                  "2️⃣ اضبط الإعدادات باستخدام `/application edit`\n"
                  "3️⃣ فعّل النموذج باستخدام `/application toggle`",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


class AddQuestionModal(discord.ui.Modal):
    """Modal لإضافة سؤال"""
    def __init__(self, application_system: ApplicationSystem, form_id: str, *args, **kwargs):
        super().__init__(*args, **kwargs, title="❓ إضافة سؤال")
        self.app_system = application_system
        self.form_id = form_id
        
        self.add_item(discord.ui.InputText(
            label="نص السؤال",
            placeholder="ما هو اسمك؟",
            max_length=200,
            required=True
        ))
        
        self.add_item(discord.ui.InputText(
            label="نوع السؤال",
            placeholder="text, textarea, number, select, yes_no",
            max_length=20,
            required=True
        ))
        
        self.add_item(discord.ui.InputText(
            label="مطلوب؟ (yes/no)",
            placeholder="yes",
            max_length=3,
            required=True
        ))
        
        self.add_item(discord.ui.InputText(
            label="خيارات (للاختيار من متعدد)",
            placeholder="خيار1, خيار2, خيار3",
            style=discord.InputTextStyle.long,
            required=False
        ))
    
    async def callback(self, interaction: discord.Interaction):
        label = self.children[0].value
        q_type = self.children[1].value.lower()
        required = self.children[2].value.lower() == "yes"
        options_str = self.children[3].value
        
        # Validate type
        valid_types = ["text", "textarea", "number", "select", "multiselect", "yes_no"]
        if q_type not in valid_types:
            await interaction.response.send_message(
                f"❌ نوع غير صحيح! الأنواع المتاحة:\n{', '.join(valid_types)}",
                ephemeral=True
            )
            return
        
        # Parse options
        options = []
        if options_str and q_type in ["select", "multiselect"]:
            options = [opt.strip() for opt in options_str.split(",")]
        
        # Add question
        success = await self.app_system.add_question(
            form_id=self.form_id,
            label=label,
            question_type=q_type,
            required=required,
            options=options
        )
        
        if success:
            embed = discord.Embed(
                title="✅ تم إضافة السؤال!",
                description=f"**السؤال:** {label}\n**النوع:** {q_type}\n**إجباري:** {'نعم' if required else 'لا'}",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(
                "❌ فشل في إضافة السؤال!",
                ephemeral=True
            )


class SubmissionModal(discord.ui.Modal):
    """Modal لتقديم الطلب"""
    def __init__(self, application_system: ApplicationSystem, form: dict, *args, **kwargs):
        super().__init__(*args, **kwargs, title=f"📝 {form['title']}")
        self.app_system = application_system
        self.form = form
        
        # Add up to 5 questions (Discord limit)
        questions = form.get("questions", [])[:5]
        for q in questions:
            style = discord.InputTextStyle.long if q["type"] == "textarea" else discord.InputTextStyle.short
            
            self.add_item(discord.ui.InputText(
                label=q["label"],
                placeholder=q.get("placeholder", ""),
                style=style,
                required=q.get("required", True),
                max_length=q.get("max_length", 1000 if q["type"] == "textarea" else 200)
            ))
    
    async def callback(self, interaction: discord.Interaction):
        # Collect answers
        answers = []
        for i, child in enumerate(self.children):
            question = self.form["questions"][i]
            answers.append({
                "question_id": question["question_id"],
                "question_label": question["label"],
                "answer": child.value
            })
        
        # Submit application
        success, error, submission = await self.app_system.submit_application(
            form_id=self.form["form_id"],
            guild_id=str(interaction.guild.id),
            user_id=str(interaction.user.id),
            user=interaction.user,
            answers=answers
        )
        
        if not success:
            await interaction.response.send_message(error, ephemeral=True)
            return
        
        # Send confirmation to user
        success_msg = self.form.get("success_message", "✅ تم إرسال تقديمك بنجاح!")
        embed = discord.Embed(
            title="✅ تم تقديم الطلب!",
            description=success_msg,
            color=discord.Color.green()
        )
        embed.add_field(name="Submission ID", value=f"`{submission['submission_id']}`")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Send to review channel
        review_channel_id = self.form.get("review_channel_id")
        if review_channel_id:
            channel = interaction.guild.get_channel(int(review_channel_id))
            if channel:
                review_embed = self.app_system.create_submission_embed(
                    submission, self.form, interaction.user
                )
                review_view = ReviewView(self.app_system, submission["submission_id"])
                await channel.send(embed=review_embed, view=review_view)


class ReviewView(discord.ui.View):
    """أزرار مراجعة التقديم"""
    def __init__(self, application_system: ApplicationSystem, submission_id: str):
        super().__init__(timeout=None)
        self.app_system = application_system
        self.submission_id = submission_id
    
    @discord.ui.button(label="✅ قبول", style=discord.ButtonStyle.success, custom_id="accept_submission")
    async def accept_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        # Show reason modal
        modal = ReviewReasonModal(self.app_system, self.submission_id, "accept")
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="❌ رفض", style=discord.ButtonStyle.danger, custom_id="reject_submission")
    async def reject_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        modal = ReviewReasonModal(self.app_system, self.submission_id, "reject")
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="📦 أرشفة", style=discord.ButtonStyle.secondary, custom_id="archive_submission")
    async def archive_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        success = await self.app_system.archive_submission(self.submission_id)
        if success:
            self.disable_all_items()
            await interaction.response.edit_message(view=self)
            await interaction.followup.send("📦 تم أرشفة التقديم", ephemeral=True)
        else:
            await interaction.response.send_message("❌ فشلت الأرشفة!", ephemeral=True)


class ReviewReasonModal(discord.ui.Modal):
    """Modal لسبب القبول/الرفض"""
    def __init__(self, application_system: ApplicationSystem, submission_id: str, action: str):
        super().__init__(title=f"{'قبول' if action == 'accept' else 'رفض'} التقديم")
        self.app_system = application_system
        self.submission_id = submission_id
        self.action = action
        
        self.add_item(discord.ui.InputText(
            label="السبب (اختياري)",
            style=discord.InputTextStyle.long,
            placeholder="اكتب سبب القرار...",
            required=False,
            max_length=500
        ))
    
    async def callback(self, interaction: discord.Interaction):
        reason = self.children[0].value or None
        
        success = await self.app_system.review_submission(
            submission_id=self.submission_id,
            reviewer_id=str(interaction.user.id),
            action=self.action,
            reason=reason
        )
        
        if not success:
            await interaction.response.send_message("❌ فشلت المراجعة!", ephemeral=True)
            return
        
        # Get submission and form
        submission = await self.app_system.get_submission(self.submission_id)
        form = await self.app_system.get_form(submission["form_id"])
        
        # Update message
        user = await interaction.client.fetch_user(int(submission["user_id"]))
        embed = self.app_system.create_submission_embed(submission, form, user)
        
        await interaction.message.edit(embed=embed, view=None)
        
        # Send DM to user
        try:
            dm_embed = discord.Embed(
                title=f"{'✅ تم قبول' if self.action == 'accept' else '❌ تم رفض'} تقديمك!",
                description=f"**النموذج:** {form['title']}\n**السبب:** {reason or 'لا يوجد'}",
                color=discord.Color.green() if self.action == "accept" else discord.Color.red()
            )
            await user.send(embed=dm_embed)
        except:
            pass
        
        # Give role if accepted
        if self.action == "accept" and form.get("accepted_role_id"):
            guild = interaction.guild
            role = guild.get_role(int(form["accepted_role_id"]))
            member = guild.get_member(int(submission["user_id"]))
            if role and member:
                await member.add_roles(role)
        
        await interaction.response.send_message(
            f"{'✅ تم القبول' if self.action == 'accept' else '❌ تم الرفض'} بنجاح!",
            ephemeral=True
        )


class FormSelectMenu(discord.ui.Select):
    """قائمة اختيار النماذج"""
    def __init__(self, forms: list):
        options = [
            discord.SelectOption(
                label=form["title"][:100],
                description=f"Status: {'Active' if form.get('is_active') else 'Inactive'}",
                value=form["form_id"],
                emoji="✅" if form.get("is_active") else "❌"
            )
            for form in forms[:25]  # Discord limit
        ]
        
        super().__init__(
            placeholder="اختر نموذج...",
            options=options
        )
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"تم اختيار: `{self.values[0]}`",
            ephemeral=True
        )


class Applications(commands.Cog):
    """نظام التقديمات المتكامل"""
    
    def __init__(self, bot):
        self.bot = bot
        self.app_system: ApplicationSystem = None
    
    async def cog_load(self):
        """تهيئة النظام عند تحميل Cog"""
        if hasattr(self.bot, 'db'):
            self.app_system = ApplicationSystem(self.bot.db)
    
    # ===== Application Commands Group =====
    application = discord.SlashCommandGroup(
        name="application",
        description="إدارة نظام التقديمات"
    )
    
    @application.command(name="setup", description="📝 إنشاء نموذج تقديم جديد")
    @commands.has_permissions(administrator=True)
    async def application_setup(self, ctx: discord.ApplicationContext):
        """إنشاء نموذج تقديم جديد"""
        modal = FormSetupModal(self.app_system)
        await ctx.send_modal(modal)
    
    @application.command(name="add-question", description="❓ إضافة سؤال لنموذج")
    @commands.has_permissions(administrator=True)
    @option("form_id", description="معرف النموذج")
    async def add_question(self, ctx: discord.ApplicationContext, form_id: str):
        """إضافة سؤال لنموذج"""
        # Verify form exists
        form = await self.app_system.get_form(form_id)
        if not form:
            await ctx.respond("❌ النموذج غير موجود!", ephemeral=True)
            return
        
        if form["guild_id"] != str(ctx.guild.id):
            await ctx.respond("❌ هذا النموذج لا ينتمي لهذا السيرفر!", ephemeral=True)
            return
        
        modal = AddQuestionModal(self.app_system, form_id)
        await ctx.send_modal(modal)
    
    @application.command(name="list", description="📋 عرض جميع النماذج")
    async def list_forms(self, ctx: discord.ApplicationContext):
        """عرض جميع نماذج السيرفر"""
        forms = await self.app_system.get_guild_forms(str(ctx.guild.id))
        
        if not forms:
            await ctx.respond("📭 لا توجد نماذج بعد!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="📋 نماذج التقديم",
            description=f"عدد النماذج: {len(forms)}",
            color=discord.Color.blue()
        )
        
        for form in forms[:10]:  # Show first 10
            status = "✅ نشط" if form.get("is_active") else "❌ معطل"
            stats = form.get("stats", {})
            
            embed.add_field(
                name=f"{form['title']} ({status})",
                value=f"**ID:** `{form['form_id']}`\n"
                      f"**الأسئلة:** {len(form.get('questions', []))}\n"
                      f"**التقديمات:** {stats.get('total_submissions', 0)}",
                inline=True
            )
        
        await ctx.respond(embed=embed, ephemeral=True)
    
    @application.command(name="view", description="👁️ عرض تفاصيل نموذج")
    @option("form_id", description="معرف النموذج")
    async def view_form(self, ctx: discord.ApplicationContext, form_id: str):
        """عرض تفاصيل نموذج"""
        form = await self.app_system.get_form(form_id)
        
        if not form:
            await ctx.respond("❌ النموذج غير موجود!", ephemeral=True)
            return
        
        embed = self.app_system.create_form_embed(form)
        await ctx.respond(embed=embed, ephemeral=True)
    
    @application.command(name="toggle", description="🔄 تفعيل/تعطيل نموذج")
    @commands.has_permissions(administrator=True)
    @option("form_id", description="معرف النموذج")
    async def toggle_form(self, ctx: discord.ApplicationContext, form_id: str):
        """تفعيل/تعطيل نموذج"""
        success = await self.app_system.toggle_form_status(form_id)
        
        if success:
            form = await self.app_system.get_form(form_id)
            status = "✅ مفعل" if form.get("is_active") else "❌ معطل"
            await ctx.respond(f"تم تغيير حالة النموذج إلى: {status}", ephemeral=True)
        else:
            await ctx.respond("❌ فشل في تغيير الحالة!", ephemeral=True)
    
    @application.command(name="delete", description="🗑️ حذف نموذج")
    @commands.has_permissions(administrator=True)
    @option("form_id", description="معرف النموذج")
    async def delete_form(self, ctx: discord.ApplicationContext, form_id: str):
        """حذف نموذج"""
        form = await self.app_system.get_form(form_id)
        if not form:
            await ctx.respond("❌ النموذج غير موجود!", ephemeral=True)
            return
        
        # Confirmation
        embed = discord.Embed(
            title="⚠️ تأكيد الحذف",
            description=f"هل أنت متأكد من حذف **{form['title']}**?\n"
                       "⚠️ سيتم حذف جميع التقديمات المرتبطة!",
            color=discord.Color.red()
        )
        
        view = discord.ui.View()
        confirm_btn = discord.ui.Button(label="✅ تأكيد", style=discord.ButtonStyle.danger)
        cancel_btn = discord.ui.Button(label="❌ إلغاء", style=discord.ButtonStyle.secondary)
        
        async def confirm_callback(interaction):
            success = await self.app_system.delete_form(form_id)
            if success:
                await interaction.response.edit_message(
                    content="✅ تم حذف النموذج!",
                    embed=None,
                    view=None
                )
            else:
                await interaction.response.edit_message(
                    content="❌ فشل الحذف!",
                    embed=None,
                    view=None
                )
        
        async def cancel_callback(interaction):
            await interaction.response.edit_message(
                content="❌ تم إلغاء الحذف",
                embed=None,
                view=None
            )
        
        confirm_btn.callback = confirm_callback
        cancel_btn.callback = cancel_callback
        
        view.add_item(confirm_btn)
        view.add_item(cancel_btn)
        
        await ctx.respond(embed=embed, view=view, ephemeral=True)
    
    @application.command(name="submit", description="📨 تقديم طلب")
    @option("form_id", description="معرف النموذج")
    async def submit_application(self, ctx: discord.ApplicationContext, form_id: str):
        """تقديم طلب"""
        form = await self.app_system.get_form(form_id)
        
        if not form:
            await ctx.respond("❌ النموذج غير موجود!", ephemeral=True)
            return
        
        if not form.get("is_active"):
            await ctx.respond("❌ النموذج غير نشط حالياً!", ephemeral=True)
            return
        
        # Check if user can submit
        can_submit, error = await self.app_system.can_user_submit(
            str(ctx.user.id), form_id, str(ctx.guild.id)
        )
        
        if not can_submit:
            await ctx.respond(error, ephemeral=True)
            return
        
        # Show submission modal (up to 5 questions)
        questions = form.get("questions", [])
        if len(questions) == 0:
            await ctx.respond("❌ النموذج لا يحتوي على أسئلة!", ephemeral=True)
            return
        
        if len(questions) <= 5:
            modal = SubmissionModal(self.app_system, form)
            await ctx.send_modal(modal)
        else:
            # For forms with >5 questions, show info
            await ctx.respond(
                f"⚠️ هذا النموذج يحتوي على {len(questions)} سؤال.\n"
                "سيتم عرض أول 5 أسئلة فقط.",
                ephemeral=True
            )
            await asyncio.sleep(2)
            modal = SubmissionModal(self.app_system, form)
            await ctx.send_modal(modal)
    
    @application.command(name="mystatus", description="📊 حالة تقديماتك")
    async def my_status(self, ctx: discord.ApplicationContext):
        """عرض حالة تقديمات المستخدم"""
        submissions = await self.app_system.get_user_submissions(str(ctx.user.id))
        
        if not submissions:
            await ctx.respond("📭 ليس لديك أي تقديمات بعد!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="📊 تقديماتك",
            description=f"عدد التقديمات: {len(submissions)}",
            color=discord.Color.blue()
        )
        
        for sub in submissions[:10]:  # Show first 10
            form = await self.app_system.get_form(sub["form_id"])
            status_emoji = {
                "pending": "⏳",
                "accepted": "✅",
                "rejected": "❌",
                "archived": "📦"
            }
            
            embed.add_field(
                name=f"{status_emoji.get(sub['status'], '❔')} {form['title'] if form else 'Unknown'}",
                value=f"**Status:** {sub['status'].upper()}\n"
                      f"**Submitted:** <t:{int(sub['submitted_at'].timestamp())}:R>",
                inline=True
            )
        
        await ctx.respond(embed=embed, ephemeral=True)
    
    @application.command(name="submissions", description="📋 عرض تقديمات نموذج")
    @commands.has_permissions(manage_guild=True)
    @option("form_id", description="معرف النموذج")
    @option("status", description="حالة التقديمات", choices=["pending", "accepted", "rejected", "all"], required=False)
    async def view_submissions(
        self,
        ctx: discord.ApplicationContext,
        form_id: str,
        status: Optional[str] = "pending"
    ):
        """عرض تقديمات نموذج"""
        form = await self.app_system.get_form(form_id)
        if not form:
            await ctx.respond("❌ النموذج غير موجود!", ephemeral=True)
            return
        
        status_filter = None if status == "all" else status
        submissions = await self.app_system.get_form_submissions(form_id, status_filter)
        
        if not submissions:
            await ctx.respond(f"📭 لا توجد تقديمات {status}!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"📋 تقديمات: {form['title']}",
            description=f"عدد التقديمات: {len(submissions)}",
            color=discord.Color.blue()
        )
        
        for sub in submissions[:10]:
            user_id = sub["user_id"]
            status_emoji = {
                "pending": "⏳",
                "accepted": "✅",
                "rejected": "❌",
                "archived": "📦"
            }
            
            embed.add_field(
                name=f"{status_emoji.get(sub['status'], '❔')} <@{user_id}>",
                value=f"**ID:** `{sub['submission_id']}`\n"
                      f"**Status:** {sub['status'].upper()}\n"
                      f"**Date:** <t:{int(sub['submitted_at'].timestamp())}:R>",
                inline=True
            )
        
        await ctx.respond(embed=embed, ephemeral=True)
    
    @application.command(name="stats", description="📊 إحصائيات النظام")
    @commands.has_permissions(manage_guild=True)
    async def application_stats(self, ctx: discord.ApplicationContext):
        """إحصائيات النظام"""
        stats = await self.app_system.get_guild_stats(str(ctx.guild.id))
        
        embed = discord.Embed(
            title="📊 إحصائيات التقديمات",
            color=discord.Color.gold()
        )
        
        embed.add_field(
            name="📋 النماذج",
            value=f"**العدد:** {stats['total_forms']}",
            inline=True
        )
        
        embed.add_field(
            name="📨 التقديمات",
            value=f"**الكلي:** {stats['total_submissions']}\n"
                  f"**قيد الانتظار:** {stats['pending']}\n"
                  f"**مقبول:** {stats['accepted']}\n"
                  f"**مرفوض:** {stats['rejected']}",
            inline=True
        )
        
        embed.add_field(
            name="📈 معدل القبول",
            value=f"**{stats['acceptance_rate']}%**",
            inline=True
        )
        
        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(Applications(bot))
