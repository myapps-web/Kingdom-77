"""
Leveling System Schema for Kingdom-77 Bot v3.0
===============================================
MongoDB collections structure for XP and leveling system
"""

# Collection: user_levels
"""
{
    "_id": ObjectId,
    "guild_id": "123456789",           # Server ID
    "user_id": "987654321",            # User ID
    "xp": 1250,                        # Total XP earned
    "level": 5,                        # Current level
    "messages": 125,                   # Total messages sent
    "last_xp_time": "2025-10-29T12:00:00Z",  # Last time XP was earned (cooldown)
    "total_xp": 1250,                  # Total XP (including spent)
    "rank_card_color": "#5865F2",      # Custom rank card color
    "created_at": "2025-10-29T10:00:00Z",
    "updated_at": "2025-10-29T12:00:00Z"
}

Indexes:
- guild_id + user_id (compound, unique) - for user lookup
- guild_id + xp (compound) - for leaderboards
- guild_id + level (compound) - for level queries
"""

# Collection: guild_level_config
"""
{
    "_id": ObjectId,
    "guild_id": "123456789",           # Server ID
    "enabled": true,                   # Enable/disable leveling
    "xp_rate": 1.0,                    # XP multiplier (0.5-2.0)
    "xp_per_message": [15, 25],        # Random range per message
    "cooldown": 60,                    # Cooldown in seconds (default 60s)
    "level_up_channel": null,          # Channel for level up messages (null = same channel)
    "level_up_message": "🎉 {user} leveled up to **Level {level}**!",  # Custom message
    "no_xp_roles": [],                 # Roles that don't earn XP
    "no_xp_channels": [],              # Channels where XP isn't earned
    "double_xp_roles": [],             # Roles with 2x XP
    "level_roles": {                   # Level-based role rewards
        "5": "role_id_1",
        "10": "role_id_2",
        "20": "role_id_3"
    },
    "stack_roles": false,              # Keep previous level roles
    "announce_level_up": true,         # Announce level ups
    "updated_at": "2025-10-29T12:00:00Z"
}

Indexes:
- guild_id (unique) - one config per guild
"""

# Collection: level_rewards
"""
{
    "_id": ObjectId,
    "guild_id": "123456789",
    "level": 10,                       # Level requirement
    "role_id": "role_123",             # Role to give
    "role_name": "Level 10",           # Role name (for display)
    "created_at": "2025-10-29T12:00:00Z"
}

Indexes:
- guild_id + level (compound) - for level rewards lookup
"""

# Collection: xp_transactions (optional - for debugging/analytics)
"""
{
    "_id": ObjectId,
    "guild_id": "123456789",
    "user_id": "987654321",
    "xp_change": 20,                   # XP gained/lost
    "reason": "message",               # message, bonus, admin_add, admin_remove
    "timestamp": "2025-10-29T12:00:00Z"
}

Indexes:
- guild_id + user_id + timestamp - for user XP history
"""


# XP and Level Calculation Formulas

def calculate_level_from_xp(xp: int) -> int:
    """Calculate level from total XP (Nova System).
    
    Formula: Level = floor(XP / 100)
    Each level requires 100 XP more than the previous.
    
    Examples:
    - 0-99 XP = Level 0
    - 100-199 XP = Level 1
    - 200-299 XP = Level 2
    - 1000-1099 XP = Level 10
    - 5000-5099 XP = Level 50
    """
    return int(xp // 100)


def calculate_xp_for_level(level: int) -> int:
    """Calculate XP required to reach a level (Nova System).
    
    Formula: XP = Level × 100
    
    Examples:
    - Level 1 = 100 XP
    - Level 5 = 500 XP
    - Level 10 = 1,000 XP
    - Level 20 = 2,000 XP
    - Level 50 = 5,000 XP
    - Level 100 = 10,000 XP
    """
    return level * 100


def calculate_xp_for_next_level(current_level: int) -> int:
    """Calculate XP needed for next level."""
    return calculate_xp_for_level(current_level + 1)


def calculate_progress_to_next_level(current_xp: int, current_level: int) -> dict:
    """Calculate progress percentage to next level (Nova System).
    
    Returns:
        dict with current_xp, needed_xp, next_level_xp, percentage
    """
    current_level_xp = calculate_xp_for_level(current_level)
    next_level_xp = calculate_xp_for_level(current_level + 1)
    
    xp_in_current_level = current_xp - current_level_xp
    xp_needed_for_level = 100  # Always 100 XP per level in Nova system
    
    percentage = (xp_in_current_level / xp_needed_for_level) * 100 if xp_needed_for_level > 0 else 100
    
    return {
        "current_xp": xp_in_current_level,
        "needed_xp": xp_needed_for_level,
        "next_level_xp": next_level_xp,
        "percentage": min(100, percentage)
    }


# Example usage:
"""
# Add XP to user
user_data = await db.user_levels.find_one({"guild_id": guild_id, "user_id": user_id})
if not user_data:
    user_data = {
        "guild_id": guild_id,
        "user_id": user_id,
        "xp": 0,
        "level": 0,
        "messages": 0,
        "last_xp_time": None,
        "total_xp": 0,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }

# Add XP
old_level = user_data["level"]
user_data["xp"] += 20
user_data["messages"] += 1
user_data["total_xp"] += 20
user_data["last_xp_time"] = datetime.utcnow().isoformat()
user_data["updated_at"] = datetime.utcnow().isoformat()

# Calculate new level
new_level = calculate_level_from_xp(user_data["xp"])
user_data["level"] = new_level

# Check if leveled up
if new_level > old_level:
    print(f"Level up! {old_level} -> {new_level}")

# Save to database
await db.user_levels.update_one(
    {"guild_id": guild_id, "user_id": user_id},
    {"$set": user_data},
    upsert=True
)

# Get leaderboard
leaderboard = await db.user_levels.find({"guild_id": guild_id}).sort("xp", -1).limit(10).to_list(length=None)
"""


# Validation functions

def validate_user_level(data: dict) -> bool:
    """Validate user level document."""
    required = ["guild_id", "user_id", "xp", "level", "messages"]
    return all(k in data for k in required)


def validate_guild_config(data: dict) -> bool:
    """Validate guild level config."""
    required = ["guild_id"]
    return "guild_id" in data


def validate_level_reward(data: dict) -> bool:
    """Validate level reward document."""
    required = ["guild_id", "level", "role_id"]
    return all(k in data for k in required)
