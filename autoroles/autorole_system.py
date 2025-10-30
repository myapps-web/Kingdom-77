"""
نظام الرتب التلقائية (Auto-Roles System)
Kingdom-77 Bot v3.0

هذا الملف يحتوي على جميع عمليات نظام الرتب التلقائية
"""

import discord
import asyncio
from typing import Optional, Dict, List, Any, Union
from datetime import datetime

from database.autoroles_schema import (
    create_reaction_role_document,
    add_role_to_reaction_role,
    create_level_role_document,
    create_join_role_document,
    create_guild_autoroles_config_document,
    get_reaction_role_by_message_query,
    get_level_roles_query,
    get_level_role_for_level_query,
    get_join_roles_query,
    get_join_roles_for_target_query,
    get_all_reaction_roles_query,
    parse_emoji,
    emoji_to_string,
    emojis_match,
    validate_reaction_role_mode,
    validate_level_role,
    validate_join_role_target_type,
    validate_delay_seconds
)


class AutoRoleSystem:
    """نظام إدارة الرتب التلقائية"""
    
    def __init__(self, db):
        """
        تهيئة نظام الرتب التلقائية
        
        Args:
            db: قاعدة البيانات MongoDB
        """
        self.db = db
        self.reaction_roles = db.reaction_roles
        self.level_roles = db.level_roles
        self.join_roles = db.join_roles
        self.config = db.guild_autoroles_config
    
    # ====================================
    # إدارة إعدادات السيرفر
    # ====================================
    
    async def get_guild_config(self, guild_id: int) -> Dict[str, Any]:
        """
        الحصول على إعدادات الرتب التلقائية للسيرفر
        
        Args:
            guild_id: معرف السيرفر
        
        Returns:
            إعدادات السيرفر
        """
        config = await self.config.find_one({"guild_id": guild_id})
        
        if not config:
            # إنشاء إعدادات افتراضية
            config = create_guild_autoroles_config_document(guild_id)
            await self.config.insert_one(config)
        
        return config
    
    async def update_guild_config(
        self,
        guild_id: int,
        updates: Dict[str, Any]
    ) -> bool:
        """
        تحديث إعدادات الرتب التلقائية للسيرفر
        
        Args:
            guild_id: معرف السيرفر
            updates: التحديثات المطلوبة
        
        Returns:
            True إذا نجح التحديث
        """
        updates["updated_at"] = datetime.utcnow()
        
        result = await self.config.update_one(
            {"guild_id": guild_id},
            {"$set": updates}
        )
        
        return result.modified_count > 0
    
    # ====================================
    # Reaction Roles
    # ====================================
    
    async def create_reaction_role(
        self,
        guild_id: int,
        message_id: int,
        channel_id: int,
        title: str,
        description: str,
        mode: str = "toggle",
        **kwargs
    ) -> Dict[str, Any]:
        """
        إنشاء Reaction Role جديد
        
        Args:
            guild_id: معرف السيرفر
            message_id: معرف الرسالة
            channel_id: معرف القناة
            title: العنوان
            description: الوصف
            mode: نمط العمل (toggle, unique, multiple)
            **kwargs: معاملات إضافية
        
        Returns:
            مستند الـ Reaction Role
        """
        if not validate_reaction_role_mode(mode):
            raise ValueError(f"نمط غير صحيح: {mode}")
        
        rr_doc = create_reaction_role_document(
            guild_id, message_id, channel_id, title, description, mode
        )
        
        # إضافة المعاملات الإضافية
        rr_doc.update(kwargs)
        
        await self.reaction_roles.insert_one(rr_doc)
        
        # تحديث العداد
        await self.config.update_one(
            {"guild_id": guild_id},
            {"$inc": {"total_reaction_roles": 1}}
        )
        
        return rr_doc
    
    async def get_reaction_role(
        self,
        guild_id: int,
        message_id: int
    ) -> Optional[Dict[str, Any]]:
        """الحصول على Reaction Role من خلال معرف الرسالة"""
        return await self.reaction_roles.find_one(
            get_reaction_role_by_message_query(guild_id, message_id)
        )
    
    async def get_all_reaction_roles(
        self,
        guild_id: int,
        enabled_only: bool = True
    ) -> List[Dict[str, Any]]:
        """الحصول على جميع Reaction Roles"""
        return await self.reaction_roles.find(
            get_all_reaction_roles_query(guild_id, enabled_only)
        ).to_list(length=None)
    
    async def add_role_to_reaction(
        self,
        guild_id: int,
        message_id: int,
        emoji: str,
        role_id: int,
        label: str,
        description: Optional[str] = None
    ) -> bool:
        """
        إضافة رتبة إلى Reaction Role
        
        Args:
            guild_id: معرف السيرفر
            message_id: معرف الرسالة
            emoji: الإيموجي
            role_id: معرف الرتبة
            label: التسمية
            description: الوصف (اختياري)
        
        Returns:
            True إذا نجحت الإضافة
        """
        parsed_emoji = parse_emoji(emoji)
        role_data = add_role_to_reaction_role(parsed_emoji, role_id, label, description)
        
        result = await self.reaction_roles.update_one(
            get_reaction_role_by_message_query(guild_id, message_id),
            {
                "$push": {"roles": role_data},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        return result.modified_count > 0
    
    async def remove_role_from_reaction(
        self,
        guild_id: int,
        message_id: int,
        emoji: str
    ) -> bool:
        """إزالة رتبة من Reaction Role"""
        parsed_emoji = parse_emoji(emoji)
        
        result = await self.reaction_roles.update_one(
            get_reaction_role_by_message_query(guild_id, message_id),
            {
                "$pull": {"roles": {"emoji": parsed_emoji}},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        return result.modified_count > 0
    
    async def update_reaction_role(
        self,
        guild_id: int,
        message_id: int,
        updates: Dict[str, Any]
    ) -> bool:
        """تحديث Reaction Role"""
        updates["updated_at"] = datetime.utcnow()
        
        result = await self.reaction_roles.update_one(
            get_reaction_role_by_message_query(guild_id, message_id),
            {"$set": updates}
        )
        
        return result.modified_count > 0
    
    async def delete_reaction_role(
        self,
        guild_id: int,
        message_id: int
    ) -> bool:
        """حذف Reaction Role"""
        result = await self.reaction_roles.delete_one(
            get_reaction_role_by_message_query(guild_id, message_id)
        )
        
        if result.deleted_count > 0:
            await self.config.update_one(
                {"guild_id": guild_id},
                {"$inc": {"total_reaction_roles": -1}}
            )
        
        return result.deleted_count > 0
    
    async def handle_reaction_add(
        self,
        payload: discord.RawReactionActionEvent,
        bot: discord.Client
    ) -> Optional[discord.Role]:
        """
        معالجة إضافة رد فعل (Event Handler)
        
        Args:
            payload: بيانات رد الفعل
            bot: البوت
        
        Returns:
            الرتبة الممنوحة أو None
        """
        # الحصول على Reaction Role
        rr = await self.get_reaction_role(payload.guild_id, payload.message_id)
        if not rr or not rr.get("enabled", True):
            return None
        
        # البحث عن الرتبة المطابقة للإيموجي
        emoji_str = emoji_to_string(payload.emoji)
        role_data = None
        
        for r in rr.get("roles", []):
            if emojis_match(r["emoji"], emoji_str):
                role_data = r
                break
        
        if not role_data:
            return None
        
        # الحصول على العضو والرتبة
        guild = bot.get_guild(payload.guild_id)
        if not guild:
            return None
        
        member = guild.get_member(payload.user_id)
        if not member:
            return None
        
        role = guild.get_role(role_data["role_id"])
        if not role:
            return None
        
        # التحقق من الرتبة المطلوبة
        required_role_id = rr.get("required_role")
        if required_role_id:
            required_role = guild.get_role(required_role_id)
            if required_role and required_role not in member.roles:
                return None
        
        # معالجة حسب النمط
        mode = rr.get("mode", "toggle")
        
        if mode == "unique":
            # إزالة جميع الرتب الأخرى من هذا الـ reaction role
            for r in rr.get("roles", []):
                if r["role_id"] != role_data["role_id"]:
                    other_role = guild.get_role(r["role_id"])
                    if other_role and other_role in member.roles:
                        try:
                            await member.remove_roles(other_role, reason="Reaction Role (unique mode)")
                        except:
                            pass
        
        # إعطاء الرتبة
        if role not in member.roles:
            try:
                await member.add_roles(role, reason="Reaction Role")
                
                # تحديث الإحصائيات
                await self.config.update_one(
                    {"guild_id": payload.guild_id},
                    {"$inc": {"total_roles_given": 1}}
                )
                
                return role
            except discord.Forbidden:
                pass
            except discord.HTTPException:
                pass
        
        return None
    
    async def handle_reaction_remove(
        self,
        payload: discord.RawReactionActionEvent,
        bot: discord.Client
    ) -> Optional[discord.Role]:
        """
        معالجة إزالة رد فعل (Event Handler)
        
        Args:
            payload: بيانات رد الفعل
            bot: البوت
        
        Returns:
            الرتبة المزالة أو None
        """
        # الحصول على Reaction Role
        rr = await self.get_reaction_role(payload.guild_id, payload.message_id)
        if not rr or not rr.get("enabled", True):
            return None
        
        # في نمط unique لا نزيل الرتبة
        if rr.get("mode") == "unique":
            return None
        
        # البحث عن الرتبة
        emoji_str = emoji_to_string(payload.emoji)
        role_data = None
        
        for r in rr.get("roles", []):
            if emojis_match(r["emoji"], emoji_str):
                role_data = r
                break
        
        if not role_data:
            return None
        
        # الحصول على العضو والرتبة
        guild = bot.get_guild(payload.guild_id)
        if not guild:
            return None
        
        member = guild.get_member(payload.user_id)
        if not member:
            return None
        
        role = guild.get_role(role_data["role_id"])
        if not role:
            return None
        
        # إزالة الرتبة
        if role in member.roles:
            try:
                await member.remove_roles(role, reason="Reaction Role removed")
                
                # تحديث الإحصائيات
                await self.config.update_one(
                    {"guild_id": payload.guild_id},
                    {"$inc": {"total_roles_removed": 1}}
                )
                
                return role
            except discord.Forbidden:
                pass
            except discord.HTTPException:
                pass
        
        return None
    
    # ====================================
    # Level Roles
    # ====================================
    
    async def add_level_role(
        self,
        guild_id: int,
        level: int,
        role_id: int,
        remove_previous: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        إضافة Level Role
        
        Args:
            guild_id: معرف السيرفر
            level: المستوى
            role_id: معرف الرتبة
            remove_previous: إزالة رتب المستويات السابقة
            **kwargs: معاملات إضافية
        
        Returns:
            مستند الـ Level Role
        """
        is_valid, error_msg = validate_level_role(level, role_id)
        if not is_valid:
            raise ValueError(error_msg)
        
        lr_doc = create_level_role_document(guild_id, level, role_id, remove_previous)
        lr_doc.update(kwargs)
        
        await self.level_roles.insert_one(lr_doc)
        
        # تحديث العداد
        await self.config.update_one(
            {"guild_id": guild_id},
            {"$inc": {"total_level_roles": 1}}
        )
        
        return lr_doc
    
    async def remove_level_role(
        self,
        guild_id: int,
        level: int,
        role_id: Optional[int] = None
    ) -> bool:
        """
        إزالة Level Role
        
        Args:
            guild_id: معرف السيرفر
            level: المستوى
            role_id: معرف الرتبة (اختياري - لإزالة رتبة محددة)
        
        Returns:
            True إذا نجحت الإزالة
        """
        query = {"guild_id": guild_id, "level": level}
        if role_id:
            query["role_id"] = role_id
        
        result = await self.level_roles.delete_one(query)
        
        if result.deleted_count > 0:
            await self.config.update_one(
                {"guild_id": guild_id},
                {"$inc": {"total_level_roles": -1}}
            )
        
        return result.deleted_count > 0
    
    async def get_level_roles(
        self,
        guild_id: int,
        enabled_only: bool = True
    ) -> List[Dict[str, Any]]:
        """الحصول على جميع Level Roles"""
        return await self.level_roles.find(
            get_level_roles_query(guild_id, enabled_only)
        ).sort("level", 1).to_list(length=None)
    
    async def get_roles_for_level(
        self,
        guild_id: int,
        level: int
    ) -> List[Dict[str, Any]]:
        """الحصول على رتب لمستوى معين"""
        return await self.level_roles.find(
            get_level_role_for_level_query(guild_id, level)
        ).to_list(length=None)
    
    async def assign_level_roles(
        self,
        guild_id: int,
        user_id: int,
        level: int,
        bot: discord.Client
    ) -> List[discord.Role]:
        """
        إعطاء رتب المستوى للعضو (يُستدعى عند level up)
        
        Args:
            guild_id: معرف السيرفر
            user_id: معرف المستخدم
            level: المستوى الجديد
            bot: البوت
        
        Returns:
            قائمة الرتب الممنوحة
        """
        # التحقق من التفعيل
        config = await self.get_guild_config(guild_id)
        if not config.get("level_roles_enabled", True):
            return []
        
        # الحصول على رتب هذا المستوى
        level_roles = await self.get_roles_for_level(guild_id, level)
        if not level_roles:
            return []
        
        guild = bot.get_guild(guild_id)
        if not guild:
            return []
        
        member = guild.get_member(user_id)
        if not member:
            return []
        
        granted_roles = []
        
        for lr in level_roles:
            role = guild.get_role(lr["role_id"])
            if not role:
                continue
            
            # إزالة رتب المستويات السابقة إذا كان مطلوباً
            if lr.get("remove_previous", False):
                all_level_roles = await self.get_level_roles(guild_id)
                for other_lr in all_level_roles:
                    if other_lr["level"] < level:
                        other_role = guild.get_role(other_lr["role_id"])
                        if other_role and other_role in member.roles:
                            try:
                                await member.remove_roles(other_role, reason="Level Role (previous level)")
                            except:
                                pass
            
            # إعطاء الرتبة
            if role not in member.roles:
                try:
                    await member.add_roles(role, reason=f"Level Role (Level {level})")
                    granted_roles.append(role)
                    
                    # تحديث الإحصائيات
                    await self.config.update_one(
                        {"guild_id": guild_id},
                        {"$inc": {"total_roles_given": 1}}
                    )
                except:
                    pass
        
        return granted_roles
    
    # ====================================
    # Join Roles
    # ====================================
    
    async def add_join_role(
        self,
        guild_id: int,
        role_id: int,
        target_type: str = "all",
        delay_seconds: int = 0,
        **kwargs
    ) -> Dict[str, Any]:
        """
        إضافة Join Role
        
        Args:
            guild_id: معرف السيرفر
            role_id: معرف الرتبة
            target_type: نوع الهدف (all, humans, bots)
            delay_seconds: تأخير قبل إعطاء الرتبة
            **kwargs: معاملات إضافية
        
        Returns:
            مستند الـ Join Role
        """
        if not validate_join_role_target_type(target_type):
            raise ValueError(f"نوع هدف غير صحيح: {target_type}")
        
        is_valid, error_msg = validate_delay_seconds(delay_seconds)
        if not is_valid:
            raise ValueError(error_msg)
        
        jr_doc = create_join_role_document(guild_id, role_id, target_type)
        jr_doc["delay_seconds"] = delay_seconds
        jr_doc.update(kwargs)
        
        await self.join_roles.insert_one(jr_doc)
        
        # تحديث العداد
        await self.config.update_one(
            {"guild_id": guild_id},
            {"$inc": {"total_join_roles": 1}}
        )
        
        return jr_doc
    
    async def remove_join_role(
        self,
        guild_id: int,
        role_id: int
    ) -> bool:
        """إزالة Join Role"""
        result = await self.join_roles.delete_one({
            "guild_id": guild_id,
            "role_id": role_id
        })
        
        if result.deleted_count > 0:
            await self.config.update_one(
                {"guild_id": guild_id},
                {"$inc": {"total_join_roles": -1}}
            )
        
        return result.deleted_count > 0
    
    async def get_join_roles(
        self,
        guild_id: int,
        enabled_only: bool = True
    ) -> List[Dict[str, Any]]:
        """الحصول على جميع Join Roles"""
        return await self.join_roles.find(
            get_join_roles_query(guild_id, enabled_only)
        ).to_list(length=None)
    
    async def assign_join_roles(
        self,
        member: discord.Member
    ) -> List[discord.Role]:
        """
        إعطاء رتب الانضمام للعضو الجديد (Event Handler)
        
        Args:
            member: العضو الجديد
        
        Returns:
            قائمة الرتب الممنوحة
        """
        # التحقق من التفعيل
        config = await self.get_guild_config(member.guild.id)
        if not config.get("join_roles_enabled", True):
            return []
        
        # الحصول على Join Roles المناسبة
        join_roles = await self.join_roles.find(
            get_join_roles_for_target_query(member.guild.id, member.bot)
        ).to_list(length=None)
        
        if not join_roles:
            return []
        
        granted_roles = []
        
        for jr in join_roles:
            # التحقق من ignore_returning
            if jr.get("ignore_returning", False) and len(member.roles) > 1:
                # العضو لديه رتب بالفعل (عائد)
                continue
            
            role = member.guild.get_role(jr["role_id"])
            if not role:
                continue
            
            # التأخير إذا كان مطلوباً
            delay = jr.get("delay_seconds", 0)
            if delay > 0:
                await asyncio.sleep(delay)
            
            # إعطاء الرتبة
            if role not in member.roles:
                try:
                    await member.add_roles(role, reason="Join Role")
                    granted_roles.append(role)
                    
                    # تحديث الإحصائيات
                    await self.config.update_one(
                        {"guild_id": member.guild.id},
                        {"$inc": {"total_roles_given": 1}}
                    )
                except:
                    pass
        
        return granted_roles
    
    # ====================================
    # دوال مساعدة
    # ====================================
    
    async def get_statistics(self, guild_id: int) -> Dict[str, Any]:
        """الحصول على إحصائيات الرتب التلقائية"""
        config = await self.get_guild_config(guild_id)
        
        return {
            "total_reaction_roles": config.get("total_reaction_roles", 0),
            "total_level_roles": config.get("total_level_roles", 0),
            "total_join_roles": config.get("total_join_roles", 0),
            "total_roles_given": config.get("total_roles_given", 0),
            "total_roles_removed": config.get("total_roles_removed", 0)
        }
