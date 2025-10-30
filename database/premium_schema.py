"""
Premium System Database Schema
Handles subscriptions, payments, and premium features

Collections:
- premium_subscriptions: User/Guild subscriptions
- premium_features: Available premium features
- payment_history: Payment transactions
- feature_usage: Feature usage tracking
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
import os

# MongoDB connection
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB", "kingdom77")

class PremiumSchema:
    """Premium database schema and operations"""
    
    def __init__(self, client: AsyncIOMotorClient):
        self.db = client[MONGODB_DB]
        self.subscriptions = self.db.premium_subscriptions
        self.features = self.db.premium_features
        self.payments = self.db.payment_history
        self.usage = self.db.feature_usage
    
    async def initialize(self):
        """Initialize collections and indexes"""
        # Subscriptions indexes
        await self.subscriptions.create_index("user_id")
        await self.subscriptions.create_index("guild_id")
        await self.subscriptions.create_index("status")
        await self.subscriptions.create_index("expires_at")
        await self.subscriptions.create_index([("user_id", 1), ("guild_id", 1)])
        
        # Features indexes
        await self.features.create_index("feature_id", unique=True)
        await self.features.create_index("tier")
        
        # Payments indexes
        await self.payments.create_index("user_id")
        await self.payments.create_index("stripe_payment_id")
        await self.payments.create_index("created_at")
        
        # Usage indexes
        await self.usage.create_index([("guild_id", 1), ("feature_id", 1)])
        await self.usage.create_index("timestamp")
        
        # Initialize default features
        await self.initialize_default_features()
    
    async def initialize_default_features(self):
        """Initialize default premium features"""
        default_features = [
            # Leveling Features
            {
                "feature_id": "xp_boost",
                "name": "XP Boost",
                "description": "2x XP multiplier for all members",
                "tier": "basic",
                "category": "leveling",
                "enabled": True
            },
            {
                "feature_id": "custom_level_card",
                "name": "Custom Level Cards",
                "description": "Customize level up card design and colors",
                "tier": "basic",
                "category": "leveling",
                "enabled": True
            },
            {
                "feature_id": "unlimited_level_roles",
                "name": "Unlimited Level Roles",
                "description": "Create unlimited level role rewards",
                "tier": "basic",
                "category": "leveling",
                "enabled": True
            },
            
            # Moderation Features
            {
                "feature_id": "advanced_automod",
                "name": "Advanced Auto-Moderation",
                "description": "AI-powered content filtering and spam detection",
                "tier": "premium",
                "category": "moderation",
                "enabled": True
            },
            {
                "feature_id": "custom_mod_actions",
                "name": "Custom Mod Actions",
                "description": "Create custom moderation actions and workflows",
                "tier": "premium",
                "category": "moderation",
                "enabled": True
            },
            
            # Ticket Features
            {
                "feature_id": "unlimited_tickets",
                "name": "Unlimited Tickets",
                "description": "Remove ticket limits and create unlimited categories",
                "tier": "basic",
                "category": "tickets",
                "enabled": True
            },
            {
                "feature_id": "ticket_analytics",
                "name": "Ticket Analytics",
                "description": "Detailed analytics and reporting for tickets",
                "tier": "premium",
                "category": "tickets",
                "enabled": True
            },
            
            # Dashboard Features
            {
                "feature_id": "advanced_dashboard",
                "name": "Advanced Dashboard",
                "description": "Access to advanced dashboard features and analytics",
                "tier": "basic",
                "category": "dashboard",
                "enabled": True
            },
            {
                "feature_id": "custom_branding",
                "name": "Custom Branding",
                "description": "Remove bot branding and add your own",
                "tier": "premium",
                "category": "dashboard",
                "enabled": True
            },
            
            # General Features
            {
                "feature_id": "priority_support",
                "name": "Priority Support",
                "description": "Get priority support from the team",
                "tier": "basic",
                "category": "support",
                "enabled": True
            },
            {
                "feature_id": "custom_commands",
                "name": "Custom Commands",
                "description": "Create unlimited custom commands",
                "tier": "premium",
                "category": "general",
                "enabled": True
            },
            {
                "feature_id": "api_access",
                "name": "API Access",
                "description": "Access to developer API",
                "tier": "enterprise",
                "category": "developer",
                "enabled": True
            }
        ]
        
        for feature in default_features:
            await self.features.update_one(
                {"feature_id": feature["feature_id"]},
                {"$set": feature},
                upsert=True
            )
    
    # Subscription Operations
    
    async def create_subscription(
        self,
        user_id: str,
        guild_id: str,
        tier: str,
        duration_days: int,
        stripe_subscription_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new premium subscription"""
        now = datetime.utcnow()
        expires_at = now + timedelta(days=duration_days)
        
        subscription = {
            "user_id": user_id,
            "guild_id": guild_id,
            "tier": tier,  # basic, premium, enterprise
            "status": "active",
            "created_at": now,
            "expires_at": expires_at,
            "stripe_subscription_id": stripe_subscription_id,
            "auto_renew": True if stripe_subscription_id else False,
            "features": await self.get_tier_features(tier),
            "metadata": {}
        }
        
        result = await self.subscriptions.insert_one(subscription)
        subscription["_id"] = result.inserted_id
        return subscription
    
    async def get_subscription(self, user_id: str, guild_id: str) -> Optional[Dict[str, Any]]:
        """Get active subscription for user/guild"""
        return await self.subscriptions.find_one({
            "user_id": user_id,
            "guild_id": guild_id,
            "status": "active",
            "expires_at": {"$gt": datetime.utcnow()}
        })
    
    async def get_guild_subscription(self, guild_id: str) -> Optional[Dict[str, Any]]:
        """Get active subscription for guild"""
        return await self.subscriptions.find_one({
            "guild_id": guild_id,
            "status": "active",
            "expires_at": {"$gt": datetime.utcnow()}
        })
    
    async def update_subscription_status(
        self,
        subscription_id: str,
        status: str
    ) -> bool:
        """Update subscription status"""
        from bson import ObjectId
        result = await self.subscriptions.update_one(
            {"_id": ObjectId(subscription_id)},
            {"$set": {"status": status, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0
    
    async def renew_subscription(
        self,
        subscription_id: str,
        duration_days: int
    ) -> bool:
        """Renew subscription"""
        from bson import ObjectId
        subscription = await self.subscriptions.find_one({"_id": ObjectId(subscription_id)})
        if not subscription:
            return False
        
        new_expires_at = subscription["expires_at"] + timedelta(days=duration_days)
        result = await self.subscriptions.update_one(
            {"_id": ObjectId(subscription_id)},
            {
                "$set": {
                    "expires_at": new_expires_at,
                    "status": "active",
                    "updated_at": datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0
    
    async def cancel_subscription(self, subscription_id: str) -> bool:
        """Cancel subscription"""
        from bson import ObjectId
        result = await self.subscriptions.update_one(
            {"_id": ObjectId(subscription_id)},
            {
                "$set": {
                    "status": "cancelled",
                    "auto_renew": False,
                    "cancelled_at": datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0
    
    # Feature Operations
    
    async def get_tier_features(self, tier: str) -> List[str]:
        """Get all features for a tier"""
        features = []
        
        # Basic tier includes basic features
        if tier in ["basic", "premium", "enterprise"]:
            basic_features = await self.features.find({
                "tier": "basic",
                "enabled": True
            }).to_list(None)
            features.extend([f["feature_id"] for f in basic_features])
        
        # Premium tier includes premium features
        if tier in ["premium", "enterprise"]:
            premium_features = await self.features.find({
                "tier": "premium",
                "enabled": True
            }).to_list(None)
            features.extend([f["feature_id"] for f in premium_features])
        
        # Enterprise tier includes all features
        if tier == "enterprise":
            enterprise_features = await self.features.find({
                "tier": "enterprise",
                "enabled": True
            }).to_list(None)
            features.extend([f["feature_id"] for f in enterprise_features])
        
        return list(set(features))
    
    async def has_feature(
        self,
        guild_id: str,
        feature_id: str
    ) -> bool:
        """Check if guild has access to a feature"""
        subscription = await self.get_guild_subscription(guild_id)
        if not subscription:
            return False
        
        return feature_id in subscription.get("features", [])
    
    async def get_all_features(self) -> List[Dict[str, Any]]:
        """Get all available features"""
        return await self.features.find({"enabled": True}).to_list(None)
    
    async def get_features_by_tier(self, tier: str) -> List[Dict[str, Any]]:
        """Get features by tier"""
        return await self.features.find({
            "tier": tier,
            "enabled": True
        }).to_list(None)
    
    # Payment Operations
    
    async def record_payment(
        self,
        user_id: str,
        guild_id: str,
        amount: float,
        currency: str,
        tier: str,
        stripe_payment_id: str,
        status: str = "completed"
    ) -> Dict[str, Any]:
        """Record a payment transaction"""
        payment = {
            "user_id": user_id,
            "guild_id": guild_id,
            "amount": amount,
            "currency": currency,
            "tier": tier,
            "stripe_payment_id": stripe_payment_id,
            "status": status,
            "created_at": datetime.utcnow(),
            "metadata": {}
        }
        
        result = await self.payments.insert_one(payment)
        payment["_id"] = result.inserted_id
        return payment
    
    async def get_payment_history(
        self,
        user_id: Optional[str] = None,
        guild_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get payment history"""
        query = {}
        if user_id:
            query["user_id"] = user_id
        if guild_id:
            query["guild_id"] = guild_id
        
        return await self.payments.find(query).sort(
            "created_at", -1
        ).limit(limit).to_list(limit)
    
    # Usage Tracking
    
    async def track_feature_usage(
        self,
        guild_id: str,
        feature_id: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """Track feature usage"""
        usage = {
            "guild_id": guild_id,
            "feature_id": feature_id,
            "user_id": user_id,
            "timestamp": datetime.utcnow(),
            "metadata": metadata or {}
        }
        
        await self.usage.insert_one(usage)
    
    async def get_feature_usage_stats(
        self,
        guild_id: str,
        days: int = 30
    ) -> Dict[str, int]:
        """Get feature usage statistics"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        pipeline = [
            {
                "$match": {
                    "guild_id": guild_id,
                    "timestamp": {"$gte": start_date}
                }
            },
            {
                "$group": {
                    "_id": "$feature_id",
                    "count": {"$sum": 1}
                }
            }
        ]
        
        results = await self.usage.aggregate(pipeline).to_list(None)
        return {item["_id"]: item["count"] for item in results}
    
    # Cleanup Operations
    
    async def cleanup_expired_subscriptions(self):
        """Mark expired subscriptions as inactive"""
        result = await self.subscriptions.update_many(
            {
                "status": "active",
                "expires_at": {"$lt": datetime.utcnow()}
            },
            {
                "$set": {
                    "status": "expired",
                    "updated_at": datetime.utcnow()
                }
            }
        )
        return result.modified_count
    
    # Statistics
    
    async def get_subscription_stats(self) -> Dict[str, Any]:
        """Get subscription statistics"""
        total = await self.subscriptions.count_documents({})
        active = await self.subscriptions.count_documents({
            "status": "active",
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        by_tier = {}
        for tier in ["basic", "premium", "enterprise"]:
            count = await self.subscriptions.count_documents({
                "tier": tier,
                "status": "active",
                "expires_at": {"$gt": datetime.utcnow()}
            })
            by_tier[tier] = count
        
        return {
            "total": total,
            "active": active,
            "by_tier": by_tier
        }


# Pricing Configuration
PREMIUM_TIERS = {
    "basic": {
        "name": "Basic",
        "price_monthly": 0,  # Free
        "price_yearly": 0,   # Free
        "features": [
            "unlimited_level_roles",
            "unlimited_tickets",
            "advanced_dashboard",
            "priority_support"
        ],
        "limits": {
            "max_custom_commands": 10,
            "max_autoroles": 20
        }
    },
    "premium": {
        "name": "Premium",
        "price_monthly": 9.99,
        "price_yearly": 99.99,
        "features": [
            # All Basic features +
            "xp_boost",
            "custom_level_card",
            "advanced_automod",
            "custom_mod_actions",
            "ticket_analytics",
            "custom_branding",
            "custom_commands",
            "api_access",
            "dedicated_support",
            "custom_integrations"
        ],
        "limits": {
            "max_custom_commands": -1,  # Unlimited
            "max_autoroles": -1  # Unlimited
        }
    }
}
