"""
Kingdom-77 Bot - Suggestions System Database Schema
نظام قاعدة بيانات الاقتراحات المتقدم

Collections:
- suggestions: الاقتراحات الرئيسية
- suggestion_votes: أصوات الأعضاء
- suggestion_comments: التعليقات على الاقتراحات
- suggestion_settings: إعدادات النظام لكل سيرفر
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from enum import Enum


class SuggestionStatus(str, Enum):
    """حالات الاقتراح"""
    PENDING = "pending"          # قيد المراجعة
    APPROVED = "approved"        # موافق عليه
    DENIED = "denied"           # مرفوض
    IMPLEMENTED = "implemented"  # تم التنفيذ
    DUPLICATE = "duplicate"      # مكرر
    CONSIDERING = "considering"  # قيد النظر


class SuggestionsSchema:
    """Schema for Suggestions System"""
    
    def __init__(self, db):
        self.db = db
        self.suggestions = db.suggestions
        self.votes = db.suggestion_votes
        self.comments = db.suggestion_comments
        self.settings = db.suggestion_settings
    
    async def setup_indexes(self):
        """إنشاء الـ indexes للأداء الأفضل"""
        # Suggestions indexes
        await self.suggestions.create_index([("guild_id", 1), ("suggestion_id", 1)], unique=True)
        await self.suggestions.create_index([("guild_id", 1), ("status", 1)])
        await self.suggestions.create_index([("guild_id", 1), ("user_id", 1)])
        await self.suggestions.create_index([("created_at", -1)])
        
        # Votes indexes
        await self.votes.create_index([("guild_id", 1), ("suggestion_id", 1), ("user_id", 1)], unique=True)
        await self.votes.create_index([("suggestion_id", 1)])
        
        # Comments indexes
        await self.comments.create_index([("suggestion_id", 1)])
        await self.comments.create_index([("created_at", -1)])
        
        # Settings indexes
        await self.settings.create_index("guild_id", unique=True)
    
    # ============= Suggestion Management =============
    
    async def create_suggestion(
        self,
        guild_id: int,
        user_id: int,
        title: str,
        description: str,
        anonymous: bool = False,
        attachments: List[str] = None
    ) -> Dict[str, Any]:
        """إنشاء اقتراح جديد"""
        
        # الحصول على آخر suggestion_id
        last_suggestion = await self.suggestions.find_one(
            {"guild_id": str(guild_id)},
            sort=[("suggestion_id", -1)]
        )
        
        next_id = 1
        if last_suggestion:
            next_id = last_suggestion.get("suggestion_id", 0) + 1
        
        suggestion = {
            "guild_id": str(guild_id),
            "suggestion_id": next_id,
            "user_id": str(user_id),
            "title": title,
            "description": description,
            "status": SuggestionStatus.PENDING.value,
            "anonymous": anonymous,
            "attachments": attachments or [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            
            # Vote counters
            "upvotes": 0,
            "downvotes": 0,
            "neutral_votes": 0,
            
            # Metadata
            "message_id": None,  # Discord message ID
            "channel_id": None,
            "staff_response": None,
            "staff_responder_id": None,
            "reviewed_at": None,
            "implemented_at": None,
            
            # Tags
            "tags": [],
            "priority": "normal"  # low, normal, high
        }
        
        result = await self.suggestions.insert_one(suggestion)
        suggestion["_id"] = result.inserted_id
        
        return suggestion
    
    async def get_suggestion(
        self,
        guild_id: int,
        suggestion_id: int
    ) -> Optional[Dict[str, Any]]:
        """الحصول على اقتراح محدد"""
        return await self.suggestions.find_one({
            "guild_id": str(guild_id),
            "suggestion_id": suggestion_id
        })
    
    async def update_suggestion_status(
        self,
        guild_id: int,
        suggestion_id: int,
        status: str,
        staff_id: int,
        response: Optional[str] = None
    ) -> bool:
        """تحديث حالة الاقتراح"""
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow(),
            "staff_responder_id": str(staff_id),
            "reviewed_at": datetime.utcnow()
        }
        
        if response:
            update_data["staff_response"] = response
        
        if status == SuggestionStatus.IMPLEMENTED.value:
            update_data["implemented_at"] = datetime.utcnow()
        
        result = await self.suggestions.update_one(
            {
                "guild_id": str(guild_id),
                "suggestion_id": suggestion_id
            },
            {"$set": update_data}
        )
        
        return result.modified_count > 0
    
    async def delete_suggestion(
        self,
        guild_id: int,
        suggestion_id: int
    ) -> bool:
        """حذف اقتراح"""
        # حذف الاقتراح
        result = await self.suggestions.delete_one({
            "guild_id": str(guild_id),
            "suggestion_id": suggestion_id
        })
        
        # حذف الأصوات المرتبطة
        await self.votes.delete_many({
            "guild_id": str(guild_id),
            "suggestion_id": suggestion_id
        })
        
        # حذف التعليقات المرتبطة
        await self.comments.delete_many({
            "guild_id": str(guild_id),
            "suggestion_id": suggestion_id
        })
        
        return result.deleted_count > 0
    
    async def update_suggestion_message(
        self,
        guild_id: int,
        suggestion_id: int,
        message_id: int,
        channel_id: int
    ) -> bool:
        """تحديث معلومات رسالة الاقتراح"""
        result = await self.suggestions.update_one(
            {
                "guild_id": str(guild_id),
                "suggestion_id": suggestion_id
            },
            {
                "$set": {
                    "message_id": str(message_id),
                    "channel_id": str(channel_id),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return result.modified_count > 0
    
    async def list_suggestions(
        self,
        guild_id: int,
        status: Optional[str] = None,
        user_id: Optional[int] = None,
        limit: int = 50,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        """الحصول على قائمة الاقتراحات"""
        query = {"guild_id": str(guild_id)}
        
        if status:
            query["status"] = status
        
        if user_id:
            query["user_id"] = str(user_id)
        
        cursor = self.suggestions.find(query).sort("created_at", -1).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def get_user_suggestions_count(
        self,
        guild_id: int,
        user_id: int
    ) -> int:
        """عدد اقتراحات المستخدم"""
        return await self.suggestions.count_documents({
            "guild_id": str(guild_id),
            "user_id": str(user_id)
        })
    
    # ============= Voting System =============
    
    async def add_vote(
        self,
        guild_id: int,
        suggestion_id: int,
        user_id: int,
        vote_type: str  # upvote, downvote, neutral
    ) -> Dict[str, Any]:
        """إضافة أو تحديث صوت"""
        
        # التحقق من وجود صوت سابق
        existing_vote = await self.votes.find_one({
            "guild_id": str(guild_id),
            "suggestion_id": suggestion_id,
            "user_id": str(user_id)
        })
        
        if existing_vote:
            old_vote_type = existing_vote["vote_type"]
            
            # تحديث الصوت
            await self.votes.update_one(
                {
                    "guild_id": str(guild_id),
                    "suggestion_id": suggestion_id,
                    "user_id": str(user_id)
                },
                {
                    "$set": {
                        "vote_type": vote_type,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # تحديث العدادات في الاقتراح
            await self._update_vote_counters(guild_id, suggestion_id, old_vote_type, vote_type)
            
            return {"changed": True, "old_vote": old_vote_type, "new_vote": vote_type}
        
        else:
            # إضافة صوت جديد
            vote = {
                "guild_id": str(guild_id),
                "suggestion_id": suggestion_id,
                "user_id": str(user_id),
                "vote_type": vote_type,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            await self.votes.insert_one(vote)
            
            # تحديث العدادات
            await self._update_vote_counters(guild_id, suggestion_id, None, vote_type)
            
            return {"changed": True, "old_vote": None, "new_vote": vote_type}
    
    async def remove_vote(
        self,
        guild_id: int,
        suggestion_id: int,
        user_id: int
    ) -> bool:
        """إزالة صوت"""
        
        # الحصول على الصوت الحالي
        vote = await self.votes.find_one({
            "guild_id": str(guild_id),
            "suggestion_id": suggestion_id,
            "user_id": str(user_id)
        })
        
        if not vote:
            return False
        
        # حذف الصوت
        result = await self.votes.delete_one({
            "guild_id": str(guild_id),
            "suggestion_id": suggestion_id,
            "user_id": str(user_id)
        })
        
        if result.deleted_count > 0:
            # تحديث العدادات
            await self._update_vote_counters(guild_id, suggestion_id, vote["vote_type"], None)
            return True
        
        return False
    
    async def get_user_vote(
        self,
        guild_id: int,
        suggestion_id: int,
        user_id: int
    ) -> Optional[str]:
        """الحصول على صوت المستخدم"""
        vote = await self.votes.find_one({
            "guild_id": str(guild_id),
            "suggestion_id": suggestion_id,
            "user_id": str(user_id)
        })
        
        return vote["vote_type"] if vote else None
    
    async def _update_vote_counters(
        self,
        guild_id: int,
        suggestion_id: int,
        old_vote: Optional[str],
        new_vote: Optional[str]
    ):
        """تحديث عدادات الأصوات"""
        
        update_data = {}
        
        # إزالة الصوت القديم
        if old_vote == "upvote":
            update_data["upvotes"] = -1
        elif old_vote == "downvote":
            update_data["downvotes"] = -1
        elif old_vote == "neutral":
            update_data["neutral_votes"] = -1
        
        # إضافة الصوت الجديد
        if new_vote == "upvote":
            update_data["upvotes"] = update_data.get("upvotes", 0) + 1
        elif new_vote == "downvote":
            update_data["downvotes"] = update_data.get("downvotes", 0) + 1
        elif new_vote == "neutral":
            update_data["neutral_votes"] = update_data.get("neutral_votes", 0) + 1
        
        if update_data:
            await self.suggestions.update_one(
                {
                    "guild_id": str(guild_id),
                    "suggestion_id": suggestion_id
                },
                {
                    "$inc": update_data,
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
    
    # ============= Comments System =============
    
    async def add_comment(
        self,
        guild_id: int,
        suggestion_id: int,
        user_id: int,
        content: str
    ) -> Dict[str, Any]:
        """إضافة تعليق على اقتراح"""
        
        comment = {
            "guild_id": str(guild_id),
            "suggestion_id": suggestion_id,
            "user_id": str(user_id),
            "content": content,
            "created_at": datetime.utcnow(),
            "edited": False,
            "edited_at": None
        }
        
        result = await self.comments.insert_one(comment)
        comment["_id"] = result.inserted_id
        
        return comment
    
    async def get_comments(
        self,
        guild_id: int,
        suggestion_id: int,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """الحصول على تعليقات اقتراح"""
        cursor = self.comments.find({
            "guild_id": str(guild_id),
            "suggestion_id": suggestion_id
        }).sort("created_at", 1).limit(limit)
        
        return await cursor.to_list(length=limit)
    
    async def delete_comment(
        self,
        guild_id: int,
        comment_id: str
    ) -> bool:
        """حذف تعليق"""
        from bson import ObjectId
        
        result = await self.comments.delete_one({
            "guild_id": str(guild_id),
            "_id": ObjectId(comment_id)
        })
        
        return result.deleted_count > 0
    
    # ============= Settings Management =============
    
    async def get_settings(self, guild_id: int) -> Dict[str, Any]:
        """الحصول على إعدادات النظام"""
        settings = await self.settings.find_one({"guild_id": str(guild_id)})
        
        if not settings:
            # الإعدادات الافتراضية
            settings = {
                "guild_id": str(guild_id),
                "enabled": True,
                "suggestions_channel_id": None,
                "review_channel_id": None,
                "staff_role_ids": [],
                
                # Voting settings
                "allow_voting": True,
                "voting_emojis": {
                    "upvote": "👍",
                    "downvote": "👎",
                    "neutral": "🤷"
                },
                
                # Submission settings
                "allow_anonymous": True,
                "require_approval": False,
                "min_suggestion_length": 10,
                "max_suggestion_length": 2000,
                "cooldown_minutes": 10,
                
                # Display settings
                "show_author": True,
                "show_vote_count": True,
                "dm_notifications": True,
                
                # Limits
                "max_suggestions_per_user": 10,  # Free tier
                "max_active_suggestions": 50,
                
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            await self.settings.insert_one(settings)
        
        return settings
    
    async def update_settings(
        self,
        guild_id: int,
        settings_data: Dict[str, Any]
    ) -> bool:
        """تحديث الإعدادات"""
        settings_data["updated_at"] = datetime.utcnow()
        
        result = await self.settings.update_one(
            {"guild_id": str(guild_id)},
            {"$set": settings_data},
            upsert=True
        )
        
        return result.modified_count > 0 or result.upserted_id is not None
    
    # ============= Statistics =============
    
    async def get_statistics(self, guild_id: int) -> Dict[str, Any]:
        """إحصائيات الاقتراحات"""
        
        pipeline = [
            {"$match": {"guild_id": str(guild_id)}},
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }
            }
        ]
        
        status_counts = {}
        async for doc in self.suggestions.aggregate(pipeline):
            status_counts[doc["_id"]] = doc["count"]
        
        total = await self.suggestions.count_documents({"guild_id": str(guild_id)})
        
        # أكثر المستخدمين نشاطاً
        top_users_pipeline = [
            {"$match": {"guild_id": str(guild_id)}},
            {
                "$group": {
                    "_id": "$user_id",
                    "count": {"$sum": 1},
                    "total_upvotes": {"$sum": "$upvotes"}
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        
        top_users = []
        async for doc in self.suggestions.aggregate(top_users_pipeline):
            top_users.append({
                "user_id": doc["_id"],
                "suggestions_count": doc["count"],
                "total_upvotes": doc["total_upvotes"]
            })
        
        return {
            "total_suggestions": total,
            "status_breakdown": status_counts,
            "top_contributors": top_users,
            "total_votes": await self.votes.count_documents({"guild_id": str(guild_id)})
        }
    
    async def get_leaderboard(
        self,
        guild_id: int,
        sort_by: str = "suggestions",  # suggestions, upvotes
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """لوحة المتصدرين"""
        
        if sort_by == "suggestions":
            sort_field = "count"
        else:  # upvotes
            sort_field = "total_upvotes"
        
        pipeline = [
            {"$match": {"guild_id": str(guild_id)}},
            {
                "$group": {
                    "_id": "$user_id",
                    "count": {"$sum": 1},
                    "total_upvotes": {"$sum": "$upvotes"},
                    "total_downvotes": {"$sum": "$downvotes"},
                    "approved_count": {
                        "$sum": {
                            "$cond": [{"$eq": ["$status", "approved"]}, 1, 0]
                        }
                    },
                    "implemented_count": {
                        "$sum": {
                            "$cond": [{"$eq": ["$status", "implemented"]}, 1, 0]
                        }
                    }
                }
            },
            {"$sort": {sort_field: -1}},
            {"$limit": limit}
        ]
        
        leaderboard = []
        async for doc in self.suggestions.aggregate(pipeline):
            leaderboard.append({
                "user_id": doc["_id"],
                "suggestions_count": doc["count"],
                "total_upvotes": doc["total_upvotes"],
                "total_downvotes": doc["total_downvotes"],
                "approved_count": doc["approved_count"],
                "implemented_count": doc["implemented_count"],
                "score": doc["total_upvotes"] - doc["total_downvotes"]
            })
        
        return leaderboard
