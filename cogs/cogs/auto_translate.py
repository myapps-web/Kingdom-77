import os
import json
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands
from deep_translator import GoogleTranslator


DATA_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'discord-bot', 'channel_langs.json')


def load_data() -> dict:
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_data(data: dict):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class AutoTranslate(commands.Cog):
    """Automatic per-channel translation with slash commands to configure."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.data = load_data()

    async def cog_load(self) -> None:
        # register app commands group under /translate
        self.group = app_commands.Group(name='translate', description='Translation commands')

        @self.group.command(name='set_channel_language', description='Set default target language for this channel (e.g. en, ar)')
        @app_commands.describe(lang='Target language code, e.g. en, ar, fr', embed='Send translations as embed (true/false)')
        async def set_channel_language(interaction: discord.Interaction, lang: str, embed: Optional[bool] = False):
            # Restrict to users with Manage Channels permission
            if not interaction.user.guild_permissions.manage_channels:
                await interaction.response.send_message('⚠️ You need the Manage Channels permission to change channel language.', ephemeral=True)
                return
            channel_id = str(interaction.channel_id)
            # store dict per channel: {'lang': 'en', 'embed': True}
            self.data[channel_id] = {'lang': lang, 'embed': bool(embed)}
            save_data(self.data)
            await interaction.response.send_message(f'✅ Channel default language set to `{lang}` (embed={embed})', ephemeral=True)

        @self.group.command(name='get_channel_language', description='Get the configured target language for this channel')
        async def get_channel_language(interaction: discord.Interaction):
            channel_id = str(interaction.channel_id)
            info = self.data.get(channel_id)
            if info:
                # info can be string (legacy) or dict
                if isinstance(info, dict):
                    lang = info.get('lang')
                    embed_flag = info.get('embed', False)
                    await interaction.response.send_message(f'🔎 This channel translates to `{lang}` by default (embed={embed_flag}).', ephemeral=True)
                else:
                    await interaction.response.send_message(f'🔎 This channel translates to `{info}` by default.', ephemeral=True)
            else:
                await interaction.response.send_message('ℹ️ No default language configured for this channel.', ephemeral=True)

        @self.group.command(name='clear_channel_language', description='Clear the configured target language for this channel')
        async def clear_channel_language(interaction: discord.Interaction):
            # Restrict to users with Manage Channels permission
            if not interaction.user.guild_permissions.manage_channels:
                await interaction.response.send_message('⚠️ You need the Manage Channels permission to change channel language.', ephemeral=True)
                return
            channel_id = str(interaction.channel_id)
            if channel_id in self.data:
                del self.data[channel_id]
                save_data(self.data)
                await interaction.response.send_message('✅ Channel default language cleared.', ephemeral=True)
            else:
                await interaction.response.send_message('ℹ️ No language was set for this channel.', ephemeral=True)

        @self.group.command(name='manual', description='Manually translate a text to a target language')
        @app_commands.describe(lang='Target language code, e.g. en, ar, fr', text='Text to translate')
        async def manual(interaction: discord.Interaction, lang: str, text: str):
            await interaction.response.defer()
            try:
                translated = GoogleTranslator(source='auto', target=lang).translate(text)
                await interaction.followup.send(f'🔤 **Translated ({lang})**:\n{translated}')
            except Exception as e:
                await interaction.followup.send(f'⚠️ Translation failed: {e}')

        @self.group.command(name='detect', description='Detect the language of a text')
        @app_commands.describe(text='Text to detect language for')
        async def detect(interaction: discord.Interaction, text: str):
            await interaction.response.defer()
            try:
                # use Google translate public endpoint to detect language
                import requests
                from urllib.parse import quote_plus
                q = quote_plus(text)
                url = f'https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=en&dt=t&q={q}'
                r = requests.get(url, timeout=10)
                data = r.json()
                detected = data[2] if len(data) > 2 else None
                if detected:
                    await interaction.followup.send(f'🔎 Detected language: `{detected}`')
                else:
                    await interaction.followup.send('ℹ️ Could not detect language')
            except Exception as e:
                await interaction.followup.send(f'⚠️ Detection failed: {e}')

        try:
            self.bot.tree.add_command(self.group)
        except Exception:
            # if command already exists, ignore
            pass

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # ignore bots and webhooks
        if message.author.bot or message.webhook_id:
            return

        channel_id = str(message.channel.id)
        info = self.data.get(channel_id)
        if not info:
            return
        # support legacy value
        if isinstance(info, dict):
            target_lang = info.get('lang')
            use_embed = info.get('embed', False)
        else:
            target_lang = info
            use_embed = False

        # ignore empty content
        text = message.content.strip()
        if not text:
            return

        # don't translate commands (starting with ! or /)
        if text.startswith('!') or text.startswith('/'):
            return

        try:
            translated = GoogleTranslator(source='auto', target=target_lang).translate(text)
            if translated and translated != text:
                # reply with translation
                if use_embed:
                    embed = discord.Embed(title=f'Translated ({target_lang})', description=translated, color=0x2F3136)
                    await message.reply(embed=embed, mention_author=False)
                else:
                    await message.reply(f'🔤 **Translated ({target_lang})**:\n{translated}', mention_author=False)
        except Exception:
            # silently ignore translation errors to avoid spamming
            return


async def setup(bot: commands.Bot):
    await bot.add_cog(AutoTranslate(bot))
