"""
Moderation Database Schema for Kingdom-77 Bot v3.0
===================================================
MongoDB collections structure for moderation system
"""

# Collection: warnings
"""
{
    "_id": ObjectId,
    "guild_id": "123456789",           # Server ID
    "user_id": "987654321",            # Warned user ID
    "moderator_id": "111222333",       # Moderator who issued warning
    "warning_id": "warn_abc123",       # Unique warning ID
    "reason": "Spam messages",         # Warning reason
    "timestamp": "2025-10-29T12:00:00Z",  # ISO format
    "active": true,                    # false if cleared
    "cleared_by": null,                # Moderator who cleared (if any)
    "cleared_at": null                 # When cleared (if any)
}

Indexes:
- guild_id + user_id (compound) - for fast user warning lookup
- warning_id (unique) - for direct warning access
- guild_id + active - for active warnings count
"""

# Collection: mod_actions
"""
{
    "_id": ObjectId,
    "guild_id": "123456789",           # Server ID
    "action_id": "action_xyz456",      # Unique action ID
    "action_type": "mute",             # warn, mute, unmute, kick, ban, unban
    "user_id": "987654321",            # Target user ID
    "user_tag": "User#1234",           # Username for logs
    "moderator_id": "111222333",       # Moderator who took action
    "moderator_tag": "Mod#5678",       # Mod username
    "reason": "Inappropriate behavior", # Action reason
    "duration": 3600,                  # Duration in seconds (for mute)
    "timestamp": "2025-10-29T12:00:00Z",  # When action was taken
    "expires_at": "2025-10-29T13:00:00Z", # When action expires (for temp actions)
    "active": true,                    # false if action ended/revoked
    "ended_by": null,                  # Who ended the action early
    "ended_at": null                   # When action was ended early
}

Indexes:
- guild_id + user_id (compound) - for user history
- action_id (unique) - for direct access
- guild_id + timestamp - for logs chronological order
- expires_at + active - for finding expired temp actions
"""

# Collection: guild_mod_config
"""
{
    "_id": ObjectId,
    "guild_id": "123456789",           # Server ID
    "mod_log_channel": "999888777",    # Channel for mod logs
    "auto_mod_enabled": false,         # Auto-moderation (future)
    "warn_threshold": 3,               # Warnings before auto-action
    "warn_action": "mute",             # Action at threshold: mute, kick, ban
    "warn_action_duration": 3600,      # Duration for auto-action
    "mute_role": "666555444",          # Role for muted users
    "mod_roles": ["123", "456"],       # Roles allowed to moderate
    "settings": {
        "log_warnings": true,
        "log_mutes": true,
        "log_kicks": true,
        "log_bans": true,
        "dm_on_action": true,          # DM user when actioned
        "require_reason": true         # Require reason for actions
    },
    "updated_at": "2025-10-29T12:00:00Z"
}

Indexes:
- guild_id (unique) - one config per guild
"""

# Collection: temp_actions (for tracking temporary mutes/bans)
"""
{
    "_id": ObjectId,
    "guild_id": "123456789",
    "user_id": "987654321",
    "action_type": "mute",             # mute, ban
    "action_id": "action_xyz456",      # Reference to mod_actions
    "expires_at": "2025-10-29T13:00:00Z",
    "task_id": "task_123",             # Background task ID
    "completed": false
}

Indexes:
- guild_id + user_id + action_type (compound) - for finding active actions
- expires_at + completed - for expired actions cleanup
"""


# Helper functions for schema validation

def validate_warning(data: dict) -> bool:
    """Validate warning document."""
    required = ["guild_id", "user_id", "moderator_id", "warning_id", "reason", "timestamp"]
    return all(k in data for k in required)


def validate_mod_action(data: dict) -> bool:
    """Validate mod action document."""
    required = ["guild_id", "action_id", "action_type", "user_id", "moderator_id", "reason", "timestamp"]
    valid_types = ["warn", "mute", "unmute", "kick", "ban", "unban"]
    return (
        all(k in data for k in required) and
        data.get("action_type") in valid_types
    )


def validate_guild_config(data: dict) -> bool:
    """Validate guild mod config."""
    required = ["guild_id"]
    return all(k in data for k in required)


# Example usage:
"""
# Create warning
warning = {
    "guild_id": "123456789",
    "user_id": "987654321",
    "moderator_id": "111222333",
    "warning_id": f"warn_{uuid.uuid4().hex[:8]}",
    "reason": "Spam",
    "timestamp": datetime.utcnow().isoformat(),
    "active": True,
    "cleared_by": None,
    "cleared_at": None
}

# Insert to MongoDB
await db.warnings.insert_one(warning)

# Get user warnings
warnings = await db.warnings.find({
    "guild_id": guild_id,
    "user_id": user_id,
    "active": True
}).to_list(length=None)

# Clear warning
await db.warnings.update_one(
    {"warning_id": warning_id},
    {"$set": {
        "active": False,
        "cleared_by": moderator_id,
        "cleared_at": datetime.utcnow().isoformat()
    }}
)
"""
