from discord.ext import commands
from deep_translator import GoogleTranslator
import requests
from urllib.parse import quote_plus
from typing import Optional


class Translate(commands.Cog):
    """Simple translation cog using deep-translator (GoogleTranslator)."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='translate', help='Translate text to a target language. Usage: !translate <to> <text>')
    async def translate(self, ctx, to: str, *, text: str):
        """Translate the given text to the language code `to` (e.g., en, ar, fr)."""
        try:
            translated = GoogleTranslator(source='auto', target=to).translate(text)
            await ctx.send(f"🔤 **Translated ({to})**:\n{translated}")
        except Exception as e:
            await ctx.send(f"⚠️ Translation failed: {e}")

    @commands.command(name='tr', help='Detect language and translate to channel default or specified target. Usage: !tr [to] <text>')
    async def tr(self, ctx, to_or_text: str, *, text: Optional[str] = None):
        """If two params given, first is target lang. If only one, it will detect and show language and translation to channel configured target if any."""
        try:
            if text is None:
                # only one argument: treat it as text; detect language
                text = to_or_text
                # detect language via google translate endpoint
                q = quote_plus(text)
                url = f'https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=en&dt=t&q={q}'
                r = requests.get(url, timeout=10)
                data = r.json()
                detected = data[2] if len(data) > 2 else None
                # translate to channel default if set
                channel_id = str(ctx.channel.id)
                from .. import __package__
                # try to read channel default
                default = None
                try:
                    import json, os
                    df = os.path.join(os.path.dirname(__file__), '..', '..', 'discord-bot', 'channel_langs.json')
                    with open(df, 'r', encoding='utf-8') as f:
                        d = json.load(f)
                        info = d.get(channel_id)
                        if isinstance(info, dict):
                            default = info.get('lang')
                        else:
                            default = info
                except Exception:
                    default = None

                msg = f'🔎 Detected language: `{detected}`' if detected else 'ℹ️ Could not detect language'
                if default:
                    translated = GoogleTranslator(source='auto', target=default).translate(text)
                    msg += f"\n🔤 Translated to channel default ({default}):\n{translated}"
                await ctx.send(msg)
            else:
                # two params: to and text
                to = to_or_text
                translated = GoogleTranslator(source='auto', target=to).translate(text)
                await ctx.send(f"🔤 **Translated ({to})**:\n{translated}")
        except Exception as e:
            await ctx.send(f"⚠️ Translation failed: {e}")


async def setup(bot):
    await bot.add_cog(Translate(bot))
