"""
Giveaways Database Schema - Kingdom-77 Bot
MongoDB collections and operations for giveaway system.
"""

from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import random


class GiveawaysSchema:
    """Database schema for giveaways system"""
    
    def __init__(self, db):
        self.db = db
        self.giveaways = db.giveaways
        self.giveaway_entries = db.giveaway_entries
        self.giveaway_winners = db.giveaway_winners
    
    # ============= Giveaways Collection =============
    
    async def create_giveaway(
        self,
        guild_id: int,
        channel_id: int,
        message_id: int,
        host_id: int,
        prize: str,
        winners_count: int,
        end_time: datetime,
        requirements: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Create a new giveaway"""
        document = {
            "guild_id": guild_id,
            "channel_id": channel_id,
            "message_id": message_id,
            "host_id": host_id,
            "prize": prize,
            "description": None,
            "winners_count": winners_count,
            "end_time": end_time,
            "requirements": requirements or {},
            "status": "active",  # active, ended, cancelled
            "entries_count": 0,
            "created_at": datetime.now(),
            "ended_at": None,
            "winners": [],
            "settings": {
                "allow_host": False,  # Can host enter?
                "ping_winners": True,
                "dm_winners": True,
                "show_entries": True
            }
        }
        
        return await self.giveaways.insert_one(document)
    
    async def get_giveaway(self, guild_id: int, message_id: int) -> Optional[Dict[str, Any]]:
        """Get giveaway by message ID"""
        return await self.giveaways.find_one({
            "guild_id": guild_id,
            "message_id": message_id
        })
    
    async def get_giveaway_by_id(self, giveaway_id: str) -> Optional[Dict[str, Any]]:
        """Get giveaway by ID"""
        from bson import ObjectId
        return await self.giveaways.find_one({"_id": ObjectId(giveaway_id)})
    
    async def get_active_giveaways(self, guild_id: int) -> List[Dict[str, Any]]:
        """Get all active giveaways in guild"""
        cursor = self.giveaways.find({
            "guild_id": guild_id,
            "status": "active"
        }).sort("end_time", 1)
        
        return await cursor.to_list(None)
    
    async def get_all_giveaways(
        self,
        guild_id: int,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get giveaways with optional status filter"""
        query = {"guild_id": guild_id}
        
        if status:
            query["status"] = status
        
        cursor = self.giveaways.find(query).sort("created_at", -1).limit(limit)
        return await cursor.to_list(limit)
    
    async def update_giveaway(
        self,
        guild_id: int,
        message_id: int,
        updates: Dict[str, Any]
    ) -> Any:
        """Update giveaway"""
        updates["updated_at"] = datetime.now()
        
        return await self.giveaways.update_one(
            {"guild_id": guild_id, "message_id": message_id},
            {"$set": updates}
        )
    
    async def end_giveaway(
        self,
        guild_id: int,
        message_id: int,
        winners: List[int]
    ) -> Any:
        """Mark giveaway as ended"""
        return await self.giveaways.update_one(
            {"guild_id": guild_id, "message_id": message_id},
            {
                "$set": {
                    "status": "ended",
                    "ended_at": datetime.now(),
                    "winners": winners
                }
            }
        )
    
    async def cancel_giveaway(self, guild_id: int, message_id: int) -> Any:
        """Cancel giveaway"""
        return await self.giveaways.update_one(
            {"guild_id": guild_id, "message_id": message_id},
            {
                "$set": {
                    "status": "cancelled",
                    "ended_at": datetime.now()
                }
            }
        )
    
    async def delete_giveaway(self, guild_id: int, message_id: int) -> Any:
        """Delete giveaway and all related data"""
        # Delete entries
        await self.giveaway_entries.delete_many({
            "guild_id": guild_id,
            "message_id": message_id
        })
        
        # Delete winners
        await self.giveaway_winners.delete_many({
            "guild_id": guild_id,
            "message_id": message_id
        })
        
        # Delete giveaway
        return await self.giveaways.delete_one({
            "guild_id": guild_id,
            "message_id": message_id
        })
    
    async def increment_entries(self, guild_id: int, message_id: int) -> Any:
        """Increment entries count"""
        return await self.giveaways.update_one(
            {"guild_id": guild_id, "message_id": message_id},
            {"$inc": {"entries_count": 1}}
        )
    
    async def decrement_entries(self, guild_id: int, message_id: int) -> Any:
        """Decrement entries count"""
        return await self.giveaways.update_one(
            {"guild_id": guild_id, "message_id": message_id},
            {"$inc": {"entries_count": -1}}
        )
    
    # ============= Giveaway Entries Collection =============
    
    async def add_entry(
        self,
        guild_id: int,
        message_id: int,
        user_id: int,
        entry_data: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Add user entry to giveaway"""
        document = {
            "guild_id": guild_id,
            "message_id": message_id,
            "user_id": user_id,
            "entered_at": datetime.now(),
            "entry_data": entry_data or {}
        }
        
        result = await self.giveaway_entries.insert_one(document)
        
        # Increment entries count
        await self.increment_entries(guild_id, message_id)
        
        return result
    
    async def remove_entry(self, guild_id: int, message_id: int, user_id: int) -> Any:
        """Remove user entry from giveaway"""
        result = await self.giveaway_entries.delete_one({
            "guild_id": guild_id,
            "message_id": message_id,
            "user_id": user_id
        })
        
        if result.deleted_count > 0:
            # Decrement entries count
            await self.decrement_entries(guild_id, message_id)
        
        return result
    
    async def has_entered(self, guild_id: int, message_id: int, user_id: int) -> bool:
        """Check if user has entered giveaway"""
        entry = await self.giveaway_entries.find_one({
            "guild_id": guild_id,
            "message_id": message_id,
            "user_id": user_id
        })
        
        return entry is not None
    
    async def get_entries(self, guild_id: int, message_id: int) -> List[Dict[str, Any]]:
        """Get all entries for giveaway"""
        cursor = self.giveaway_entries.find({
            "guild_id": guild_id,
            "message_id": message_id
        })
        
        return await cursor.to_list(None)
    
    async def get_entries_count(self, guild_id: int, message_id: int) -> int:
        """Get count of entries"""
        return await self.giveaway_entries.count_documents({
            "guild_id": guild_id,
            "message_id": message_id
        })
    
    async def get_user_entries(self, guild_id: int, user_id: int) -> List[Dict[str, Any]]:
        """Get all giveaways user has entered"""
        cursor = self.giveaway_entries.find({
            "guild_id": guild_id,
            "user_id": user_id
        })
        
        return await cursor.to_list(None)
    
    # ============= Giveaway Winners Collection =============
    
    async def add_winner(
        self,
        guild_id: int,
        message_id: int,
        user_id: int,
        prize: str,
        claimed: bool = False
    ) -> Any:
        """Add giveaway winner"""
        document = {
            "guild_id": guild_id,
            "message_id": message_id,
            "user_id": user_id,
            "prize": prize,
            "won_at": datetime.now(),
            "claimed": claimed,
            "notified": False
        }
        
        return await self.giveaway_winners.insert_one(document)
    
    async def get_winners(self, guild_id: int, message_id: int) -> List[Dict[str, Any]]:
        """Get winners of giveaway"""
        cursor = self.giveaway_winners.find({
            "guild_id": guild_id,
            "message_id": message_id
        })
        
        return await cursor.to_list(None)
    
    async def get_user_wins(self, guild_id: int, user_id: int) -> List[Dict[str, Any]]:
        """Get all giveaways user has won"""
        cursor = self.giveaway_winners.find({
            "guild_id": guild_id,
            "user_id": user_id
        }).sort("won_at", -1)
        
        return await cursor.to_list(None)
    
    async def mark_winner_notified(self, guild_id: int, message_id: int, user_id: int) -> Any:
        """Mark winner as notified"""
        return await self.giveaway_winners.update_one(
            {
                "guild_id": guild_id,
                "message_id": message_id,
                "user_id": user_id
            },
            {"$set": {"notified": True}}
        )
    
    async def mark_prize_claimed(self, guild_id: int, message_id: int, user_id: int) -> Any:
        """Mark prize as claimed"""
        return await self.giveaway_winners.update_one(
            {
                "guild_id": guild_id,
                "message_id": message_id,
                "user_id": user_id
            },
            {"$set": {"claimed": True, "claimed_at": datetime.now()}}
        )
    
    # ============= Statistics & Analytics =============
    
    async def get_guild_statistics(
        self,
        guild_id: int,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get giveaway statistics for guild"""
        since = datetime.now() - timedelta(days=days)
        
        # Count giveaways by status
        total = await self.giveaways.count_documents({
            "guild_id": guild_id,
            "created_at": {"$gte": since}
        })
        
        active = await self.giveaways.count_documents({
            "guild_id": guild_id,
            "status": "active"
        })
        
        ended = await self.giveaways.count_documents({
            "guild_id": guild_id,
            "status": "ended",
            "created_at": {"$gte": since}
        })
        
        cancelled = await self.giveaways.count_documents({
            "guild_id": guild_id,
            "status": "cancelled",
            "created_at": {"$gte": since}
        })
        
        # Total entries and winners
        total_entries = await self.giveaway_entries.count_documents({
            "guild_id": guild_id
        })
        
        total_winners = await self.giveaway_winners.count_documents({
            "guild_id": guild_id
        })
        
        # Most active participants
        pipeline = [
            {"$match": {"guild_id": guild_id}},
            {"$group": {
                "_id": "$user_id",
                "entries": {"$sum": 1}
            }},
            {"$sort": {"entries": -1}},
            {"$limit": 10}
        ]
        
        top_participants = await self.giveaway_entries.aggregate(pipeline).to_list(10)
        
        return {
            "total_giveaways": total,
            "active_giveaways": active,
            "ended_giveaways": ended,
            "cancelled_giveaways": cancelled,
            "total_entries": total_entries,
            "total_winners": total_winners,
            "avg_entries_per_giveaway": total_entries / total if total > 0 else 0,
            "top_participants": [
                {
                    "user_id": str(p["_id"]),
                    "entries": p["entries"]
                }
                for p in top_participants
            ],
            "period_days": days
        }
    
    async def get_user_statistics(
        self,
        guild_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """Get giveaway statistics for user"""
        # Count entries
        entries_count = await self.giveaway_entries.count_documents({
            "guild_id": guild_id,
            "user_id": user_id
        })
        
        # Count wins
        wins_count = await self.giveaway_winners.count_documents({
            "guild_id": guild_id,
            "user_id": user_id
        })
        
        # Win rate
        win_rate = (wins_count / entries_count * 100) if entries_count > 0 else 0
        
        # Recent entries
        recent_entries = await self.giveaway_entries.find({
            "guild_id": guild_id,
            "user_id": user_id
        }).sort("entered_at", -1).limit(5).to_list(5)
        
        # Recent wins
        recent_wins = await self.giveaway_winners.find({
            "guild_id": guild_id,
            "user_id": user_id
        }).sort("won_at", -1).limit(5).to_list(5)
        
        return {
            "total_entries": entries_count,
            "total_wins": wins_count,
            "win_rate": round(win_rate, 2),
            "recent_entries": [
                {
                    "message_id": str(e["message_id"]),
                    "entered_at": e["entered_at"].isoformat()
                }
                for e in recent_entries
            ],
            "recent_wins": [
                {
                    "message_id": str(w["message_id"]),
                    "prize": w["prize"],
                    "won_at": w["won_at"].isoformat(),
                    "claimed": w.get("claimed", False)
                }
                for w in recent_wins
            ]
        }
    
    # ============= Cleanup & Maintenance =============
    
    async def cleanup_old_giveaways(self, days: int = 90) -> int:
        """Delete giveaways older than specified days"""
        cutoff = datetime.now() - timedelta(days=days)
        
        # Find old giveaways
        old_giveaways = await self.giveaways.find({
            "status": {"$in": ["ended", "cancelled"]},
            "ended_at": {"$lt": cutoff}
        }).to_list(None)
        
        count = 0
        for giveaway in old_giveaways:
            await self.delete_giveaway(
                giveaway["guild_id"],
                giveaway["message_id"]
            )
            count += 1
        
        return count
    
    async def get_ended_giveaways(self) -> List[Dict[str, Any]]:
        """Get giveaways that should be ended"""
        cursor = self.giveaways.find({
            "status": "active",
            "end_time": {"$lte": datetime.now()}
        })
        
        return await cursor.to_list(None)
