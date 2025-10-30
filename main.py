"""
Kingdom-77 Discord Translation Bot
===================================
A multi-language Discord bot with translation, rating system, and role-based permissions.

Features:
- Automatic message translation based on channel language settings
- User rating system for bot feedback
- Role-based permission management for language settings
- Support for 7 languages: Arabic, English, Turkish, Japanese, French, Korean, Italian
"""

# ============================================================================
# IMPORTS
# ============================================================================

import os
import json
import logging
from typing import Dict
from datetime import datetime

from dotenv import load_dotenv
from langdetect import detect, LangDetectException
from deep_translator import GoogleTranslator
import discord
import asyncio
from discord import app_commands
from discord.ext import commands, tasks

# Import MongoDB database module
from database import db, init_database, close_database

# Import Redis cache module
from cache import cache, init_cache, close_cache


# ============================================================================
# LOGGING SETUP
# ============================================================================

# Initialize logging early to avoid NameError
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


# ============================================================================
# CONFIGURATION
# ============================================================================

# Bot version
VERSION = "3.6"

# Load environment variables
load_dotenv()

TOKEN = os.getenv("TOKEN") or os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")
BOT_OWNER_ID = int(os.getenv("BOT_OWNER_ID", "1234567890"))  # Will use env var if available

# Bot control state
bot_disabled = False  # When True, all commands except /control are disabled
priority_guilds = []  # List of guild IDs for fast command sync

def check_bot_enabled():
    """Check if bot is enabled. Returns True if enabled or user is owner."""
    return not bot_disabled

