"""
Economy API Endpoints
====================
FastAPI endpoints for economy dashboard management.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/economy", tags=["economy"])


# ==================== PYDANTIC MODELS ====================

class WalletResponse(BaseModel):
    """Wallet response model"""
    user_id: int
    cash: int
    bank: int
    total: int
    bank_space: int
    last_daily: Optional[datetime] = None
    last_weekly: Optional[datetime] = None


class ShopItemCreate(BaseModel):
    """Shop item creation model"""
    item_id: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=200)
    price: int = Field(..., gt=0)
    category: Literal["role", "item", "boost", "other"]
    role_id: Optional[int] = None
    stock: int = Field(default=-1)
    emoji: Optional[str] = None


class ShopItemUpdate(BaseModel):
    """Shop item update model"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1, max_length=200)
    price: Optional[int] = Field(None, gt=0)
    stock: Optional[int] = None
    emoji: Optional[str] = None


class ShopItemResponse(BaseModel):
    """Shop item response model"""
    guild_id: int
    item_id: str
    name: str
    description: str
    price: int
    category: str
    role_id: Optional[int] = None
    stock: int
    emoji: Optional[str] = None
    purchases: int
    created_at: datetime


class TransactionResponse(BaseModel):
    """Transaction response model"""
    guild_id: int
    user_id: int
    type: str
    amount: int
    details: dict
    timestamp: datetime


class LeaderboardEntry(BaseModel):
    """Leaderboard entry model"""
    user_id: int
    cash: int
    bank: int
    total: int
    rank: int


class GamblingStatsResponse(BaseModel):
    """Gambling stats response model"""
    guild_id: int
    user_id: int
    games: dict
    total_bet: int
    total_won: int
    total_lost: int


class BalanceUpdate(BaseModel):
    """Balance update model"""
    amount: int
    location: Literal["cash", "bank"] = "cash"
    operation: Literal["add", "set"] = "add"


# ==================== WALLET ENDPOINTS ====================

