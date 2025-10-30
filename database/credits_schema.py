"""
Kingdom-77 Bot v3.8 - Credits & Economy System Database Schema

This module defines the MongoDB collections and schemas for the K77 Credits economy system.

Collections:
- user_credits: User credit balances and settings
- credit_transactions: All credit transactions history
- shop_items: Available items in the shop (frames, badges, banners, themes)
- user_inventory: Items owned by users
- daily_claims: Daily claim tracking
- credit_packages: Credit purchase packages with bonuses

Author: Kingdom-77 Team
Date: 2024
"""

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB Connection
MONGO_URI = os.getenv('MONGO_URI')
client = AsyncIOMotorClient(MONGO_URI)
db = client['kingdom77']

# Collections
user_credits_collection = db['user_credits']
credit_transactions_collection = db['credit_transactions']
shop_items_collection = db['shop_items']
user_inventory_collection = db['user_inventory']
daily_claims_collection = db['daily_claims']
credit_packages_collection = db['credit_packages']


# ============================================================
# CREDIT PACKAGES CONFIGURATION
# ============================================================

CREDIT_PACKAGES = [
    {
        "package_id": "starter",
        "name": "Starter Pack",
        "name_ar": "حزمة المبتدئين",
        "base_credits": 500,
        "bonus_credits": 100,
        "total_credits": 600,
        "price_usd": 4.99,
        "price_sar": 18.70,
        "popular": False,
        "emoji": "🎯"
    },
    {
        "package_id": "value",
        "name": "Value Pack",
        "name_ar": "حزمة القيمة",
        "base_credits": 1000,
        "bonus_credits": 300,
        "total_credits": 1300,
        "price_usd": 9.99,
        "price_sar": 37.46,
        "popular": True,
        "emoji": "💎"
    },
    {
        "package_id": "mega",
        "name": "Mega Pack",
        "name_ar": "الحزمة الضخمة",
        "base_credits": 2000,
        "bonus_credits": 800,
        "total_credits": 2800,
        "price_usd": 19.99,
        "price_sar": 74.96,
        "popular": False,
        "emoji": "⚡"
    },
    {
        "package_id": "ultimate",
        "name": "Ultimate Pack",
        "name_ar": "الحزمة النهائية",
        "base_credits": 5000,
        "bonus_credits": 2000,
        "total_credits": 7000,
        "price_usd": 49.90,
        "price_sar": 187.13,
        "popular": False,
        "emoji": "❄️",
        "badge": "BEST VALUE"
    }
]


# ============================================================
# SHOP ITEMS CONFIGURATION
# ============================================================

