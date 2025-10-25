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
from discord.ext import commands


# ============================================================================
# CONFIGURATION
# ============================================================================

# Load environment variables
load_dotenv()

TOKEN = os.getenv("TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

# File paths for data persistence
if os.path.dirname(__file__):
    BASE_DIR = os.path.dirname(__file__)
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    CHANNELS_FILE = os.path.join(DATA_DIR, 'channels.json')
    RATINGS_FILE = os.path.join(DATA_DIR, 'ratings.json')
    ROLES_FILE = os.path.join(DATA_DIR, 'allowed_roles.json')
else:
    DATA_DIR = 'data'
    CHANNELS_FILE = os.path.join(DATA_DIR, 'channels.json')
    RATINGS_FILE = os.path.join(DATA_DIR, 'ratings.json')
    ROLES_FILE = os.path.join(DATA_DIR, 'allowed_roles.json')

# Create data directory if it doesn't exist
os.makedirs(DATA_DIR, exist_ok=True)

# Supported languages
SUPPORTED = {
    'ar': 'Arabic',
    'en': 'English',
    'tr': 'Turkish',
    'ja': 'Japanese',
    'fr': 'French',
    'ko': 'Korean',
    'it': 'Italian'
}

# Logging configuration
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================

def load_channels() -> Dict[str, str]:
    """Load channel language configurations from file."""
    try:
        with open(CHANNELS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.info(f"Loaded {len(data)} channel configurations from {CHANNELS_FILE}")
            return data
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


# ============================================================================
# DATA SAVING FUNCTIONS (ASYNC)
# ============================================================================

async def save_channels(data: Dict[str, str]):
    """Asynchronously save channel language configuration to disk."""
    loop = asyncio.get_running_loop()

    def _write(d):
        tmp = CHANNELS_FILE + '.tmp'
        try:
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(d, f, ensure_ascii=False, indent=2)
            os.replace(tmp, CHANNELS_FILE)
            logger.info(f"Saved {len(d)} channel configurations to {CHANNELS_FILE}")
        except Exception as e:
            logger.error(f"Error saving to {CHANNELS_FILE}: {e}")
            try:
                with open(CHANNELS_FILE, 'w', encoding='utf-8') as f:
                    json.dump(d, f, ensure_ascii=False, indent=2)
                logger.info(f"Fallback: Saved {len(d)} configurations directly to {CHANNELS_FILE}")
            except Exception as e2:
                logger.error(f"Fallback save also failed: {e2}")

    await loop.run_in_executor(None, _write, data)


async def save_ratings(data: Dict[str, dict]):
    """Asynchronously save user ratings to disk."""
    loop = asyncio.get_running_loop()

    def _write(d):
        tmp = RATINGS_FILE + '.tmp'
        try:
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(d, f, ensure_ascii=False, indent=2)
            os.replace(tmp, RATINGS_FILE)
            logger.info(f"Saved {len(d)} ratings to {RATINGS_FILE}")
        except Exception as e:
            logger.error(f"Error saving to {RATINGS_FILE}: {e}")
            try:
                with open(RATINGS_FILE, 'w', encoding='utf-8') as f:
                    json.dump(d, f, ensure_ascii=False, indent=2)
                logger.info(f"Fallback: Saved {len(d)} ratings directly to {RATINGS_FILE}")
            except Exception as e2:
                logger.error(f"Fallback save also failed: {e2}")

    await loop.run_in_executor(None, _write, data)


async def save_allowed_roles(data: Dict[str, list]):
    """Asynchronously save allowed roles to disk."""
    loop = asyncio.get_running_loop()

    def _write(d):
        tmp = ROLES_FILE + '.tmp'
        try:
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(d, f, ensure_ascii=False, indent=2)
            os.replace(tmp, ROLES_FILE)
            logger.info(f"Saved allowed roles for {len(d)} guilds to {ROLES_FILE}")
        except Exception as e:
            logger.error(f"Error saving to {ROLES_FILE}: {e}")
            try:
                with open(ROLES_FILE, 'w', encoding='utf-8') as f:
                    json.dump(d, f, ensure_ascii=False, indent=2)
                logger.info(f"Fallback: Saved allowed roles directly to {ROLES_FILE}")
            except Exception as e2:
                logger.error(f"Fallback save also failed: {e2}")

    await loop.run_in_executor(None, _write, data)


# ============================================================================
# BOT INITIALIZATION
# ============================================================================

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Global state
channel_langs = load_channels()
bot_ratings = {}
allowed_roles = {}

# Translation cache for faster responses
translation_cache = {}  # {(text_hash, source_lang, target_lang): translated_text}
CACHE_MAX_SIZE = 1000  # Maximum cache entries


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
                emb.set_author(name=str(bot.user), icon_url=avatar.url)
    except Exception:
        pass
    return emb


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


# ============================================================================
# BOT EVENTS
# ============================================================================

@bot.event
async def on_ready():
    """Called when the bot is ready and connected to Discord."""
    logger.info(f"Logged in as {bot.user}")
    logger.info(f"Bot is in {len(bot.guilds)} server(s)")
    
    # Load data from files
    global channel_langs, bot_ratings, allowed_roles
    loop = asyncio.get_event_loop()
    channel_langs = await loop.run_in_executor(None, load_channels)
    bot_ratings = await loop.run_in_executor(None, load_ratings)
    allowed_roles = await loop.run_in_executor(None, load_allowed_roles)
    
    # Log application commands
    try:
        cmds = [c.name for c in bot.tree.walk_commands()]
        if cmds:
            logger.info(f"Application commands present: {cmds}")
        else:
            logger.info("No application commands found in bot.tree.")
    except Exception as e:
        logger.debug(f"Could not list app commands: {e}")
    
    # Clear guild-specific commands
    try:
        for guild in bot.guilds:
            try:
                bot.tree.clear_commands(guild=guild)
                await bot.tree.sync(guild=guild)
                logger.info(f"Cleared guild-specific commands from {guild.name}")
            except Exception as e:
                logger.warning(f"Could not clear commands from {guild.name}: {e}")
    except Exception as e:
        logger.error(f"Error clearing guild commands: {e}")
    
    # Sync slash commands
    try:
        if GUILD_ID:
            guild = discord.Object(id=int(GUILD_ID))
            bot.tree.copy_global_to(guild=guild)
            await bot.tree.sync(guild=guild)
            logger.info(f"Synced app commands to guild {GUILD_ID}")
        else:
            await bot.tree.sync()
            logger.info(f"Global sync completed for {len(bot.guilds)} servers (may take up to 1 hour to propagate)")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")
    
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


@bot.event
async def on_guild_join(guild: discord.Guild):
    """Log when the bot joins a new server."""
    logger.info(f"Joined new guild: {guild.name} (ID: {guild.id})")


@bot.event
async def on_guild_remove(guild: discord.Guild):
    """Log when the bot is removed from a server and clean up data."""
    logger.info(f"Removed from guild: {guild.name} (ID: {guild.id})")
    
    try:
        guild_id = str(guild.id)
        channels_to_remove = []
        
        for ch_id in list(channel_langs.keys()):
            if ch_id.startswith(guild_id):
                channels_to_remove.append(ch_id)
        
        for ch_id in channels_to_remove:
            del channel_langs[ch_id]
        
        if channels_to_remove:
            await save_channels(channel_langs)
            logger.info(f"Cleaned up {len(channels_to_remove)} channel settings from {guild.name}")
    except Exception as e:
        logger.error(f"Error cleaning up guild data for {guild.name}: {e}")


@bot.event
async def on_message(message: discord.Message):
    """Handle message translation based on channel language settings."""
    # Ignore bots and webhooks
    if message.author.bot or message.webhook_id:
        return

    channel_id = str(message.channel.id)
    target = channel_langs.get(channel_id)
    if not target:
        return

    content = message.content.strip()
    if not content:
        return

    try:
        detected = detect(content)
    except LangDetectException:
        logger.debug("Could not detect language")
        return

    # Check if target language is supported
    if target not in SUPPORTED:
        logger.warning(f"Target language '{target}' not in SUPPORTED list")
        return

    # Only translate if detected language is different from target
    if detected == target:
        logger.debug(f"Message already in target language ({target}), skipping")
        return

    # Create cache key (using hash to handle long messages)
    cache_key = (hash(content), detected, target)
    
    # Check cache first for faster response
    if cache_key in translation_cache:
        translated = translation_cache[cache_key]
        logger.debug(f"Using cached translation for '{content[:30]}...'")
    else:
        # Translate using deep-translator API (faster and more reliable)
        try:
            # deep-translator uses async-friendly approach
            translated = GoogleTranslator(source=detected, target=target).translate(content)
            
            # Store in cache
            if translated:
                translation_cache[cache_key] = translated
                
                # Clean cache if too large (remove 20% oldest entries)
                if len(translation_cache) > CACHE_MAX_SIZE:
                    remove_count = CACHE_MAX_SIZE // 5
                    for _ in range(remove_count):
                        translation_cache.pop(next(iter(translation_cache)))
                    logger.debug(f"Cache cleaned: removed {remove_count} entries")
                    
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
        logger.info(f"Detected '{detected}' message in '{target}' channel → Translated to {SUPPORTED.get(target, target)}")
    else:
        logger.debug(f"Translation result is same as original, skipping")
        
    # Allow other commands to be processed
    try:
        await bot.process_commands(message)
    except Exception:
        pass


# ============================================================================
# UI COMPONENTS
# ============================================================================

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
            channel_langs[channel_id] = code
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
    """View containing the language selection dropdown."""
    
    def __init__(self, channel):
        super().__init__()
        self.channel = channel
        self.add_item(LanguageSelect(SUPPORTED))


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


class ChannelListView(discord.ui.View):
    """Paginated view for channel list with 5 channels per page."""
    
    def __init__(self, configured_channels: list, unconfigured_channels: list, guild_name: str):
        super().__init__(timeout=180)
        self.configured = configured_channels
        self.unconfigured = unconfigured_channels
        self.guild_name = guild_name
        self.current_page = 0
        self.items_per_page = 5
        
        # Calculate total pages
        total_configured_pages = (len(self.configured) + self.items_per_page - 1) // self.items_per_page if self.configured else 1
        total_unconfigured_pages = (len(self.unconfigured) + self.items_per_page - 1) // self.items_per_page if self.unconfigured else 0
        self.total_pages = total_configured_pages + total_unconfigured_pages
        
        self.update_buttons()
    
    def get_embed(self) -> discord.Embed:
        """Generate embed for current page."""
        configured_pages = (len(self.configured) + self.items_per_page - 1) // self.items_per_page if self.configured else 1
        
        if self.current_page < configured_pages:
            start_idx = self.current_page * self.items_per_page
            end_idx = min(start_idx + self.items_per_page, len(self.configured))
            
            if self.configured:
                items = self.configured[start_idx:end_idx]
                desc = '**Channels with Language Settings:**\n\n' + '\n'.join(items)
            else:
                desc = '**Channels with Language Settings:**\n\nNo channels have language settings configured.'
        else:
            page_in_unconfigured = self.current_page - configured_pages
            start_idx = page_in_unconfigured * self.items_per_page
            end_idx = min(start_idx + self.items_per_page, len(self.unconfigured))
            
            items = self.unconfigured[start_idx:end_idx]
            desc = '**Channels without Language Settings:**\n\n' + '\n'.join(items)
        
        emb = make_embed(
            title=f'Channel Language Overview - {self.guild_name}',
            description=desc
        )
        emb.set_footer(text=f'Page {self.current_page + 1} of {self.total_pages}')
        return emb
    
    def update_buttons(self):
        """Enable/disable navigation buttons based on current page."""
        self.previous_button.disabled = (self.current_page == 0)
        self.next_button.disabled = (self.current_page >= self.total_pages - 1)
    
    @discord.ui.button(label='◀️ Previous', style=discord.ButtonStyle.primary, custom_id='previous')
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.get_embed(), view=self)
        else:
            await interaction.response.defer()
    
    @discord.ui.button(label='Next ▶️', style=discord.ButtonStyle.primary, custom_id='next')
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.get_embed(), view=self)
        else:
            await interaction.response.defer()
    
    async def on_timeout(self):
        """Disable buttons when view times out."""
        for item in self.children:
            item.disabled = True


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


