"""
Localization Package for Kingdom-77 Bot

Provides multi-language support for the bot and dashboard.
"""

from .i18n import (
    I18nManager,
    i18n_manager,
    t,
    translated_command
)

__all__ = [
    'I18nManager',
    'i18n_manager',
    't',
    'translated_command'
]
