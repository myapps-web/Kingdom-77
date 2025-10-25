import os
import json
import logging
from typing import Dict

from dotenv import load_dotenv
from langdetect import detect, LangDetectException
from googletrans import Translator
import discord
from discord import app_commands
from discord.ext import commands


# Load environment (for local testing; in Replit TOKEN will come from env)
load_dotenv()

TOKEN = os.getenv("TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

CHANNELS_FILE = os.path.join(os.path.dirname(__file__), 'channels.json')

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
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_channels(data: Dict[str, str]):
    with open(CHANNELS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# Logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
translator = Translator()
channel_langs = load_channels()


# Slash command for ping
@bot.tree.command(name='ping', description='Check if the bot is responsive')
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message('Pong! 🏓', ephemeral=True)

@bot.tree.command(name='help', description='Show all available commands')
async def help(interaction: discord.Interaction):
    commands_list = [
        '`/setlang [channel]` - Set default language for a channel (with dropdown selection)',
        '`/getlang [channel]` - Get language setting for a channel',
        '`/listlangs` - List all supported languages',
        '`/removelang [channel]` - Remove language setting for a channel',
        '`/listchannels` - List all channels with their language settings',
        '`/ping` - Check if the bot is responsive',
        '`/help` - Show this help message'
    ]
    
    await interaction.response.send_message(
        '**Available Commands:**\n\n' + '\n'.join(commands_list),
        ephemeral=True
    )


@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user}")
    # Log which application (slash) commands are currently registered in the tree
    try:
        cmds = [c.name for c in bot.tree.walk_commands()]
        if cmds:
            logger.info(f"Application commands present: {cmds}")
        else:
            logger.info("No application commands found in bot.tree.")
            if not GUILD_ID:
                logger.info("Note: No GUILD_ID set — global registration can take up to an hour. Set GUILD_ID in Replit Secrets for fast guild sync.")
    except Exception as e:
        logger.debug(f"Could not list app commands: {e}")
    # Sync slash commands
    try:
        if GUILD_ID:
            guild = discord.Object(id=int(GUILD_ID))
            bot.tree.copy_global_to(guild=guild)
            await bot.tree.sync(guild=guild)
            logger.info(f"Synced app commands to guild {GUILD_ID}")
        else:
            await bot.tree.sync()
            logger.info("Synced app commands globally")
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
            await interaction.response.send_message('⚠️ You need Manage Channels permission to use this command.', ephemeral=True)
            return
        
        code = self.values[0]
        channel_id = str(self.view.channel.id)
        channel_langs[channel_id] = code
        save_channels(channel_langs)
        await interaction.response.send_message(
            f'✅ Channel language set to {SUPPORTED[code]} ({code}) for {self.view.channel.mention}',
            ephemeral=True
        )

class ChannelSelect(discord.ui.ChannelSelect):
    def __init__(self):
        super().__init__(
            placeholder="Select a channel...",
            channel_types=[
                discord.ChannelType.text,
                discord.ChannelType.voice,
                discord.ChannelType.forum,
                discord.ChannelType.news
            ]
        )

    async def callback(self, interaction: discord.Interaction):
        self.view.channel = self.values[0]
        # Update the language select view
        lang_view = LanguageView(self.view.channel)
        await interaction.response.send_message(
            f"Select language for {self.view.channel.mention}:",
            view=lang_view,
            ephemeral=True
        )

class ChannelView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.channel = None
        self.add_item(ChannelSelect())

class LanguageView(discord.ui.View):
    def __init__(self, channel):
        super().__init__()
        self.channel = channel
        self.add_item(LanguageSelect(SUPPORTED))

@bot.tree.command(name='setlang', description='Set default language for a channel')
@app_commands.describe(
    channel='Select channel to set language for (optional, defaults to current channel)'
)
async def setlang(interaction: discord.Interaction, channel: discord.TextChannel = None):
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message('⚠️ You need Manage Channels permission to use this command.', ephemeral=True)
        return

    if channel:
        # If channel is specified directly, show language selection
        view = LanguageView(channel)
        await interaction.response.send_message(
            f"Select language for {channel.mention}:",
            view=view,
            ephemeral=True
        )
    else:
        # If no channel specified, show channel selection first
        view = ChannelView()
        await interaction.response.send_message(
            "Select a channel:",
            view=view,
            ephemeral=True
        )

@bot.tree.command(name='getlang', description='Get language setting for a channel')
@app_commands.describe(
    channel='Select channel to check language for (optional, defaults to current channel)'
)
async def getlang(interaction: discord.Interaction, channel: discord.TextChannel = None):
    target_channel = channel or interaction.channel
    channel_id = str(target_channel.id)
    current_lang = channel_langs.get(channel_id)
    
    if current_lang:
        await interaction.response.send_message(
            f'Language for {target_channel.mention}: {SUPPORTED[current_lang]} ({current_lang})',
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            f'No language set for {target_channel.mention}',
            ephemeral=True
        )

@bot.tree.command(name='listlangs', description='List all supported languages')
async def listlangs(interaction: discord.Interaction):
    langs_list = [f'{code}: {name}' for code, name in SUPPORTED.items()]
    await interaction.response.send_message(
        'Supported languages:\n' + '\n'.join(langs_list),
        ephemeral=True
    )

@bot.tree.command(name='listchannels', description='List all channels with their language settings')
async def listchannels(interaction: discord.Interaction):
    if not interaction.guild:
        await interaction.response.send_message('This command can only be used in a server.', ephemeral=True)
        return

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
                lang_name = SUPPORTED[lang_code]
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
        message.extend(unconfigured_channels)
    
    await interaction.response.send_message('\n'.join(message), ephemeral=True)

@bot.tree.command(name='removelang', description='Remove language setting for a channel')
@app_commands.describe(
    channel='Select channel to remove language setting from (optional, defaults to current channel)'
)
async def removelang(interaction: discord.Interaction, channel: discord.TextChannel = None):
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message('⚠️ You need Manage Channels permission to use this command.', ephemeral=True)
        return

    target_channel = channel or interaction.channel
    channel_id = str(target_channel.id)
    
    if channel_id in channel_langs:
        old_lang = channel_langs[channel_id]
        del channel_langs[channel_id]
        save_channels(channel_langs)
        await interaction.response.send_message(
            f'✅ Removed language setting for {target_channel.mention} (was {SUPPORTED[old_lang]}).',
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            f'No language was set for {target_channel.mention}.',
            ephemeral=True
        )


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
    except LangDetectException:
        return

    if detected == target:
        return

    if detected not in SUPPORTED or target not in SUPPORTED:
        return

    # translate
    try:
        # Pass detected language as source to translator to avoid wrong auto-detection
        logger.debug(f"Translating message from detected='{detected}' to target='{target}' in channel={channel_id}")
        res = translator.translate(content, src=detected, dest=target)
        translated = getattr(res, 'text', str(res))
        # send reply
        await message.reply(translated, mention_author=False)
        logger.info(f"Detected '{detected}' message in '{target}' channel → Translated to {SUPPORTED[target]}")
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