# ============================================================================
# SLASH COMMANDS - GENERAL
# ============================================================================

@bot.tree.command(name='ping', description='Check if the bot is responsive')
async def ping(interaction: discord.Interaction):
    """Check bot responsiveness and latency."""
    ws_ms = round(bot.latency * 1000)
    color = _choose_latency_color(ws_ms)
    emoji = "🟢" if ws_ms < 100 else ("🟡" if ws_ms < 250 else "🔴")
    emb = make_embed(title=f"Pong! {emoji} 🏓", description=f"WebSocket latency: **{ws_ms} ms**", color=color)
    emb.set_footer(text="Latency may vary. Measures websocket heartbeat latency.")
    await interaction.response.send_message(embed=emb, ephemeral=False)


@bot.tree.command(name='help', description='Show all available commands')
async def help(interaction: discord.Interaction):
    """Display help information with available commands."""
    is_admin = interaction.user.guild_permissions.administrator or interaction.guild.owner_id == interaction.user.id
    
    commands_list = [
        '**Language Management:**',
        '`/setlang [channel]` - Set default language for a channel',
        '`/getlang [channel]` - Get language setting for a channel',
        '`/removelang [channel]` - Remove language setting for a channel',
        '`/listchannels` - List all channels with their language settings',
        '`/listlangs` - List all supported languages',
        '',
        '**Bot Information:**',
        '`/rate` - Rate your experience with the bot',
        '`/ratings` - View bot rating statistics',
        '`/ping` - Check if the bot is responsive',
        '`/help` - Show this help message'
    ]
    
    if is_admin:
        admin_commands = [
            '',
            '**Admin Commands:**',
            '`/addrole <role>` - Add a role that can manage language settings',
            '`/removerole <role>` - Remove a role from language management',
            '`/listroles` - List all roles with language management permissions',
            '`/debug` - Show bot debug information'
        ]
        commands_list.extend(admin_commands)
    
    desc = '\n'.join(commands_list)
    
    if is_admin:
        desc += '\n\n**Permission System:**\nBy default, Server Owner and Administrators can manage languages. Use `/addrole` to grant permissions to specific roles.'
    
    emb = make_embed(title='Bot Commands', description=desc)
    emb.set_footer(text="Use autocomplete to easily select channels!")
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
            for ch_id, lang in list(guild_configs.items())[:10]:
                try:
                    ch = interaction.guild.get_channel(int(ch_id))
                    if ch:
                        info.append(f"• {ch.mention}: {SUPPORTED.get(lang, lang)}")
                    else:
                        info.append(f"• Channel ID {ch_id}: {SUPPORTED.get(lang, lang)} (channel not found)")
                except Exception:
                    info.append(f"• Channel ID {ch_id}: {SUPPORTED.get(lang, lang)}")
            
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


