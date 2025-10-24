from discord.ext import commands
from deep_translator import GoogleTranslator


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


async def setup(bot):
    await bot.add_cog(Translate(bot))
