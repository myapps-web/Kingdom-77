"""
Economy System Core
==================
Main economy system with work, crime, gambling, and shop management.
"""

import discord
import random
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple, Any
import logging

logger = logging.getLogger(__name__)


class EconomySystem:
    """Core economy system"""
    
    def __init__(self, db):
        self.db = db
        
        # Default settings
        self.default_settings = {
            "currency_name": "Coins",
            "currency_symbol": "🪙",
            "daily_amount": 100,
            "weekly_amount": 700,
            "work_min": 50,
            "work_max": 150,
            "work_cooldown": 3600,  # 1 hour
            "crime_min": 100,
            "crime_max": 300,
            "crime_success_rate": 0.6,
            "crime_cooldown": 7200,  # 2 hours
            "initial_bank_space": 1000,
            "bank_space_upgrade_cost": 500,
            "bank_space_upgrade_amount": 1000
        }
        
        # Work job messages
        self.work_jobs = [
            ("مبرمج", "لقد كتبت بعض الأكواد وحصلت على", "💻"),
            ("مصمم", "لقد صممت شعاراً جميلاً وحصلت على", "🎨"),
            ("طباخ", "لقد طبخت وجبة شهية وحصلت على", "👨‍🍳"),
            ("سائق", "لقد أوصلت زبوناً وحصلت على", "🚗"),
            ("معلم", "لقد علمت الطلاب وحصلت على", "👨‍🏫"),
            ("طبيب", "لقد عالجت مريضاً وحصلت على", "👨‍⚕️"),
            ("مهندس", "لقد صممت مبنى وحصلت على", "👷"),
            ("كاتب", "لقد كتبت مقالاً وحصلت على", "✍️"),
            ("موسيقي", "لقد عزفت أغنية وحصلت على", "🎵"),
            ("فنان", "لقد رسمت لوحة وحصلت على", "🎭")
        ]
        
        # Crime scenarios
        self.crime_scenarios = {
            "success": [
                ("سرقة بنك", "لقد سرقت بنكاً ونجحت في الهروب!", "💰"),
                ("قرصنة", "لقد اخترقت نظاماً وحصلت على", "💻"),
                ("سطو", "لقد سطوت على متجر وحصلت على", "🏪"),
                ("نصب", "لقد نصبت على شخص وحصلت على", "🎭"),
                ("تهريب", "لقد هربت بضائع وحصلت على", "📦")
            ],
            "fail": [
                ("القبض عليك", "تم القبض عليك! دفعت غرامة قدرها", "👮"),
                ("الفشل", "فشلت في الجريمة ودفعت", "❌"),
                ("الإصابة", "أصبت أثناء الجريمة وتكلف علاجك", "🏥"),
                ("الخسارة", "خسرت في الجريمة مبلغ", "💸")
            ]
        }
        
    # ==================== CURRENCY OPERATIONS ====================
    
    async def get_balance(self, guild_id: int, user_id: int) -> Dict[str, int]:
        """Get user balance"""
        wallet = await self.db.get_wallet(guild_id, user_id)
        if not wallet:
            return {"cash": 0, "bank": 0, "total": 0}
        
        return {
            "cash": wallet.get("cash", 0),
            "bank": wallet.get("bank", 0),
            "total": wallet.get("cash", 0) + wallet.get("bank", 0),
            "bank_space": wallet.get("bank_space", 1000)
        }
    
    async def add_money(
        self,
        guild_id: int,
        user_id: int,
        amount: int,
        location: str = "cash"
    ) -> bool:
        """Add money to user"""
        return await self.db.update_balance(guild_id, user_id, amount, location, "add")
    
    async def remove_money(
        self,
        guild_id: int,
        user_id: int,
        amount: int,
        location: str = "cash"
    ) -> bool:
        """Remove money from user"""
        return await self.db.update_balance(guild_id, user_id, -amount, location, "add")
    
    async def can_afford(
        self,
        guild_id: int,
        user_id: int,
        amount: int,
        location: str = "cash"
    ) -> bool:
        """Check if user can afford amount"""
        balance = await self.get_balance(guild_id, user_id)
        return balance[location] >= amount
    
    # ==================== REWARDS ====================
    
    async def claim_daily(
        self,
        guild_id: int,
        user_id: int,
        amount: Optional[int] = None
    ) -> Tuple[bool, str, int]:
        """
        Claim daily reward
        Returns: (success, message, amount)
        """
        if amount is None:
            amount = self.default_settings["daily_amount"]
        
        success = await self.db.claim_daily(guild_id, user_id, amount)
        
        if success:
            return True, f"تم استلام مكافأتك اليومية!", amount
        else:
            return False, "لقد استلمت مكافأتك اليومية بالفعل! عد بعد 24 ساعة.", 0
    
    async def claim_weekly(
        self,
        guild_id: int,
        user_id: int,
        amount: Optional[int] = None
    ) -> Tuple[bool, str, int]:
        """
        Claim weekly reward
        Returns: (success, message, amount)
        """
        if amount is None:
            amount = self.default_settings["weekly_amount"]
        
        success = await self.db.claim_weekly(guild_id, user_id, amount)
        
        if success:
            return True, f"تم استلام مكافأتك الأسبوعية!", amount
        else:
            return False, "لقد استلمت مكافأتك الأسبوعية بالفعل! عد بعد 7 أيام.", 0
    
    async def get_daily_cooldown(self, guild_id: int, user_id: int) -> Optional[timedelta]:
        """Get remaining time until daily reward"""
        reward = await self.db.rewards.find_one({
            "guild_id": guild_id,
            "user_id": user_id
        })
        
        if not reward or not reward.get("last_daily"):
            return None
        
        now = datetime.utcnow()
        last_claim = reward["last_daily"]
        cooldown_end = last_claim + timedelta(hours=24)
        
        if now >= cooldown_end:
            return None
        
        return cooldown_end - now
    
    async def get_weekly_cooldown(self, guild_id: int, user_id: int) -> Optional[timedelta]:
        """Get remaining time until weekly reward"""
        reward = await self.db.rewards.find_one({
            "guild_id": guild_id,
            "user_id": user_id
        })
        
        if not reward or not reward.get("last_weekly"):
            return None
        
        now = datetime.utcnow()
        last_claim = reward["last_weekly"]
        cooldown_end = last_claim + timedelta(days=7)
        
        if now >= cooldown_end:
            return None
        
        return cooldown_end - now
    
    # ==================== WORK SYSTEM ====================
    
    async def work(self, guild_id: int, user_id: int) -> Tuple[bool, str, int, str]:
        """
        Work to earn money
        Returns: (success, message, amount, emoji)
        """
        # Check cooldown
        wallet = await self.db.get_wallet(guild_id, user_id)
        if wallet.get("last_work"):
            now = datetime.utcnow()
            last_work = wallet["last_work"]
            cooldown_end = last_work + timedelta(seconds=self.default_settings["work_cooldown"])
            
            if now < cooldown_end:
                remaining = cooldown_end - now
                minutes = int(remaining.total_seconds() / 60)
                return False, f"يجب الانتظار {minutes} دقيقة قبل العمل مرة أخرى!", 0, "⏳"
        
        # Random work
        job_name, job_desc, emoji = random.choice(self.work_jobs)
        amount = random.randint(
            self.default_settings["work_min"],
            self.default_settings["work_max"]
        )
        
        # Add money
        await self.add_money(guild_id, user_id, amount)
        
        # Update last_work
        await self.db.wallets.update_one(
            {"guild_id": guild_id, "user_id": user_id},
            {"$set": {"last_work": datetime.utcnow()}}
        )
        
        # Log transaction
        await self.db.log_transaction(guild_id, user_id, "work", amount, {"job": job_name})
        
        message = f"**{job_name}**\n{job_desc} **{amount}** 🪙"
        return True, message, amount, emoji
    
    async def get_work_cooldown(self, guild_id: int, user_id: int) -> Optional[timedelta]:
        """Get remaining work cooldown"""
        wallet = await self.db.get_wallet(guild_id, user_id)
        
        if not wallet.get("last_work"):
            return None
        
        now = datetime.utcnow()
        last_work = wallet["last_work"]
        cooldown_end = last_work + timedelta(seconds=self.default_settings["work_cooldown"])
        
        if now >= cooldown_end:
            return None
        
        return cooldown_end - now
    
    # ==================== CRIME SYSTEM ====================
    
    async def crime(self, guild_id: int, user_id: int) -> Tuple[bool, str, int, str]:
        """
        Commit a crime
        Returns: (success, message, amount, emoji)
        """
        # Check cooldown
        wallet = await self.db.get_wallet(guild_id, user_id)
        if wallet.get("last_crime"):
            now = datetime.utcnow()
            last_crime = wallet["last_crime"]
            cooldown_end = last_crime + timedelta(seconds=self.default_settings["crime_cooldown"])
            
            if now < cooldown_end:
                remaining = cooldown_end - now
                minutes = int(remaining.total_seconds() / 60)
                return False, f"يجب الانتظار {minutes} دقيقة قبل ارتكاب جريمة أخرى!", 0, "⏳"
        
        # Check if success
        success = random.random() < self.default_settings["crime_success_rate"]
        
        if success:
            # Success
            crime_name, crime_desc, emoji = random.choice(self.crime_scenarios["success"])
            amount = random.randint(
                self.default_settings["crime_min"],
                self.default_settings["crime_max"]
            )
            
            await self.add_money(guild_id, user_id, amount)
            message = f"**{crime_name}**\n{crime_desc} **{amount}** 🪙"
            
            # Log transaction
            await self.db.log_transaction(guild_id, user_id, "crime_success", amount, {"crime": crime_name})
        else:
            # Fail
            crime_name, crime_desc, emoji = random.choice(self.crime_scenarios["fail"])
            amount = random.randint(50, 150)
            
            # Check if can afford fine
            balance = await self.get_balance(guild_id, user_id)
            if balance["cash"] < amount:
                amount = balance["cash"]
            
            await self.remove_money(guild_id, user_id, amount)
            message = f"**{crime_name}**\n{crime_desc} **{amount}** 🪙"
            amount = -amount
            
            # Log transaction
            await self.db.log_transaction(guild_id, user_id, "crime_fail", amount, {"crime": crime_name})
        
        # Update last_crime
        await self.db.wallets.update_one(
            {"guild_id": guild_id, "user_id": user_id},
            {"$set": {"last_crime": datetime.utcnow()}}
        )
        
        return success, message, amount, emoji
    
    async def get_crime_cooldown(self, guild_id: int, user_id: int) -> Optional[timedelta]:
        """Get remaining crime cooldown"""
        wallet = await self.db.get_wallet(guild_id, user_id)
        
        if not wallet.get("last_crime"):
            return None
        
        now = datetime.utcnow()
        last_crime = wallet["last_crime"]
        cooldown_end = last_crime + timedelta(seconds=self.default_settings["crime_cooldown"])
        
        if now >= cooldown_end:
            return None
        
        return cooldown_end - now
    
    # ==================== GAMBLING ====================
    
    async def slots(
        self,
        guild_id: int,
        user_id: int,
        bet: int
    ) -> Tuple[bool, List[str], int, str]:
        """
        Play slots
        Returns: (won, symbols, payout, message)
        """
        # Check balance
        if not await self.can_afford(guild_id, user_id, bet):
            return False, [], 0, "ليس لديك ما يكفي من المال!"
        
        # Deduct bet
        await self.remove_money(guild_id, user_id, bet)
        
        # Slot symbols
        symbols = ["🍒", "🍋", "🍊", "🍇", "💎", "7️⃣", "🔔", "⭐"]
        weights = [30, 25, 20, 15, 5, 3, 1, 1]  # Probability weights
        
        # Spin
        result = random.choices(symbols, weights=weights, k=3)
        
        # Calculate payout
        won = False
        payout = 0
        message = ""
        
        if result[0] == result[1] == result[2]:
            # All three match
            if result[0] == "7️⃣":
                payout = bet * 50
                message = "🎰 **JACKPOT!** ثلاث سبعات!"
            elif result[0] == "💎":
                payout = bet * 25
                message = "💎 **رائع!** ثلاث ألماسات!"
            elif result[0] == "⭐":
                payout = bet * 15
                message = "⭐ **ممتاز!** ثلاث نجوم!"
            else:
                payout = bet * 10
                message = f"🎉 **فوز!** ثلاث {result[0]}!"
            won = True
        elif result[0] == result[1] or result[1] == result[2] or result[0] == result[2]:
            # Two match
            payout = bet * 2
            message = "😊 **فوز صغير!** رمزان متطابقان!"
            won = True
        else:
            message = "😢 **خسارة!** حظ أوفر في المرة القادمة!"
        
        if won:
            await self.add_money(guild_id, user_id, payout)
        
        # Update gambling stats
        await self.db.update_gambling_stats(guild_id, user_id, "slots", bet, won, payout)
        
        # Log transaction
        await self.db.log_transaction(
            guild_id, user_id,
            "slots_win" if won else "slots_loss",
            payout if won else -bet,
            {"symbols": result}
        )
        
        return won, result, payout, message
    
    async def coinflip(
        self,
        guild_id: int,
        user_id: int,
        bet: int,
        choice: str
    ) -> Tuple[bool, str, int, str]:
        """
        Coinflip game
        Returns: (won, result, payout, message)
        """
        # Check balance
        if not await self.can_afford(guild_id, user_id, bet):
            return False, "", 0, "ليس لديك ما يكفي من المال!"
        
        # Deduct bet
        await self.remove_money(guild_id, user_id, bet)
        
        # Flip
        result = random.choice(["heads", "tails"])
        won = result == choice
        
        payout = 0
        if won:
            payout = bet * 2
            await self.add_money(guild_id, user_id, payout)
            message = f"🪙 **فزت!** العملة جاءت على {'صورة' if result == 'heads' else 'كتابة'}!"
        else:
            message = f"😢 **خسرت!** العملة جاءت على {'صورة' if result == 'heads' else 'كتابة'}."
        
        # Update gambling stats
        await self.db.update_gambling_stats(guild_id, user_id, "coinflip", bet, won, payout)
        
        # Log transaction
        await self.db.log_transaction(
            guild_id, user_id,
            "coinflip_win" if won else "coinflip_loss",
            payout if won else -bet,
            {"choice": choice, "result": result}
        )
        
        return won, result, payout, message
    
    async def dice(
        self,
        guild_id: int,
        user_id: int,
        bet: int
    ) -> Tuple[bool, int, int, int, str]:
        """
        Dice game (roll higher than bot)
        Returns: (won, user_roll, bot_roll, payout, message)
        """
        # Check balance
        if not await self.can_afford(guild_id, user_id, bet):
            return False, 0, 0, 0, "ليس لديك ما يكفي من المال!"
        
        # Deduct bet
        await self.remove_money(guild_id, user_id, bet)
        
        # Roll
        user_roll = random.randint(1, 6)
        bot_roll = random.randint(1, 6)
        
        won = False
        payout = 0
        
        if user_roll > bot_roll:
            payout = bet * 2
            await self.add_money(guild_id, user_id, payout)
            message = f"🎲 **فزت!** رميتك: {user_roll} | رمية البوت: {bot_roll}"
            won = True
        elif user_roll == bot_roll:
            # Tie - return bet
            await self.add_money(guild_id, user_id, bet)
            message = f"🤝 **تعادل!** رميتك: {user_roll} | رمية البوت: {bot_roll}"
        else:
            message = f"😢 **خسرت!** رميتك: {user_roll} | رمية البوت: {bot_roll}"
        
        # Update gambling stats
        await self.db.update_gambling_stats(guild_id, user_id, "dice", bet, won, payout)
        
        # Log transaction
        await self.db.log_transaction(
            guild_id, user_id,
            "dice_win" if won else "dice_loss",
            payout if won else -bet,
            {"user_roll": user_roll, "bot_roll": bot_roll}
        )
        
        return won, user_roll, bot_roll, payout, message
    
    # ==================== SHOP OPERATIONS ====================
    
    async def buy_item(
        self,
        guild_id: int,
        user_id: int,
        item_id: str,
        member: discord.Member
    ) -> Tuple[bool, str]:
        """
        Buy item from shop
        Returns: (success, message)
        """
        item = await self.db.get_item(guild_id, item_id)
        if not item:
            return False, "العنصر غير موجود!"
        
        # Check stock
        if item["stock"] == 0:
            return False, "العنصر غير متوفر حالياً!"
        
        # Check balance
        if not await self.can_afford(guild_id, user_id, item["price"]):
            return False, f"ليس لديك ما يكفي من المال! السعر: {item['price']} 🪙"
        
        # Purchase
        success = await self.db.purchase_item(guild_id, user_id, item_id)
        
        if not success:
            return False, "فشلت عملية الشراء!"
        
        # If role, add to user
        if item["category"] == "role" and item.get("role_id"):
            try:
                role = member.guild.get_role(item["role_id"])
                if role:
                    await member.add_roles(role)
            except Exception as e:
                logger.error(f"Error adding role: {e}")
        
        return True, f"تم شراء **{item['name']}** بنجاح! 🎉"
    
    async def sell_item(
        self,
        guild_id: int,
        user_id: int,
        item_id: str,
        quantity: int = 1
    ) -> Tuple[bool, str, int]:
        """
        Sell item from inventory
        Returns: (success, message, amount)
        """
        # Check inventory
        inventory = await self.db.get_inventory(guild_id, user_id)
        user_item = None
        
        for inv_item in inventory:
            if inv_item["item_id"] == item_id:
                user_item = inv_item
                break
        
        if not user_item or user_item["quantity"] < quantity:
            return False, "ليس لديك هذا العنصر!", 0
        
        # Get item info
        item = await self.db.get_item(guild_id, item_id)
        if not item:
            return False, "العنصر غير موجود في المتجر!", 0
        
        # Calculate sell price (50% of buy price)
        sell_price = int(item["price"] * 0.5 * quantity)
        
        # Remove from inventory
        success = await self.db.remove_from_inventory(guild_id, user_id, item_id, quantity)
        if not success:
            return False, "فشلت عملية البيع!", 0
        
        # Add money
        await self.add_money(guild_id, user_id, sell_price)
        
        # Log transaction
        await self.db.log_transaction(
            guild_id, user_id, "sell",
            sell_price,
            {"item_id": item_id, "quantity": quantity}
        )
        
        return True, f"تم بيع **{quantity}x {item['name']}** مقابل **{sell_price}** 🪙", sell_price
    
    # ==================== LEADERBOARD ====================
    
    async def get_leaderboard(
        self,
        guild_id: int,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get economy leaderboard"""
        return await self.db.get_leaderboard(guild_id, limit, "total")
    
    # ==================== BANK OPERATIONS ====================
    
    async def upgrade_bank(
        self,
        guild_id: int,
        user_id: int
    ) -> Tuple[bool, str, int]:
        """
        Upgrade bank space
        Returns: (success, message, new_space)
        """
        wallet = await self.db.get_wallet(guild_id, user_id)
        current_space = wallet.get("bank_space", 1000)
        
        cost = self.default_settings["bank_space_upgrade_cost"]
        
        # Check balance
        if not await self.can_afford(guild_id, user_id, cost):
            return False, f"تحتاج إلى **{cost}** 🪙 لترقية البنك!", current_space
        
        # Deduct money
        await self.remove_money(guild_id, user_id, cost)
        
        # Upgrade
        new_space = current_space + self.default_settings["bank_space_upgrade_amount"]
        await self.db.wallets.update_one(
            {"guild_id": guild_id, "user_id": user_id},
            {"$set": {"bank_space": new_space}}
        )
        
        # Log transaction
        await self.db.log_transaction(guild_id, user_id, "bank_upgrade", -cost, {"new_space": new_space})
        
        return True, f"تمت ترقية البنك! المساحة الجديدة: **{new_space}** 🪙", new_space