# ============================================================================
# SLASH COMMANDS - LANGUAGE MANAGEMENT
# ============================================================================

@bot.tree.command(name='setlang', description='Set default language for a channel')
@app_commands.describe(
    channel='Select channel to set language for (optional, defaults to current channel)'
)
@app_commands.autocomplete(channel=channel_autocomplete)
async def setlang(interaction: discord.Interaction, channel: str = None):
    """Set the default language for a channel."""
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
        
        view = LanguageView(target_channel)
        emb = make_embed(
            title='Set Language',
            description=f'Please select a language for {target_channel.mention}:',
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


@bot.tree.command(name='getlang', description='Get language setting for a configured channel')
@app_commands.describe(
    channel='Select a channel from the list (only channels with language settings are shown)'
)
@app_commands.autocomplete(channel=configured_channel_autocomplete)
async def getlang(interaction: discord.Interaction, channel: str):
    """Get the current language setting for a channel. Only shows channels that have a language configured."""
    try:
        # Check if a channel was selected
        if not channel:
            emb = make_embed(
                title='Channel Required',
                description='⚠️ Please select a channel from the dropdown list.\n\n💡 **Tip:** Only channels with configured languages appear in the list.',
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return
            
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
                description='❌ Invalid channel selection.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return
        
        channel_id = str(target_channel.id)
        lang_code = channel_langs.get(channel_id)
        
        if lang_code:
            lang_name = SUPPORTED.get(lang_code, 'Unknown')
            flag_emoji = {
                'ar': '🇸🇦',
                'en': '🇬🇧',
                'tr': '🇹🇷',
                'ja': '🇯🇵',
                'fr': '🇫🇷',
                'ko': '🇰🇷',
                'it': '🇮🇹'
            }.get(lang_code, '🌐')
            
            emb = make_embed(
                title=f'{flag_emoji} Channel Language',
                description=f'{target_channel.mention} is set to **{lang_name}** (`{lang_code}`)\n\n✅ Messages in other languages will be automatically translated to {lang_name}.',
                color=discord.Color.green()
            )
        else:
            emb = make_embed(
                title='No Language Set',
                description=f'{target_channel.mention} has no language configured.\n\n💡 Use `/setlang` to set a language for this channel.',
                color=discord.Color.dark_grey()
            )
        
        await interaction.response.send_message(embed=emb, ephemeral=True)
    except Exception as e:
        logger.error(f"Error in getlang command: {e}")
        emb = make_embed(
            title='Error',
            description=f'❌ An error occurred: {str(e)}',
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=emb, ephemeral=True)


@bot.tree.command(name='listlangs', description='List all supported languages')
async def listlangs(interaction: discord.Interaction):
    """List all supported languages."""
    lang_list = [f'• **{name}** (`{code}`)' for code, name in SUPPORTED.items()]
    desc = '**Supported Languages:**\n\n' + '\n'.join(lang_list)
    desc += '\n\nUse `/setlang` to configure a channel.'
    
    emb = make_embed(title='Supported Languages', description=desc)
    await interaction.response.send_message(embed=emb, ephemeral=True)


@bot.tree.command(name='listchannels', description='List all channels with their language settings')
async def listchannels(interaction: discord.Interaction):
    """List all channels with pagination."""
    if not interaction.guild:
        emb = make_embed(
            title='Error',
            description='This command can only be used in a server.',
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=emb, ephemeral=True)
        return

    try:
        channels = interaction.guild.channels
        
        configured_channels = []
        unconfigured_channels = []
        
        for channel in channels:
            if isinstance(channel, (discord.TextChannel, discord.VoiceChannel, discord.ForumChannel)):
                channel_id = str(channel.id)
                if channel_id in channel_langs:
                    lang_code = channel_langs[channel_id]
                    lang_name = SUPPORTED.get(lang_code, 'Unknown')
                    configured_channels.append(f'{channel.mention}: {lang_name} ({lang_code})')
                else:
                    unconfigured_channels.append(f'{channel.mention}: No language set')
        
        view = ChannelListView(configured_channels, unconfigured_channels, interaction.guild.name)
        emb = view.get_embed()
        
        await interaction.response.send_message(embed=emb, view=view, ephemeral=True)
    except Exception as e:
        logger.error(f"Error in listchannels command: {e}")
        emb = make_embed(
            title='Error',
            description=f'❌ An error occurred: {str(e)}',
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=emb, ephemeral=True)


@bot.tree.command(name='removelang', description='Remove language setting for a channel')
@app_commands.describe(
    channel='Select channel to remove language setting from (shows only configured channels)'
)
@app_commands.autocomplete(channel=configured_channel_autocomplete)
async def removelang(interaction: discord.Interaction, channel: str = None):
    """Remove language configuration from a channel."""
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
            old_lang = channel_langs[channel_id]
            del channel_langs[channel_id]
            await save_channels(channel_langs)
            emb = make_embed(
                title='Removed',
                description=f'✅ Removed language setting for {target_channel.mention} (was {SUPPORTED[old_lang]}).',
                color=discord.Color.green()
            )
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


# ============================================================================
# SLASH COMMANDS - RATING SYSTEM
# ============================================================================

@bot.tree.command(name='rate', description='Rate your experience with the bot')
async def rate(interaction: discord.Interaction):
    """Allow users to rate the bot with a star rating system."""
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
    
    await interaction.response.send_message(embed=emb, ephemeral=False)


# ============================================================================
# SLASH COMMANDS - ROLE MANAGEMENT (ADMIN ONLY)
# ============================================================================

@bot.tree.command(name='addrole', description='Add a mentionable role that can manage language settings (Admin only)')
@app_commands.describe(
    role='Select a mentionable role to grant language management permissions'
)
@app_commands.autocomplete(role=mentionable_role_autocomplete)
async def addrole(interaction: discord.Interaction, role: str):
    """Add a role to the allowed roles list for language management. Only shows mentionable roles."""
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
        
        if guild_id not in allowed_roles:
            allowed_roles[guild_id] = []
        
        if role_id in allowed_roles[guild_id]:
            emb = make_embed(
                title='Role Already Added',
                description=f'⚠️ {role_obj.mention} is already in the allowed roles list.',
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return
        
        allowed_roles[guild_id].append(role_id)
        await save_allowed_roles(allowed_roles)
        
        # Get role permissions details
        perm_details = []
        if role_obj.permissions.administrator:
            perm_details.append("• **Administrator** - Full server management")
        
        perm_details.extend([
            "• Set channel languages (`/setlang`)",
            "• Remove language settings (`/removelang`)",
            "• View channel languages (`/getlang`)"
        ])
        
        emb = make_embed(
            title='Role Added ✅',
            description=f'Successfully added {role_obj.mention} to allowed roles.\n\n**Granted Permissions:**\n' + '\n'.join(perm_details) + '\n\n✅ Members with this role can now manage channel language settings.',
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=emb, ephemeral=True)
        logger.info(f"Role {role_obj.name} ({role_id}) added to allowed roles in guild {interaction.guild.name}")
        
    except Exception as e:
        logger.error(f"Error in addrole command: {e}")
        emb = make_embed(
            title='Error',
            description=f'❌ An error occurred: {str(e)}',
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=emb, ephemeral=True)


@bot.tree.command(name='removerole', description='Remove a role from language management permissions (Admin only)')
@app_commands.describe(
    role='Select an allowed role to remove from language management permissions'
)
@app_commands.autocomplete(role=allowed_role_autocomplete)
async def removerole(interaction: discord.Interaction, role: str):
    """Remove a role from the allowed roles list. Only shows roles that have been added."""
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
                description='⚠️ There are no allowed roles configured for this server.\n\n💡 Use `/addrole` to add roles with language management permissions.',
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
                description=f'⚠️ {role_obj.mention} is not in the allowed roles list.\n\n💡 Only roles added with `/addrole` can be removed.',
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return
        
        # Get role permissions details for confirmation message
        perm_details = []
        if role_obj.permissions.administrator:
            perm_details.append("• Administrator privileges")
        perm_details.append("• Set channel languages (`/setlang`)")
        perm_details.append("• Remove language settings (`/removelang`)")
        perm_details.append("• View channel languages (`/getlang`)")
        
        # Remove role
        allowed_roles[guild_id].remove(role_id)
        await save_allowed_roles(allowed_roles)
        
        emb = make_embed(
            title='Role Removed ✅',
            description=f'Successfully removed {role_obj.mention} from allowed roles.\n\n**Revoked Permissions:**\n' + '\n'.join(perm_details) + '\n\n⚠️ Members with this role can no longer manage language settings.',
            color=discord.Color.green()
        )
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


@bot.tree.command(name='listroles', description='List all roles with language management permissions')
async def listroles(interaction: discord.Interaction):
    """List all allowed roles for the current guild with their permission details."""
    try:
        guild_id = str(interaction.guild.id)
        
        if guild_id not in allowed_roles or not allowed_roles[guild_id]:
            emb = make_embed(
                title='Allowed Roles 📋',
                description='No custom roles configured for language management.\n\n**Default Access:**\n• 👑 Server Owner - Full control\n• 🛡️ Administrators - Full control\n\n💡 Use `/addrole` to grant language management permissions to specific roles.',
                color=discord.Color.blurple()
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return
        
        # Build role list with permission details
        role_list = []
        for role_id in allowed_roles[guild_id]:
            role = interaction.guild.get_role(int(role_id))
            if role:
                # Determine permission level
                if role.permissions.administrator:
                    perm_badge = "🛡️ Admin"
                elif role.permissions.manage_channels:
                    perm_badge = "⚙️ Manage Channels"
                else:
                    perm_badge = "🌐 Language Manager"
                
                role_list.append(f'• {role.mention} **{perm_badge}**')
            else:
                role_list.append(f'• ~~Deleted Role~~ (ID: {role_id})')
        
        description = '**Roles with language management permissions:**\n\n' + '\n'.join(role_list)
        description += '\n\n**Built-in Access:**\n• 👑 Server Owner - Full control\n• 🛡️ Administrators - Full control'
        description += '\n\n**All above roles can:**\n✅ Set channel languages (`/setlang`)\n✅ Remove language settings (`/removelang`)\n✅ View language settings (`/getlang`)'
        
        emb = make_embed(
            title='Allowed Roles 📋',
            description=description,
            color=discord.Color.blurple()
        )
        emb.set_footer(text=f"Total custom roles: {len(allowed_roles[guild_id])} • Use /addrole or /removerole to manage")
        
        await interaction.response.send_message(embed=emb, ephemeral=True)
        
    except Exception as e:
        logger.error(f"Error in listroles command: {e}")
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
    bot.run(TOKEN)