SHOP_ITEMS = {
    "frames": [
        {
            "item_id": "frame_gold",
            "name": "Golden Frame",
            "name_ar": "إطار ذهبي",
            "description": "Luxurious golden border for your level card",
            "description_ar": "إطار ذهبي فاخر لبطاقة المستوى",
            "type": "frame",
            "price": 500,
            "rarity": "epic",
            "preview_url": "https://example.com/frames/gold.png",
            "color": "#FFD700",
            "emoji": "👑"
        },
        {
            "item_id": "frame_diamond",
            "name": "Diamond Frame",
            "name_ar": "إطار الماس",
            "description": "Rare diamond border with sparkle effects",
            "description_ar": "إطار ماسي نادر مع تأثيرات لامعة",
            "type": "frame",
            "price": 1000,
            "rarity": "legendary",
            "preview_url": "https://example.com/frames/diamond.png",
            "color": "#B9F2FF",
            "emoji": "💎"
        },
        {
            "item_id": "frame_fire",
            "name": "Fire Frame",
            "name_ar": "إطار ناري",
            "description": "Blazing fire border",
            "description_ar": "إطار ناري ملتهب",
            "type": "frame",
            "price": 750,
            "rarity": "epic",
            "preview_url": "https://example.com/frames/fire.png",
            "color": "#FF4500",
            "emoji": "🔥"
        },
        {
            "item_id": "frame_ice",
            "name": "Ice Frame",
            "name_ar": "إطار جليدي",
            "description": "Frozen ice border",
            "description_ar": "إطار جليدي متجمد",
            "type": "frame",
            "price": 750,
            "rarity": "epic",
            "preview_url": "https://example.com/frames/ice.png",
            "color": "#00CED1",
            "emoji": "❄️"
        }
    ],
    "badges": [
        {
            "item_id": "badge_vip",
            "name": "VIP Badge",
            "name_ar": "شارة VIP",
            "description": "Exclusive VIP status badge",
            "description_ar": "شارة حالة VIP حصرية",
            "type": "badge",
            "price": 300,
            "rarity": "rare",
            "preview_url": "https://example.com/badges/vip.png",
            "emoji": "⭐"
        },
        {
            "item_id": "badge_king",
            "name": "King Badge",
            "name_ar": "شارة الملك",
            "description": "Royal crown badge",
            "description_ar": "شارة التاج الملكي",
            "type": "badge",
            "price": 800,
            "rarity": "legendary",
            "preview_url": "https://example.com/badges/king.png",
            "emoji": "👑"
        },
        {
            "item_id": "badge_supporter",
            "name": "Supporter Badge",
            "name_ar": "شارة الداعم",
            "description": "Thank you for supporting Kingdom-77!",
            "description_ar": "شكراً لدعمك Kingdom-77!",
            "type": "badge",
            "price": 250,
            "rarity": "common",
            "preview_url": "https://example.com/badges/supporter.png",
            "emoji": "💖"
        }
    ],
    "banners": [
        {
            "item_id": "banner_sunset",
            "name": "Sunset Banner",
            "name_ar": "خلفية الغروب",
            "description": "Beautiful sunset background",
            "description_ar": "خلفية غروب جميلة",
            "type": "banner",
            "price": 400,
            "rarity": "rare",
            "preview_url": "https://example.com/banners/sunset.png",
            "emoji": "🌅"
        },
        {
            "item_id": "banner_galaxy",
            "name": "Galaxy Banner",
            "name_ar": "خلفية المجرة",
            "description": "Cosmic galaxy background",
            "description_ar": "خلفية مجرة كونية",
            "type": "banner",
            "price": 600,
            "rarity": "epic",
            "preview_url": "https://example.com/banners/galaxy.png",
            "emoji": "🌌"
        },
        {
            "item_id": "banner_ocean",
            "name": "Ocean Banner",
            "name_ar": "خلفية المحيط",
            "description": "Calm ocean waves background",
            "description_ar": "خلفية أمواج محيط هادئة",
            "type": "banner",
            "price": 400,
            "rarity": "rare",
            "preview_url": "https://example.com/banners/ocean.png",
            "emoji": "🌊"
        }
    ],
    "themes": [
        {
            "item_id": "theme_cyberpunk",
            "name": "Cyberpunk Theme",
            "name_ar": "ثيم سايبربنك",
            "description": "Futuristic cyberpunk level card design",
            "description_ar": "تصميم بطاقة مستوى مستقبلي سايبربنك",
            "type": "theme",
            "price": 1200,
            "rarity": "legendary",
            "preview_url": "https://example.com/themes/cyberpunk.png",
            "emoji": "🤖"
        },
        {
            "item_id": "theme_fantasy",
            "name": "Fantasy Theme",
            "name_ar": "ثيم خيالي",
            "description": "Magical fantasy level card design",
            "description_ar": "تصميم بطاقة مستوى خيالي سحري",
            "type": "theme",
            "price": 1000,
            "rarity": "epic",
            "preview_url": "https://example.com/themes/fantasy.png",
            "emoji": "🧙"
        }
    ]
}


# ============================================================
# DAILY CLAIM CONFIGURATION
# ============================================================

DAILY_CLAIM_MIN = 5
DAILY_CLAIM_MAX = 10
DAILY_CLAIM_COOLDOWN_HOURS = 24


# ============================================================
# PREMIUM COSTS (Credits)
# ============================================================

PREMIUM_COSTS = {
    "monthly": 500,      # 500 credits for 1 month premium
    "yearly": 5000       # 5000 credits for 12 months premium (save 1000 vs monthly)
}


# ============================================================
# DATABASE SCHEMAS
# ============================================================

class UserCredits:
    """User credits balance and settings."""
    
    @staticmethod
    async def create_indexes():
        """Create necessary indexes for user_credits collection."""
        await user_credits_collection.create_index("user_id", unique=True)
        await user_credits_collection.create_index("last_daily_claim")
    
    @staticmethod
    async def get_user(user_id: int) -> Optional[Dict[str, Any]]:
        """Get user credits data."""
        return await user_credits_collection.find_one({"user_id": user_id})
    
    @staticmethod
    async def create_user(user_id: int, username: str) -> Dict[str, Any]:
        """Create new user credits account."""
        user_data = {
            "user_id": user_id,
            "username": username,
            "balance": 0,
            "total_earned": 0,
            "total_spent": 0,
            "total_purchased": 0,
            "last_daily_claim": None,
            "daily_claim_streak": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        await user_credits_collection.insert_one(user_data)
        return user_data
    
    @staticmethod
    async def get_or_create_user(user_id: int, username: str) -> Dict[str, Any]:
        """Get existing user or create new one."""
        user = await UserCredits.get_user(user_id)
        if not user:
            user = await UserCredits.create_user(user_id, username)
        return user
    
    @staticmethod
    async def update_balance(user_id: int, amount: int) -> bool:
        """Update user balance (can be positive or negative)."""
        result = await user_credits_collection.update_one(
            {"user_id": user_id},
            {
                "$inc": {"balance": amount},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        return result.modified_count > 0
    
    @staticmethod
    async def update_daily_claim(user_id: int, amount: int) -> bool:
        """Update last daily claim time and streak."""
        user = await UserCredits.get_user(user_id)
        if not user:
            return False
        
        # Check if streak continues (claimed within 48 hours)
        streak = user.get('daily_claim_streak', 0)
        last_claim = user.get('last_daily_claim')
        
        if last_claim:
            hours_since_claim = (datetime.utcnow() - last_claim).total_seconds() / 3600
            if hours_since_claim < 48:
                streak += 1
            else:
                streak = 1
        else:
            streak = 1
        
        result = await user_credits_collection.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "last_daily_claim": datetime.utcnow(),
                    "daily_claim_streak": streak,
                    "updated_at": datetime.utcnow()
                },
                "$inc": {
                    "balance": amount,
                    "total_earned": amount
                }
            }
        )
        return result.modified_count > 0


