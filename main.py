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


# Simple ping command to verify prefix commands work in guilds
@bot.command(name='ping')
async def ping(ctx: commands.Context):
    """Simple test command to verify prefix commands are received and respond."""
    await ctx.send('Pong!')


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


@bot.tree.command(name='setlang', description='Set default language for this channel')
@app_commands.describe(language='Language code (ar, en, tr, ja, fr, ko, it)')
async def setlang(interaction: discord.Interaction, language: str):
    # permission: manage_channels
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message('⚠️ You need Manage Channels permission to use this command.', ephemeral=True)
        return
    code = language.lower()
    if code not in SUPPORTED:
        await interaction.response.send_message(f"⚠️ Unsupported language. Supported: {', '.join(SUPPORTED.keys())}", ephemeral=True)
        return
    channel_id = str(interaction.channel_id)
    channel_langs[channel_id] = code
    save_channels(channel_langs)
    await interaction.response.send_message(f'✅ Channel language set to {SUPPORTED[code]} ({code})', ephemeral=True)


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
    # ignore commands
    if content.startswith('/') or content.startswith('!'):
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
        res = translator.translate(content, dest=target)
        translated = res.text
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
