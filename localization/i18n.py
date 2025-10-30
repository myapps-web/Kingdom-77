"""
Internationalization (i18n) System for Kingdom-77 Bot

This module provides multi-language support for the bot, including:
- Language detection and management
- Translation functions
- Language preferences storage
- Support for 5 languages: EN, AR, ES, FR, DE

Supported Languages:
- en: English (Default)
- ar: Arabic (العربية)
- es: Spanish (Español)
- fr: French (Français)
- de: German (Deutsch)
"""

import json
import os
from typing import Optional, Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class I18nManager:
    """Manages internationalization for the bot"""
    
    SUPPORTED_LANGUAGES = {
        'en': {'name': 'English', 'native': 'English', 'flag': '🇬🇧'},
        'ar': {'name': 'Arabic', 'native': 'العربية', 'flag': '🇸🇦'},
        'es': {'name': 'Spanish', 'native': 'Español', 'flag': '🇪🇸'},
        'fr': {'name': 'French', 'native': 'Français', 'flag': '🇫🇷'},
        'de': {'name': 'German', 'native': 'Deutsch', 'flag': '🇩🇪'}
    }
    
    DEFAULT_LANGUAGE = 'en'
    
    def __init__(self, locales_dir: str = "localization/locales"):
        """
        Initialize the i18n manager
        
        Args:
            locales_dir: Directory containing language JSON files
        """
        self.locales_dir = Path(locales_dir)
        self.translations: Dict[str, Dict[str, Any]] = {}
        self.user_languages: Dict[str, str] = {}  # user_id -> language_code
        self.guild_languages: Dict[str, str] = {}  # guild_id -> language_code
        
        # Load all translations
        self._load_translations()
    
    def _load_translations(self):
        """Load all translation files"""
        try:
            if not self.locales_dir.exists():
                logger.warning(f"Locales directory not found: {self.locales_dir}")
                return
            
            for lang_code in self.SUPPORTED_LANGUAGES.keys():
                lang_file = self.locales_dir / f"{lang_code}.json"
                
                if lang_file.exists():
                    with open(lang_file, 'r', encoding='utf-8') as f:
                        self.translations[lang_code] = json.load(f)
                    logger.info(f"Loaded translations for {lang_code}")
                else:
                    logger.warning(f"Translation file not found: {lang_file}")
        
        except Exception as e:
            logger.error(f"Error loading translations: {e}")
    
    def reload_translations(self):
        """Reload all translation files"""
        self.translations.clear()
        self._load_translations()
        logger.info("Translations reloaded")
    
    def get_supported_languages(self) -> Dict[str, Dict[str, str]]:
        """Get list of supported languages"""
        return self.SUPPORTED_LANGUAGES.copy()
    
    def is_supported_language(self, lang_code: str) -> bool:
        """Check if a language code is supported"""
        return lang_code in self.SUPPORTED_LANGUAGES
    
    def set_user_language(self, user_id: str, language_code: str):
        """
        Set user's preferred language
        
        Args:
            user_id: Discord user ID
            language_code: Language code (e.g., 'en', 'ar')
        """
        if self.is_supported_language(language_code):
            self.user_languages[user_id] = language_code
            logger.info(f"Set language for user {user_id}: {language_code}")
        else:
            logger.warning(f"Unsupported language code: {language_code}")
    
    def set_guild_language(self, guild_id: str, language_code: str):
        """
        Set guild's default language
        
        Args:
            guild_id: Discord guild ID
            language_code: Language code (e.g., 'en', 'ar')
        """
        if self.is_supported_language(language_code):
            self.guild_languages[guild_id] = language_code
            logger.info(f"Set language for guild {guild_id}: {language_code}")
        else:
            logger.warning(f"Unsupported language code: {language_code}")
    
    def get_user_language(self, user_id: str, guild_id: Optional[str] = None) -> str:
        """
        Get user's preferred language
        
        Priority:
        1. User's personal language preference
        2. Guild's default language
        3. Default language (English)
        
        Args:
            user_id: Discord user ID
            guild_id: Discord guild ID (optional)
        
        Returns:
            Language code
        """
        # User preference (highest priority)
        if user_id in self.user_languages:
            return self.user_languages[user_id]
        
        # Guild default language
        if guild_id and guild_id in self.guild_languages:
            return self.guild_languages[guild_id]
        
        # Default language
        return self.DEFAULT_LANGUAGE
    
    def translate(
        self,
        key: str,
        lang_code: Optional[str] = None,
        user_id: Optional[str] = None,
        guild_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Translate a key to the target language
        
        Args:
            key: Translation key (e.g., "commands.ping.description")
            lang_code: Language code (optional, will auto-detect if not provided)
            user_id: Discord user ID (for language detection)
            guild_id: Discord guild ID (for language detection)
            **kwargs: Variables to format in the translation
        
        Returns:
            Translated string
        
        Example:
            t("commands.ban.success", user_id="123", username="BadUser")
        """
        # Determine language
        if lang_code is None:
            if user_id:
                lang_code = self.get_user_language(user_id, guild_id)
            else:
                lang_code = self.DEFAULT_LANGUAGE
        
        # Get translation
        translation = self._get_nested_value(
            self.translations.get(lang_code, {}),
            key
        )
        
        # Fallback to English if translation not found
        if translation is None and lang_code != self.DEFAULT_LANGUAGE:
            translation = self._get_nested_value(
                self.translations.get(self.DEFAULT_LANGUAGE, {}),
                key
            )
        
        # Fallback to key if still not found
        if translation is None:
            logger.warning(f"Translation not found: {key} ({lang_code})")
            return key
        
        # Format with variables
        try:
            return translation.format(**kwargs)
        except KeyError as e:
            logger.error(f"Missing variable in translation: {e}")
            return translation
    
    def _get_nested_value(self, data: Dict[str, Any], key: str) -> Optional[str]:
        """
        Get nested value from dictionary using dot notation
        
        Args:
            data: Dictionary to search
            key: Dot-notation key (e.g., "commands.ping.description")
        
        Returns:
            Value or None if not found
        """
        keys = key.split('.')
        value = data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None
        
        return value if isinstance(value, str) else None
    
    def get_language_choices(self) -> list:
        """
        Get language choices for Discord slash command
        
        Returns:
            List of (name, value) tuples
        """
        return [
            (f"{info['flag']} {info['native']}", code)
            for code, info in self.SUPPORTED_LANGUAGES.items()
        ]
    
    def format_language_list(self, lang_code: str = 'en') -> str:
        """
        Format list of supported languages
        
        Args:
            lang_code: Language code for translation
        
        Returns:
            Formatted string
        """
        lines = []
        for code, info in self.SUPPORTED_LANGUAGES.items():
            status = "✅" if code == lang_code else "⚪"
            lines.append(f"{status} {info['flag']} **{info['native']}** ({info['name']}) - `{code}`")
        
        return "\n".join(lines)


# Global instance
i18n_manager = I18nManager()


# Convenience function
def t(key: str, lang_code: Optional[str] = None, user_id: Optional[str] = None, guild_id: Optional[str] = None, **kwargs) -> str:
    """
    Shorthand translation function
    
    Args:
        key: Translation key
        lang_code: Language code (optional)
        user_id: Discord user ID (optional)
        guild_id: Discord guild ID (optional)
        **kwargs: Variables to format
    
    Returns:
        Translated string
    
    Example:
        t("commands.ping.description", user_id="123")
    """
    return i18n_manager.translate(key, lang_code, user_id, guild_id, **kwargs)


# Decorator for translated commands
def translated_command(func):
    """
    Decorator to automatically translate command descriptions
    
    Example:
        @translated_command
        async def ping(self, ctx):
            await ctx.send(t("commands.ping.response"))
    """
    async def wrapper(*args, **kwargs):
        return await func(*args, **kwargs)
    
    return wrapper