class CreditTransaction:
    """Credit transaction history."""
    
    @staticmethod
    async def create_indexes():
        """Create necessary indexes for transactions collection."""
        await credit_transactions_collection.create_index("user_id")
        await credit_transactions_collection.create_index("transaction_type")
        await credit_transactions_collection.create_index("created_at")
    
    @staticmethod
    async def create_transaction(
        user_id: int,
        transaction_type: str,
        amount: int,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new transaction.
        
        Types: daily_claim, purchase, spend, gift_sent, gift_received, 
               premium_purchase, shop_purchase, transfer_sent, transfer_received
        """
        transaction = {
            "user_id": user_id,
            "transaction_type": transaction_type,
            "amount": amount,
            "description": description,
            "metadata": metadata or {},
            "created_at": datetime.utcnow()
        }
        result = await credit_transactions_collection.insert_one(transaction)
        transaction['_id'] = result.inserted_id
        return transaction
    
    @staticmethod
    async def get_user_transactions(
        user_id: int,
        limit: int = 50,
        transaction_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get user's transaction history."""
        query = {"user_id": user_id}
        if transaction_type:
            query["transaction_type"] = transaction_type
        
        cursor = credit_transactions_collection.find(query).sort("created_at", -1).limit(limit)
        return await cursor.to_list(length=limit)


class ShopItem:
    """Shop items management."""
    
    @staticmethod
    async def create_indexes():
        """Create necessary indexes for shop_items collection."""
        await shop_items_collection.create_index("item_id", unique=True)
        await shop_items_collection.create_index("type")
        await shop_items_collection.create_index("rarity")
    
    @staticmethod
    async def initialize_shop():
        """Initialize shop with default items."""
        for category, items in SHOP_ITEMS.items():
            for item in items:
                existing = await shop_items_collection.find_one({"item_id": item['item_id']})
                if not existing:
                    item['enabled'] = True
                    item['stock'] = -1  # -1 means unlimited
                    item['total_sales'] = 0
                    item['created_at'] = datetime.utcnow()
                    await shop_items_collection.insert_one(item)
    
    @staticmethod
    async def get_all_items(item_type: Optional[str] = None, enabled_only: bool = True) -> List[Dict[str, Any]]:
        """Get all shop items, optionally filtered by type."""
        query = {}
        if item_type:
            query['type'] = item_type
        if enabled_only:
            query['enabled'] = True
        
        cursor = shop_items_collection.find(query).sort("price", 1)
        return await cursor.to_list(length=None)
    
    @staticmethod
    async def get_item(item_id: str) -> Optional[Dict[str, Any]]:
        """Get specific item by ID."""
        return await shop_items_collection.find_one({"item_id": item_id})
    
    @staticmethod
    async def increment_sales(item_id: str) -> bool:
        """Increment item sales count."""
        result = await shop_items_collection.update_one(
            {"item_id": item_id},
            {"$inc": {"total_sales": 1}}
        )
        return result.modified_count > 0


class UserInventory:
    """User inventory management."""
    
    @staticmethod
    async def create_indexes():
        """Create necessary indexes for user_inventory collection."""
        await user_inventory_collection.create_index([("user_id", 1), ("item_id", 1)], unique=True)
        await user_inventory_collection.create_index("user_id")
    
    @staticmethod
    async def add_item(user_id: int, item_id: str, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add item to user inventory."""
        inventory_item = {
            "user_id": user_id,
            "item_id": item_id,
            "item_name": item_data.get('name', 'Unknown'),
            "item_type": item_data.get('type', 'unknown'),
            "equipped": False,
            "acquired_at": datetime.utcnow()
        }
        
        try:
            await user_inventory_collection.insert_one(inventory_item)
            return inventory_item
        except Exception:
            # Item already exists
            return await user_inventory_collection.find_one({"user_id": user_id, "item_id": item_id})
    
    @staticmethod
    async def has_item(user_id: int, item_id: str) -> bool:
        """Check if user owns an item."""
        item = await user_inventory_collection.find_one({"user_id": user_id, "item_id": item_id})
        return item is not None
    
    @staticmethod
    async def get_user_inventory(user_id: int, item_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get user's inventory."""
        query = {"user_id": user_id}
        if item_type:
            query['item_type'] = item_type
        
        cursor = user_inventory_collection.find(query).sort("acquired_at", -1)
        return await cursor.to_list(length=None)
    
    @staticmethod
    async def equip_item(user_id: int, item_id: str, item_type: str) -> bool:
        """Equip an item (unequip others of same type)."""
        # Unequip all items of same type
        await user_inventory_collection.update_many(
            {"user_id": user_id, "item_type": item_type},
            {"$set": {"equipped": False}}
        )
        
        # Equip the selected item
        result = await user_inventory_collection.update_one(
            {"user_id": user_id, "item_id": item_id},
            {"$set": {"equipped": True}}
        )
        return result.modified_count > 0
    
    @staticmethod
    async def get_equipped_items(user_id: int) -> Dict[str, Dict[str, Any]]:
        """Get all equipped items by type."""
        cursor = user_inventory_collection.find({"user_id": user_id, "equipped": True})
        items = await cursor.to_list(length=None)
        
        equipped = {}
        for item in items:
            equipped[item['item_type']] = item
        return equipped


class CreditPackage:
    """Credit packages management."""
    
    @staticmethod
    async def create_indexes():
        """Create necessary indexes for credit_packages collection."""
        await credit_packages_collection.create_index("package_id", unique=True)
    
    @staticmethod
    async def initialize_packages():
        """Initialize credit packages."""
        for package in CREDIT_PACKAGES:
            existing = await credit_packages_collection.find_one({"package_id": package['package_id']})
            if not existing:
                package['enabled'] = True
                package['total_sales'] = 0
                package['created_at'] = datetime.utcnow()
                await credit_packages_collection.insert_one(package)
    
    @staticmethod
    async def get_all_packages() -> List[Dict[str, Any]]:
        """Get all credit packages."""
        cursor = credit_packages_collection.find({"enabled": True}).sort("price_usd", 1)
        return await cursor.to_list(length=None)
    
    @staticmethod
    async def get_package(package_id: str) -> Optional[Dict[str, Any]]:
        """Get specific package by ID."""
        return await credit_packages_collection.find_one({"package_id": package_id})


# ============================================================
# INITIALIZATION
# ============================================================

async def initialize_credits_database():
    """Initialize all credits-related collections and indexes."""
    print("🔄 Initializing Credits & Economy Database...")
    
    # Create indexes
    await UserCredits.create_indexes()
    await CreditTransaction.create_indexes()
    await ShopItem.create_indexes()
    await UserInventory.create_indexes()
    await CreditPackage.create_indexes()
    
    # Initialize shop items
    await ShopItem.initialize_shop()
    
    # Initialize credit packages
    await CreditPackage.initialize_packages()
    
    print("✅ Credits & Economy Database initialized successfully!")


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_rarity_emoji(rarity: str) -> str:
    """Get emoji for item rarity."""
    rarity_emojis = {
        "common": "⚪",
        "rare": "🔵",
        "epic": "🟣",
        "legendary": "🟡"
    }
    return rarity_emojis.get(rarity.lower(), "⚪")


def get_rarity_color(rarity: str) -> int:
    """Get embed color for item rarity."""
    rarity_colors = {
        "common": 0x808080,    # Gray
        "rare": 0x0099FF,      # Blue
        "epic": 0x9B59B6,      # Purple
        "legendary": 0xFFD700  # Gold
    }
    return rarity_colors.get(rarity.lower(), 0x808080)


# Export all
__all__ = [
    'user_credits_collection',
    'credit_transactions_collection',
    'shop_items_collection',
    'user_inventory_collection',
    'daily_claims_collection',
    'credit_packages_collection',
    'UserCredits',
    'CreditTransaction',
    'ShopItem',
    'UserInventory',
    'CreditPackage',
    'CREDIT_PACKAGES',
    'SHOP_ITEMS',
    'DAILY_CLAIM_MIN',
    'DAILY_CLAIM_MAX',
    'DAILY_CLAIM_COOLDOWN_HOURS',
    'PREMIUM_COSTS',
    'initialize_credits_database',
    'get_rarity_emoji',
    'get_rarity_color'
]