def load_priority_guilds():
    """Load priority guilds from secret file or local file."""
    global priority_guilds
    priority_guilds = []
    
    # Try to load from Render secret file first
    secret_file = '/etc/secrets/priority_guilds.txt'
    if os.path.exists(secret_file):
        try:
            with open(secret_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and line.isdigit():
                        priority_guilds.append(int(line))
            logger.info(f"✅ Loaded {len(priority_guilds)} priority guilds from secret file")
            return priority_guilds
        except Exception as e:
            logger.error(f"❌ Error loading secret file: {e}")
    
    # Fallback to local file
    local_file = os.path.join(os.path.dirname(__file__), 'priority_guilds.txt')
    if os.path.exists(local_file):
        try:
            with open(local_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and line.isdigit():
                        priority_guilds.append(int(line))
            logger.info(f"✅ Loaded {len(priority_guilds)} priority guilds from local file")
        except Exception as e:
            logger.error(f"❌ Error loading local file: {e}")
    
    return priority_guilds

def save_priority_guilds():
    """Save priority guilds to local file."""
    local_file = os.path.join(os.path.dirname(__file__), 'priority_guilds.txt')
    try:
        with open(local_file, 'w', encoding='utf-8') as f:
            f.write("# Priority Guilds for Fast Command Sync\n")
            f.write("# Add one guild ID per line\n\n")
            for guild_id in priority_guilds:
                f.write(f"{guild_id}\n")
        logger.info(f"✅ Saved {len(priority_guilds)} priority guilds to local file")
        return True
    except Exception as e:
        logger.error(f"❌ Error saving priority guilds: {e}")
        return False

# File paths for data persistence
# Use /data for Render persistent disk, fallback to local data/
if os.getenv("DATA_DIR"):
    # Render with persistent disk
    DATA_DIR = os.getenv("DATA_DIR")
elif os.path.dirname(__file__):
    BASE_DIR = os.path.dirname(__file__)
    DATA_DIR = os.path.join(BASE_DIR, 'data')
else:
    DATA_DIR = 'data'

CHANNELS_FILE = os.path.join(DATA_DIR, 'channels.json')
RATINGS_FILE = os.path.join(DATA_DIR, 'ratings.json')
ROLES_FILE = os.path.join(DATA_DIR, 'allowed_roles.json')
ROLE_LANGUAGES_FILE = os.path.join(DATA_DIR, 'role_languages.json')
ROLE_PERMISSIONS_FILE = os.path.join(DATA_DIR, 'role_permissions.json')
SERVERS_FILE = os.path.join(DATA_DIR, 'servers.json')
TRANSLATION_STATS_FILE = os.path.join(DATA_DIR, 'translation_stats.json')

# Bot stats file (local only)
if os.path.dirname(__file__):
    BASE_DIR = os.path.dirname(__file__)
    BOT_STATS_FILE = os.path.join(BASE_DIR, 'bot_stats.txt')
else:
    BOT_STATS_FILE = 'bot_stats.txt'

# Create data directory if it doesn't exist
os.makedirs(DATA_DIR, exist_ok=True)
logger.info(f"📁 Data directory: {DATA_DIR}")

# Supported languages for translation
SUPPORTED = {
    'ar': 'Arabic',
    'en': 'English',
    'tr': 'Turkish',
    'ja': 'Japanese',
    'fr': 'French',
    'ko': 'Korean',
    'it': 'Italian',
    'zh-CN': 'Chinese'
}

# Extended language names for better detection display
LANGUAGE_NAMES = {
    'ar': 'Arabic', 'en': 'English', 'tr': 'Turkish', 'ja': 'Japanese',
    'fr': 'French', 'ko': 'Korean', 'it': 'Italian', 'es': 'Spanish',
    'de': 'German', 'pt': 'Portuguese', 'ru': 'Russian', 'zh-cn': 'Chinese',
    'zh-tw': 'Chinese (Traditional)', 'hi': 'Hindi', 'bn': 'Bengali',
    'ur': 'Urdu', 'id': 'Indonesian', 'ms': 'Malay', 'th': 'Thai',
    'vi': 'Vietnamese', 'tl': 'Filipino', 'nl': 'Dutch', 'pl': 'Polish',
    'uk': 'Ukrainian', 'ro': 'Romanian', 'el': 'Greek', 'cs': 'Czech',
    'sv': 'Swedish', 'da': 'Danish', 'fi': 'Finnish', 'no': 'Norwegian',
    'he': 'Hebrew', 'fa': 'Persian', 'sw': 'Swahili', 'so': 'Somali',
    'auto': 'Auto-detected'
}

# Bot permissions that can be assigned to roles
BOT_PERMISSIONS = {
    'setlang': {
        'name': 'Set Channel Language',
        'description': 'Can set default language for channels',
        'emoji': '🌍',
        'command': '/channel addlang',
        'category': 'Channel Management'
    },
    'removelang': {
        'name': 'Remove Channel Language',
        'description': 'Can remove language settings from channels',
        'emoji': '🗑️',
        'command': '/channel deletelang',
        'category': 'Channel Management'
    },
    'set_quality': {
        'name': 'Set Translation Quality',
        'description': 'Can change translation quality mode for channels',
        'emoji': '⚡',
        'command': '/channel quality',
        'category': 'Channel Management'
    },
    'setrolelang': {
        'name': 'Set Role Language',
        'description': 'Can assign default languages to roles',
        'emoji': '🎭',
        'command': '/role setlang',
        'category': 'Role Management'
    },
    'removerolelang': {
        'name': 'Remove Role Language',
        'description': 'Can remove language assignments from roles',
        'emoji': '🗑️',
        'command': '/role removelang',
        'category': 'Role Management'
    },
    'manage_roles': {
        'name': 'Manage Bot Roles',
        'description': 'Can add/remove allowed roles and set permissions',
        'emoji': '👥',
        'command': '/role add, /role remove',
        'category': 'Role Management'
    }
}

# Translation messages for different languages
TRANSLATION_MESSAGES = {
    'ar': {
        'same_language': '⚠️ هذه الرسالة بالفعل باللغة العربية.',
        'same_language_title': 'نفس اللغة',
        'translation_failed': '❌ فشل ترجمة الرسالة. الرجاء المحاولة مرة أخرى.',
        'translation_failed_title': 'فشلت الترجمة',
        'translation_error': '❌ حدث خطأ أثناء الترجمة:',
        'translation_error_title': 'خطأ في الترجمة',
        'original_message': '📝 الرسالة الأصلية',
        'to': 'إلى'
    },
    'en': {
        'same_language': '⚠️ This message is already in English.',
        'same_language_title': 'Same Language',
        'translation_failed': '❌ Could not translate the message. Please try again.',
        'translation_failed_title': 'Translation Failed',
        'translation_error': '❌ An error occurred during translation:',
        'translation_error_title': 'Translation Error',
        'original_message': '📝 Original Message',
        'to': 'to'
    },
    'tr': {
        'same_language': '⚠️ Bu mesaj zaten Türkçe.',
        'same_language_title': 'Aynı Dil',
        'translation_failed': '❌ Mesaj çevrilemedi. Lütfen tekrar deneyin.',
        'translation_failed_title': 'Çeviri Başarısız',
        'translation_error': '❌ Çeviri sırasında bir hata oluştu:',
        'translation_error_title': 'Çeviri Hatası',
        'original_message': '📝 Orijinal Mesaj',
        'to': 'için'
    },
    'ja': {
        'same_language': '⚠️ このメッセージはすでに日本語です。',
        'same_language_title': '同じ言語',
        'translation_failed': '❌ メッセージを翻訳できませんでした。もう一度お試しください。',
        'translation_failed_title': '翻訳失敗',
        'translation_error': '❌ 翻訳中にエラーが発生しました：',
        'translation_error_title': '翻訳エラー',
        'original_message': '📝 元のメッセージ',
        'to': 'へ'
    },
    'fr': {
        'same_language': '⚠️ Ce message est déjà en français.',
        'same_language_title': 'Même Langue',
        'translation_failed': '❌ Impossible de traduire le message. Veuillez réessayer.',
        'translation_failed_title': 'Échec de la Traduction',
        'translation_error': '❌ Une erreur s\'est produite lors de la traduction :',
        'translation_error_title': 'Erreur de Traduction',
        'original_message': '📝 Message Original',
        'to': 'en'
    },
    'ko': {
        'same_language': '⚠️ 이 메시지는 이미 한국어입니다.',
        'same_language_title': '같은 언어',
        'translation_failed': '❌ 메시지를 번역할 수 없습니다. 다시 시도해주세요.',
        'translation_failed_title': '번역 실패',
        'translation_error': '❌ 번역 중 오류가 발생했습니다:',
        'translation_error_title': '번역 오류',
        'original_message': '📝 원본 메시지',
        'to': '로'
    },
    'it': {
        'same_language': '⚠️ Questo messaggio è già in italiano.',
        'same_language_title': 'Stessa Lingua',
        'translation_failed': '❌ Impossibile tradurre il messaggio. Riprova.',
        'translation_failed_title': 'Traduzione Fallita',
        'translation_error': '❌ Si è verificato un errore durante la traduzione:',
        'translation_error_title': 'Errore di Traduzione',
        'original_message': '📝 Messaggio Originale',
        'to': 'in'
    },
    'zh-CN': {
        'same_language': '⚠️ 此消息已经是中文。',
        'same_language_title': '相同语言',
        'translation_failed': '❌ 无法翻译消息。请重试。',
        'translation_failed_title': '翻译失败',
        'translation_error': '❌ 翻译时发生错误：',
        'translation_error_title': '翻译错误',
        'original_message': '📝 原始消息',
        'to': '到'
    }
}

def get_translation_message(lang_code: str, key: str) -> str:
    """Get translated message for a specific language.
    If the language is not pre-defined, automatically translates from English."""
    
    # If language is pre-defined, use it
    if lang_code in TRANSLATION_MESSAGES and key in TRANSLATION_MESSAGES[lang_code]:
        return TRANSLATION_MESSAGES[lang_code][key]
    
    # For languages not pre-defined, translate from English automatically
    if lang_code not in TRANSLATION_MESSAGES:
        english_message = TRANSLATION_MESSAGES['en'].get(key, '')
        if english_message:
            try:
                # Use GoogleTranslator to translate the message to the target language
                translated = GoogleTranslator(source='en', target=lang_code).translate(english_message)
                return translated
            except Exception as e:
                logger.warning(f"Failed to auto-translate message '{key}' to '{lang_code}': {e}")
                # Fallback to English
                return english_message
    
    # Final fallback to English
    return TRANSLATION_MESSAGES['en'].get(key, '')


# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================

def load_channels() -> Dict[str, dict]:
    """Load channel language configurations from file.
    Format: {
        channel_id: {
            'primary': 'lang_code',
            'secondary': 'lang_code' (optional),
            'blacklisted_languages': ['lang1', 'lang2'] (optional),
            'translation_quality': 'fast' | 'quality' | 'auto' (optional)
        }
    }
    Or legacy format: {channel_id: 'lang_code'} which gets converted.
    """
    try:
        with open(CHANNELS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Convert legacy format (string) to new format (dict)
            converted_data = {}
            for channel_id, value in data.items():
                if isinstance(value, str):
                    # Legacy format: just a string language code
                    converted_data[channel_id] = {
                        'primary': value,
                        'secondary': None,
                        'blacklisted_languages': [],
                        'translation_quality': 'fast'
                    }
                elif isinstance(value, dict):
                    # New format: dict with primary and optional secondary + blacklist + quality
                    converted_data[channel_id] = {
                        'primary': value.get('primary'),
                        'secondary': value.get('secondary'),
                        'blacklisted_languages': value.get('blacklisted_languages', []),
                        'translation_quality': value.get('translation_quality', 'fast')
                    }
                else:
                    logger.warning(f"Unknown format for channel {channel_id}, skipping")
            logger.info(f"Loaded {len(converted_data)} channel configurations from {CHANNELS_FILE}")
            return converted_data
    except FileNotFoundError:
        logger.info(f"No channels.json found at {CHANNELS_FILE}, starting fresh")
        return {}
    except Exception as e:
        logger.error(f"Error loading channels from {CHANNELS_FILE}: {e}")
        return {}


def load_ratings() -> Dict[str, dict]:
    """Load user ratings from file."""
    try:
        with open(RATINGS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.info(f"Loaded {len(data)} ratings from {RATINGS_FILE}")
            return data
    except FileNotFoundError:
        logger.info(f"No ratings.json found at {RATINGS_FILE}, starting fresh")
        return {}
    except Exception as e:
        logger.error(f"Error loading ratings from {RATINGS_FILE}: {e}")
        return {}


def load_allowed_roles() -> Dict[str, list]:
    """Load allowed roles for each guild from file."""
    try:
        with open(ROLES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.info(f"Loaded allowed roles for {len(data)} guilds from {ROLES_FILE}")
            return data
    except FileNotFoundError:
        logger.info(f"No allowed_roles.json found at {ROLES_FILE}, starting fresh")
        return {}
    except Exception as e:
        logger.error(f"Error loading allowed roles from {ROLES_FILE}: {e}")
        return {}


def load_role_languages() -> Dict[str, Dict[str, str]]:
    """Load role language mappings from file.
    Format: {'guild_id': {'role_id': 'language_code'}}
    """
    try:
        with open(ROLE_LANGUAGES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.info(f"Loaded role languages for {len(data)} guilds from {ROLE_LANGUAGES_FILE}")
            return data
    except FileNotFoundError:
        logger.info(f"No role_languages.json found at {ROLE_LANGUAGES_FILE}, starting fresh")
        return {}
    except Exception as e:
        logger.error(f"Error loading role languages from {ROLE_LANGUAGES_FILE}: {e}")
        return {}


def load_role_permissions() -> Dict[str, Dict[str, list]]:
    """Load role permissions from file.
    Format: {'guild_id': {'role_id': ['permission1', 'permission2']}}
    """
    try:
        with open(ROLE_PERMISSIONS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.info(f"Loaded role permissions for {len(data)} guilds from {ROLE_PERMISSIONS_FILE}")
            return data
    except FileNotFoundError:
        logger.info(f"No role_permissions.json found at {ROLE_PERMISSIONS_FILE}, starting fresh")
        return {}
    except Exception as e:
        logger.error(f"Error loading role permissions from {ROLE_PERMISSIONS_FILE}: {e}")
        return {}


def load_servers() -> Dict[str, dict]:
    """Load server information from file.
    Format: {'guild_id': {'name': 'Server Name', 'joined_at': 'ISO timestamp', 'active': True, 'left_at': None}}
    """
    try:
        with open(SERVERS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.info(f"Loaded {len(data)} server records from {SERVERS_FILE}")
            return data
    except FileNotFoundError:
        logger.info(f"No servers.json found at {SERVERS_FILE}, starting fresh")
        return {}
    except Exception as e:
        logger.error(f"Error loading servers from {SERVERS_FILE}: {e}")
        return {}


# ============================================================================
# DATA SAVING FUNCTIONS (ASYNC)
# ============================================================================

async def save_channels(data: Dict[str, dict]):
    """Save channel configurations to MongoDB and JSON (backup)."""
    # Try MongoDB first
    try:
        import database.mongodb as mongodb_module
        if mongodb_module.db and mongodb_module.db.client:
            for channel_id, settings in data.items():
                await save_channel_to_mongodb(channel_id, settings)
            logger.info(f"✅ Saved {len(data)} channel configurations to MongoDB")
    except Exception as e:
        logger.error(f"Error saving channels to MongoDB: {e}")
    
    # Also save to JSON as backup
    loop = asyncio.get_running_loop()
    def _write(d):
        tmp = CHANNELS_FILE + '.tmp'
        try:
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(d, f, ensure_ascii=False, indent=2)
            os.replace(tmp, CHANNELS_FILE)
            logger.info(f"Saved {len(d)} channel configurations to {CHANNELS_FILE} (backup)")
        except Exception as e:
            logger.error(f"Error saving to {CHANNELS_FILE}: {e}")

    await loop.run_in_executor(None, _write, data)


async def save_ratings(data: Dict[str, dict]):
    """Save user ratings to MongoDB and JSON (backup)."""
    # Try MongoDB first
    try:
        import database.mongodb as mongodb_module
        if mongodb_module.db and mongodb_module.db.client:
            for user_id, rating_data in data.items():
                await save_rating_to_mongodb(user_id, rating_data)
            logger.info(f"✅ Saved {len(data)} ratings to MongoDB")
    except Exception as e:
        logger.error(f"Error saving ratings to MongoDB: {e}")
    
    # Also save to JSON as backup
    loop = asyncio.get_running_loop()
    def _write(d):
        tmp = RATINGS_FILE + '.tmp'
        try:
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(d, f, ensure_ascii=False, indent=2)
            os.replace(tmp, RATINGS_FILE)
            logger.info(f"Saved {len(d)} ratings to {RATINGS_FILE} (backup)")
        except Exception as e:
            logger.error(f"Error saving to {RATINGS_FILE}: {e}")

    await loop.run_in_executor(None, _write, data)


async def save_allowed_roles(data: Dict[str, list]):
    """Save allowed roles to MongoDB and JSON (backup)."""
    # Try MongoDB first
    try:
        import database.mongodb as mongodb_module
        if mongodb_module.db and mongodb_module.db.client:
            for guild_id, roles in data.items():
                await save_guild_to_mongodb(guild_id, {
                    "guild_id": guild_id,
                    "roles.allowed_roles": roles
                })
            logger.info(f"✅ Saved allowed roles for {len(data)} guilds to MongoDB")
    except Exception as e:
        logger.error(f"Error saving allowed roles to MongoDB: {e}")
    
    # Also save to JSON as backup
    loop = asyncio.get_running_loop()
    def _write(d):
        tmp = ROLES_FILE + '.tmp'
        try:
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(d, f, ensure_ascii=False, indent=2)
            os.replace(tmp, ROLES_FILE)
            logger.info(f"Saved allowed roles for {len(d)} guilds to {ROLES_FILE} (backup)")
        except Exception as e:
            logger.error(f"Error saving to {ROLES_FILE}: {e}")

    await loop.run_in_executor(None, _write, data)


async def save_role_languages(data: Dict[str, Dict[str, str]]):
    """Save role language mappings to MongoDB and JSON (backup)."""
    # Try MongoDB first
    try:
        import database.mongodb as mongodb_module
        if mongodb_module.db and mongodb_module.db.client:
            for guild_id, role_langs in data.items():
                await save_guild_to_mongodb(guild_id, {
                    "guild_id": guild_id,
                    "roles.role_languages": role_langs
                })
            logger.info(f"✅ Saved role languages for {len(data)} guilds to MongoDB")
    except Exception as e:
        logger.error(f"Error saving role languages to MongoDB: {e}")
    
    # Also save to JSON as backup
    loop = asyncio.get_running_loop()
    def _write(d):
        tmp = ROLE_LANGUAGES_FILE + '.tmp'
        try:
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(d, f, ensure_ascii=False, indent=2)
            os.replace(tmp, ROLE_LANGUAGES_FILE)
            logger.info(f"Saved role languages for {len(d)} guilds to {ROLE_LANGUAGES_FILE} (backup)")
        except Exception as e:
            logger.error(f"Error saving to {ROLE_LANGUAGES_FILE}: {e}")

    await loop.run_in_executor(None, _write, data)


async def save_role_permissions(data: Dict[str, Dict[str, list]]):
    """Save role permissions to MongoDB and JSON (backup)."""
    # Try MongoDB first
    try:
        import database.mongodb as mongodb_module
        if mongodb_module.db and mongodb_module.db.client:
            for guild_id, role_perms in data.items():
                await save_guild_to_mongodb(guild_id, {
                    "guild_id": guild_id,
                    "roles.role_permissions": role_perms
                })
            logger.info(f"✅ Saved role permissions for {len(data)} guilds to MongoDB")
    except Exception as e:
        logger.error(f"Error saving role permissions to MongoDB: {e}")
    
    # Also save to JSON as backup
    loop = asyncio.get_running_loop()
    def _write(d):
        tmp = ROLE_PERMISSIONS_FILE + '.tmp'
        try:
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(d, f, ensure_ascii=False, indent=2)
            os.replace(tmp, ROLE_PERMISSIONS_FILE)
            logger.info(f"Saved role permissions for {len(d)} guilds to {ROLE_PERMISSIONS_FILE} (backup)")
        except Exception as e:
            logger.error(f"Error saving to {ROLE_PERMISSIONS_FILE}: {e}")

    await loop.run_in_executor(None, _write, data)


async def save_servers(data: Dict[str, dict]):
    """Save server information to MongoDB and JSON (backup)."""
    # Try MongoDB first
    try:
        import database.mongodb as mongodb_module
        if mongodb_module.db and mongodb_module.db.client:
            for guild_id, server_info in data.items():
                await save_guild_to_mongodb(guild_id, {
                    "guild_id": guild_id,
                    "name": server_info.get('name'),
                    "joined_at": server_info.get('joined_at'),
                    "active": server_info.get('active', True),
                    "left_at": server_info.get('left_at')
                })
            logger.info(f"✅ Saved {len(data)} server records to MongoDB")
    except Exception as e:
        logger.error(f"Error saving servers to MongoDB: {e}")
    
    # Also save to JSON as backup
    loop = asyncio.get_running_loop()
    def _write(d):
        tmp = SERVERS_FILE + '.tmp'
        try:
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(d, f, ensure_ascii=False, indent=2)
            os.replace(tmp, SERVERS_FILE)
            logger.info(f"Saved {len(d)} server records to {SERVERS_FILE} (backup)")
        except Exception as e:
            logger.error(f"Error saving to {SERVERS_FILE}: {e}")
            try:
                with open(SERVERS_FILE, 'w', encoding='utf-8') as f:
                    json.dump(d, f, ensure_ascii=False, indent=2)
                logger.info(f"Fallback: Saved server records directly to {SERVERS_FILE}")
            except Exception as e2:
                logger.error(f"Fallback save also failed: {e2}")

    await loop.run_in_executor(None, _write, data)


# ============================================================================
# MONGODB HELPER FUNCTIONS (v3.0)
# ============================================================================

async def load_data_from_mongodb():
    """Load all data from MongoDB into global variables."""
    global channel_langs, bot_ratings, allowed_roles, role_languages, role_permissions, servers_data
    
    try:
        import database.mongodb as mongodb_module
        if not mongodb_module.db or not mongodb_module.db.client:
            logger.warning("MongoDB not connected, using empty data")
            channel_langs = {}
            bot_ratings = {}
            allowed_roles = {}
            role_languages = {}
            role_permissions = {}
            servers_data = {}
            return
        
        # Load channels from MongoDB
        channels_from_db = await mongodb_module.db.db.channels.find().to_list(length=None)
        channel_langs = {}
        for ch in channels_from_db:
            channel_id = ch.get('channel_id')
            if channel_id:
                channel_langs[channel_id] = {
                    'primary': ch.get('primary'),
                    'secondary': ch.get('secondary'),
                    'blacklisted_languages': ch.get('blacklisted_languages', []),
                    'translation_quality': ch.get('translation_quality', 'fast')
                }
        
        logger.info(f"✅ Loaded {len(channel_langs)} channels from MongoDB")
        
        # Load ratings from MongoDB
        ratings_from_db = await mongodb_module.db.db.ratings.find().to_list(length=None)
        bot_ratings = {}
        for rating in ratings_from_db:
            user_id = rating.get('user_id')
            if user_id:
                bot_ratings[user_id] = {
                    'rating': rating.get('rating'),
                    'comment': rating.get('comment', ''),
                    'timestamp': rating.get('timestamp')
                }
        
        logger.info(f"✅ Loaded {len(bot_ratings)} ratings from MongoDB")
        
        # Load guilds (for roles and settings)
        guilds_from_db = await mongodb_module.db.db.guilds.find().to_list(length=None)
        allowed_roles = {}
        role_languages = {}
        role_permissions = {}
        servers_data = {}
        
        for guild in guilds_from_db:
            guild_id = guild.get('guild_id')
            if not guild_id:
                continue
            
            # Allowed roles
            if 'roles' in guild and 'allowed_roles' in guild['roles']:
                allowed_roles[guild_id] = guild['roles']['allowed_roles']
            
            # Role languages
            if 'roles' in guild and 'role_languages' in guild['roles']:
                role_languages[guild_id] = guild['roles']['role_languages']
            
            # Role permissions
            if 'roles' in guild and 'role_permissions' in guild['roles']:
                role_permissions[guild_id] = guild['roles']['role_permissions']
            
            # Server data
            servers_data[guild_id] = {
                'name': guild.get('name', ''),
                'joined_at': guild.get('joined_at'),
                'active': guild.get('active', True),
                'left_at': guild.get('left_at')
            }
        
        logger.info(f"✅ Loaded data for {len(guilds_from_db)} guilds from MongoDB")
        
    except Exception as e:
        logger.error(f"❌ Error loading data from MongoDB: {e}")
        # Fallback to empty data
        channel_langs = {}
        bot_ratings = {}
        allowed_roles = {}
        role_languages = {}
        role_permissions = {}
        servers_data = {}


# ============================================================================
# CACHE LAYER (v3.0)
# ============================================================================

async def get_channel_settings_cached(channel_id: str) -> dict:
    """Get channel settings from cache or MongoDB.
    
    Args:
        channel_id: Discord channel ID
        
    Returns:
        Channel settings dict or None
    """
    # Try cache first
    if cache and cache.connected:
        cached = await cache.get_json(f"channel:{channel_id}")
        if cached:
            logger.debug(f"Cache HIT: channel:{channel_id}")
            return cached
        logger.debug(f"Cache MISS: channel:{channel_id}")
    
    # Load from MongoDB
    try:
        import database.mongodb as mongodb_module
        if mongodb_module.db and mongodb_module.db.client:
            doc = await mongodb_module.db.db.channels.find_one({"channel_id": channel_id})
            if doc:
                settings = {
                    'primary': doc.get('primary'),
                    'secondary': doc.get('secondary'),
                    'blacklisted_languages': doc.get('blacklisted_languages', []),
                    'translation_quality': doc.get('translation_quality', 'fast')
                }
                # Cache for 5 minutes
                if cache and cache.connected:
                    await cache.set_json(f"channel:{channel_id}", settings, ttl=300)
                return settings
    except Exception as e:
        logger.error(f"Error loading channel from MongoDB: {e}")
    
    return None


async def get_guild_settings_cached(guild_id: str) -> dict:
    """Get guild settings from cache or MongoDB.
    
    Args:
        guild_id: Discord guild ID
        
    Returns:
        Guild settings dict or None
    """
    # Try cache first
    if cache and cache.connected:
        cached = await cache.get_json(f"guild:{guild_id}")
        if cached:
            logger.debug(f"Cache HIT: guild:{guild_id}")
            return cached
        logger.debug(f"Cache MISS: guild:{guild_id}")
    
    # Load from MongoDB
    try:
        import database.mongodb as mongodb_module
        if mongodb_module.db and mongodb_module.db.client:
            doc = await mongodb_module.db.db.guilds.find_one({"guild_id": guild_id})
            if doc:
                # Cache for 10 minutes
                if cache and cache.connected:
                    await cache.set_json(f"guild:{guild_id}", doc, ttl=600)
                return doc
    except Exception as e:
        logger.error(f"Error loading guild from MongoDB: {e}")
    
    return None


async def invalidate_channel_cache(channel_id: str):
    """Invalidate channel settings cache."""
    if cache and cache.connected:
        await cache.delete(f"channel:{channel_id}")
        logger.debug(f"Invalidated cache: channel:{channel_id}")


async def invalidate_guild_cache(guild_id: str):
    """Invalidate guild settings cache."""
    if cache and cache.connected:
        await cache.delete(f"guild:{guild_id}")
        logger.debug(f"Invalidated cache: guild:{guild_id}")


# ============================================================================
# MONGODB SAVE OPERATIONS
# ============================================================================

async def save_channel_to_mongodb(channel_id: str, settings: dict):
    """Save single channel settings to MongoDB."""
    try:
        import database.mongodb as mongodb_module
        if not mongodb_module.db or not mongodb_module.db.client:
            logger.warning("MongoDB not connected, skipping save")
            return False
        
        await mongodb_module.db.db.channels.update_one(
            {"channel_id": channel_id},
            {
                "$set": {
                    "channel_id": channel_id,
                    "primary": settings.get('primary'),
                    "secondary": settings.get('secondary'),
                    "blacklisted_languages": settings.get('blacklisted_languages', []),
                    "translation_quality": settings.get('translation_quality', 'fast')
                }
            },
            upsert=True
        )
        
        # Invalidate cache
        await invalidate_channel_cache(channel_id)
        
        return True
    except Exception as e:
        logger.error(f"Error saving channel to MongoDB: {e}")
        return False


async def save_rating_to_mongodb(user_id: str, rating_data: dict):
    """Save user rating to MongoDB."""
    try:
        import database.mongodb as mongodb_module
        if not mongodb_module.db or not mongodb_module.db.client:
            logger.warning("MongoDB not connected, skipping save")
            return False
        
        await mongodb_module.db.db.ratings.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "user_id": user_id,
                    "rating": rating_data.get('rating'),
                    "comment": rating_data.get('comment', ''),
                    "timestamp": rating_data.get('timestamp')
                }
            },
            upsert=True
        )
        return True
    except Exception as e:
        logger.error(f"Error saving rating to MongoDB: {e}")
        return False


async def save_guild_to_mongodb(guild_id: str, guild_data: dict):
    """Save guild settings to MongoDB."""
    try:
        import database.mongodb as mongodb_module
        if not mongodb_module.db or not mongodb_module.db.client:
            logger.warning("MongoDB not connected, skipping save")
            return False
        
        await mongodb_module.db.db.guilds.update_one(
            {"guild_id": guild_id},
            {"$set": guild_data},
            upsert=True
        )
        return True
    except Exception as e:
        logger.error(f"Error saving guild to MongoDB: {e}")
        return False


async def delete_channel_from_mongodb(channel_id: str):
    """Delete channel from MongoDB."""
    try:
        import database.mongodb as mongodb_module
        if not mongodb_module.db or not mongodb_module.db.client:
            logger.warning("MongoDB not connected, skipping delete")
            return False
        
        await mongodb_module.db.db.channels.delete_one({"channel_id": channel_id})
        return True
    except Exception as e:
        logger.error(f"Error deleting channel from MongoDB: {e}")
        return False


def update_bot_stats():
    """Update bot statistics text file with comprehensive information."""
    try:
        # Ensure global variables are available
        if 'servers_data' not in globals() or 'bot_ratings' not in globals():
            logger.warning("Cannot update bot stats: data not yet loaded")
            return
        
        # Calculate statistics
        total_servers = len(servers_data)
        active_servers = sum(1 for s in servers_data.values() if s.get('active', False))
        left_servers = total_servers - active_servers
        
        # Calculate ratings
        total_raters = len(bot_ratings)
        if total_raters > 0:
            total_rating_sum = sum(r.get('rating', 0) for r in bot_ratings.values())
            average_rating = total_rating_sum / total_raters
        else:
            average_rating = 0.0
        
        # Count ratings by value
        rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for rating_data in bot_ratings.values():
            rating = rating_data.get('rating', 0)
            if rating in rating_counts:
                rating_counts[rating] += 1
        
        # Count configured channels
        configured_channels = len(channel_langs)
        dual_lang_channels = sum(1 for c in channel_langs.values() if isinstance(c, dict) and c.get('secondary'))
        
        # Count roles
        total_allowed_roles = sum(len(roles) for roles in allowed_roles.values())
        
        # Generate report
        from datetime import datetime
        current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
        
        report = f"""
╔═══════════════════════════════════════════════════════════════╗
║              BOT STATISTICS REPORT                            ║
║         Kingdom-77 Translation Bot                            ║
╚═══════════════════════════════════════════════════════════════╝

📅 Last Updated: {current_time}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 SERVER STATISTICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Servers (All-Time):     {total_servers}
├─ Active Servers:            {active_servers} ✅
└─ Left Servers:              {left_servers} ❌

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⭐ RATING STATISTICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Raters:                 {total_raters}
Average Rating:               {average_rating:.2f} / 5.00 ⭐

Rating Distribution:
  ⭐⭐⭐⭐⭐ (5 Stars):       {rating_counts[5]} users
  ⭐⭐⭐⭐   (4 Stars):       {rating_counts[4]} users
  ⭐⭐⭐     (3 Stars):       {rating_counts[3]} users
  ⭐⭐       (2 Stars):       {rating_counts[2]} users
  ⭐         (1 Star):        {rating_counts[1]} users

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 CHANNEL CONFIGURATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Configured Channels:          {configured_channels}
├─ Single Language:           {configured_channels - dual_lang_channels}
└─ Dual Language:             {dual_lang_channels} ↔️

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🛡️ ROLE PERMISSIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Allowed Roles:          {total_allowed_roles}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 DETAILED SERVER LIST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        
        # Add active servers
        active_list = [s for s in servers_data.values() if s.get('active', False)]
        if active_list:
            report += "✅ ACTIVE SERVERS:\n\n"
            for i, server in enumerate(sorted(active_list, key=lambda x: x.get('joined_at', '')), 1):
                report += f"{i}. {server.get('name', 'Unknown')}\n"
                report += f"   └─ Joined: {server.get('joined_at', 'Unknown')}\n"
            report += "\n"
        
        # Add left servers
        left_list = [s for s in servers_data.values() if not s.get('active', False)]
        if left_list:
            report += "❌ LEFT SERVERS:\n\n"
            for i, server in enumerate(sorted(left_list, key=lambda x: x.get('left_at', '')), 1):
                report += f"{i}. {server.get('name', 'Unknown')}\n"
                report += f"   ├─ Joined: {server.get('joined_at', 'Unknown')}\n"
                report += f"   └─ Left: {server.get('left_at', 'Unknown')}\n"
            report += "\n"
        
        report += """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 NOTE: This file is auto-generated and updates automatically.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        # Write to file
        with open(BOT_STATS_FILE, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"Bot statistics updated: {active_servers} active, {left_servers} left, {total_raters} raters")
    
    except Exception as e:
        logger.error(f"Error updating bot stats file: {e}")


async def cleanup_old_server_data():
    """Clean up data from servers that left more than 7 days ago.
    Removes channels, roles, permissions, and role languages for old servers.
    """
    from datetime import datetime, timedelta
    
    try:
        if 'servers_data' not in globals():
            logger.warning("Cannot cleanup: servers_data not loaded")
            return
        
        current_time = datetime.utcnow()
        cleanup_threshold = timedelta(days=7)
        
        cleaned_servers = []
        cleaned_channels = 0
        cleaned_roles = 0
        cleaned_permissions = 0
        cleaned_role_langs = 0
        
        # Find servers that left more than 7 days ago
        for guild_id, server_info in list(servers_data.items()):
            if not server_info.get('active', True):
                left_at_str = server_info.get('left_at')
                if left_at_str:
                    try:
                        left_at = datetime.fromisoformat(left_at_str)
                        time_since_left = current_time - left_at
                        
                        if time_since_left >= cleanup_threshold:
                            # Mark for cleanup
                            server_name = server_info.get('name', 'Unknown')
                            cleaned_servers.append((guild_id, server_name))
                            
                            logger.debug(f"Cleaning data for server: {server_name} (left {time_since_left.days} days ago)")
                            
                            # Clean channel language configurations
                            # We need to check which channels belong to this guild
                            channels_to_remove = []
                            for ch_id in list(channel_langs.keys()):
                                try:
                                    channel = bot.get_channel(int(ch_id))
                                    # If channel doesn't exist or belongs to the guild being cleaned
                                    if channel is None:
                                        channels_to_remove.append(ch_id)
                                    elif str(channel.guild.id) == guild_id:
                                        channels_to_remove.append(ch_id)
                                except (ValueError, AttributeError):
                                    # Invalid channel ID, remove it
                                    channels_to_remove.append(ch_id)
                            
                            for ch_id in channels_to_remove:
                                if ch_id in channel_langs:
                                    del channel_langs[ch_id]
                                    cleaned_channels += 1
                            
                            # Clean allowed roles
                            if guild_id in allowed_roles:
                                cleaned_roles += len(allowed_roles[guild_id])
                                del allowed_roles[guild_id]
                            
                            # Clean role permissions
                            if guild_id in role_permissions:
                                for role_id, perms in role_permissions[guild_id].items():
                                    cleaned_permissions += len(perms) if isinstance(perms, list) else 1
                                del role_permissions[guild_id]
                            
                            # Clean role languages
                            if guild_id in role_languages:
                                cleaned_role_langs += len(role_languages[guild_id])
                                del role_languages[guild_id]
                            
                    except ValueError as e:
                        logger.warning(f"Invalid date format for guild {guild_id}: {e}")
        
        # Save all changes if any cleanup was done
        if cleaned_servers:
            await save_channels(channel_langs)
            await save_allowed_roles(allowed_roles)
            await save_role_permissions(role_permissions)
            await save_role_languages(role_languages)
            update_bot_stats()
            
            logger.info(f"🧹 Cleanup completed: {len(cleaned_servers)} servers, "
                       f"{cleaned_channels} channels, {cleaned_roles} roles, "
                       f"{cleaned_permissions} permission entries, {cleaned_role_langs} role languages")
            
            for guild_id, server_name in cleaned_servers:
                logger.info(f"  ├─ Cleaned data for: {server_name} (ID: {guild_id})")
        else:
            logger.debug("✅ No old server data to cleanup (all servers active or within 7-day grace period)")
            
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        
        # Save all changes if any cleanup was done
        if cleaned_servers:
            await save_channels(channel_langs)
            await save_allowed_roles(allowed_roles)
            await save_role_permissions(role_permissions)
            await save_role_languages(role_languages)
            update_bot_stats()
            
            logger.info(f"🧹 Cleanup completed: {len(cleaned_servers)} servers, "
                       f"{cleaned_channels} channels, {cleaned_roles} roles, "
                       f"{cleaned_permissions} permissions, {cleaned_role_langs} role languages")
            
            for guild_id, server_name in cleaned_servers:
                logger.info(f"  ├─ Cleaned data for: {server_name} (ID: {guild_id})")
        else:
            logger.debug("No old server data to cleanup")
            
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")


# ============================================================================
# BOT INITIALIZATION
# ============================================================================

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Global state
channel_langs = load_channels()
bot_ratings = load_ratings()
allowed_roles = load_allowed_roles()
role_languages = load_role_languages()
role_permissions = load_role_permissions()
servers_data = load_servers()

# Translation cache for faster responses
translation_cache = {}  # {(text_hash, source_lang, target_lang): translated_text}
CACHE_MAX_SIZE = 10000  # Maximum cache entries (increased for better performance)

# Command Groups for organized slash commands
channel_group = app_commands.Group(name="channel", description="📋 Manage channel language settings")
role_group = app_commands.Group(name="role", description="🛡️ Manage role permissions and languages")
view_group = app_commands.Group(name="view", description="👁️ View bot information and lists")

# Register groups with the bot
bot.tree.add_command(channel_group)
bot.tree.add_command(role_group)
bot.tree.add_command(view_group)


# ============================================================================
# BACKGROUND TASKS
# ============================================================================

@tasks.loop(hours=24)
async def daily_cleanup_task():
    """Daily task to cleanup data from servers that left more than 7 days ago."""
    logger.info("🧹 Running daily cleanup task...")
    await cleanup_old_server_data()


@daily_cleanup_task.before_loop
async def before_daily_cleanup():
    """Wait until bot is ready before starting the cleanup task."""
    await bot.wait_until_ready()
    logger.info("Daily cleanup task initialized")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def _choose_latency_color(ms: float) -> discord.Color:
    """Return a color based on latency in milliseconds."""
    if ms < 100:
        return discord.Color.green()
    if ms < 250:
        return discord.Color.gold()
    return discord.Color.red()


def make_embed(title: str = None, description: str = None, *, color: discord.Color = None) -> discord.Embed:
    """Create a consistent embed for bot responses."""
    if color is None:
        color = discord.Color.blurple()
    emb = discord.Embed(title=title, description=description, color=color)
    try:
        if bot.user:
            avatar = getattr(bot.user, 'display_avatar', None)
            if avatar:
                # Use display_name or name without discriminator
                bot_name = bot.user.display_name if hasattr(bot.user, 'display_name') else bot.user.name
                emb.set_author(name=bot_name, icon_url=avatar.url)
    except Exception:
        pass
    return emb


async def smart_translate(text: str, source_lang: str, target_lang: str, quality_mode: str = 'fast') -> tuple:
    """Translate text with smart quality selection.
    
    Args:
        text: Text to translate
        source_lang: Source language code
        target_lang: Target language code
        quality_mode: 'fast', 'quality', or 'auto'
    
    Returns:
        tuple: (translated_text, actual_mode_used)
    """
    try:
        # Auto mode: intelligently choose based on content
        if quality_mode == 'auto':
            text_length = len(text)
            
            # Long messages (>500 chars) or technical content → quality mode
            if text_length > 500:
                quality_mode = 'quality'
                logger.debug(f"Auto mode: Using quality (long message: {text_length} chars)")
            
            # Check for technical terms (basic detection)
            technical_indicators = ['API', 'HTTP', 'JSON', 'SQL', 'function', 'class', 'error', 'exception']
            if any(term in text for term in technical_indicators):
                quality_mode = 'quality'
                logger.debug("Auto mode: Using quality (technical content detected)")
            else:
                quality_mode = 'fast'
                logger.debug("Auto mode: Using fast (regular message)")
        
        # Fast mode: Google Translator (current system)
        if quality_mode == 'fast':
            translated = GoogleTranslator(source=source_lang, target=target_lang).translate(text)
            return (translated, 'fast')
        
        # Quality mode: Try to use better translator
        # For now, we'll use Google but could add DeepL or LibreTranslate later
        elif quality_mode == 'quality':
            # TODO: Add DeepL API integration in future
            # For now, use Google with note that it's fast mode
            translated = GoogleTranslator(source=source_lang, target=target_lang).translate(text)
            return (translated, 'fast')  # Return 'fast' since we're using Google
        
        else:
            # Fallback to fast
            translated = GoogleTranslator(source=source_lang, target=target_lang).translate(text)
            return (translated, 'fast')
    
    except Exception as e:
        logger.error(f"Translation error in smart_translate: {e}")
        return (None, quality_mode)


def has_permission(member: discord.Member, guild_id: str) -> bool:
    """Check if member has permission to use admin commands.
    
    Permission is granted if:
    1. Member is server owner
    2. Member has Administrator permission
    3. Member has one of the allowed roles for this guild
    """
    # Server owner always has permission
    if member.guild.owner_id == member.id:
        return True
    
    # Administrator permission always has access
    if member.guild_permissions.administrator:
        return True
    
    # Check if guild has configured allowed roles
    if guild_id in allowed_roles and allowed_roles[guild_id]:
        member_role_ids = {str(role.id) for role in member.roles}
        allowed_role_ids = set(allowed_roles[guild_id])
        if member_role_ids & allowed_role_ids:
            return True
        return False
    
    # Default: require manage_channels permission
    return member.guild_permissions.manage_channels


def has_specific_permission(member: discord.Member, guild_id: str, permission: str) -> bool:
    """Check if member has a specific bot permission.
    
    Permission is granted if:
    1. Member is server owner (has all permissions)
    2. Member has Administrator permission (has all permissions)
    3. Member has a role with the specific permission assigned
    """
    # Server owner and administrators have all permissions
    if member.guild.owner_id == member.id or member.guild_permissions.administrator:
        return True
    
    # Check if member has a role with this specific permission
    if guild_id in role_permissions:
        member_role_ids = [str(role.id) for role in member.roles]
        for role_id in member_role_ids:
            if role_id in role_permissions[guild_id]:
                if permission in role_permissions[guild_id][role_id]:
                    return True
    
    return False


# ============================================================================
# BOT EVENTS
# ============================================================================

@bot.event
async def on_ready():
    """Called when the bot is ready and connected to Discord."""
    from datetime import datetime
    
    logger.info(f"Logged in as {bot.user}")
    logger.info(f"Bot is in {len(bot.guilds)} server(s)")
    logger.info(f"🔑 BOT_OWNER_ID configured as: {BOT_OWNER_ID}")
    
    # Initialize Redis cache (optional - improves performance)
    redis_connected = False
    redis_url = os.getenv('REDIS_URL') or os.getenv('REDIS_URI')
    if redis_url:
        try:
            await init_cache(redis_url)
            redis_connected = True
            logger.info("✅ Redis cache initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Redis: {e}")
            logger.warning("⚠️ Bot will continue without caching")
    else:
        logger.info("ℹ️ Redis not configured - skipping cache initialization")
    
    # Initialize MongoDB connection
    mongodb_connected = False
    try:
        await init_database()
        mongodb_connected = True
        logger.info("✅ MongoDB connection initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize MongoDB: {e}")
        logger.warning("⚠️ Bot will fallback to JSON files")
    
    # Load Moderation and Leveling Cogs if MongoDB is available
    if mongodb_connected:
        try:
            await bot.load_extension("cogs.cogs.moderation")
            logger.info("✅ Moderation cog loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load moderation cog: {e}")
        
        try:
            await bot.load_extension("cogs.cogs.leveling")
            logger.info("✅ Leveling cog loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load leveling cog: {e}")
        
        try:
            await bot.load_extension("cogs.cogs.tickets")
            logger.info("✅ Tickets cog loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load tickets cog: {e}")
        
        try:
            await bot.load_extension("cogs.cogs.autoroles")
            logger.info("✅ Auto-Roles cog loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load autoroles cog: {e}")
    
    # Load data from MongoDB or JSON files
    global channel_langs, bot_ratings, allowed_roles, role_languages, role_permissions, servers_data
    
    if mongodb_connected:
        # Load from MongoDB (v3.0)
        try:
            await load_data_from_mongodb()
            logger.info("✅ All data loaded from MongoDB")
        except Exception as e:
            logger.error(f"❌ Error loading from MongoDB, falling back to JSON: {e}")
            loop = asyncio.get_event_loop()
            channel_langs = await loop.run_in_executor(None, load_channels)
            bot_ratings = await loop.run_in_executor(None, load_ratings)
            allowed_roles = await loop.run_in_executor(None, load_allowed_roles)
            role_languages = await loop.run_in_executor(None, load_role_languages)
            role_permissions = await loop.run_in_executor(None, load_role_permissions)
            servers_data = await loop.run_in_executor(None, load_servers)
    else:
        # Fallback to JSON files (v2.8 compatibility)
        loop = asyncio.get_event_loop()
        channel_langs = await loop.run_in_executor(None, load_channels)
        bot_ratings = await loop.run_in_executor(None, load_ratings)
        allowed_roles = await loop.run_in_executor(None, load_allowed_roles)
        role_languages = await loop.run_in_executor(None, load_role_languages)
        role_permissions = await loop.run_in_executor(None, load_role_permissions)
        servers_data = await loop.run_in_executor(None, load_servers)
        logger.info("✅ All data loaded from JSON files")
    
    # Update server tracking for current guilds
    try:
        for guild in bot.guilds:
            guild_id = str(guild.id)
            if guild_id not in servers_data:
                # New server not yet tracked
                servers_data[guild_id] = {
                    'name': guild.name,
                    'joined_at': datetime.utcnow().isoformat(),
                    'active': True,
                    'left_at': None
                }
            else:
                # Update existing server to active
                servers_data[guild_id]['active'] = True
                servers_data[guild_id]['name'] = guild.name  # Update name in case it changed
        
        await save_servers(servers_data)
        update_bot_stats()
        logger.info(f"✅ Server tracking updated: {len([s for s in servers_data.values() if s.get('active')])} active servers")
    except Exception as e:
        logger.error(f"Error updating server tracking: {e}")
    
    # Run initial cleanup for old servers
    try:
        logger.info("Running initial cleanup check...")
        await cleanup_old_server_data()
    except Exception as e:
        logger.error(f"Error during initial cleanup: {e}")
    
    # Start daily cleanup task
    if not daily_cleanup_task.is_running():
        daily_cleanup_task.start()
        logger.info("✅ Daily cleanup task started")
    
    # Load priority guilds
    try:
        load_priority_guilds()
        if priority_guilds:
            logger.info(f"✅ Loaded {len(priority_guilds)} priority guilds")
    except Exception as e:
        logger.error(f"Error loading priority guilds: {e}")
    
    # 🎁 Check existing guilds for owner match and auto-add to priority
    try:
        auto_added_count = 0
        for guild in bot.guilds:
            if guild.owner_id == BOT_OWNER_ID and guild.id not in priority_guilds:
                priority_guilds.append(guild.id)
                auto_added_count += 1
                logger.info(f"👑 Auto-added existing guild {guild.name} to priority guilds (owner match)")
        
        if auto_added_count > 0:
            save_priority_guilds()
            logger.info(f"✅ Auto-added {auto_added_count} existing guild(s) to priority list")
    except Exception as e:
        logger.error(f"Error checking existing guilds: {e}")
    
    # Log application commands
    try:
        cmds = [c.name for c in bot.tree.walk_commands()]
        if cmds:
            logger.info(f"Application commands present: {cmds}")
        else:
            logger.info("No application commands found in bot.tree.")
    except Exception as e:
        logger.debug(f"Could not list app commands: {e}")
    
    # Sync slash commands to priority guilds first (fast sync)
    if priority_guilds:
        try:
            logger.info(f"Starting fast sync for {len(priority_guilds)} priority guilds...")
            for guild_id in priority_guilds:
                try:
                    synced = await bot.tree.sync(guild=discord.Object(id=guild_id))
                    guild = bot.get_guild(guild_id)
                    guild_name = guild.name if guild else f"ID:{guild_id}"
                    logger.info(f"✅ Fast synced {len(synced)} commands to {guild_name}")
                except Exception as e:
                    logger.error(f"❌ Failed to sync guild {guild_id}: {e}")
        except Exception as e:
            logger.error(f"Error during priority guild sync: {e}")
    
    # Sync slash commands globally
    try:
        logger.info("Starting global command sync...")
        synced = await bot.tree.sync()
        logger.info(f"✅ Successfully synced {len(synced)} global commands")
        logger.info(f"Commands synced: {[cmd.name for cmd in synced]}")
        logger.info("Note: Global commands may take up to 1 hour to appear in all servers")
    except Exception as e:
        logger.error(f"❌ Failed to sync commands: {e}")
    
    # Log other info
    try:
        cmds = [c.name for c in bot.commands]
        logger.info(f"Registered prefix commands: {cmds}")
    except Exception as e:
        logger.debug(f"Could not list prefix commands: {e}")

    try:
        loaded = list(bot.cogs.keys())
        logger.info(f"Loaded cogs: {loaded}")
    except Exception as e:
        logger.debug(f"Could not list loaded cogs: {e}")


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Global error handler for application commands."""
    # Check if bot is disabled (allow owner to bypass)
    if bot_disabled and interaction.user.id != BOT_OWNER_ID:
        # Command executed while bot is disabled - silently ignore
        if not interaction.response.is_done():
            try:
                await interaction.response.send_message("Bot is currently disabled.", ephemeral=True, delete_after=3)
            except:
                pass
        return
    
    # Handle other errors
    if isinstance(error, app_commands.CommandNotFound):
        return  # Ignore command not found errors
    
    logger.error(f"Command error: {error}")


@bot.event
async def on_guild_join(guild: discord.Guild):
    """Log when the bot joins a new server and track it."""
    from datetime import datetime
    
    logger.info(f"Joined new guild: {guild.name} (ID: {guild.id})")
    
    try:
        guild_id = str(guild.id)
        servers_data[guild_id] = {
            'name': guild.name,
            'joined_at': datetime.utcnow().isoformat(),
            'active': True,
            'left_at': None
        }
        await save_servers(servers_data)
        update_bot_stats()
        logger.info(f"✅ Recorded server join: {guild.name}")
        
        # 🎁 Hidden Feature: Auto-add to priority guilds if owner matches bot owner
        if guild.owner_id == BOT_OWNER_ID and guild.id not in priority_guilds:
            priority_guilds.append(guild.id)
            save_priority_guilds()
            logger.info(f"👑 Auto-added guild {guild.name} to priority guilds (owner match)")
            
            # Sync commands immediately for this priority guild
            try:
                guild_obj = discord.Object(id=guild.id)
                bot.tree.copy_global_to(guild=guild_obj)
                await bot.tree.sync(guild=guild_obj)
                logger.info(f"⚡ Fast-synced commands for priority guild: {guild.name}")
            except Exception as sync_error:
                logger.error(f"Error syncing commands for priority guild: {sync_error}")
                
    except Exception as e:
        logger.error(f"Error recording server join: {e}")


@bot.event
async def on_guild_remove(guild: discord.Guild):
    """Clean up ALL server data when bot is removed from a guild."""
    from datetime import datetime
    
    logger.info(f"🚪 Removed from guild: {guild.name} (ID: {guild.id})")
    
    try:
        guild_id = str(guild.id)
        removed_counts = {
            'channels': 0,
            'roles': 0,
            'role_languages': 0,
            'role_permissions': 0
        }
        
        # Mark server as inactive
        if guild_id in servers_data:
            servers_data[guild_id]['active'] = False
            servers_data[guild_id]['left_at'] = datetime.utcnow().isoformat()
        else:
            servers_data[guild_id] = {
                'name': guild.name,
                'joined_at': 'Unknown',
                'active': False,
                'left_at': datetime.utcnow().isoformat()
            }
        
        await save_servers(servers_data)
        
        # 1. Clean up channel language settings
        channels_to_remove = [ch_id for ch_id in list(channel_langs.keys()) 
                             if ch_id.startswith(guild_id)]
        for ch_id in channels_to_remove:
            del channel_langs[ch_id]
            removed_counts['channels'] += 1
        
        if channels_to_remove:
            await save_channels(channel_langs)
        
        # 2. Clean up allowed roles
        roles_to_remove = [role_id for role_id in list(allowed_roles.keys()) 
                          if role_id.startswith(guild_id)]
        for role_id in roles_to_remove:
            del allowed_roles[role_id]
            removed_counts['roles'] += 1
        
        if roles_to_remove:
            await save_allowed_roles(allowed_roles)
        
        # 3. Clean up role languages
        role_langs_to_remove = [role_id for role_id in list(role_languages.keys()) 
                               if role_id.startswith(guild_id)]
        for role_id in role_langs_to_remove:
            del role_languages[role_id]
            removed_counts['role_languages'] += 1
        
        if role_langs_to_remove:
            await save_role_languages(role_languages)
        
        # 4. Clean up role permissions
        role_perms_to_remove = [role_id for role_id in list(role_permissions.keys()) 
                               if role_id.startswith(guild_id)]
        for role_id in role_perms_to_remove:
            del role_permissions[role_id]
            removed_counts['role_permissions'] += 1
        
        if role_perms_to_remove:
            await save_role_permissions(role_permissions)
        
        # 🎁 Hidden Feature: Remove from priority guilds if present
        if guild.id in priority_guilds:
            priority_guilds.remove(guild.id)
            save_priority_guilds()
            logger.info(f"👑 Removed guild {guild.name} from priority guilds")
        
        # Log cleanup summary
        total_removed = sum(removed_counts.values())
        if total_removed > 0:
            logger.info(f"🧹 Cleaned up {guild.name} data:")
            logger.info(f"   • {removed_counts['channels']} channel settings")
            logger.info(f"   • {removed_counts['roles']} allowed roles")
            logger.info(f"   • {removed_counts['role_languages']} role languages")
            logger.info(f"   • {removed_counts['role_permissions']} role permissions")
            logger.info(f"   ✅ Total: {total_removed} entries removed")
        else:
            logger.info(f"✅ No data to clean up for {guild.name}")
        
        update_bot_stats()
        
    except Exception as e:
        logger.error(f"❌ Error cleaning up guild data for {guild.name}: {e}")


@bot.event
async def on_message(message: discord.Message):
    """Handle message translation based on channel language settings with dual language support."""
    try:
        # Check if bot is disabled
        if bot_disabled:
            return
        
        # Ignore bots and webhooks
        if message.author.bot or message.webhook_id:
            return
        
        # Handle XP for leveling system (Nova style)
        if message.guild and not message.author.bot:
            try:
                from leveling.level_system import get_leveling_system
                if db and db.client:
                    leveling = get_leveling_system(db.db)
                    config = await leveling.get_guild_config(str(message.guild.id))
                    
                    # Check if leveling is enabled
                    if config.get("enabled", True):
                        # Check if channel is excluded
                        no_xp_channels = config.get("no_xp_channels", [])
                        if str(message.channel.id) not in no_xp_channels:
                            # Check if user has excluded role
                            no_xp_roles = config.get("no_xp_roles", [])
                            member = message.guild.get_member(message.author.id)
                            if member and not any(str(role.id) in no_xp_roles for role in member.roles):
                                # Check cooldown (60 seconds by default)
                                cooldown = config.get("cooldown", 60)
                                on_cooldown = await leveling.check_cooldown(
                                    str(message.guild.id),
                                    str(message.author.id),
                                    cooldown
                                )
                                
                                if not on_cooldown:
                                    # Calculate XP (15-25 by default, Nova style)
                                    xp_gain = await leveling.calculate_xp_gain(
                                        str(message.guild.id),
                                        str(message.author.id),
                                        member
                                    )
                                    
                                    # Add XP
                                    leveled_up, new_level, user_data = await leveling.add_xp(
                                        str(message.guild.id),
                                        str(message.author.id),
                                        xp_gain
                                    )
                                    
                                    # Assign level roles if leveled up
                                    if leveled_up:
                                        try:
                                            from autoroles import AutoRoleSystem
                                            autorole_system = AutoRoleSystem(db.db)
                                            await autorole_system.assign_level_roles(
                                                message.guild.id,
                                                message.author.id,
                                                new_level,
                                                bot
                                            )
                                        except Exception as role_error:
                                            logger.error(f"Error assigning level roles: {role_error}")
                                    
                                    # Announce level up (Nova style)
                                    if leveled_up and config.get("announce_level_up", True):
                                        level_up_msg = config.get(
                                            "level_up_message",
                                            "🎉 {user} leveled up to **Level {level}**!"
                                        )
                                        level_up_msg = level_up_msg.replace("{user}", member.mention)
                                        level_up_msg = level_up_msg.replace("{level}", str(new_level))
                                        
                                        # Send in same channel or custom channel
                                        level_up_channel_id = config.get("level_up_channel")
                                        target_channel = message.channel
                                        if level_up_channel_id:
                                            custom_channel = message.guild.get_channel(int(level_up_channel_id))
                                            if custom_channel:
                                                target_channel = custom_channel
                                        
                                        await target_channel.send(level_up_msg)
            except Exception as e:
                logger.error(f"Error in XP handler: {e}")

        channel_id = str(message.channel.id)
        channel_config = channel_langs.get(channel_id)
        if not channel_config:
            return

        content = message.content.strip()
        if not content:
            return

        # Extract primary and secondary languages
        if isinstance(channel_config, dict):
            primary_lang = channel_config.get('primary')
            secondary_lang = channel_config.get('secondary')
            blacklisted_languages = channel_config.get('blacklisted_languages', [])
        else:
            # Legacy support: if it's a string, treat it as primary only
            primary_lang = channel_config
            secondary_lang = None
            blacklisted_languages = []

        if not primary_lang:
            return

        try:
            detected = detect(content)
        except LangDetectException:
            logger.debug("Could not detect language")
            return
        except Exception as e:
            logger.error(f"Language detection error: {e}")
            return

        # Check if detected language is blacklisted
        if detected in blacklisted_languages:
            logger.debug(f"Language '{detected}' is blacklisted in this channel, skipping translation")
            return

        # Check if languages are supported
        if primary_lang not in SUPPORTED:
            logger.warning(f"Primary language '{primary_lang}' not in SUPPORTED list")
            return
        
        if secondary_lang and secondary_lang not in SUPPORTED:
            logger.warning(f"Secondary language '{secondary_lang}' not in SUPPORTED list")
            secondary_lang = None

        # Determine target language based on detected language
        target = None
        
        if secondary_lang:
            # Dual language mode: bidirectional translation between primary and secondary
            if detected == primary_lang:
                # Message is in primary → translate to secondary
                target = secondary_lang
                logger.debug(f"Detected primary language ({primary_lang}), translating to secondary ({secondary_lang})")
            elif detected == secondary_lang:
                # Message is in secondary → translate to primary
                target = primary_lang
                logger.debug(f"Detected secondary language ({secondary_lang}), translating to primary ({primary_lang})")
            else:
                # Message is in another language (not primary or secondary) → translate to primary (default)
                target = primary_lang
                logger.debug(f"Detected other language ({detected}), translating to primary ({primary_lang})")
        else:
            # Single language mode: translate all messages to primary language
            # This allows non-primary language messages to be translated
            target = primary_lang
            logger.debug(f"Single language mode: translating {detected} to primary ({primary_lang})")
            
            # Skip translation only if message is already in primary AND same as result would be
            # We still process it to allow translation to happen

        # Create cache key (using hash to handle long messages)
        cache_key = (hash(content), detected, target)
        
        # Check cache first for faster response
        if cache_key in translation_cache:
            translated = translation_cache[cache_key]
            translation_mode_used = 'cached'
            logger.debug(f"Using cached translation for '{content[:30]}...'")
        else:
            # Get quality mode from channel config (only if dict, otherwise default to 'fast')
            if isinstance(channel_config, dict):
                quality_mode = channel_config.get('translation_quality', 'fast')
            else:
                quality_mode = 'fast'  # Legacy format (string) doesn't have quality setting
            
            # Translate using smart quality selection
            try:
                translated, translation_mode_used = await smart_translate(
                    text=content,
                    source_lang=detected,
                    target_lang=target,
                    quality_mode=quality_mode
                )
                
                # Store in cache
                if translated:
                    translation_cache[cache_key] = translated
                    
                    # Smart cache cleaning: remove same amount of oldest unused entries as new ones added
                    if len(translation_cache) > CACHE_MAX_SIZE:
                        # Calculate how many entries to remove (entries added beyond limit)
                        excess_count = len(translation_cache) - CACHE_MAX_SIZE
                        # Remove oldest entries (FIFO - First In First Out)
                        for _ in range(excess_count):
                            if translation_cache:  # Check if not empty
                                translation_cache.pop(next(iter(translation_cache)))
                        logger.debug(f"Cache cleaned: removed {excess_count} oldest entries")
                        
            except Exception as e:
                logger.error(f"Translation API error: {e}")
                return

        if not translated:
            logger.debug("Translation returned empty")
            return

        # Only send translation if it's different from original
        if translated and translated.strip() != content.strip():
            emb = make_embed(title='Translation', description=translated, color=discord.Color.blue())
            try:
                detected_name = SUPPORTED.get(detected, detected)
                target_name = SUPPORTED.get(target, target)
                emb.set_footer(text=f"{detected_name} → {target_name}")
            except Exception:
                pass
            await message.reply(embed=emb, mention_author=False)
            logger.info(f"Detected '{detected}' message in channel with primary='{primary_lang}' secondary='{secondary_lang}' → Translated to {SUPPORTED.get(target, target)}")
        else:
            logger.debug(f"Translation result is same as original, skipping")
            
        # Allow other commands to be processed
        try:
            await bot.process_commands(message)
        except Exception:
            pass
    
    except Exception as e:
        logger.error(f"❌ Error in on_message handler: {e}", exc_info=True)


# ============================================================================
# AUTO-ROLES EVENT HANDLERS
# ============================================================================

@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    """Handle reaction add for Reaction Roles"""
    try:
        # Ignore bot reactions
        if payload.user_id == bot.user.id:
            return
        
        # Check if MongoDB is connected
        if not db or not db.client:
            return
        
        from autoroles import AutoRoleSystem
        autorole_system = AutoRoleSystem(db.db)
        
        # Handle reaction
        role = await autorole_system.handle_reaction_add(payload, bot)
        
        if role:
            logger.info(f"✅ Reaction Role: Gave {role.name} to user {payload.user_id}")
        
    except Exception as e:
        logger.error(f"❌ Error in on_raw_reaction_add: {e}", exc_info=True)


@bot.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    """Handle reaction remove for Reaction Roles"""
    try:
        # Ignore bot reactions
        if payload.user_id == bot.user.id:
            return
        
        # Check if MongoDB is connected
        if not db or not db.client:
            return
        
        from autoroles import AutoRoleSystem
        autorole_system = AutoRoleSystem(db.db)
        
        # Handle reaction
        role = await autorole_system.handle_reaction_remove(payload, bot)
        
        if role:
            logger.info(f"✅ Reaction Role: Removed {role.name} from user {payload.user_id}")
        
    except Exception as e:
        logger.error(f"❌ Error in on_raw_reaction_remove: {e}", exc_info=True)


@bot.event
async def on_member_join(member: discord.Member):
    """Handle member join for Join Roles"""
    try:
        # Check if MongoDB is connected
        if not db or not db.client:
            return
        
        from autoroles import AutoRoleSystem
        autorole_system = AutoRoleSystem(db.db)
        
        # Assign join roles
        roles = await autorole_system.assign_join_roles(member)
        
        if roles:
            roles_names = [r.name for r in roles]
            logger.info(f"✅ Join Roles: Gave {', '.join(roles_names)} to {member.name}")
        
    except Exception as e:
        logger.error(f"❌ Error in on_member_join: {e}", exc_info=True)


# ============================================================================
# UI COMPONENTS
# ============================================================================

class PrimaryLanguageSelect(discord.ui.Select):
    """Dropdown menu for selecting primary language."""
    
    def __init__(self, supported_langs):
        options = [
            discord.SelectOption(
                label=f"{name} ({code})",
                value=code,
                description=f"Set primary language to {name}"
            ) for code, name in supported_langs.items()
        ]
        super().__init__(
            placeholder="Choose primary language...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="primary_lang_select"
        )

    async def callback(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        if not has_permission(interaction.user, guild_id):
            emb = make_embed(
                title='Permission Denied',
                description='⚠️ You need proper permissions to use this command.\n\nRequired: Server Owner, Administrator, or an allowed role.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return
        
        try:
            code = self.values[0]
            self.view.primary_lang = code
            
            # Update the embed to show selection
            emb = make_embed(
                title='Set Languages',
                description=f'✅ **Primary Language:** {SUPPORTED[code]} ({code})\n\n' +
                           '➡️ Now select a **secondary language** (optional).\n' +
                           'Or click **Save** to save with primary language only.',
                color=discord.Color.blurple()
            )
            await interaction.response.edit_message(embed=emb, view=self.view)
        except Exception as e:
            logger.error(f"Error in PrimaryLanguageSelect callback: {e}")
            emb = make_embed(
                title='Error',
                description=f'❌ Failed to select language: {str(e)}',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)


class SecondaryLanguageSelect(discord.ui.Select):
    """Dropdown menu for selecting secondary language."""
    
    def __init__(self, supported_langs):
        options = [
            discord.SelectOption(
                label=f"{name} ({code})",
                value=code,
                description=f"Set secondary language to {name}"
            ) for code, name in supported_langs.items()
        ]
        super().__init__(
            placeholder="Choose secondary language (optional)...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="secondary_lang_select"
        )

    async def callback(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        if not has_permission(interaction.user, guild_id):
            emb = make_embed(
                title='Permission Denied',
                description='⚠️ You need proper permissions to use this command.\n\nRequired: Server Owner, Administrator, or an allowed role.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return
        
        try:
            code = self.values[0]
            
            # Check if secondary is same as primary
            if self.view.primary_lang and code == self.view.primary_lang:
                emb = make_embed(
                    title='Invalid Selection',
                    description='⚠️ Secondary language cannot be the same as primary language.\nPlease choose a different language.',
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=emb, ephemeral=True)
                return
            
            self.view.secondary_lang = code
            
            # Update the embed to show both selections
            primary_text = f'{SUPPORTED[self.view.primary_lang]} ({self.view.primary_lang})' if self.view.primary_lang else 'Not selected'
            emb = make_embed(
                title='Set Languages',
                description=f'✅ **Primary Language:** {primary_text}\n' +
                           f'✅ **Secondary Language:** {SUPPORTED[code]} ({code})\n\n' +
                           '➡️ Click **Save** to confirm.',
                color=discord.Color.blurple()
            )
            await interaction.response.edit_message(embed=emb, view=self.view)
        except Exception as e:
            logger.error(f"Error in SecondaryLanguageSelect callback: {e}")
            emb = make_embed(
                title='Error',
                description=f'❌ Failed to select language: {str(e)}',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)


class BlacklistLanguageSelect(discord.ui.Select):
    """Multi-select dropdown menu for blacklisting languages (optional)."""
    
    def __init__(self, supported_langs):
        options = [
            discord.SelectOption(
                label=f"{name} ({code})",
                value=code,
                description=f"Don't translate {name} messages"
            ) for code, name in supported_langs.items()
        ]
        super().__init__(
            placeholder="Choose languages to ignore (optional)...",
            min_values=0,
            max_values=min(10, len(options)),  # Max 10 blacklisted languages
            options=options,
            custom_id="blacklist_lang_select"
        )

    async def callback(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        if not has_permission(interaction.user, guild_id):
            emb = make_embed(
                title='Permission Denied',
                description='⚠️ You need proper permissions to use this command.\n\nRequired: Server Owner, Administrator, or an allowed role.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return
        
        try:
            blacklisted = self.values
            
            # Check if primary or secondary language is in blacklist
            conflicts = []
            if self.view.primary_lang and self.view.primary_lang in blacklisted:
                conflicts.append(f"Primary ({SUPPORTED[self.view.primary_lang]})")
            if self.view.secondary_lang and self.view.secondary_lang in blacklisted:
                conflicts.append(f"Secondary ({SUPPORTED[self.view.secondary_lang]})")
            
            if conflicts:
                emb = make_embed(
                    title='Invalid Selection',
                    description=f'⚠️ You cannot blacklist your channel languages!\n\nConflicts: {", ".join(conflicts)}\n\nPlease remove them from the blacklist.',
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=emb, ephemeral=True)
                return
            
            self.view.blacklisted_languages = blacklisted
            
            # Update the embed to show all selections
            primary_text = f'{SUPPORTED[self.view.primary_lang]} ({self.view.primary_lang})' if self.view.primary_lang else 'Not selected'
            secondary_text = f'{SUPPORTED[self.view.secondary_lang]} ({self.view.secondary_lang})' if self.view.secondary_lang else 'None'
            
            blacklist_text = 'None'
            if blacklisted:
                blacklist_names = [f'{SUPPORTED[code]} ({code})' for code in blacklisted]
                blacklist_text = ', '.join(blacklist_names)
            
            emb = make_embed(
                title='Set Languages',
                description=f'✅ **Primary Language:** {primary_text}\n' +
                           f'✅ **Secondary Language:** {secondary_text}\n' +
                           f'🚫 **Blacklisted Languages:** {blacklist_text}\n\n' +
                           '➡️ Click **Save** to confirm.',
                color=discord.Color.blurple()
            )
            await interaction.response.edit_message(embed=emb, view=self.view)
        except Exception as e:
            logger.error(f"Error in BlacklistLanguageSelect callback: {e}")
            emb = make_embed(
                title='Error',
                description=f'❌ Failed to select languages: {str(e)}',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)


class DualLanguageView(discord.ui.View):
    """View containing dual language selection dropdowns and save button."""
    
    def __init__(self, channel):
        super().__init__(timeout=180)
        self.channel = channel
        self.primary_lang = None
        self.secondary_lang = None
        self.blacklisted_languages = []
        self.add_item(PrimaryLanguageSelect(SUPPORTED))
        self.add_item(SecondaryLanguageSelect(SUPPORTED))
        self.add_item(BlacklistLanguageSelect(SUPPORTED))
    
    @discord.ui.button(label='Save', style=discord.ButtonStyle.green, emoji='💾', custom_id='save_languages')
    async def save_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild_id = str(interaction.guild.id)
        if not has_permission(interaction.user, guild_id):
            emb = make_embed(
                title='Permission Denied',
                description='⚠️ You need proper permissions to use this command.\n\nRequired: Server Owner, Administrator, or an allowed role.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return
        
        if not self.primary_lang:
            emb = make_embed(
                title='No Selection',
                description='⚠️ Please select at least a primary language before saving.',
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return
        
        try:
            channel_id = str(self.channel.id)
            channel_langs[channel_id] = {
                'primary': self.primary_lang,
                'secondary': self.secondary_lang,
                'blacklisted_languages': self.blacklisted_languages,
                'translation_quality': 'fast'  # Default quality mode
            }
            await save_channels(channel_langs)
            
            # Build success message
            primary_name = SUPPORTED[self.primary_lang]
            description = f'✅ Channel {self.channel.mention} configured successfully!\n\n'
            description += f'**Primary Language:** {primary_name} ({self.primary_lang})\n'
            
            if self.secondary_lang:
                secondary_name = SUPPORTED[self.secondary_lang]
                description += f'**Secondary Language:** {secondary_name} ({self.secondary_lang})\n'
            
            if self.blacklisted_languages:
                blacklist_names = [f'{SUPPORTED[code]} ({code})' for code in self.blacklisted_languages]
                description += f'**Blacklisted Languages:** {", ".join(blacklist_names)}\n'
            
            description += '\n📝 **How it works:**\n'
            
            if self.blacklisted_languages:
                blacklist_display = ', '.join([SUPPORTED[code] for code in self.blacklisted_languages])
                description += f'� **{blacklist_display}** messages will NOT be translated\n'
            
            if self.secondary_lang:
                description += f'�📌 Messages in **{primary_name}** → Translated to **{SUPPORTED[self.secondary_lang]}**\n'
                description += f'📌 Messages in **{SUPPORTED[self.secondary_lang]}** → Translated to **{primary_name}**\n'
                description += f'📌 Other languages → Translated to **{primary_name}** (primary)'
            else:
                description += f'📌 All messages (except blacklisted) → Translated to **{primary_name}**'
            
            emb = make_embed(
                title='Languages Set',
                description=description,
                color=discord.Color.green()
            )
            
            # Disable all components
            for item in self.children:
                item.disabled = True
            
            await interaction.response.edit_message(embed=emb, view=self)
        except Exception as e:
            logger.error(f"Error saving languages: {e}")
            emb = make_embed(
                title='Error',
                description=f'❌ Failed to save languages: {str(e)}',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)
    
    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey, emoji='❌', custom_id='cancel_languages')
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        emb = make_embed(
            title='Cancelled',
            description='❌ Language setup cancelled.',
            color=discord.Color.red()
        )
        # Disable all components
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(embed=emb, view=self)


# Legacy single language view (kept for compatibility)
class LanguageSelect(discord.ui.Select):
    """Dropdown menu for selecting a language."""
    
    def __init__(self, supported_langs):
        options = [
            discord.SelectOption(
                label=f"{name} ({code})",
                value=code,
                description=f"Set channel language to {name}"
            ) for code, name in supported_langs.items()
        ]
        super().__init__(
            placeholder="Choose a language...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        if not has_permission(interaction.user, guild_id):
            emb = make_embed(
                title='Permission Denied',
                description='⚠️ You need proper permissions to use this command.\n\nRequired: Server Owner, Administrator, or an allowed role.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return
        
        try:
            code = self.values[0]
            channel_id = str(self.view.channel.id)
            channel_langs[channel_id] = {
                'primary': code,
                'secondary': None,
                'blacklisted_languages': [],
                'translation_quality': 'fast'
            }
            await save_channels(channel_langs)
            emb = make_embed(
                title='Language set',
                description=f'✅ Channel language set to **{SUPPORTED[code]}** ({code}) for {self.view.channel.mention}',
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)
        except Exception as e:
            logger.error(f"Error in LanguageSelect callback: {e}")
            emb = make_embed(
                title='Error',
                description=f'❌ Failed to set language: {str(e)}',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)


class LanguageView(discord.ui.View):
    """View containing the language selection dropdown (legacy compatibility)."""
    
    def __init__(self, channel):
        super().__init__()
        self.channel = channel
        self.add_item(LanguageSelect(SUPPORTED))


class PermissionSelect(discord.ui.Select):
    """Multi-select dropdown for choosing bot permissions."""
    
    def __init__(self):
        options = []
        for perm_key, perm_data in BOT_PERMISSIONS.items():
            options.append(discord.SelectOption(
                label=perm_data['name'],
                value=perm_key,
                description=perm_data['description'][:100],
                emoji=perm_data['emoji']
            ))
        
        super().__init__(
            placeholder="Select permissions for this role...",
            min_values=1,
            max_values=len(options),
            options=options,
            custom_id="permission_select"
        )
    
    async def callback(self, interaction: discord.Interaction):
        # This will be handled by the parent View
        await self.view.handle_permissions(interaction, self.values)


class RolePermissionView(discord.ui.View):
    """View for selecting permissions when adding a role."""
    
    def __init__(self, role: discord.Role, guild_id: str, role_id: str):
        super().__init__(timeout=300)
        self.role = role
        self.guild_id = guild_id
        self.role_id = role_id
        self.selected_permissions = []
        self.add_item(PermissionSelect())
    
    async def handle_permissions(self, interaction: discord.Interaction, permissions: list):
        """Handle the permission selection."""
        self.selected_permissions = permissions
        
        # Save to allowed_roles
        if self.guild_id not in allowed_roles:
            allowed_roles[self.guild_id] = []
        
        if self.role_id not in allowed_roles[self.guild_id]:
            allowed_roles[self.guild_id].append(self.role_id)
        
        # Save permissions
        if self.guild_id not in role_permissions:
            role_permissions[self.guild_id] = {}
        
        role_permissions[self.guild_id][self.role_id] = permissions
        
        await save_allowed_roles(allowed_roles)
        await save_role_permissions(role_permissions)
        
        # Create detailed embed
        perm_list = []
        for perm_key in permissions:
            perm_data = BOT_PERMISSIONS[perm_key]
            perm_list.append(f"{perm_data['emoji']} **{perm_data['name']}** - {perm_data['command']}")
        
        emb = make_embed(
            title='Role Added Successfully ✅',
            description=f'{self.role.mention} has been granted the selected permissions.',
            color=discord.Color.green()
        )
        emb.add_field(
            name=f'✨ Granted Permissions ({len(permissions)})',
            value='\n'.join(perm_list),
            inline=False
        )
        emb.add_field(
            name='👥 Members Affected',
            value=f'{len(self.role.members)} member(s) can now use these commands.',
            inline=False
        )
        emb.set_footer(text=f'Use /role editperms to revoke permissions • Use /role perms to modify')
        
        await interaction.response.edit_message(embed=emb, view=None)
        logger.info(f"Role {self.role.name} added with permissions: {', '.join(permissions)}")


class RatingView(discord.ui.View):
    """UI for rating the bot with star buttons."""
    
    def __init__(self):
        super().__init__(timeout=180)
    
    @discord.ui.button(label="⭐", style=discord.ButtonStyle.secondary, custom_id="rate_1")
    async def rate_1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_rating(interaction, 1)
    
    @discord.ui.button(label="⭐⭐", style=discord.ButtonStyle.secondary, custom_id="rate_2")
    async def rate_2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_rating(interaction, 2)
    
    @discord.ui.button(label="⭐⭐⭐", style=discord.ButtonStyle.secondary, custom_id="rate_3")
    async def rate_3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_rating(interaction, 3)
    
    @discord.ui.button(label="⭐⭐⭐⭐", style=discord.ButtonStyle.secondary, custom_id="rate_4")
    async def rate_4(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_rating(interaction, 4)
    
    @discord.ui.button(label="⭐⭐⭐⭐⭐", style=discord.ButtonStyle.primary, custom_id="rate_5")
    async def rate_5(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_rating(interaction, 5)
    
    async def _handle_rating(self, interaction: discord.Interaction, stars: int):
        """Handle rating submission."""
        user_id = str(interaction.user.id)
        was_update = user_id in bot_ratings
        
        bot_ratings[user_id] = {
            'rating': stars,
            'timestamp': datetime.utcnow().isoformat(),
            'username': str(interaction.user)
        }
        
        await save_ratings(bot_ratings)
        update_bot_stats()  # Update stats file when rating changes
        
        star_text = "⭐" * stars
        action = "updated" if was_update else "submitted"
        
        emb = make_embed(
            title='Rating Submitted! 🎉',
            description=f'Thank you for rating the bot!\n\nYour rating: {star_text} ({stars}/5)\n\nYour feedback has been {action} successfully.',
            color=discord.Color.gold()
        )
        emb.set_footer(text=f"Use /ratings to see overall statistics")
        
        await interaction.response.send_message(embed=emb, ephemeral=True)
        logger.info(f"User {interaction.user} rated the bot {stars}/5 ({action})")


class TranslationLanguageView(discord.ui.View):
    """View for selecting translation language when user has multiple role languages."""
    
    def __init__(self, user_languages: list, message_content: str, source_lang: str):
        super().__init__(timeout=180)
        self.user_languages = user_languages  # [(lang_code, lang_name), ...]
        self.message_content = message_content
        self.source_lang = source_lang
        
        # Add buttons for each language (max 5 per row)
        for lang_code, lang_name in user_languages[:5]:  # Discord limit: 5 buttons per row
            flag_emoji = {
                'ar': '🇸🇦', 'en': '🇬🇧', 'tr': '🇹🇷',
                'ja': '🇯🇵', 'fr': '🇫🇷', 'ko': '🇰🇷', 'it': '🇮🇹', 'zh-CN': '🇨🇳'
            }.get(lang_code, '🌐')
            
            button = discord.ui.Button(
                label=f"{flag_emoji} {lang_name}",
                style=discord.ButtonStyle.primary,
                custom_id=f"translate_{lang_code}"
            )
            button.callback = self.create_callback(lang_code, lang_name)
            self.add_item(button)
    
    def create_callback(self, target_lang: str, lang_name: str):
        """Create callback function for translation button."""
        async def callback(interaction: discord.Interaction):
            try:
                # Check if same language
                if self.source_lang == target_lang:
                    emb = make_embed(
                        title=get_translation_message(target_lang, 'same_language_title'),
                        description=get_translation_message(target_lang, 'same_language').replace('العربية', lang_name).replace('English', lang_name).replace('Türkçe', lang_name).replace('日本語', lang_name).replace('français', lang_name).replace('한국어', lang_name).replace('italiano', lang_name).replace('中文', lang_name),
                        color=discord.Color.orange()
                    )
                    await interaction.response.send_message(embed=emb, ephemeral=True)
                    return
                
                # Translate using cache or API
                cache_key = (hash(self.message_content), self.source_lang, target_lang)
                
                if cache_key in translation_cache:
                    translated = translation_cache[cache_key]
                else:
                    translated = GoogleTranslator(source=self.source_lang, target=target_lang).translate(self.message_content)
                    if translated:
                        translation_cache[cache_key] = translated
                        
                        # Smart cache cleaning: remove same amount of oldest unused entries as new ones added
                        if len(translation_cache) > CACHE_MAX_SIZE:
                            excess_count = len(translation_cache) - CACHE_MAX_SIZE
                            for _ in range(excess_count):
                                if translation_cache:
                                    translation_cache.pop(next(iter(translation_cache)))
                
                if not translated:
                    emb = make_embed(
                        title=get_translation_message(target_lang, 'translation_failed_title'),
                        description=get_translation_message(target_lang, 'translation_failed'),
                        color=discord.Color.red()
                    )
                    await interaction.response.send_message(embed=emb, ephemeral=True)
                    return
                
                # Create translation embed
                source_name = LANGUAGE_NAMES.get(self.source_lang, f'Unknown ({self.source_lang})')
                flag_emoji = {
                    'ar': '🇸🇦', 'en': '🇬🇧', 'tr': '🇹🇷',
                    'ja': '🇯🇵', 'fr': '🇫🇷', 'ko': '🇰🇷', 'it': '🇮🇹', 'zh-CN': '🇨🇳'
                }.get(target_lang, '🌐')
                
                emb = make_embed(
                    title=f'{flag_emoji} {lang_name}',
                    description=f'━━━━━━━━━━━━━━━━━━━━━\n{translated}\n━━━━━━━━━━━━━━━━━━━━━',
                    color=discord.Color.blue()
                )
                emb.add_field(
                    name=get_translation_message(target_lang, 'original_message'),
                    value=self.message_content[:1024] if len(self.message_content) <= 1024 else self.message_content[:1021] + '...',
                    inline=False
                )
                emb.set_footer(text=f'{source_name} → {lang_name}')
                
                await interaction.response.send_message(embed=emb, ephemeral=True)
                logger.info(f"User {interaction.user} translated message from {self.source_lang} to {target_lang}")
                
            except Exception as e:
                logger.error(f"Error in translation button callback: {e}")
                emb = make_embed(
                    title=get_translation_message(target_lang, 'translation_error_title'),
                    description=f'{get_translation_message(target_lang, "translation_error")} {str(e)}',
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=emb, ephemeral=True)
        
        return callback


class ChannelListView(discord.ui.View):
    """Paginated view for channel list with dropdown filter and navigation."""
    
    def __init__(self, configured_channels: list, unconfigured_channels: list, guild_name: str):
        super().__init__(timeout=180)
        self.configured = configured_channels
        self.unconfigured = unconfigured_channels
        self.guild_name = guild_name
        self.current_page = 0
        self.items_per_page = 5
        self.view_mode = 'configured'  # 'configured' or 'unconfigured'
        
        # Add dropdown first
        self.add_item(ChannelFilterSelect(self))
        
        # Calculate total pages for each mode
        self.configured_pages = (len(self.configured) + self.items_per_page - 1) // self.items_per_page if self.configured else 0
        self.unconfigured_pages = (len(self.unconfigured) + self.items_per_page - 1) // self.items_per_page if self.unconfigured else 0
        
        self.update_buttons()
    
    def get_total_pages(self) -> int:
        """Get total pages for current view mode."""
        if self.view_mode == 'configured':
            return max(1, self.configured_pages)
        else:
            return max(1, self.unconfigured_pages)
    
    def get_embed(self) -> discord.Embed:
        """Generate embed for current page and view mode."""
        if self.view_mode == 'configured':
            if not self.configured:
                desc = '**Channels with Language Settings:**\n\n❌ No channels have language settings configured.\n\n💡 Use `/channel addlang` to configure channel languages.'
            else:
                start_idx = self.current_page * self.items_per_page
                end_idx = min(start_idx + self.items_per_page, len(self.configured))
                items = self.configured[start_idx:end_idx]
                desc = '**Channels with Language Settings:**\n\n' + '\n'.join(items)
        else:  # unconfigured
            if not self.unconfigured:
                desc = '**Channels without Language Settings:**\n\n✅ All channels have language settings configured!'
            else:
                start_idx = self.current_page * self.items_per_page
                end_idx = min(start_idx + self.items_per_page, len(self.unconfigured))
                items = self.unconfigured[start_idx:end_idx]
                desc = '**Channels without Language Settings:**\n\n' + '\n'.join(items)
        
        total_pages = self.get_total_pages()
        emb = make_embed(
            title=f'Channel Language Overview - {self.guild_name}',
            description=desc
        )
        emb.set_footer(text=f'Page {self.current_page + 1} of {total_pages} • Filter: {self.view_mode.title()}')
        return emb
    
    def update_buttons(self):
        """Enable/disable navigation buttons based on current page and available data."""
        total_pages = self.get_total_pages()
        has_data = (self.view_mode == 'configured' and self.configured) or (self.view_mode == 'unconfigured' and self.unconfigured)
        
        # Disable buttons if no data or only one page
        self.previous_button.disabled = (self.current_page == 0) or not has_data or total_pages <= 1
        self.next_button.disabled = (self.current_page >= total_pages - 1) or not has_data or total_pages <= 1
    
    @discord.ui.button(label='◀️', style=discord.ButtonStyle.secondary, custom_id='previous', row=1)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.get_embed(), view=self)
        else:
            await interaction.response.defer()
    
    @discord.ui.button(label='▶️', style=discord.ButtonStyle.secondary, custom_id='next', row=1)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        total_pages = self.get_total_pages()
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.get_embed(), view=self)
        else:
            await interaction.response.defer()
    
    async def on_timeout(self):
        """Disable all components when view times out."""
        for item in self.children:
            item.disabled = True


class ChannelFilterSelect(discord.ui.Select):
    """Dropdown to filter between configured and unconfigured channels."""
    
    def __init__(self, parent_view: ChannelListView):
        self.parent_view = parent_view
        
        # Count channels
        configured_count = len(parent_view.configured)
        unconfigured_count = len(parent_view.unconfigured)
        
        options = [
            discord.SelectOption(
                label=f'Channels with Language ({configured_count})',
                value='configured',
                description='Show channels that have language settings',
                emoji='✅',
                default=True
            ),
            discord.SelectOption(
                label=f'Channels without Language ({unconfigured_count})',
                value='unconfigured',
                description='Show channels without language settings',
                emoji='⚪'
            )
        ]
        
        super().__init__(
            placeholder='Select channel filter...',
            options=options,
            custom_id='channel_filter',
            row=0
        )
    
    async def callback(self, interaction: discord.Interaction):
        """Handle filter selection."""
        self.parent_view.view_mode = self.values[0]
        self.parent_view.current_page = 0  # Reset to first page
        
        # Update dropdown default selection
        for option in self.options:
            option.default = (option.value == self.values[0])
        
        self.parent_view.update_buttons()
        await interaction.response.edit_message(embed=self.parent_view.get_embed(), view=self.parent_view)


# ============================================================================
# AUTOCOMPLETE FUNCTIONS
# ============================================================================

async def channel_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    """Autocomplete for channel selection - shows all text channels."""
    if not interaction.guild:
        return []
    
    channels = [
        ch for ch in interaction.guild.channels 
        if isinstance(ch, (discord.TextChannel, discord.VoiceChannel, discord.ForumChannel))
    ]
    
    if current:
        channels = [ch for ch in channels if current.lower() in ch.name.lower()]
    
    return [
        app_commands.Choice(name=f"#{ch.name}", value=str(ch.id))
        for ch in channels[:25]
    ]


async def configured_channel_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    """Autocomplete for configured channels only - shows only channels with language settings."""
    if not interaction.guild:
        return []
    
    guild_channel_ids = {str(ch.id) for ch in interaction.guild.channels}
    
    configured = []
    for ch_id, lang_code in channel_langs.items():
        if ch_id in guild_channel_ids:
            ch = interaction.guild.get_channel(int(ch_id))
            if ch and isinstance(ch, (discord.TextChannel, discord.VoiceChannel, discord.ForumChannel)):
                lang_name = SUPPORTED.get(lang_code, lang_code)
                configured.append((ch, lang_name))
    
    if current:
        configured = [(ch, lang) for ch, lang in configured if current.lower() in ch.name.lower()]
    
    return [
        app_commands.Choice(name=f"#{ch.name} ({lang})", value=str(ch.id))
        for ch, lang in configured[:25]
    ]


async def mentionable_role_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    """Autocomplete for mentionable roles only - shows only roles with mentionable enabled."""
    if not interaction.guild:
        return []
    
    # Get all mentionable roles (excluding @everyone)
    mentionable_roles = [
        role for role in interaction.guild.roles 
        if role.mentionable and role.name != "@everyone"
    ]
    
    # Filter by current input
    if current:
        mentionable_roles = [
            role for role in mentionable_roles 
            if current.lower() in role.name.lower()
        ]
    
    # Sort by position (highest first) and limit to 25
    mentionable_roles.sort(key=lambda r: r.position, reverse=True)
    
    return [
        app_commands.Choice(name=f"@{role.name}", value=str(role.id))
        for role in mentionable_roles[:25]
    ]


async def allowed_role_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    """Autocomplete for allowed roles only - shows only roles that have been added to language management."""
    if not interaction.guild:
        return []
    
    guild_id = str(interaction.guild.id)
    
    # Get allowed role IDs for this guild
    if guild_id not in allowed_roles or not allowed_roles[guild_id]:
        return []
    
    # Get role objects for allowed roles
    allowed_role_objs = []
    for role_id in allowed_roles[guild_id]:
        role = interaction.guild.get_role(int(role_id))
        if role:
            allowed_role_objs.append(role)
    
    # Filter by current input
    if current:
        allowed_role_objs = [
            role for role in allowed_role_objs 
            if current.lower() in role.name.lower()
        ]
    
    # Sort by position (highest first)
    allowed_role_objs.sort(key=lambda r: r.position, reverse=True)
    
    # Get role permissions details
    role_choices = []
    for role in allowed_role_objs[:25]:
        # Determine permissions level
        if role.permissions.administrator:
            perm_text = "Admin"
        else:
            perm_text = "Language Manager"
        
        role_choices.append(
            app_commands.Choice(
                name=f"@{role.name} ({perm_text})", 
                value=str(role.id)
            )
        )
    
    return role_choices


class UnifiedListView(discord.ui.View):
    """Unified view for all list commands with dropdown filters and pagination."""
    
    def __init__(self, interaction: discord.Interaction):
        super().__init__(timeout=300)
        self.interaction = interaction
        self.current_tab = 'channels'
        self.channel_filter = 'configured'  # configured, unconfigured
        self.language_filter = 'primary'    # primary, all
        self.page = 0
        self.items_per_page = 8
        self.update_view()
    
    def update_view(self):
        """Update view components based on current tab."""
        self.clear_items()
        
        # Tab buttons (Row 0)
        self.add_item(discord.ui.Button(
            label="📋 Channels",
            style=discord.ButtonStyle.primary if self.current_tab == 'channels' else discord.ButtonStyle.secondary,
            custom_id="tab_channels",
            row=0
        ))
        self.add_item(discord.ui.Button(
            label="🌐 Languages",
            style=discord.ButtonStyle.primary if self.current_tab == 'languages' else discord.ButtonStyle.secondary,
            custom_id="tab_languages",
            row=0
        ))
        self.add_item(discord.ui.Button(
            label="🛡️ Roles",
            style=discord.ButtonStyle.primary if self.current_tab == 'roles' else discord.ButtonStyle.secondary,
            custom_id="tab_roles",
            row=0
        ))
        self.add_item(discord.ui.Button(
            label="🎭 Role Languages",
            style=discord.ButtonStyle.primary if self.current_tab == 'role_languages' else discord.ButtonStyle.secondary,
            custom_id="tab_role_languages",
            row=0
        ))
        
        # Add dropdown for channels/languages tabs (Row 1)
        if self.current_tab == 'channels':
            select = discord.ui.Select(
                placeholder="Filter channels...",
                options=[
                    discord.SelectOption(label="Configured Channels", value="configured", emoji="✅", 
                                       description="Channels with language settings", 
                                       default=self.channel_filter == 'configured'),
                    discord.SelectOption(label="Unconfigured Channels", value="unconfigured", emoji="⚪",
                                       description="Channels without language settings",
                                       default=self.channel_filter == 'unconfigured')
                ],
                custom_id="channel_filter",
                row=1
            )
            select.callback = self.on_channel_filter
            self.add_item(select)
        elif self.current_tab == 'languages':
            select = discord.ui.Select(
                placeholder="Select language category...",
                options=[
                    discord.SelectOption(label="Primary Languages (8)", value="primary", emoji="⭐",
                                       description="Languages you can set for channels",
                                       default=self.language_filter == 'primary'),
                    discord.SelectOption(label="All Languages (35+)", value="all", emoji="🌍",
                                       description="All languages bot can translate",
                                       default=self.language_filter == 'all')
                ],
                custom_id="language_filter",
                row=1
            )
            select.callback = self.on_language_filter
            self.add_item(select)
        
        # Pagination buttons (Row 2) - only for channels and languages with all filter
        if self.current_tab in ['channels', 'languages']:
            total_items = self.get_total_items()
            total_pages = max(1, (total_items + self.items_per_page - 1) // self.items_per_page)
            
            if total_pages > 1:
                prev_btn = discord.ui.Button(
                    label="◀️ Previous",
                    style=discord.ButtonStyle.gray,
                    custom_id="prev_page",
                    disabled=self.page == 0,
                    row=2
                )
                prev_btn.callback = self.prev_page
                self.add_item(prev_btn)
                
                page_btn = discord.ui.Button(
                    label=f"Page {self.page + 1}/{total_pages}",
                    style=discord.ButtonStyle.secondary,
                    custom_id="page_info",
                    disabled=True,
                    row=2
                )
                self.add_item(page_btn)
                
                next_btn = discord.ui.Button(
                    label="Next ▶️",
                    style=discord.ButtonStyle.gray,
                    custom_id="next_page",
                    disabled=self.page >= total_pages - 1,
                    row=2
                )
                next_btn.callback = self.next_page
                self.add_item(next_btn)
        
        # Set callbacks for tab buttons
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                if item.custom_id == "tab_channels":
                    item.callback = self.show_channels
                elif item.custom_id == "tab_languages":
                    item.callback = self.show_languages
                elif item.custom_id == "tab_roles":
                    item.callback = self.show_roles
                elif item.custom_id == "tab_role_languages":
                    item.callback = self.show_role_languages
    
    def get_total_items(self) -> int:
        """Get total items for current view."""
        if self.current_tab == 'channels':
            guild = self.interaction.guild
            if self.channel_filter == 'configured':
                return sum(1 for ch in guild.text_channels if str(ch.id) in channel_langs)
            else:
                return sum(1 for ch in guild.text_channels if str(ch.id) not in channel_langs)
        elif self.current_tab == 'languages':
            if self.language_filter == 'primary':
                return len(SUPPORTED)
            else:
                return len(LANGUAGE_NAMES)
        return 0
    
    async def on_channel_filter(self, interaction: discord.Interaction):
        """Handle channel filter change."""
        self.channel_filter = interaction.data['values'][0]
        self.page = 0  # Reset to first page
        self.update_view()
        embed = self.get_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def on_language_filter(self, interaction: discord.Interaction):
        """Handle language filter change."""
        self.language_filter = interaction.data['values'][0]
        self.page = 0  # Reset to first page
        self.update_view()
        embed = self.get_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def prev_page(self, interaction: discord.Interaction):
        """Go to previous page."""
        self.page = max(0, self.page - 1)
        self.update_view()
        embed = self.get_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def next_page(self, interaction: discord.Interaction):
        """Go to next page."""
        total_items = self.get_total_items()
        max_page = max(0, (total_items + self.items_per_page - 1) // self.items_per_page - 1)
        self.page = min(max_page, self.page + 1)
        self.update_view()
        embed = self.get_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def show_channels(self, interaction: discord.Interaction):
        """Show channels tab."""
        self.current_tab = 'channels'
        self.page = 0
        self.update_view()
        embed = self.get_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def show_languages(self, interaction: discord.Interaction):
        """Show languages tab."""
        self.current_tab = 'languages'
        self.page = 0
        self.update_view()
        embed = self.get_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def show_roles(self, interaction: discord.Interaction):
        """Show roles tab."""
        self.current_tab = 'roles'
        self.page = 0
        self.update_view()
        embed = self.get_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def show_role_languages(self, interaction: discord.Interaction):
        """Show role languages tab."""
        self.current_tab = 'role_languages'
        self.page = 0
        self.update_view()
        embed = self.get_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    def get_embed(self) -> discord.Embed:
        """Get current embed based on tab."""
        if self.current_tab == 'channels':
            return self.get_channels_embed()
        elif self.current_tab == 'languages':
            return self.get_languages_embed()
        elif self.current_tab == 'roles':
            return self.get_roles_embed()
        else:
            return self.get_role_languages_embed()
    
    def get_channels_embed(self) -> discord.Embed:
        """Generate channels list embed with pagination."""
        guild = self.interaction.guild
        
        # Get filtered channels
        if self.channel_filter == 'configured':
            channels_list = []
            for channel in guild.text_channels:
                channel_id = str(channel.id)
                if channel_id in channel_langs:
                    channel_config = channel_langs[channel_id]
                    
                    # Handle both old (string) and new (dict) formats
                    if isinstance(channel_config, dict):
                        primary_lang = channel_config.get('primary')
                        secondary_lang = channel_config.get('secondary')
                    else:
                        primary_lang = channel_config
                        secondary_lang = None
                    
                    # Get language names
                    primary_name = SUPPORTED.get(primary_lang, primary_lang) if primary_lang else 'Unknown'
                    
                    # Flag emojis
                    flag_emoji = {
                        'ar': '🇸🇦', 'en': '🇬🇧', 'tr': '🇹🇷',
                        'ja': '🇯🇵', 'fr': '🇫🇷', 'ko': '🇰🇷', 'it': '🇮🇹', 'zh-CN': '🇨🇳'
                    }.get(primary_lang, '🌐')
                    
                    # Build display text
                    if secondary_lang:
                        secondary_name = SUPPORTED.get(secondary_lang, secondary_lang)
                        secondary_flag = {
                            'ar': '🇸🇦', 'en': '🇬🇧', 'tr': '🇹🇷',
                            'ja': '🇯🇵', 'fr': '🇫🇷', 'ko': '�🇷', 'it': '🇮🇹', 'zh-CN': '🇨🇳'
                        }.get(secondary_lang, '�🌐')
                        channels_list.append(
                            f"{flag_emoji} {channel.mention} → **{primary_name}** (`{primary_lang}`) ↔️ {secondary_flag} **{secondary_name}** (`{secondary_lang}`)"
                        )
                    else:
                        channels_list.append(f"{flag_emoji} {channel.mention} → **{primary_name}** (`{primary_lang}`)")
        else:
            channels_list = []
            for channel in guild.text_channels:
                if str(channel.id) not in channel_langs:
                    channels_list.append(f"⚪ {channel.mention}")
        
        # Pagination
        start_idx = self.page * self.items_per_page
        end_idx = start_idx + self.items_per_page
        page_items = channels_list[start_idx:end_idx]
        total_pages = max(1, (len(channels_list) + self.items_per_page - 1) // self.items_per_page)
        
        filter_label = "✅ Configured" if self.channel_filter == 'configured' else "⚪ Unconfigured"
        
        emb = make_embed(
            title=f'📋 Channel Language Settings - {filter_label}',
            color=discord.Color.green() if self.channel_filter == 'configured' else discord.Color.greyple()
        )
        
        if page_items:
            emb.description = '\n'.join(page_items)
        else:
            emb.description = f'❌ No {filter_label.lower()} channels found.'
        
        emb.set_footer(text=f'Page {self.page + 1}/{total_pages} • Total: {len(channels_list)} channels • ↔️ = Bidirectional translation')
        return emb
    
    def get_languages_embed(self) -> discord.Embed:
        """Generate languages embed with pagination."""
        if self.language_filter == 'primary':
            # Primary languages
            langs = []
            for code, name in SUPPORTED.items():
                flag_emoji = {
                    'ar': '🇸🇦', 'en': '🇬🇧', 'tr': '🇹🇷',
                    'ja': '🇯🇵', 'fr': '🇫🇷', 'ko': '🇰🇷', 'it': '🇮🇹', 'zh-CN': '🇨🇳'
                }.get(code, '🌐')
                langs.append(f"{flag_emoji} **{name}** (`{code}`)")
            
            emb = make_embed(
                title='⭐ Primary Translation Languages',
                description='**These languages can be set for channels:**\n\n' + '\n'.join(langs),
                color=discord.Color.gold()
            )
            emb.set_footer(text=f'Total: {len(SUPPORTED)} primary languages • Use /channel addlang to set')
            return emb
        else:
            # All languages with pagination
            langs = []
            for code, name in sorted(LANGUAGE_NAMES.items(), key=lambda x: x[1]):
                is_primary = code in SUPPORTED
                emoji = "⭐" if is_primary else "🌍"
                langs.append(f"{emoji} **{name}** (`{code}`)")
            
            # Pagination
            start_idx = self.page * self.items_per_page
            end_idx = start_idx + self.items_per_page
            page_items = langs[start_idx:end_idx]
            total_pages = max(1, (len(langs) + self.items_per_page - 1) // self.items_per_page)
            
            emb = make_embed(
                title='🌍 All Supported Languages',
                description='⭐ = Can be set for channels\n🌍 = Can be translated\n\n' + '\n'.join(page_items),
                color=discord.Color.blue()
            )
            emb.set_footer(text=f'Page {self.page + 1}/{total_pages} • Total: {len(LANGUAGE_NAMES)} languages')
            return emb
    
    def get_roles_embed(self) -> discord.Embed:
        """Generate roles list embed."""
        guild = self.interaction.guild
        guild_id = str(guild.id)
        
        emb = make_embed(
            title='🛡️ Language Management Permissions',
            color=discord.Color.gold()
        )
        
        if guild_id not in allowed_roles or not allowed_roles[guild_id]:
            emb.description = '**No custom roles configured.**\n\n✅ Server Owner and Administrators have full access by default.\n\n💡 Use `/role perms` to grant permissions to specific roles.'
        else:
            role_list = []
            for role_id in allowed_roles[guild_id]:
                role = guild.get_role(int(role_id))
                if role:
                    # Get permissions for this role
                    perms = role_permissions.get(guild_id, {}).get(role_id, [])
                    perm_count = len(perms) if perms else 'All'
                    badge = '🔒' if role.permissions.administrator else '✅'
                    role_list.append(f'{badge} {role.mention} — **{perm_count}** permissions')
                else:
                    role_list.append(f'❌ ~~Deleted Role~~ (ID: {role_id})')
            
            emb.add_field(
                name=f'📋 Allowed Roles ({len(allowed_roles[guild_id])})',
                value='\n'.join(role_list),
                inline=False
            )
            
            emb.add_field(
                name='🔐 Built-in Access',
                value='• 👑 Server Owner — Full control\n• 🛡️ Administrators — Full control',
                inline=False
            )
        
        emb.set_footer(text='💡 Use /role perms or /role editperms to manage permissions')
        return emb
    
    def get_role_languages_embed(self) -> discord.Embed:
        """Generate role languages embed."""
        guild = self.interaction.guild
        guild_id = str(guild.id)
        
        emb = make_embed(
            title='🎭 Role Language Assignments',
            color=discord.Color.purple()
        )
        
        if guild_id not in role_languages or not role_languages[guild_id]:
            emb.description = '**No role language assignments yet.**\n\n**How to set up:**\n1. Use `/role setlang` to assign languages to roles\n2. Members with those roles can right-click messages\n3. Select "Translate Message" to translate instantly\n\n💡 **Example:** Assign English to @English-Speakers role'
        else:
            role_list = []
            for role_id, lang_code in role_languages[guild_id].items():
                role = guild.get_role(int(role_id))
                lang_name = SUPPORTED.get(lang_code, lang_code)
                flag_emoji = {
                    'ar': '🇸🇦', 'en': '🇬🇧', 'tr': '🇹🇷',
                    'ja': '🇯🇵', 'fr': '🇫🇷', 'ko': '🇰🇷', 'it': '🇮🇹', 'zh-CN': '🇨🇳'
                }.get(lang_code, '🌐')
                
                if role:
                    member_count = len(role.members)
                    role_list.append(f'{flag_emoji} {role.mention} → **{lang_name}** ({member_count} members)')
                else:
                    role_list.append(f'{flag_emoji} ~~Deleted Role~~ (ID: {role_id}) → **{lang_name}**')
            
            emb.add_field(
                name=f'✨ Configured Roles ({len(role_languages[guild_id])})',
                value='\n'.join(role_list),
                inline=False
            )
            
            emb.add_field(
                name='🖱️ How it works',
                value='✅ Right-click any message\n✅ Select "Translate Message"\n✅ Instant translation to your role language',
                inline=False
            )
        
        emb.set_footer(text='💡 Use /role setlang to assign role languages')
        return emb


# ============================================================================
# CONTEXT MENU COMMANDS
# ============================================================================

@bot.tree.context_menu(name='Translate Message')
async def translate_message_context(interaction: discord.Interaction, message: discord.Message):
    """Context menu command to translate a message based on user's role languages."""
    try:
        # Get message content
        content = message.content.strip()
        
        if not content:
            emb = make_embed(
                title='No Text Content',
                description='⚠️ This message has no text content to translate.',
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return
        
        # Get user's role languages
        guild_id = str(interaction.guild.id)
        user_role_ids = [str(role.id) for role in interaction.user.roles]
        
        user_languages = []
        if guild_id in role_languages:
            for role_id in user_role_ids:
                if role_id in role_languages[guild_id]:
                    lang_code = role_languages[guild_id][role_id]
                    lang_name = SUPPORTED.get(lang_code, lang_code)
                    user_languages.append((lang_code, lang_name))
        
        # If user has no role languages, show error
        if not user_languages:
            emb = make_embed(
                title='No Language Roles',
                description='⚠️ You don\'t have any language roles assigned.\n\n💡 **Ask an admin to:**\n1. Use `/role setlang` to assign languages to roles\n2. Give you a role with a language assigned',
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return
        
        # Detect message language
        try:
            detected = detect(content)
        except Exception as e:
            logger.debug(f"Language detection failed: {e}")
            detected = 'auto'
        
        # If only one language, translate directly
        if len(user_languages) == 1:
            target_lang, lang_name = user_languages[0]
            
            # Check if same language
            if detected == target_lang:
                emb = make_embed(
                    title=get_translation_message(target_lang, 'same_language_title'),
                    description=get_translation_message(target_lang, 'same_language').replace('العربية', lang_name).replace('English', lang_name).replace('Türkçe', lang_name).replace('日本語', lang_name).replace('français', lang_name).replace('한국어', lang_name).replace('italiano', lang_name).replace('中文', lang_name),
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=emb, ephemeral=True)
                return
            
            # Translate
            try:
                cache_key = (hash(content), detected, target_lang)
                
                if cache_key in translation_cache:
                    translated = translation_cache[cache_key]
                else:
                    translated = GoogleTranslator(source=detected, target=target_lang).translate(content)
                    if translated:
                        translation_cache[cache_key] = translated
                        
                        # Smart cache cleaning: remove same amount of oldest unused entries as new ones added
                        if len(translation_cache) > CACHE_MAX_SIZE:
                            excess_count = len(translation_cache) - CACHE_MAX_SIZE
                            for _ in range(excess_count):
                                if translation_cache:
                                    translation_cache.pop(next(iter(translation_cache)))
                
                if not translated:
                    emb = make_embed(
                        title=get_translation_message(target_lang, 'translation_failed_title'),
                        description=get_translation_message(target_lang, 'translation_failed'),
                        color=discord.Color.red()
                    )
                    await interaction.response.send_message(embed=emb, ephemeral=True)
                    return
                
                # Create translation embed
                source_name = LANGUAGE_NAMES.get(detected, f'Unknown ({detected})')
                flag_emoji = {
                    'ar': '🇸🇦', 'en': '🇬🇧', 'tr': '🇹🇷',
                    'ja': '🇯🇵', 'fr': '🇫🇷', 'ko': '🇰🇷', 'it': '🇮🇹', 'zh-CN': '🇨🇳'
                }.get(target_lang, '🌐')
                
                to_word = get_translation_message(target_lang, 'to')
                emb = make_embed(
                    title=f'{flag_emoji} {lang_name}',
                    description=f'━━━━━━━━━━━━━━━━━━━━━\n{translated}\n━━━━━━━━━━━━━━━━━━━━━',
                    color=discord.Color.blue()
                )
                emb.add_field(
                    name=get_translation_message(target_lang, 'original_message'),
                    value=content[:1024] if len(content) <= 1024 else content[:1021] + '...',
                    inline=False
                )
                emb.set_footer(text=f'{source_name} → {lang_name}')
                
                await interaction.response.send_message(embed=emb, ephemeral=True)
                logger.info(f"User {interaction.user} translated message from {detected} to {target_lang}")
                
            except Exception as e:
                logger.error(f"Translation error: {e}")
                emb = make_embed(
                    title=get_translation_message(target_lang, 'translation_error_title'),
                    description=f'{get_translation_message(target_lang, "translation_error")} {str(e)}',
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=emb, ephemeral=True)
        
        else:
            # Multiple languages - show selection buttons
            view = TranslationLanguageView(user_languages, content, detected)
            
            emb = make_embed(
                title='🌐 Choose Translation Language',
                description='You have multiple language roles. Please select your preferred language:',
                color=discord.Color.blurple()
            )
            emb.add_field(
                name='📝 Original Message',
                value=content[:1024] if len(content) <= 1024 else content[:1021] + '...',
                inline=False
            )
            
            await interaction.response.send_message(embed=emb, view=view, ephemeral=True)
            
    except Exception as e:
        logger.error(f"Error in translate_message_context: {e}")
        emb = make_embed(
            title='Error',
            description=f'❌ An error occurred: {str(e)}',
            color=discord.Color.red()
        )
        try:
            await interaction.response.send_message(embed=emb, ephemeral=True)
        except:
            await interaction.followup.send(embed=emb, ephemeral=True)


# ============================================================================
# BOT CONTROL PANEL (OWNER ONLY)
# ============================================================================

class PriorityGuildsModal(discord.ui.Modal, title="إضافة سيرفر مهم"):
    """Modal to add a priority guild."""
    
    guild_id = discord.ui.TextInput(
        label="ID السيرفر",
        placeholder="1234567890123456",
        required=True,
        min_length=17,
        max_length=20
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        global priority_guilds
        try:
            gid = int(self.guild_id.value)
            
            if gid in priority_guilds:
                await interaction.response.send_message(
                    "⚠️ هذا السيرفر موجود مسبقاً في القائمة!",
                    ephemeral=True
                )
                return
            
            # Check if bot is in this guild
            guild = bot.get_guild(gid)
            if not guild:
                await interaction.response.send_message(
                    "⚠️ البوت ليس موجوداً في هذا السيرفر!",
                    ephemeral=True
                )
                return
            
            priority_guilds.append(gid)
            save_priority_guilds()
            
            # Sync commands to this guild immediately
            await bot.tree.sync(guild=discord.Object(id=gid))
            
            await interaction.response.send_message(
                f"✅ تمت إضافة السيرفر **{guild.name}** وتم مزامنة الأوامر فوراً!",
                ephemeral=True
            )
            
        except ValueError:
            await interaction.response.send_message(
                "❌ يجب إدخال رقم صحيح لـ ID السيرفر!",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ حدث خطأ: {str(e)}",
                ephemeral=True
            )


class PriorityGuildsView(discord.ui.View):
    """View for managing priority guilds."""
    
    def __init__(self, parent_view=None):
        super().__init__(timeout=180)
        self.parent_view = parent_view
    
    def get_embed(self):
        """Generate embed showing priority guilds."""
        global priority_guilds
        
        embed = discord.Embed(
            title="⚡ السيرفرات ذات الأولوية",
            description="السيرفرات في هذه القائمة تحصل على تحديث فوري للأوامر",
            color=discord.Color.gold()
        )
        
        if priority_guilds:
            guilds_text = ""
            for idx, gid in enumerate(priority_guilds, 1):
                guild = bot.get_guild(gid)
                if guild:
                    guilds_text += f"{idx}. **{guild.name}** ({guild.member_count} عضو)\n"
                else:
                    guilds_text += f"{idx}. سيرفر غير معروف (ID: {gid})\n"
            
            embed.add_field(
                name=f"📋 السيرفرات المسجلة ({len(priority_guilds)})",
                value=guilds_text,
                inline=False
            )
        else:
            embed.add_field(
                name="📋 السيرفرات المسجلة",
                value="*لا توجد سيرفرات مسجلة حالياً*",
                inline=False
            )
        
        embed.set_footer(text="ℹ️ يمكنك إضافة/حذف السيرفرات من الأزرار أدناه")
        return embed
    
    @discord.ui.button(label="➕ إضافة سيرفر", style=discord.ButtonStyle.success, row=0)
    async def add_guild(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Add a new priority guild."""
        modal = PriorityGuildsModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="➖ حذف سيرفر", style=discord.ButtonStyle.danger, row=0)
    async def remove_guild(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Remove a priority guild."""
        global priority_guilds
        
        if not priority_guilds:
            await interaction.response.send_message(
                "⚠️ لا توجد سيرفرات لحذفها!",
                ephemeral=True
            )
            return
        
        # Create select menu with guilds
        options = []
        for gid in priority_guilds[:25]:  # Discord limit
            guild = bot.get_guild(gid)
            if guild:
                options.append(
                    discord.SelectOption(
                        label=guild.name[:100],
                        description=f"ID: {gid}",
                        value=str(gid)
                    )
                )
            else:
                options.append(
                    discord.SelectOption(
                        label=f"سيرفر غير معروف",
                        description=f"ID: {gid}",
                        value=str(gid)
                    )
                )
        
        class RemoveSelect(discord.ui.Select):
            def __init__(self):
                super().__init__(
                    placeholder="اختر السيرفر المراد حذفه...",
                    options=options,
                    row=0
                )
            
            async def callback(self, select_interaction: discord.Interaction):
                global priority_guilds
                gid = int(self.values[0])
                guild = bot.get_guild(gid)
                guild_name = guild.name if guild else f"ID: {gid}"
                
                priority_guilds.remove(gid)
                save_priority_guilds()
                
                await select_interaction.response.send_message(
                    f"✅ تم حذف السيرفر **{guild_name}** من القائمة!",
                    ephemeral=True
                )
        
        view = discord.ui.View(timeout=60)
        view.add_item(RemoveSelect())
        
        await interaction.response.send_message(
            "🗑️ اختر السيرفر المراد حذفه:",
            view=view,
            ephemeral=True
        )
    
    @discord.ui.button(label="📋 عرض القائمة", style=discord.ButtonStyle.primary, row=1)
    async def show_list(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Refresh the list display."""
        embed = self.get_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🔄 مزامنة الآن", style=discord.ButtonStyle.primary, row=1)
    async def sync_now(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Sync commands to all priority guilds now."""
        global priority_guilds
        
        if not priority_guilds:
            await interaction.response.send_message(
                "⚠️ لا توجد سيرفرات للمزامنة!",
                ephemeral=True
            )
            return
        
        await interaction.response.defer(ephemeral=True)
        
        success = 0
        failed = 0
        for gid in priority_guilds:
            try:
                await bot.tree.sync(guild=discord.Object(id=gid))
                success += 1
            except Exception as e:
                logger.error(f"Failed to sync guild {gid}: {e}")
                failed += 1
        
        await interaction.followup.send(
            f"✅ تمت المزامنة: {success} نجح، {failed} فشل",
            ephemeral=True
        )
    
    @discord.ui.button(label="◀️ رجوع", style=discord.ButtonStyle.secondary, row=2)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go back to main control panel."""
        if self.parent_view:
            embed = await self.parent_view.get_control_embed()
            await interaction.response.edit_message(embed=embed, view=self.parent_view)
        else:
            await interaction.response.edit_message(content="✅ تم الإغلاق", embed=None, view=None)


class BotControlView(discord.ui.View):
    """Advanced control panel for bot owner only."""
    
    def __init__(self):
        super().__init__(timeout=None)  # Persistent view
        self.update_buttons()
    
    def update_buttons(self):
        """Update button states based on bot status."""
        global bot_disabled
        # Clear and rebuild buttons
        self.clear_items()
        
        # Status button (non-functional, just shows status)
        status_btn = discord.ui.Button(
            label=f"Status: {'🔴 DISABLED' if bot_disabled else '🟢 ACTIVE'}",
            style=discord.ButtonStyle.secondary,
            disabled=True,
            row=0
        )
        self.add_item(status_btn)
        
        # Toggle button
        if bot_disabled:
            toggle_btn = discord.ui.Button(
                label="🟢 Enable Bot",
                style=discord.ButtonStyle.success,
                custom_id="enable_bot",
                row=1
            )
            toggle_btn.callback = self.enable_bot
        else:
            toggle_btn = discord.ui.Button(
                label="🔴 Disable Bot",
                style=discord.ButtonStyle.danger,
                custom_id="disable_bot",
                row=1
            )
            toggle_btn.callback = self.disable_bot
        self.add_item(toggle_btn)
        
        # Sync commands button
        sync_btn = discord.ui.Button(
            label="🔄 Sync Commands",
            style=discord.ButtonStyle.primary,
            custom_id="sync_commands",
            row=1
        )
        sync_btn.callback = self.sync_commands
        self.add_item(sync_btn)
        
        # Priority guilds management button
        priority_btn = discord.ui.Button(
            label="⚡ إدارة السيرفرات",
            style=discord.ButtonStyle.primary,
            custom_id="priority_guilds",
            row=2
        )
        priority_btn.callback = self.manage_priority_guilds
        self.add_item(priority_btn)
        
        # Refresh button
        refresh_btn = discord.ui.Button(
            label="♻️ Refresh Panel",
            style=discord.ButtonStyle.secondary,
            custom_id="refresh_panel",
            row=2
        )
        refresh_btn.callback = self.refresh_panel
        self.add_item(refresh_btn)
    
    async def disable_bot(self, interaction: discord.Interaction):
        """Disable all bot commands except /control."""
        global bot_disabled
        bot_disabled = True
        self.update_buttons()
        
        emb = make_embed(
            title='🔴 Bot Disabled',
            description='**All commands have been disabled!**\n\n'
                       '✅ Only `/control` command remains active\n'
                       '❌ All other commands are now hidden and disabled\n'
                       '⚠️ Translation system is also stopped\n\n'
                       'Use the "Enable Bot" button to restore functionality.',
            color=discord.Color.red()
        )
        await interaction.response.edit_message(embed=await self.get_control_embed(), view=self)
        logger.warning(f"Bot disabled by owner {interaction.user}")
    
    async def enable_bot(self, interaction: discord.Interaction):
        """Enable all bot commands."""
        global bot_disabled
        bot_disabled = False
        self.update_buttons()
        
        emb = make_embed(
            title='🟢 Bot Enabled',
            description='**All commands have been restored!**\n\n'
                       '✅ All commands are now active\n'
                       '✅ Translation system is running\n'
                       '✅ Bot is fully operational\n\n'
                       'Everything is back to normal.',
            color=discord.Color.green()
        )
        await interaction.response.edit_message(embed=await self.get_control_embed(), view=self)
        logger.info(f"Bot enabled by owner {interaction.user}")
    
    async def sync_commands(self, interaction: discord.Interaction):
        """Sync bot commands with Discord."""
        await interaction.response.defer(ephemeral=True)
        
        try:
            synced = await bot.tree.sync()
            emb = make_embed(
                title='Commands Synced ✅',
                description=f'Successfully synced **{len(synced)}** commands.\n\n'
                           f'Commands may take a few minutes to update.',
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=emb, ephemeral=True)
            logger.info(f"Commands synced by owner {interaction.user}: {len(synced)} commands")
        except Exception as e:
            emb = make_embed(
                title='Sync Failed ❌',
                description=f'Failed to sync commands:\n```{str(e)}```',
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=emb, ephemeral=True)
            logger.error(f"Command sync failed: {e}")
    
    async def manage_priority_guilds(self, interaction: discord.Interaction):
        """Open priority guilds management panel."""
        priority_view = PriorityGuildsView(parent_view=self)
        embed = priority_view.get_embed()
        await interaction.response.edit_message(embed=embed, view=priority_view)
    
    async def refresh_panel(self, interaction: discord.Interaction):
        """Refresh the control panel."""
        self.update_buttons()
        await interaction.response.edit_message(embed=await self.get_control_embed(), view=self)
    
    async def get_control_embed(self):
        """Generate the control panel embed."""
        global bot_disabled
        
        status_emoji = "🔴" if bot_disabled else "🟢"
        status_text = "DISABLED" if bot_disabled else "ACTIVE"
        status_color = discord.Color.red() if bot_disabled else discord.Color.green()
        
        emb = make_embed(
            title='🎛️ Bot Control Panel',
            description=f'**Current Status:** {status_emoji} **{status_text}**\n\n'
                       f'Use the buttons below to control the bot.',
            color=status_color
        )
        
        # Bot info
        emb.add_field(
            name='📊 Bot Information',
            value=f'**Servers:** {len(bot.guilds)}\n'
                  f'**Users:** {sum(g.member_count for g in bot.guilds):,}\n'
                  f'**Latency:** {round(bot.latency * 1000)}ms\n'
                  f'**Version:** Kingdom-77 v{VERSION}',
            inline=True
        )
        
        # Status info
        if bot_disabled:
            emb.add_field(
                name='⚠️ Disabled Mode',
                value='• All commands hidden\n'
                      '• Translation stopped\n'
                      '• Only /control works',
                inline=True
            )
        else:
            emb.add_field(
                name='✅ Active Mode',
                value='• All commands visible\n'
                      '• Translation active\n'
                      '• Fully operational',
                inline=True
            )
        
        emb.set_footer(text=f"Owner Control Panel • ID: {BOT_OWNER_ID}")
        
        return emb


# ============================================================================
# SLASH COMMANDS - BOT OWNER ONLY
# ============================================================================

@bot.tree.command(name='owner', description='👑 Owner Control Panel - لوحة تحكم المالك')
async def owner_panel(interaction: discord.Interaction):
    """Display bot owner control panel - accessible only by bot owner."""
    logger.info(f"🔍 Owner panel access attempt by {interaction.user} (ID: {interaction.user.id})")
    logger.info(f"🔑 Comparing with BOT_OWNER_ID: {BOT_OWNER_ID}")
    
    # Check if user is the bot owner
    if interaction.user.id != BOT_OWNER_ID:
        logger.warning(f"⛔ Owner panel access denied for {interaction.user} (ID: {interaction.user.id})")
        emb = make_embed(
            title='Access Denied',
            description='⛔ هذا الأمر مخصص لمالك البوت فقط.',
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=emb, ephemeral=True)
        return
    
    # Create control panel
    logger.info(f"✅ Owner panel access granted for owner {interaction.user}")
    view = BotControlView()
    embed = await view.get_control_embed()
    
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    logger.info(f"Owner panel accessed by owner {interaction.user}")


# ============================================================================
# SLASH COMMANDS - GENERAL
# ============================================================================

@bot.tree.command(name='ping', description='Check if the bot is responsive')
async def ping(interaction: discord.Interaction):
    """Check bot responsiveness and latency with visual indicators."""
    # Check if bot is disabled
    if bot_disabled and interaction.user.id != BOT_OWNER_ID:
        return
    
    ws_ms = round(bot.latency * 1000)
    
    # Determine emoji and status based on latency ranges
    if ws_ms < 50:
        emoji = "❄️"  # Excellent - Frozen fast
        status = "**ممتاز - سريع جداً**"
        status_en = "Excellent - Lightning Fast"
        color = discord.Color.blue()
    elif ws_ms < 100:
        emoji = "⚡"  # Great - Very fast
        status = "**رائع - سريع**"
        status_en = "Great - Very Fast"
        color = discord.Color.green()
    elif ws_ms < 200:
        emoji = "✅"  # Good - Fast
        status = "**جيد - طبيعي**"
        status_en = "Good - Normal"
        color = discord.Color.brand_green()
    elif ws_ms < 300:
        emoji = "⚠️"  # Fair - Slow
        status = "**مقبول - بطيء قليلاً**"
        status_en = "Fair - Slightly Slow"
        color = discord.Color.gold()
    elif ws_ms < 500:
        emoji = "🔥"  # Poor - Very slow
        status = "**ضعيف - بطيء**"
        status_en = "Poor - Slow"
        color = discord.Color.orange()
    else:
        emoji = "�"  # Critical - Extremely slow
        status = "**حرج - بطيء جداً**"
        status_en = "Critical - Very Slow"
        color = discord.Color.red()
    
    emb = make_embed(
        title=f"Pong! {emoji}",
        description=f"{status}\n{status_en}\n\n📡 **WebSocket Latency:** {ws_ms} ms",
        color=color
    )
    emb.set_footer(text="Latency may vary • Measures websocket heartbeat latency")
    await interaction.response.send_message(embed=emb, ephemeral=True)


@bot.tree.command(name='botstats', description='Display bot statistics and information')
async def botstats(interaction: discord.Interaction):
    """Show comprehensive bot statistics including servers and ratings."""
    # Check if bot is disabled
    if bot_disabled and interaction.user.id != BOT_OWNER_ID:
        return
    
    try:
        # Calculate statistics
        total_servers = len(servers_data)
        active_servers = sum(1 for s in servers_data.values() if s.get('active', False))
        left_servers = total_servers - active_servers
        
        # Current connected servers (might differ from tracked active servers)
        connected_servers = len(bot.guilds)
        total_members = sum(guild.member_count for guild in bot.guilds)
        
        # Calculate ratings
        total_raters = len(bot_ratings)
        if total_raters > 0:
            total_rating_sum = sum(r.get('rating', 0) for r in bot_ratings.values())
            average_rating = total_rating_sum / total_raters
        else:
            average_rating = 0.0
        
        # Count ratings by value
        rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for rating_data in bot_ratings.values():
            rating = rating_data.get('rating', 0)
            if rating in rating_counts:
                rating_counts[rating] += 1
        
        # Build star rating bar
        if total_raters > 0:
            stars_display = "⭐" * int(round(average_rating))
            stars_display += "☆" * (5 - int(round(average_rating)))
        else:
            stars_display = "☆☆☆☆☆"
        
        # Count configured channels
        configured_channels = len(channel_langs)
        dual_lang_channels = sum(1 for c in channel_langs.values() if isinstance(c, dict) and c.get('secondary'))
        
        # Create embed
        emb = make_embed(
            title='📊 Bot Statistics',
            color=discord.Color.blurple()
        )
        
        # Server Statistics
        server_stats = f"**Connected Now:** {connected_servers} servers\n"
        server_stats += f"**Total Members:** {total_members:,} users\n"
        server_stats += f"**All-Time Joins:** {total_servers} servers\n"
        server_stats += f"├─ Currently Active: {active_servers} ✅\n"
        server_stats += f"└─ Left Servers: {left_servers} ❌"
        emb.add_field(name='🌐 Server Statistics', value=server_stats, inline=False)
        
        # Rating Statistics - Simplified (General Rating Only)
        rating_stats = f"**Average Rating:** {average_rating:.2f} / 5.00\n"
        rating_stats += f"{stars_display}\n"
        rating_stats += f"**Total Raters:** {total_raters} users"
        emb.add_field(name='⭐ Bot Rating', value=rating_stats, inline=False)
        
        # Channel Configuration
        channel_stats = f"**Configured Channels:** {configured_channels}\n"
        channel_stats += f"├─ Single Language: {configured_channels - dual_lang_channels}\n"
        channel_stats += f"└─ Dual Language: {dual_lang_channels} ↔️"
        emb.add_field(name='🌐 Channel Setup', value=channel_stats, inline=True)
        
        # Bot Info
        latency_ms = round(bot.latency * 1000)
        bot_info = f"**Latency:** {latency_ms} ms\n"
        bot_info += f"**Uptime:** Since restart\n"
        bot_info += f"**Version:** Kingdom-77 v{VERSION}"
        emb.add_field(name='🤖 Bot Info', value=bot_info, inline=True)
        
        emb.set_footer(text=f"Bot ID: {bot.user.id} • Use /rate to rate the bot!")
        
        await interaction.response.send_message(embed=emb, ephemeral=True)
        
    except Exception as e:
        logger.error(f"Error in botstats command: {e}")
        emb = make_embed(
            title='Error',
            description=f'❌ An error occurred while fetching statistics: {str(e)}',
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=emb, ephemeral=True)


@bot.tree.command(name='help', description='Show all available commands')
async def help(interaction: discord.Interaction):
    """Display help information with available commands."""
    is_admin = interaction.user.guild_permissions.administrator or interaction.guild.owner_id == interaction.user.id
    is_owner = interaction.user.id == BOT_OWNER_ID
    
    # If bot is disabled, show limited help
    if bot_disabled:
        commands_list = [
            '🔒 **Bot is currently in disabled mode**',
            '',
            '**Available Commands:**',
            '`/help` - Show this help message',
            '`/ping` - Check bot latency',
            '`/debug` - Show debug information (Admin only)',
            '`/sync` - Force sync commands (Owner only)',
            '',
            '**Status:**',
            '⛔ Translation is **disabled**',
            '⛔ Channel/Role commands are **unavailable**',
            '⛔ All management features are **offline**',
            '',
            '💡 *Only essential commands are active while disabled*'
        ]
        
        desc = '\n'.join(commands_list)
        emb = make_embed(
            title='� Bot Commands (Disabled Mode)',
            description=desc,
            color=discord.Color.orange()
        )
        emb.set_footer(text="Kingdom-77 v2.8 • Bot is temporarily disabled")
        await interaction.response.send_message(embed=emb, ephemeral=True)
        return
    
    # Normal mode - show all commands
    commands_list = [
        '**�📋 Channel Commands** (`/channel`)',
        '`/channel addlang [channel]` - Set primary & secondary language',
        '`/channel deletelang [channel]` - Remove language setting',
        '`/channel quality [channel]` - Change translation quality',
        '',
        '**👁️ View Commands** (`/view`)',
        '`/view lists` - Browse all information with filters',
        '',
        '**🖱️ Context Menu:**',
        '`Right-click message → Translate Message`',
        '💡 *Requires role with assigned language*',
        '',
        '**⭐ Bot Info:**',
        '`/rate` - Rate the bot (1-5 stars)',
        '`/ratings` - View ratings statistics',
        '`/botstats` - View comprehensive bot statistics',
        '`/ping` - Check bot latency',
        '`/help` - Show this help message'
    ]
    
    if is_admin:
        admin_commands = [
            '',
            '**🛡️ Role Commands** (`/role`) *Admin Only*',
            '`/role perms <role>` - Grant bot permissions to role',
            '`/role editperms <role>` - Edit/Revoke role permissions',
            '`/role setlang <role> <language>` - Assign default language',
            '`/role removelang <role>` - Remove language assignment',
            '',
            '**🔧 Admin Tools:**',
            '`/debug` - Show debug information',
            '`/sync` - Force sync commands (if not visible)'
        ]
        commands_list.extend(admin_commands)
    
    desc = '\n'.join(commands_list)
    
    if is_admin:
        desc += '\n\n**💡 Tip:** Commands are organized in groups for easier navigation!'
    
    emb = make_embed(title='📚 Bot Commands', description=desc)
    emb.set_footer(text="Kingdom-77 v2.8 • Use autocomplete to easily select options!")
    await interaction.response.send_message(embed=emb, ephemeral=True)


@bot.tree.command(name='debug', description='Show bot debug information (Admin only)')
async def debug_info(interaction: discord.Interaction):
    """Show debug information. Requires administrator permission."""
    if not interaction.user.guild_permissions.administrator:
        emb = make_embed(
            title='Permission Denied',
            description='⚠️ You need Administrator permission to use this command.',
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=emb, ephemeral=True)
        return
    
    try:
        total_configs = len(channel_langs)
        guild_channels = [str(c.id) for c in interaction.guild.channels]
        guild_configs = {ch_id: lang for ch_id, lang in channel_langs.items() if ch_id in guild_channels}
        
        info = [
            f"**Total channel configurations:** {total_configs}",
            f"**Configurations in this server:** {len(guild_configs)}",
            f"**Channels file path:** `{CHANNELS_FILE}`",
            f"**Bot is in {len(bot.guilds)} server(s)**",
            ""
        ]
        
        if guild_configs:
            info.append("**Configured channels in this server:**")
            for ch_id, lang_config in list(guild_configs.items())[:10]:
                try:
                    ch = interaction.guild.get_channel(int(ch_id))
                    # Handle both dict and string formats
                    if isinstance(lang_config, dict):
                        primary = lang_config.get('primary', 'unknown')
                        secondary = lang_config.get('secondary')
                        quality = lang_config.get('translation_quality', 'fast')
                        
                        lang_display = f"{SUPPORTED.get(primary, primary)}"
                        if secondary:
                            lang_display += f" + {SUPPORTED.get(secondary, secondary)}"
                        lang_display += f" ({quality})"
                    else:
                        # Legacy string format
                        lang_display = SUPPORTED.get(lang_config, lang_config)
                    
                    if ch:
                        info.append(f"• {ch.mention}: {lang_display}")
                    else:
                        info.append(f"• Channel ID {ch_id}: {lang_display} (channel not found)")
                except Exception as e:
                    info.append(f"• Channel ID {ch_id}: Error loading config")
                    logger.error(f"Error displaying channel {ch_id}: {e}")
            
            if len(guild_configs) > 10:
                info.append(f"... and {len(guild_configs) - 10} more")
        else:
            info.append("No channels configured in this server.")
        
        emb = make_embed(title='Debug Information', description='\n'.join(info))
        await interaction.response.send_message(embed=emb, ephemeral=True)
        
    except Exception as e:
        logger.error(f"Error in debug command: {e}")
        emb = make_embed(
            title='Error',
            description=f'❌ An error occurred: {str(e)}',
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=emb, ephemeral=True)


@bot.tree.command(name='sync', description='Force sync bot commands (Owner only)')
async def sync_commands(interaction: discord.Interaction):
    """Force sync slash commands with Discord. Owner only."""
    if interaction.user.id != interaction.guild.owner_id and not interaction.user.guild_permissions.administrator:
        emb = make_embed(
            title='Permission Denied',
            description='⚠️ Only Server Owner or Administrator can sync commands.',
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=emb, ephemeral=True)
        return
    
    try:
        await interaction.response.defer(ephemeral=True)
        
        # Sync globally
        synced = await bot.tree.sync()
        
        emb = make_embed(
            title='Commands Synced ✅',
            description=f'Successfully synced **{len(synced)}** global commands.\n\n**Commands:**\n' + 
                       '\n'.join([f'• `/{cmd.name}`' for cmd in synced[:20]]) +
                       (f'\n... and {len(synced) - 20} more' if len(synced) > 20 else '') +
                       '\n\n⏱️ **Note:** Changes may take a few minutes to appear.',
            color=discord.Color.green()
        )
        await interaction.followup.send(embed=emb, ephemeral=True)
        logger.info(f"Commands manually synced by {interaction.user} in {interaction.guild.name}")
        
    except Exception as e:
        logger.error(f"Error syncing commands: {e}")
        emb = make_embed(
            title='Sync Failed ❌',
            description=f'Failed to sync commands:\n```{str(e)}```',
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=emb, ephemeral=True)


# ============================================================================
# SLASH COMMANDS - VIEW/LIST (GROUP)
# ============================================================================

@view_group.command(name='lists', description='Browse all bot information with filters and pagination')
async def view_lists(interaction: discord.Interaction):
    """Unified command to view all lists with tab navigation, filters, and pagination."""
    # Check if bot is disabled (only owner can use when disabled)
    if bot_disabled and interaction.user.id != BOT_OWNER_ID:
        emb = make_embed(
            title='Bot Disabled',
            description='🔒 The bot is currently disabled. Commands are unavailable.',
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=emb, ephemeral=True)
        return
    
    try:
        view = UnifiedListView(interaction)
        embed = view.get_embed()
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        logger.info(f"User {interaction.user} opened unified list view")
        
    except Exception as e:
        logger.error(f"Error in list command: {e}")
        emb = make_embed(
            title='Error',
            description=f'❌ An error occurred: {str(e)}',
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=emb, ephemeral=True)


# ============================================================================
# SLASH COMMANDS - CHANNEL LANGUAGE MANAGEMENT (GROUP)
# ============================================================================

@channel_group.command(name='addlang', description='Add/Set language for a channel')
@app_commands.describe(
    channel='Select channel to set language for (optional, defaults to current channel)'
)
@app_commands.autocomplete(channel=channel_autocomplete)
async def channel_setlang(interaction: discord.Interaction, channel: str = None):
    """Set the default language for a channel."""
    # Check if bot is disabled (only owner can use when disabled)
    if bot_disabled and interaction.user.id != BOT_OWNER_ID:
        emb = make_embed(
            title='Bot Disabled',
            description='🔒 The bot is currently disabled. Commands are unavailable.',
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=emb, ephemeral=True)
        return
    
    guild_id = str(interaction.guild.id)
    if not has_permission(interaction.user, guild_id):
        emb = make_embed(
            title='Permission Denied',
            description='⚠️ You need proper permissions to use this command.\n\nRequired: Server Owner, Administrator, or an allowed role.',
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=emb, ephemeral=True)
        return

    try:
        if channel:
            try:
                target_channel = interaction.guild.get_channel(int(channel))
                if not target_channel:
                    emb = make_embed(
                        title='Error',
                        description='❌ Channel not found.',
                        color=discord.Color.red()
                    )
                    await interaction.response.send_message(embed=emb, ephemeral=True)
                    return
            except ValueError:
                emb = make_embed(
                    title='Error',
                    description='❌ Invalid channel.',
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=emb, ephemeral=True)
                return
        else:
            target_channel = interaction.channel
        
        # Use the new dual language view
        view = DualLanguageView(target_channel)
        emb = make_embed(
            title='Set Languages',
            description=f'Configure language settings for {target_channel.mention}:\n\n' +
                       '**1️⃣ Primary Language** (Required)\n' +
                       'Main language for translation.\n\n' +
                       '**2️⃣ Secondary Language** (Optional)\n' +
                       'Enable bidirectional translation between two languages.\n\n' +
                       '**� Blacklist Languages** (Optional)\n' +
                       'Choose languages to NOT translate (they will be ignored).\n\n' +
                       '�📝 **Example:**\n' +
                       '• Primary: Arabic (ar)\n' +
                       '• Blacklist: English (en)\n' +
                       '• Result: English messages stay untranslated, all other languages → Arabic\n\n' +
                       '**How it works:**\n' +
                       '• With only primary: All messages → Primary language\n' +
                       '• With both: Messages swap between the two languages\n' +
                       '• With blacklist: Blacklisted languages are not translated\n' +
                       '• Other languages → Always translate to primary',
            color=discord.Color.blurple()
        )
        await interaction.response.send_message(embed=emb, view=view, ephemeral=True)
    except Exception as e:
        logger.error(f"Error in setlang command: {e}")
        emb = make_embed(
            title='Error',
            description=f'❌ An error occurred: {str(e)}',
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=emb, ephemeral=True)



# ============================================================================
# SLASH COMMANDS - CHANNEL LANGUAGE MANAGEMENT (GROUP)
# ============================================================================

@channel_group.command(name='deletelang', description='Delete language setting from a channel')
@app_commands.describe(
    channel='Select channel to remove language setting from (shows only configured channels)'
)
@app_commands.autocomplete(channel=configured_channel_autocomplete)
async def channel_removelang(interaction: discord.Interaction, channel: str = None):
    """Remove language configuration from a channel."""
    # Check if bot is disabled (only owner can use when disabled)
    if bot_disabled and interaction.user.id != BOT_OWNER_ID:
        emb = make_embed(
            title='Bot Disabled',
            description='🔒 The bot is currently disabled. Commands are unavailable.',
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=emb, ephemeral=True)
        return
    
    guild_id = str(interaction.guild.id)
    if not has_permission(interaction.user, guild_id):
        emb = make_embed(
            title='Permission Denied',
            description='⚠️ You need proper permissions to use this command.\n\nRequired: Server Owner, Administrator, or an allowed role.',
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=emb, ephemeral=True)
        return

    try:
        if channel:
            try:
                target_channel = interaction.guild.get_channel(int(channel))
                if not target_channel:
                    emb = make_embed(
                        title='Error',
                        description='❌ Channel not found.',
                        color=discord.Color.red()
                    )
                    await interaction.response.send_message(embed=emb, ephemeral=True)
                    return
            except ValueError:
                emb = make_embed(
                    title='Error',
                    description='❌ Invalid channel.',
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=emb, ephemeral=True)
                return
        else:
            target_channel = interaction.channel
        
        channel_id = str(target_channel.id)
        
        if channel_id in channel_langs:
            old_lang_config = channel_langs[channel_id]
            
            # Handle both dict and string formats
            if isinstance(old_lang_config, dict):
                primary = old_lang_config.get('primary', 'unknown')
                secondary = old_lang_config.get('secondary')
                
                lang_name = SUPPORTED.get(primary, primary)
                if secondary:
                    lang_name += f" + {SUPPORTED.get(secondary, secondary)}"
                
                flag_emoji = {
                    'ar': '🇸🇦', 'en': '🇬🇧', 'tr': '🇹🇷',
                    'ja': '🇯🇵', 'fr': '🇫🇷', 'ko': '🇰🇷', 'it': '🇮🇹', 'zh-CN': '🇨🇳'
                }.get(primary, '🌐')
                
                lang_code_display = primary
                if secondary:
                    lang_code_display += f", {secondary}"
            else:
                # Legacy string format
                lang_name = SUPPORTED.get(old_lang_config, old_lang_config)
                flag_emoji = {
                    'ar': '🇸🇦', 'en': '🇬🇧', 'tr': '🇹🇷',
                    'ja': '🇯🇵', 'fr': '🇫🇷', 'ko': '🇰🇷', 'it': '🇮🇹', 'zh-CN': '🇨🇳'
                }.get(old_lang_config, '🌐')
                lang_code_display = old_lang_config
            
            del channel_langs[channel_id]
            await save_channels(channel_langs)
            
            emb = make_embed(
                title='Language Setting Removed ✅',
                description=f'Successfully removed language configuration from {target_channel.mention}',
                color=discord.Color.green()
            )
            emb.add_field(
                name='🗑️ Removed Language',
                value=f'{flag_emoji} **{lang_name}** (`{lang_code_display}`)',
                inline=False
            )
            emb.add_field(
                name='⚠️ Impact',
                value='Messages in this channel will no longer be automatically translated.',
                inline=False
            )
            emb.set_footer(text=f'Use /channel addlang to configure a new language')
            await interaction.response.send_message(embed=emb, ephemeral=True)
        else:
            emb = make_embed(
                title='Remove language',
                description=f'No language was set for {target_channel.mention}.',
                color=discord.Color.dark_grey()
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)
    except Exception as e:
        logger.error(f"Error in removelang command: {e}")
        emb = make_embed(
            title='Error',
            description=f'❌ An error occurred: {str(e)}',
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=emb, ephemeral=True)


@channel_group.command(name='quality', description='Set translation quality mode for a channel')
@app_commands.describe(
    mode='Translation quality mode',
    channel='Select channel (optional, defaults to current channel)'
)
@app_commands.choices(mode=[
    app_commands.Choice(name='🚀 Fast - Quick translation (Google)', value='fast'),
    app_commands.Choice(name='🤖 Auto - Smart selection based on content', value='auto'),
])
@app_commands.autocomplete(channel=configured_channel_autocomplete)
async def channel_quality(interaction: discord.Interaction, mode: app_commands.Choice[str], channel: str = None):
    """Set translation quality mode for a channel."""
    # Check if bot is disabled (only owner can use when disabled)
    if bot_disabled and interaction.user.id != BOT_OWNER_ID:
        emb = make_embed(
            title='Bot Disabled',
            description='🔒 The bot is currently disabled. Commands are unavailable.',
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=emb, ephemeral=True)
        return
    
    guild_id = str(interaction.guild.id)
    if not has_permission(interaction.user, guild_id):
        emb = make_embed(
            title='Permission Denied',
            description='⚠️ You need proper permissions to use this command.\n\nRequired: Server Owner, Administrator, or an allowed role.',
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=emb, ephemeral=True)
        return

    try:
        if channel:
            try:
                target_channel = interaction.guild.get_channel(int(channel))
                if not target_channel:
                    emb = make_embed(
                        title='Error',
                        description='❌ Channel not found.',
                        color=discord.Color.red()
                    )
                    await interaction.response.send_message(embed=emb, ephemeral=True)
                    return
            except ValueError:
                emb = make_embed(
                    title='Error',
                    description='❌ Invalid channel.',
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=emb, ephemeral=True)
                return
        else:
            target_channel = interaction.channel
        
        channel_id = str(target_channel.id)
        
        # Check if channel has language settings
        if channel_id not in channel_langs:
            emb = make_embed(
                title='No Configuration',
                description=f'❌ {target_channel.mention} has no language settings.\n\nUse `/channel addlang` first!',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return
        
        # Update quality mode
        channel_langs[channel_id]['translation_quality'] = mode.value
        await save_channels(channel_langs)
        
        # Mode descriptions
        mode_info = {
            'fast': {
                'emoji': '🚀',
                'name': 'Fast Mode',
                'description': 'Quick translation using Google Translator.\n✅ Instant results\n✅ Good for casual conversations',
                'speed': 'Very Fast (0.1-0.3s)'
            },
            'auto': {
                'emoji': '🤖',
                'name': 'Auto Mode',
                'description': 'Smart mode that automatically chooses the best quality:\n• Short messages → Fast\n• Long messages (>500 chars) → Quality\n• Technical content → Quality\n• Regular content → Fast',
                'speed': 'Variable (0.1-1s)'
            }
        }
        
        selected_mode = mode_info.get(mode.value, mode_info['fast'])
        
        emb = make_embed(
            title=f'{selected_mode["emoji"]} Translation Quality Updated',
            description=f'**Channel:** {target_channel.mention}\n**Mode:** {selected_mode["name"]}\n\n{selected_mode["description"]}',
            color=discord.Color.green()
        )
        emb.add_field(name='⚡ Speed', value=selected_mode['speed'], inline=True)
        emb.set_footer(text='💡 Tip: Auto mode intelligently selects the best quality for each message')
        
        await interaction.response.send_message(embed=emb, ephemeral=True)
        
    except Exception as e:
        logger.error(f"Error in quality command: {e}")
        emb = make_embed(
            title='Error',
            description=f'❌ An error occurred: {str(e)}',
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=emb, ephemeral=True)


# ============================================================================
# SLASH COMMANDS - RATING SYSTEM
# ============================================================================

@bot.tree.command(name='rate', description='Rate your experience with the bot')
async def rate(interaction: discord.Interaction):
    """Allow users to rate the bot with a star rating system."""
    # Check if bot is disabled (only owner can use when disabled)
    if bot_disabled and interaction.user.id != BOT_OWNER_ID:
        emb = make_embed(
            title='Bot Disabled',
            description='🔒 The bot is currently disabled. Commands are unavailable.',
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=emb, ephemeral=True)
        return
    
    emb = make_embed(
        title='Rate the Bot ⭐',
        description='Please select your rating for the bot:\n\n⭐ = Poor\n⭐⭐ = Fair\n⭐⭐⭐ = Good\n⭐⭐⭐⭐ = Very Good\n⭐⭐⭐⭐⭐ = Excellent',
        color=discord.Color.blurple()
    )
    emb.set_footer(text="Your rating helps us improve the bot!")
    
    view = RatingView()
    await interaction.response.send_message(embed=emb, view=view, ephemeral=True)


@bot.tree.command(name='ratings', description='View bot rating statistics')
async def ratings(interaction: discord.Interaction):
    """Display overall bot rating statistics."""
    # Check if bot is disabled (only owner can use when disabled)
    if bot_disabled and interaction.user.id != BOT_OWNER_ID:
        emb = make_embed(
            title='Bot Disabled',
            description='🔒 The bot is currently disabled. Commands are unavailable.',
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=emb, ephemeral=True)
        return
    
    if not bot_ratings:
        emb = make_embed(
            title='Bot Ratings 📊',
            description='No ratings yet! Be the first to rate the bot with `/rate`',
            color=discord.Color.blurple()
        )
        await interaction.response.send_message(embed=emb, ephemeral=True)
        return
    
    # Calculate statistics
    total_ratings = len(bot_ratings)
    ratings_list = [r['rating'] for r in bot_ratings.values()]
    average_rating = sum(ratings_list) / total_ratings
    
    # Count ratings by star
    star_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for rating in ratings_list:
        star_counts[rating] += 1
    
    # Create distribution bars
    distribution = []
    for stars in range(5, 0, -1):
        count = star_counts[stars]
        percentage = (count / total_ratings) * 100
        bar_length = int(percentage / 5)
        bar = "█" * bar_length + "░" * (20 - bar_length)
        distribution.append(f"{'⭐' * stars}: {bar} {count} ({percentage:.1f}%)")
    
    # Create embed
    emb = make_embed(
        title='Bot Ratings 📊',
        description=f'**Average Rating:** {"⭐" * int(round(average_rating))} ({average_rating:.2f}/5.00)\n**Total Ratings:** {total_ratings}\n\n**Distribution:**\n' + '\n'.join(distribution),
        color=discord.Color.gold()
    )
    emb.set_footer(text="Thank you to everyone who rated the bot!")
    
    await interaction.response.send_message(embed=emb, ephemeral=True)


# ============================================================================
# SLASH COMMANDS - ROLE MANAGEMENT (ADMIN ONLY)
# ============================================================================

# ============================================================================
# SLASH COMMANDS - ROLE MANAGEMENT (GROUP)
# ============================================================================

@role_group.command(name='perms', description='Add role with custom permissions (Admin only)')
@app_commands.describe(
    role='Select a mentionable role to grant bot permissions'
)
@app_commands.autocomplete(role=mentionable_role_autocomplete)
async def role_add(interaction: discord.Interaction, role: str):
    """Add a role to the allowed roles list with custom permission selection."""
    # Check if bot is disabled (only owner can use when disabled)
    if bot_disabled and interaction.user.id != BOT_OWNER_ID:
        emb = make_embed(
            title='Bot Disabled',
            description='🔒 The bot is currently disabled. Commands are unavailable.',
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=emb, ephemeral=True)
        return
    
    if not (interaction.user.guild_permissions.administrator or interaction.guild.owner_id == interaction.user.id):
        emb = make_embed(
            title='Permission Denied',
            description='⚠️ Only Server Owner or Administrators can manage allowed roles.',
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=emb, ephemeral=True)
        return
    
    try:
        # Convert role ID string to Role object
        try:
            role_obj = interaction.guild.get_role(int(role))
            if not role_obj:
                emb = make_embed(
                    title='Error',
                    description='❌ Role not found.',
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=emb, ephemeral=True)
                return
        except ValueError:
            emb = make_embed(
                title='Error',
                description='❌ Invalid role selection.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return
        
        # Check if role is mentionable
        if not role_obj.mentionable:
            emb = make_embed(
                title='Role Not Mentionable',
                description=f'⚠️ {role_obj.mention} is not mentionable.\n\n💡 **Tip:** Enable "Allow anyone to @mention this role" in role settings.',
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return
        
        guild_id = str(interaction.guild.id)
        role_id = str(role_obj.id)
        
        # Check if role already exists
        if guild_id in allowed_roles and role_id in allowed_roles[guild_id]:
            # Show current permissions
            current_perms = role_permissions.get(guild_id, {}).get(role_id, [])
            if current_perms:
                perm_list = []
                for perm_key in current_perms:
                    perm_data = BOT_PERMISSIONS.get(perm_key, {'name': perm_key, 'emoji': '•', 'command': ''})
                    perm_list.append(f"{perm_data['emoji']} {perm_data['name']}")
                
                emb = make_embed(
                    title='Role Already Configured',
                    description=f'{role_obj.mention} already has permissions assigned.\n\n**Current Permissions:**\n' + '\n'.join(perm_list),
                    color=discord.Color.orange()
                )
                emb.set_footer(text='Use /role remove first to reconfigure')
            else:
                emb = make_embed(
                    title='Role Already Added',
                    description=f'⚠️ {role_obj.mention} is already in the allowed roles list.',
                    color=discord.Color.orange()
                )
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return
        
        # Show permission selection view
        view = RolePermissionView(role_obj, guild_id, role_id)
        
        emb = make_embed(
            title='🛡️ Select Permissions',
            description=f'Choose which permissions to grant to {role_obj.mention}\n\n**Select one or more permissions below:**',
            color=discord.Color.blurple()
        )
        
        # Add description of each permission
        perm_descriptions = []
        for perm_key, perm_data in BOT_PERMISSIONS.items():
            perm_descriptions.append(f"{perm_data['emoji']} **{perm_data['name']}**\n└ {perm_data['description']}")
        
        emb.add_field(
            name='📋 Available Permissions',
            value='\n\n'.join(perm_descriptions[:3]),
            inline=False
        )
        if len(perm_descriptions) > 3:
            emb.add_field(
                name='',
                value='\n\n'.join(perm_descriptions[3:]),
                inline=False
            )
        
        emb.set_footer(text=f'Members with this role: {len(role_obj.members)} • Timeout: 5 minutes')
        
        await interaction.response.send_message(embed=emb, view=view, ephemeral=True)
        logger.info(f"Permission selection initiated for role {role_obj.name} in guild {interaction.guild.name}")
        
    except Exception as e:
        logger.error(f"Error in addrole command: {e}")
        emb = make_embed(
            title='Error',
            description=f'❌ An error occurred: {str(e)}',
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=emb, ephemeral=True)


@role_group.command(name='editperms', description='Edit/Remove role permissions (Admin only)')
@app_commands.describe(
    role='Select an allowed role to remove from language management permissions'
)
@app_commands.autocomplete(role=allowed_role_autocomplete)
async def role_remove(interaction: discord.Interaction, role: str):
    """Remove a role from the allowed roles list. Only shows roles that have been added."""
    # Check if bot is disabled (only owner can use when disabled)
    if bot_disabled and interaction.user.id != BOT_OWNER_ID:
        emb = make_embed(
            title='Bot Disabled',
            description='🔒 The bot is currently disabled. Commands are unavailable.',
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=emb, ephemeral=True)
        return
    
    if not (interaction.user.guild_permissions.administrator or interaction.guild.owner_id == interaction.user.id):
        emb = make_embed(
            title='Permission Denied',
            description='⚠️ Only Server Owner or Administrators can manage allowed roles.',
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=emb, ephemeral=True)
        return
    
    try:
        guild_id = str(interaction.guild.id)
        
        # Check if there are any allowed roles
        if guild_id not in allowed_roles or not allowed_roles[guild_id]:
            emb = make_embed(
                title='No Allowed Roles',
                description='⚠️ There are no allowed roles configured for this server.\n\n💡 Use `/role perms` to add roles with language management permissions.',
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return
        
        # Convert role ID string to Role object
        try:
            role_obj = interaction.guild.get_role(int(role))
            if not role_obj:
                emb = make_embed(
                    title='Error',
                    description='❌ Role not found.',
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=emb, ephemeral=True)
                return
        except ValueError:
            emb = make_embed(
                title='Error',
                description='❌ Invalid role selection.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return
        
        role_id = str(role_obj.id)
        
        # Check if role is in allowed list
        if role_id not in allowed_roles[guild_id]:
            emb = make_embed(
                title='Role Not in List',
                description=f'⚠️ {role_obj.mention} is not in the allowed roles list.\n\n💡 Only roles added with `/role perms` can be edited.',
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return
        
        # Get role permissions details for confirmation message
        perm_details = []
        if role_obj.permissions.administrator:
            perm_details.append("• Administrator privileges")
        perm_details.append("• Set channel languages (`/channel addlang`)")
        perm_details.append("• Remove language settings (`/channel deletelang`)")
        perm_details.append("• View channel languages (`/view channels`)")
        
        # Remove role
        allowed_roles[guild_id].remove(role_id)
        await save_allowed_roles(allowed_roles)
        
        emb = make_embed(
            title='Role Removed ✅',
            description=f'Successfully removed {role_obj.mention} from language management permissions.',
            color=discord.Color.green()
        )
        emb.add_field(
            name='🗑️ Revoked Permissions',
            value='\n'.join(perm_details),
            inline=False
        )
        emb.add_field(
            name='⚠️ Impact',
            value='Members with this role can no longer manage channel language settings.',
            inline=False
        )
        emb.set_footer(text=f'Use /role perms to add it back • Remaining allowed roles: {len(allowed_roles.get(guild_id, []))}')
        await interaction.response.send_message(embed=emb, ephemeral=True)
        logger.info(f"Role {role_obj.name} ({role_id}) removed from allowed roles in guild {interaction.guild.name}")
        
    except Exception as e:
        logger.error(f"Error in removerole command: {e}")
        emb = make_embed(
            title='Error',
            description=f'❌ An error occurred: {str(e)}',
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=emb, ephemeral=True)



# ============================================================================
# SLASH COMMANDS - ROLE LANGUAGE MANAGEMENT (GROUP)
# ============================================================================

@role_group.command(name='setlang', description='Assign a default language to a role (Admin only)')
@app_commands.describe(
    role='Select a role to assign a language',
    language='Select the language for this role'
)
@app_commands.choices(language=[
    app_commands.Choice(name='🇸🇦 Arabic', value='ar'),
    app_commands.Choice(name='🇬🇧 English', value='en'),
    app_commands.Choice(name='🇹🇷 Turkish', value='tr'),
    app_commands.Choice(name='🇯🇵 Japanese', value='ja'),
    app_commands.Choice(name='🇫🇷 French', value='fr'),
    app_commands.Choice(name='🇰🇷 Korean', value='ko'),
    app_commands.Choice(name='🇮🇹 Italian', value='it'),
    app_commands.Choice(name='🇨🇳 Chinese', value='zh-CN')
])
async def role_setlang(interaction: discord.Interaction, role: discord.Role, language: str):
    """Assign a language to a role for context menu translation."""
    # Check if bot is disabled (only owner can use when disabled)
    if bot_disabled and interaction.user.id != BOT_OWNER_ID:
        emb = make_embed(
            title='Bot Disabled',
            description='🔒 The bot is currently disabled. Commands are unavailable.',
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=emb, ephemeral=True)
        return
    
    if not (interaction.user.guild_permissions.administrator or interaction.guild.owner_id == interaction.user.id):
        emb = make_embed(
            title='Permission Denied',
            description='⚠️ Only Server Owner or Administrators can manage role languages.',
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=emb, ephemeral=True)
        return
    
    try:
        guild_id = str(interaction.guild.id)
        role_id = str(role.id)
        
        if guild_id not in role_languages:
            role_languages[guild_id] = {}
        
        # Check if already set
        was_update = role_id in role_languages[guild_id]
        old_lang = role_languages[guild_id].get(role_id)
        
        role_languages[guild_id][role_id] = language
        await save_role_languages(role_languages)
        
        lang_name = SUPPORTED.get(language, language)
        flag_emoji = {
            'ar': '🇸🇦', 'en': '🇬🇧', 'tr': '🇹🇷',
            'ja': '🇯🇵', 'fr': '🇫🇷', 'ko': '🇰🇷', 'it': '🇮🇹', 'zh-CN': '🇨🇳'
        }.get(language, '🌐')
        
        if was_update:
            old_lang_name = SUPPORTED.get(old_lang, old_lang)
            action_text = f'updated from **{old_lang_name}** to **{flag_emoji} {lang_name}**'
        else:
            action_text = f'set to **{flag_emoji} {lang_name}**'
        
        emb = make_embed(
            title='Role Language Set ✅',
            description=f'Language for {role.mention} has been {action_text}.\n\n**What this means:**\nMembers with this role can now:\n• Right-click any message\n• Select "Translate Message"\n• Get instant translation to {lang_name}',
            color=discord.Color.green()
        )
        emb.set_footer(text='Use /view rolelanguages to see all role languages')
        
        await interaction.response.send_message(embed=emb, ephemeral=True)
        logger.info(f"Role {role.name} language set to {language} in guild {interaction.guild.name}")
        
    except Exception as e:
        logger.error(f"Error in setrolelang command: {e}")
        emb = make_embed(
            title='Error',
            description=f'❌ An error occurred: {str(e)}',
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=emb, ephemeral=True)


@role_group.command(name='removelang', description='Remove language assignment from a role (Admin only)')
@app_commands.describe(
    role='Select a role to remove language assignment'
)
async def role_removelang(interaction: discord.Interaction, role: discord.Role):
    """Remove language assignment from a role."""
    # Check if bot is disabled (only owner can use when disabled)
    if bot_disabled and interaction.user.id != BOT_OWNER_ID:
        emb = make_embed(
            title='Bot Disabled',
            description='🔒 The bot is currently disabled. Commands are unavailable.',
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=emb, ephemeral=True)
        return
    
    if not (interaction.user.guild_permissions.administrator or interaction.guild.owner_id == interaction.user.id):
        emb = make_embed(
            title='Permission Denied',
            description='⚠️ Only Server Owner or Administrators can manage role languages.',
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=emb, ephemeral=True)
        return
    
    try:
        guild_id = str(interaction.guild.id)
        role_id = str(role.id)
        
        if guild_id not in role_languages or role_id not in role_languages[guild_id]:
            emb = make_embed(
                title='Role Not Configured',
                description=f'⚠️ {role.mention} does not have a language assigned.\n\n💡 Use `/role setlang` to assign a language to this role.',
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return
        
        # Get language before removing
        old_lang = role_languages[guild_id][role_id]
        lang_name = SUPPORTED.get(old_lang, old_lang)
        flag_emoji = {
            'ar': '🇸🇦', 'en': '🇬🇧', 'tr': '🇹🇷',
            'ja': '🇯🇵', 'fr': '🇫🇷', 'ko': '🇰🇷', 'it': '🇮🇹', 'zh-CN': '🇨🇳'
        }.get(old_lang, '🌐')
        
        # Remove
        del role_languages[guild_id][role_id]
        
        # Clean up empty guild entries
        if not role_languages[guild_id]:
            del role_languages[guild_id]
        
        await save_role_languages(role_languages)
        
        emb = make_embed(
            title='Role Language Removed ✅',
            description=f'Successfully removed language assignment from {role.mention}',
            color=discord.Color.green()
        )
        emb.add_field(
            name='🗑️ Removed Language',
            value=f'{flag_emoji} **{lang_name}** (`{old_lang}`)',
            inline=False
        )
        emb.add_field(
            name='⚠️ Impact',
            value='Members with this role can no longer use "Translate Message" context menu for automatic translation.',
            inline=False
        )
        emb.set_footer(text=f'Use /role setlang to assign a new language')
        
        await interaction.response.send_message(embed=emb, ephemeral=True)
        logger.info(f"Role {role.name} language removed in guild {interaction.guild.name}")
        
    except Exception as e:
        logger.error(f"Error in removerolelang command: {e}")
        emb = make_embed(
            title='Error',
            description=f'❌ An error occurred: {str(e)}',
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=emb, ephemeral=True)



# ============================================================================
# BOT STARTUP
# ============================================================================

if __name__ == '__main__':
    if not TOKEN:
        logger.error('TOKEN is not set. Put it in Replit Secrets as TOKEN or .env locally.')
        exit(1)
    
    # Start keep-alive server for Render Web Service (required for free plan)
    try:
        from keep_alive import keep_alive
        keep_alive()
        logger.info("✅ Keep-alive server started on port 8080")
    except ImportError:
        logger.warning("⚠️ Keep-alive not enabled - Install flask: pip install flask")
    except Exception as e:
        logger.debug(f"Keep-alive error: {e}")
    
    try:
        bot.run(TOKEN)
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested...")
    finally:
        # Cleanup connections
        async def cleanup():
            await close_cache()
            await close_database()
            logger.info("✅ Connections closed gracefully")
        
        asyncio.run(cleanup())
