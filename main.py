import os
import json
import logging
from typing import Dict

from dotenv import load_dotenv
from langdetect import detect, LangDetectException
from googletrans import Translator
import discord
import asyncio
from discord import app_commands
from discord.ext import commands


# Load environment (for local testing; in Replit TOKEN will come from env)
load_dotenv()

TOKEN = os.getenv("TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

# Use absolute path or current working directory for channels.json
if os.path.dirname(__file__):
    CHANNELS_FILE = os.path.join(os.path.dirname(__file__), 'channels.json')
else:
    CHANNELS_FILE = 'channels.json'

SUPPORTED = {
    'ar': 'Arabic',
    'en': 'English',
    'tr': 'Turkish',
    'ja': 'Japanese',
    'fr': 'French',
    'ko': 'Korean',
    'it': 'Italian'
}


def load_channels() -> Dict[str, str]:
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


async def save_channels(data: Dict[str, str]):
    """Asynchronously save channel language configuration to disk.

    Writing to disk can block the event loop; offload to a thread pool so
    command handlers and UI callbacks remain responsive.
    """
    loop = asyncio.get_running_loop()

    def _write(d):
        # Use a temporary file to avoid truncation issues on crash
        tmp = CHANNELS_FILE + '.tmp'
        try:
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(d, f, ensure_ascii=False, indent=2)
            # Atomic replace
            os.replace(tmp, CHANNELS_FILE)
            logger.info(f"Saved {len(d)} channel configurations to {CHANNELS_FILE}")
        except Exception as e:
            logger.error(f"Error saving to {CHANNELS_FILE}: {e}")
            # Fallback to direct write
            try:
                with open(CHANNELS_FILE, 'w', encoding='utf-8') as f:
                    json.dump(d, f, ensure_ascii=False, indent=2)
                logger.info(f"Fallback: Saved {len(d)} configurations directly to {CHANNELS_FILE}")
            except Exception as e2:
                logger.error(f"Fallback save also failed: {e2}")

    await loop.run_in_executor(None, _write, data)


# Logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
translator = Translator()
channel_langs = load_channels()


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
    # try to set bot avatar as author icon when available
    try:
        if bot.user:
            avatar = getattr(bot.user, 'display_avatar', None)
            if avatar:
                emb.set_author(name=str(bot.user), icon_url=avatar.url)
    except Exception:
        pass
    return emb


# Slash command for ping
@bot.tree.command(name='ping', description='Check if the bot is responsive')
async def ping(interaction: discord.Interaction):
    # Show websocket latency and color-code by severity. This response is public in the channel.
    ws_ms = round(bot.latency * 1000)
    color = _choose_latency_color(ws_ms)
    emoji = "🟢" if ws_ms < 100 else ("🟡" if ws_ms < 250 else "🔴")
    emb = make_embed(title=f"Pong! {emoji} 🏓", description=f"WebSocket latency: **{ws_ms} ms**", color=color)
    emb.set_footer(text="Latency may vary. Measures websocket heartbeat latency.")
    await interaction.response.send_message(embed=emb, ephemeral=False)

@bot.tree.command(name='help', description='Show all available commands')
async def help(interaction: discord.Interaction):
    commands_list = [
        '`/setlang [channel]` - Set default language for a channel (with dropdown selection)',
        '`/getlang [channel]` - Get language setting for a channel',
        '`/listlangs` - List all supported languages',
        '`/removelang [channel]` - Remove language setting for a channel',
        '`/listchannels` - List all channels with their language settings',
        '`/debug` - Show bot debug information (Admin only)',
        '`/ping` - Check if the bot is responsive',
        '`/help` - Show this help message'
    ]
    
    desc = '**Available Commands:**\n\n' + '\n'.join(commands_list)
    emb = make_embed(title='Help', description=desc)
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
        # Get channel configurations
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
            for ch_id, lang in list(guild_configs.items())[:10]:  # Show first 10
                try:
                    channel = interaction.guild.get_channel(int(ch_id))
                    if channel:
                        info.append(f"• {channel.mention}: {SUPPORTED.get(lang, lang)}")
                    else:
                        info.append(f"• Channel ID {ch_id}: {SUPPORTED.get(lang, lang)} (channel not found)")
                except:
                    info.append(f"• Channel ID {ch_id}: {SUPPORTED.get(lang, lang)}")
            
            if len(guild_configs) > 10:
                info.append(f"... and {len(guild_configs) - 10} more")
        else:
            info.append("No channels configured in this server.")
        
        desc = '\n'.join(info)
        emb = make_embed(title='Debug Information', description=desc, color=discord.Color.blue())
        await interaction.response.send_message(embed=emb, ephemeral=True)
    except Exception as e:
        logger.error(f"Error in debug command: {e}")
        emb = make_embed(
            title='Error',
            description=f'❌ An error occurred: {str(e)}',
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=emb, ephemeral=True)


@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user}")
    logger.info(f"Bot is in {len(bot.guilds)} server(s)")
    
    # Log which application (slash) commands are currently registered in the tree
    try:
        cmds = [c.name for c in bot.tree.walk_commands()]
        if cmds:
            logger.info(f"Application commands present: {cmds}")
        else:
            logger.info("No application commands found in bot.tree.")
    except Exception as e:
        logger.debug(f"Could not list app commands: {e}")
    
    # Clear any guild-specific commands from all guilds to prevent duplicates
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
    
    # Sync slash commands globally (one time only)
    try:
        if GUILD_ID:
            # If GUILD_ID is specified, sync to that specific guild only (for fast testing)
            guild = discord.Object(id=int(GUILD_ID))
            bot.tree.copy_global_to(guild=guild)
            await bot.tree.sync(guild=guild)
            logger.info(f"Synced app commands to guild {GUILD_ID}")
        else:
            # Do global sync (commands will be available in all servers)
            # This takes up to 1 hour to propagate but prevents duplicate commands
            await bot.tree.sync()
            logger.info(f"Global sync completed for {len(bot.guilds)} servers (may take up to 1 hour to propagate)")
                
    except Exception as e:
        logger.error(f"Failed to sync app commands: {e}")

    # Log prefix commands and loaded cogs for debugging
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
    # Commands will be available via global sync (may take up to 1 hour)
    # If you need instant commands, use /sync command manually in the new server