@router.get("/{guild_id}/wallet/{user_id}", response_model=WalletResponse)
async def get_wallet(
    guild_id: int,
    user_id: int,
    economy_db = Depends(lambda: router.economy_db)
):
    """Get user wallet"""
    try:
        wallet = await economy_db.get_wallet(guild_id, user_id)
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")
        
        return WalletResponse(
            user_id=wallet["user_id"],
            cash=wallet.get("cash", 0),
            bank=wallet.get("bank", 0),
            total=wallet.get("cash", 0) + wallet.get("bank", 0),
            bank_space=wallet.get("bank_space", 1000),
            last_daily=wallet.get("last_daily"),
            last_weekly=wallet.get("last_weekly")
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting wallet: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.patch("/{guild_id}/wallet/{user_id}")
async def update_balance(
    guild_id: int,
    user_id: int,
    update: BalanceUpdate,
    economy_db = Depends(lambda: router.economy_db)
):
    """Update user balance (Admin only)"""
    try:
        success = await economy_db.update_balance(
            guild_id, user_id,
            update.amount,
            update.location,
            update.operation
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to update balance")
        
        return {"success": True, "message": "Balance updated"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating balance: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{guild_id}/leaderboard", response_model=List[LeaderboardEntry])
async def get_leaderboard(
    guild_id: int,
    limit: int = Query(10, ge=1, le=100),
    sort_by: Literal["cash", "bank", "total"] = "total",
    economy_db = Depends(lambda: router.economy_db)
):
    """Get economy leaderboard"""
    try:
        leaderboard = await economy_db.get_leaderboard(guild_id, limit, sort_by)
        
        return [
            LeaderboardEntry(
                user_id=entry["user_id"],
                cash=entry.get("cash", 0),
                bank=entry.get("bank", 0),
                total=entry.get("total", 0),
                rank=idx + 1
            )
            for idx, entry in enumerate(leaderboard)
        ]
    except Exception as e:
        logger.error(f"Error getting leaderboard: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ==================== SHOP ENDPOINTS ====================

@router.get("/{guild_id}/shop", response_model=List[ShopItemResponse])
async def get_shop_items(
    guild_id: int,
    category: Optional[Literal["role", "item", "boost", "other"]] = None,
    economy_db = Depends(lambda: router.economy_db)
):
    """Get all shop items"""
    try:
        items = await economy_db.get_shop_items(guild_id, category)
        return [ShopItemResponse(**item) for item in items]
    except Exception as e:
        logger.error(f"Error getting shop items: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{guild_id}/shop")
async def create_shop_item(
    guild_id: int,
    item: ShopItemCreate,
    economy_db = Depends(lambda: router.economy_db)
):
    """Create shop item (Admin only)"""
    try:
        success = await economy_db.create_item(
            guild_id=guild_id,
            item_id=item.item_id,
            name=item.name,
            description=item.description,
            price=item.price,
            category=item.category,
            role_id=item.role_id,
            stock=item.stock,
            emoji=item.emoji
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to create item")
        
        return {"success": True, "message": "Item created", "item_id": item.item_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating item: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{guild_id}/shop/{item_id}", response_model=ShopItemResponse)
async def get_shop_item(
    guild_id: int,
    item_id: str,
    economy_db = Depends(lambda: router.economy_db)
):
    """Get shop item details"""
    try:
        item = await economy_db.get_item(guild_id, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        return ShopItemResponse(**item)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting item: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.patch("/{guild_id}/shop/{item_id}")
async def update_shop_item(
    guild_id: int,
    item_id: str,
    update: ShopItemUpdate,
    economy_db = Depends(lambda: router.economy_db)
):
    """Update shop item (Admin only)"""
    try:
        updates = update.dict(exclude_unset=True)
        if not updates:
            raise HTTPException(status_code=400, detail="No updates provided")
        
        success = await economy_db.update_item(guild_id, item_id, updates)
        if not success:
            raise HTTPException(status_code=404, detail="Item not found")
        
        return {"success": True, "message": "Item updated"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating item: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{guild_id}/shop/{item_id}")
async def delete_shop_item(
    guild_id: int,
    item_id: str,
    economy_db = Depends(lambda: router.economy_db)
):
    """Delete shop item (Admin only)"""
    try:
        success = await economy_db.delete_item(guild_id, item_id)
        if not success:
            raise HTTPException(status_code=404, detail="Item not found")
        
        return {"success": True, "message": "Item deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting item: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ==================== INVENTORY ENDPOINTS ====================

@router.get("/{guild_id}/inventory/{user_id}")
async def get_inventory(
    guild_id: int,
    user_id: int,
    economy_db = Depends(lambda: router.economy_db)
):
    """Get user inventory"""
    try:
        inventory = await economy_db.get_inventory(guild_id, user_id)
        
        # Enrich with item details
        enriched = []
        for inv_item in inventory:
            item = await economy_db.get_item(guild_id, inv_item["item_id"])
            if item:
                enriched.append({
                    "item_id": inv_item["item_id"],
                    "quantity": inv_item["quantity"],
                    "acquired_at": inv_item.get("acquired_at"),
                    "item_name": item["name"],
                    "item_emoji": item.get("emoji"),
                    "item_description": item["description"]
                })
        
        return enriched
    except Exception as e:
        logger.error(f"Error getting inventory: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ==================== TRANSACTION ENDPOINTS ====================

@router.get("/{guild_id}/transactions", response_model=List[TransactionResponse])
async def get_transactions(
    guild_id: int,
    user_id: Optional[int] = None,
    limit: int = Query(50, ge=1, le=100),
    economy_db = Depends(lambda: router.economy_db)
):
    """Get transaction history"""
    try:
        transactions = await economy_db.get_transactions(guild_id, user_id, limit)
        return [TransactionResponse(**t) for t in transactions]
    except Exception as e:
        logger.error(f"Error getting transactions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ==================== GAMBLING STATS ENDPOINTS ====================

@router.get("/{guild_id}/gambling/{user_id}", response_model=GamblingStatsResponse)
async def get_gambling_stats(
    guild_id: int,
    user_id: int,
    economy_db = Depends(lambda: router.economy_db)
):
    """Get gambling statistics"""
    try:
        stats = await economy_db.get_gambling_stats(guild_id, user_id)
        if not stats:
            raise HTTPException(status_code=404, detail="No gambling stats found")
        
        return GamblingStatsResponse(
            guild_id=stats["guild_id"],
            user_id=stats["user_id"],
            games=stats.get("games", {}),
            total_bet=stats.get("total_bet", 0),
            total_won=stats.get("total_won", 0),
            total_lost=stats.get("total_lost", 0)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting gambling stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ==================== STATISTICS ENDPOINTS ====================

@router.get("/{guild_id}/stats")
async def get_economy_stats(
    guild_id: int,
    economy_db = Depends(lambda: router.economy_db)
):
    """Get economy statistics"""
    try:
        # Total wallets
        total_wallets = await economy_db.wallets.count_documents({"guild_id": guild_id})
        
        # Total money in circulation
        pipeline = [
            {"$match": {"guild_id": guild_id}},
            {"$group": {
                "_id": None,
                "total_cash": {"$sum": "$cash"},
                "total_bank": {"$sum": "$bank"}
            }}
        ]
        circulation = await economy_db.wallets.aggregate(pipeline).to_list(length=1)
        
        # Total shop items
        total_items = await economy_db.shop.count_documents({"guild_id": guild_id})
        
        # Total transactions
        total_transactions = await economy_db.transactions.count_documents({"guild_id": guild_id})
        
        return {
            "total_users": total_wallets,
            "total_cash": circulation[0]["total_cash"] if circulation else 0,
            "total_bank": circulation[0]["total_bank"] if circulation else 0,
            "total_money": (circulation[0]["total_cash"] + circulation[0]["total_bank"]) if circulation else 0,
            "total_shop_items": total_items,
            "total_transactions": total_transactions
        }
    except Exception as e:
        logger.error(f"Error getting economy stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ==================== REWARDS ENDPOINTS ====================

@router.post("/{guild_id}/daily/{user_id}")
async def claim_daily(
    guild_id: int,
    user_id: int,
    amount: int = Query(100, ge=1),
    economy_db = Depends(lambda: router.economy_db)
):
    """Claim daily reward"""
    try:
        success = await economy_db.claim_daily(guild_id, user_id, amount)
        
        if not success:
            return {"success": False, "message": "Already claimed today"}
        
        return {"success": True, "message": "Daily reward claimed", "amount": amount}
    except Exception as e:
        logger.error(f"Error claiming daily: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{guild_id}/weekly/{user_id}")
async def claim_weekly(
    guild_id: int,
    user_id: int,
    amount: int = Query(700, ge=1),
    economy_db = Depends(lambda: router.economy_db)
):
    """Claim weekly reward"""
    try:
        success = await economy_db.claim_weekly(guild_id, user_id, amount)
        
        if not success:
            return {"success": False, "message": "Already claimed this week"}
        
        return {"success": True, "message": "Weekly reward claimed", "amount": amount}
    except Exception as e:
        logger.error(f"Error claiming weekly: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


def init_economy_router(economy_db):
    """Initialize router with database"""
    router.economy_db = economy_db
    return router
