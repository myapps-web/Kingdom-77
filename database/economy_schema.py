"""
Economy Database Schema
======================
MongoDB collections and operations for economy system.

Collections:
- user_wallets: User balances and bank accounts
- shop_items: Server shop items
- user_inventory: User-owned items
- transactions: Transaction history
- daily_rewards: Daily/weekly claim tracking
- gambling_stats: Gambling statistics
"""

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class EconomyDatabase:
    """Economy system database operations"""
    
    def __init__(self, mongo_client, db_name: str = "kingdom77"):
        self.db = mongo_client[db_name]
        self.wallets = self.db.user_wallets
        self.shop = self.db.shop_items
        self.inventory = self.db.user_inventory
        self.transactions = self.db.transactions
        self.rewards = self.db.daily_rewards
        self.gambling = self.db.gambling_stats
        
    async def create_indexes(self):
        """Create database indexes for performance"""
        try:
            # Wallets indexes
            await self.wallets.create_index([("guild_id", 1), ("user_id", 1)], unique=True)
            await self.wallets.create_index([("guild_id", 1), ("cash", -1)])  # Leaderboard
            
            # Shop indexes
            await self.shop.create_index([("guild_id", 1), ("item_id", 1)], unique=True)
            await self.shop.create_index([("guild_id", 1), ("category", 1)])
            
            # Inventory indexes
            await self.inventory.create_index([("guild_id", 1), ("user_id", 1), ("item_id", 1)])
            
            # Transactions indexes
            await self.transactions.create_index([("guild_id", 1), ("user_id", 1), ("timestamp", -1)])
            await self.transactions.create_index([("timestamp", 1)], expireAfterSeconds=7776000)  # 90 days
            
            # Rewards indexes
            await self.rewards.create_index([("guild_id", 1), ("user_id", 1)], unique=True)
            
            # Gambling stats indexes
            await self.gambling.create_index([("guild_id", 1), ("user_id", 1)], unique=True)
            
            logger.info("Economy database indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
    
    # ==================== WALLET OPERATIONS ====================
    
    async def get_wallet(self, guild_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user's wallet"""
        try:
            wallet = await self.wallets.find_one({
                "guild_id": guild_id,
                "user_id": user_id
            })
            
            if not wallet:
                # Create new wallet
                wallet = {
                    "guild_id": guild_id,
                    "user_id": user_id,
                    "cash": 0,
                    "bank": 0,
                    "bank_space": 1000,  # Initial bank capacity
                    "created_at": datetime.utcnow(),
                    "last_daily": None,
                    "last_weekly": None,
                    "last_work": None,
                    "last_crime": None
                }
                await self.wallets.insert_one(wallet)
            
            return wallet
        except Exception as e:
            logger.error(f"Error getting wallet: {e}")
            return None
    
    async def update_balance(
        self,
        guild_id: int,
        user_id: int,
        amount: int,
        balance_type: str = "cash",  # "cash" or "bank"
        operation: str = "add"  # "add" or "set"
    ) -> bool:
        """Update user balance"""
        try:
            wallet = await self.get_wallet(guild_id, user_id)
            if not wallet:
                return False
            
            if operation == "add":
                new_amount = wallet[balance_type] + amount
            else:  # set
                new_amount = amount
            
            # Prevent negative balances
            if new_amount < 0:
                new_amount = 0
            
            # Check bank capacity
            if balance_type == "bank" and new_amount > wallet.get("bank_space", 1000):
                return False
            
            await self.wallets.update_one(
                {"guild_id": guild_id, "user_id": user_id},
                {"$set": {balance_type: new_amount}}
            )
            return True
        except Exception as e:
            logger.error(f"Error updating balance: {e}")
            return False
    
    async def transfer_money(
        self,
        guild_id: int,
        from_user: int,
        to_user: int,
        amount: int
    ) -> bool:
        """Transfer money between users"""
        try:
            from_wallet = await self.get_wallet(guild_id, from_user)
            to_wallet = await self.get_wallet(guild_id, to_user)
            
            if not from_wallet or not to_wallet:
                return False
            
            if from_wallet["cash"] < amount:
                return False
            
            # Deduct from sender
            await self.update_balance(guild_id, from_user, -amount, "cash", "add")
            
            # Add to receiver
            await self.update_balance(guild_id, to_user, amount, "cash", "add")
            
            # Log transaction
            await self.log_transaction(
                guild_id=guild_id,
                user_id=from_user,
                transaction_type="transfer",
                amount=-amount,
                details={"to_user": to_user}
            )
            
            await self.log_transaction(
                guild_id=guild_id,
                user_id=to_user,
                transaction_type="transfer",
                amount=amount,
                details={"from_user": from_user}
            )
            
            return True
        except Exception as e:
            logger.error(f"Error transferring money: {e}")
            return False
    
    async def deposit(self, guild_id: int, user_id: int, amount: int) -> bool:
        """Deposit cash to bank"""
        try:
            wallet = await self.get_wallet(guild_id, user_id)
            if not wallet:
                return False
            
            if wallet["cash"] < amount:
                return False
            
            if wallet["bank"] + amount > wallet.get("bank_space", 1000):
                return False
            
            await self.update_balance(guild_id, user_id, -amount, "cash", "add")
            await self.update_balance(guild_id, user_id, amount, "bank", "add")
            
            await self.log_transaction(guild_id, user_id, "deposit", amount)
            return True
        except Exception as e:
            logger.error(f"Error depositing: {e}")
            return False
    
    async def withdraw(self, guild_id: int, user_id: int, amount: int) -> bool:
        """Withdraw money from bank"""
        try:
            wallet = await self.get_wallet(guild_id, user_id)
            if not wallet:
                return False
            
            if wallet["bank"] < amount:
                return False
            
            await self.update_balance(guild_id, user_id, -amount, "bank", "add")
            await self.update_balance(guild_id, user_id, amount, "cash", "add")
            
            await self.log_transaction(guild_id, user_id, "withdraw", amount)
            return True
        except Exception as e:
            logger.error(f"Error withdrawing: {e}")
            return False
    
    async def get_leaderboard(
        self,
        guild_id: int,
        limit: int = 10,
        sort_by: str = "total"  # "cash", "bank", "total"
    ) -> List[Dict[str, Any]]:
        """Get economy leaderboard"""
        try:
            pipeline = [
                {"$match": {"guild_id": guild_id}},
                {"$addFields": {"total": {"$add": ["$cash", "$bank"]}}},
                {"$sort": {sort_by: -1}},
                {"$limit": limit}
            ]
            
            leaderboard = await self.wallets.aggregate(pipeline).to_list(length=limit)
            return leaderboard
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return []
    
    # ==================== SHOP OPERATIONS ====================
    
    async def create_item(
        self,
        guild_id: int,
        item_id: str,
        name: str,
        description: str,
        price: int,
        category: str = "other",
        role_id: Optional[int] = None,
        stock: int = -1,  # -1 = unlimited
        emoji: Optional[str] = None
    ) -> bool:
        """Create shop item"""
        try:
            item = {
                "guild_id": guild_id,
                "item_id": item_id,
                "name": name,
                "description": description,
                "price": price,
                "category": category,  # role, item, boost, other
                "role_id": role_id,
                "stock": stock,
                "emoji": emoji,
                "created_at": datetime.utcnow(),
                "purchases": 0
            }
            
            await self.shop.insert_one(item)
            return True
        except Exception as e:
            logger.error(f"Error creating item: {e}")
            return False
    
    async def get_item(self, guild_id: int, item_id: str) -> Optional[Dict[str, Any]]:
        """Get shop item"""
        try:
            return await self.shop.find_one({
                "guild_id": guild_id,
                "item_id": item_id
            })
        except Exception as e:
            logger.error(f"Error getting item: {e}")
            return None
    
    async def get_shop_items(
        self,
        guild_id: int,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all shop items"""
        try:
            query = {"guild_id": guild_id}
            if category:
                query["category"] = category
            
            items = await self.shop.find(query).to_list(length=100)
            return items
        except Exception as e:
            logger.error(f"Error getting shop items: {e}")
            return []
    
    async def update_item(
        self,
        guild_id: int,
        item_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Update shop item"""
        try:
            result = await self.shop.update_one(
                {"guild_id": guild_id, "item_id": item_id},
                {"$set": updates}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating item: {e}")
            return False
    
    async def delete_item(self, guild_id: int, item_id: str) -> bool:
        """Delete shop item"""
        try:
            result = await self.shop.delete_one({
                "guild_id": guild_id,
                "item_id": item_id
            })
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting item: {e}")
            return False
    
    async def purchase_item(
        self,
        guild_id: int,
        user_id: int,
        item_id: str
    ) -> bool:
        """Purchase item from shop"""
        try:
            item = await self.get_item(guild_id, item_id)
            if not item:
                return False
            
            # Check stock
            if item["stock"] == 0:
                return False
            
            # Check balance
            wallet = await self.get_wallet(guild_id, user_id)
            if wallet["cash"] < item["price"]:
                return False
            
            # Deduct money
            await self.update_balance(guild_id, user_id, -item["price"], "cash", "add")
            
            # Update stock
            if item["stock"] > 0:
                await self.shop.update_one(
                    {"guild_id": guild_id, "item_id": item_id},
                    {"$inc": {"stock": -1, "purchases": 1}}
                )
            else:
                await self.shop.update_one(
                    {"guild_id": guild_id, "item_id": item_id},
                    {"$inc": {"purchases": 1}}
                )
            
            # Add to inventory
            await self.add_to_inventory(guild_id, user_id, item_id, 1)
            
            # Log transaction
            await self.log_transaction(
                guild_id=guild_id,
                user_id=user_id,
                transaction_type="purchase",
                amount=-item["price"],
                details={"item_id": item_id, "item_name": item["name"]}
            )
            
            return True
        except Exception as e:
            logger.error(f"Error purchasing item: {e}")
            return False
    
    # ==================== INVENTORY OPERATIONS ====================
    
    async def add_to_inventory(
        self,
        guild_id: int,
        user_id: int,
        item_id: str,
        quantity: int = 1
    ) -> bool:
        """Add item to user inventory"""
        try:
            result = await self.inventory.update_one(
                {"guild_id": guild_id, "user_id": user_id, "item_id": item_id},
                {
                    "$inc": {"quantity": quantity},
                    "$setOnInsert": {"acquired_at": datetime.utcnow()}
                },
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error adding to inventory: {e}")
            return False
    
    async def remove_from_inventory(
        self,
        guild_id: int,
        user_id: int,
        item_id: str,
        quantity: int = 1
    ) -> bool:
        """Remove item from inventory"""
        try:
            inventory_item = await self.inventory.find_one({
                "guild_id": guild_id,
                "user_id": user_id,
                "item_id": item_id
            })
            
            if not inventory_item or inventory_item["quantity"] < quantity:
                return False
            
            new_quantity = inventory_item["quantity"] - quantity
            
            if new_quantity <= 0:
                await self.inventory.delete_one({
                    "guild_id": guild_id,
                    "user_id": user_id,
                    "item_id": item_id
                })
            else:
                await self.inventory.update_one(
                    {"guild_id": guild_id, "user_id": user_id, "item_id": item_id},
                    {"$set": {"quantity": new_quantity}}
                )
            
            return True
        except Exception as e:
            logger.error(f"Error removing from inventory: {e}")
            return False
    
    async def get_inventory(
        self,
        guild_id: int,
        user_id: int
    ) -> List[Dict[str, Any]]:
        """Get user inventory"""
        try:
            inventory = await self.inventory.find({
                "guild_id": guild_id,
                "user_id": user_id
            }).to_list(length=100)
            
            return inventory
        except Exception as e:
            logger.error(f"Error getting inventory: {e}")
            return []
    
    # ==================== REWARDS OPERATIONS ====================
    
    async def claim_daily(self, guild_id: int, user_id: int, amount: int) -> bool:
        """Claim daily reward"""
        try:
            now = datetime.utcnow()
            
            reward = await self.rewards.find_one({
                "guild_id": guild_id,
                "user_id": user_id
            })
            
            if reward and reward.get("last_daily"):
                last_claim = reward["last_daily"]
                if now - last_claim < timedelta(hours=24):
                    return False
            
            # Update balance
            await self.update_balance(guild_id, user_id, amount, "cash", "add")
            
            # Update reward tracking
            await self.rewards.update_one(
                {"guild_id": guild_id, "user_id": user_id},
                {
                    "$set": {"last_daily": now},
                    "$inc": {"daily_streak": 1}
                },
                upsert=True
            )
            
            # Log transaction
            await self.log_transaction(guild_id, user_id, "daily", amount)
            return True
        except Exception as e:
            logger.error(f"Error claiming daily: {e}")
            return False
    
    async def claim_weekly(self, guild_id: int, user_id: int, amount: int) -> bool:
        """Claim weekly reward"""
        try:
            now = datetime.utcnow()
            
            reward = await self.rewards.find_one({
                "guild_id": guild_id,
                "user_id": user_id
            })
            
            if reward and reward.get("last_weekly"):
                last_claim = reward["last_weekly"]
                if now - last_claim < timedelta(days=7):
                    return False
            
            # Update balance
            await self.update_balance(guild_id, user_id, amount, "cash", "add")
            
            # Update reward tracking
            await self.rewards.update_one(
                {"guild_id": guild_id, "user_id": user_id},
                {"$set": {"last_weekly": now}},
                upsert=True
            )
            
            # Log transaction
            await self.log_transaction(guild_id, user_id, "weekly", amount)
            return True
        except Exception as e:
            logger.error(f"Error claiming weekly: {e}")
            return False
    
    # ==================== TRANSACTION LOGGING ====================
    
    async def log_transaction(
        self,
        guild_id: int,
        user_id: int,
        transaction_type: str,
        amount: int,
        details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Log transaction"""
        try:
            transaction = {
                "guild_id": guild_id,
                "user_id": user_id,
                "type": transaction_type,
                "amount": amount,
                "details": details or {},
                "timestamp": datetime.utcnow()
            }
            
            await self.transactions.insert_one(transaction)
            return True
        except Exception as e:
            logger.error(f"Error logging transaction: {e}")
            return False
    
    async def get_transactions(
        self,
        guild_id: int,
        user_id: Optional[int] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get transaction history"""
        try:
            query = {"guild_id": guild_id}
            if user_id:
                query["user_id"] = user_id
            
            transactions = await self.transactions.find(query).sort(
                "timestamp", -1
            ).limit(limit).to_list(length=limit)
            
            return transactions
        except Exception as e:
            logger.error(f"Error getting transactions: {e}")
            return []
    
    # ==================== GAMBLING STATS ====================
    
    async def update_gambling_stats(
        self,
        guild_id: int,
        user_id: int,
        game_type: str,
        bet: int,
        won: bool,
        payout: int = 0
    ) -> bool:
        """Update gambling statistics"""
        try:
            update_data = {
                "$inc": {
                    f"games.{game_type}.played": 1,
                    f"games.{game_type}.bet": bet,
                    "total_bet": bet
                }
            }
            
            if won:
                update_data["$inc"][f"games.{game_type}.won"] = 1
                update_data["$inc"][f"games.{game_type}.payout"] = payout
                update_data["$inc"]["total_won"] = payout
            else:
                update_data["$inc"][f"games.{game_type}.lost"] = 1
                update_data["$inc"]["total_lost"] = bet
            
            await self.gambling.update_one(
                {"guild_id": guild_id, "user_id": user_id},
                update_data,
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error updating gambling stats: {e}")
            return False
    
    async def get_gambling_stats(
        self,
        guild_id: int,
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get gambling statistics"""
        try:
            return await self.gambling.find_one({
                "guild_id": guild_id,
                "user_id": user_id
            })
        except Exception as e:
            logger.error(f"Error getting gambling stats: {e}")
            return None
