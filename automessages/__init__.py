"""
Auto-Messages System for Kingdom-77 Bot

This module provides automatic message responses with triggers and interactions.

Features:
- Keyword triggers (case-sensitive, exact match options)
- Button triggers (custom_id based)
- Dropdown triggers (value based)
- Rich embed builder (Nova style)
- Multiple buttons per message (up to 25)
- Dropdown menus (up to 25 options)
- Role permissions & Channel restrictions
- Cooldown system
- Auto-delete messages
- Usage statistics
"""

from .automessage_system import AutoMessageSystem

__all__ = ["AutoMessageSystem"]