@bot.event
async def on_guild_remove(guild: discord.Guild):
    """Log when the bot is removed from a server and clean up data."""
    logger.info(f"Removed from guild: {guild.name} (ID: {guild.id})")
    # Clean up channel settings for this guild
    try:
        # Get all channel IDs from this guild before it's removed
        guild_channel_ids = {str(c.id) for c in guild.channels}
        channels_to_remove = [ch_id for ch_id in list(channel_langs.keys()) 
                             if ch_id in guild_channel_ids]
        
        for ch_id in channels_to_remove:
            del channel_langs[ch_id]
        
        if channels_to_remove:
            await save_channels(channel_langs)
            logger.info(f"Cleaned up {len(channels_to_remove)} channel settings from {guild.name}")
    except Exception as e:
        logger.error(f"Error cleaning up guild data for {guild.name}: {e}")


class LanguageSelect(discord.ui.Select):
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
        if not interaction.user.guild_permissions.manage_channels:
            emb = make_embed(
                title='Permission Denied',
                description='⚠️ You need Manage Channels permission to use this command.',
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
    def __init__(self, channel):
        super().__init__()
        self.channel = channel
        self.add_item(LanguageSelect(SUPPORTED))


async def channel_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    """Autocomplete for channel selection - shows all text channels."""
    if not interaction.guild:
        return []
    
    # Get all text channels in the guild
    channels = [
        ch for ch in interaction.guild.channels 
        if isinstance(ch, (discord.TextChannel, discord.VoiceChannel, discord.ForumChannel))
    ]
    
    # Filter by current input
    if current:
        channels = [ch for ch in channels if current.lower() in ch.name.lower()]
    
    # Return up to 25 choices (Discord limit)
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
    
    # Get guild channel IDs
    guild_channel_ids = {str(ch.id) for ch in interaction.guild.channels}
    
    # Filter to only configured channels in this guild
    configured = []
    for ch_id, lang_code in channel_langs.items():
        if ch_id in guild_channel_ids:
            ch = interaction.guild.get_channel(int(ch_id))
            if ch and isinstance(ch, (discord.TextChannel, discord.VoiceChannel, discord.ForumChannel)):
                lang_name = SUPPORTED.get(lang_code, lang_code)
                configured.append((ch, lang_name))
    
    # Filter by current input
    if current:
        configured = [(ch, lang) for ch, lang in configured if current.lower() in ch.name.lower()]
    
    # Return up to 25 choices
    return [
        app_commands.Choice(name=f"#{ch.name} ({lang})", value=str(ch.id))
        for ch, lang in configured[:25]
    ]


@bot.tree.command(name='setlang', description='Set default language for a channel')
@app_commands.describe(
    channel='Select channel to set language for (optional, defaults to current channel)'
)
@app_commands.autocomplete(channel=channel_autocomplete)
async def setlang(interaction: discord.Interaction, channel: str = None):
    if not interaction.user.guild_permissions.manage_channels:
        emb = make_embed(
            title='Permission Denied',
            description='⚠️ You need Manage Channels permission to use this command.',
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=emb, ephemeral=True)
        return

    try:
        # If channel is provided as string (ID from autocomplete), get the channel object
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
            # Use current channel if none specified
            target_channel = interaction.channel
        
        # Show language selection for the target channel
        view = LanguageView(target_channel)
        await interaction.response.send_message(
            f"Select language for {target_channel.mention}:",
            view=view,
            ephemeral=True
        )
    except Exception as e:
        logger.error(f"Error in setlang command: {e}")
        emb = make_embed(
            title='Error',
            description=f'❌ An error occurred: {str(e)}',
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=emb, ephemeral=True)

@bot.tree.command(name='getlang', description='Get language setting for a channel')
@app_commands.describe(
    channel='Select channel to check language for (optional, defaults to current channel)'
)
@app_commands.autocomplete(channel=configured_channel_autocomplete)
async def getlang(interaction: discord.Interaction, channel: str = None):
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
        current_lang = channel_langs.get(channel_id)
        
        if current_lang:
            emb = make_embed(
                title='Channel Language',
                description=f'Language for {target_channel.mention}: **{SUPPORTED[current_lang]}** ({current_lang})'
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)
        else:
            emb = make_embed(
                title='Channel Language',
                description=f'No language set for {target_channel.mention}',
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
    langs_list = [f'{code}: {name}' for code, name in SUPPORTED.items()]
    emb = make_embed(title='Supported languages', description='\n'.join(langs_list))
    await interaction.response.send_message(embed=emb, ephemeral=True)

@bot.tree.command(name='listchannels', description='List all channels with their language settings')
async def listchannels(interaction: discord.Interaction):
    if not interaction.guild:
        emb = make_embed(
            title='Error',
            description='This command can only be used in a server.',
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=emb, ephemeral=True)
        return

    try:
        # Get all text and voice channels in the guild
        channels = interaction.guild.channels
        
        # Filter channels that have language settings
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
        
        # Create the message
        message = ['**Channels with Language Settings:**']
        if configured_channels:
            message.extend(configured_channels)
        else:
            message.append('No channels have language settings configured.')
        
        message.append('\n**Channels without Language Settings:**')
        if unconfigured_channels:
            # Limit to first 20 to avoid message too long
            if len(unconfigured_channels) > 20:
                message.extend(unconfigured_channels[:20])
                message.append(f'... and {len(unconfigured_channels) - 20} more')
            else:
                message.extend(unconfigured_channels)
        
        desc = '\n'.join(message)
        # Discord embed description limit is 4096 characters
        if len(desc) > 4096:
            desc = desc[:4093] + '...'
        
        emb = make_embed(title='Channel language overview', description=desc)
        await interaction.response.send_message(embed=emb, ephemeral=True)
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
    if not interaction.user.guild_permissions.manage_channels:
        emb = make_embed(
            title='Permission Denied',
            description='⚠️ You need Manage Channels permission to use this command.',
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


@bot.event
async def on_message(message: discord.Message):
    # Ignore bots and webhooks
    if message.author.bot or message.webhook_id:
        return

    channel_id = str(message.channel.id)
    target = channel_langs.get(channel_id)
    if not target:
        # nothing configured for this channel
        return

    content = message.content.strip()
    if not content:
        return
    # If this message is a prefix command (starts with '!'), let the command processor handle it.
    if content.startswith('!'):
        try:
            await bot.process_commands(message)
        except Exception:
            pass
        return

    # Slash commands are interactions and won't appear as message content; ignore literal messages
    # that start with '/' to avoid accidental translations of written slashes.
    if content.startswith('/'):
        return

    try:
        detected = detect(content)
        logger.debug(f"Detected language: {detected} for message in channel {channel_id} (target: {target})")
    except LangDetectException as e:
        logger.debug(f"Could not detect language for message: {e}")
        return

    if detected == target:
        logger.debug(f"Message already in target language ({target}), skipping translation")
        return

    # Check if target language is supported (we can translate FROM any language TO supported languages)
    if target not in SUPPORTED:
        logger.debug(f"Target language {target} is not supported")
        return

    # translate
    try:
        # Pass detected language as source to translator to avoid wrong auto-detection
        logger.info(f"Translating from {detected} to {target} in channel {channel_id}")
        res = translator.translate(content, src=detected, dest=target)
        translated = getattr(res, 'text', str(res))
        
        # Only send translation if it's different from original
        if translated and translated.strip() != content.strip():
            # send reply as embed
            emb = make_embed(title='Translation', description=translated, color=discord.Color.blue())
            try:
                # Show detected language name if it's in SUPPORTED, otherwise just the code
                detected_name = SUPPORTED.get(detected, detected)
                target_name = SUPPORTED.get(target, target)
                emb.set_footer(text=f"{detected_name} → {target_name}")
            except Exception:
                pass
            await message.reply(embed=emb, mention_author=False)
            logger.info(f"Detected '{detected}' message in '{target}' channel → Translated to {SUPPORTED.get(target, target)}")
        else:
            logger.debug(f"Translation result is same as original, skipping")
    except Exception as e:
        logger.error(f"Translation error: {e}")
    # Allow other commands (if any) to be processed
    try:
        await bot.process_commands(message)
    except Exception:
        pass


if __name__ == '__main__':
    if not TOKEN:
        logger.error('TOKEN is not set. Put it in Replit Secrets as TOKEN or .env locally.')
        exit(1)
    bot.run(TOKEN)

# Run instructions:
# 1. On Replit, add Secrets: TOKEN (your bot token), optionally GUILD_ID for fast slash command sync.
# 2. Press Run. The bot will start and sync slash commands. Use /setlang <code> in a channel to set its language.
# 3. Send messages in languages different from the channel language — the bot will translate and reply.
