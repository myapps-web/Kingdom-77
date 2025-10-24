import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ تم تسجيل الدخول كبوت: {bot.user}")
    # تحميل جميع Cogs الموجودة في المشروع (يدعم الهيكل cogs/cogs/*.py)
    project_root = os.path.dirname(__file__)
    # المسار المتوقع للموديلات: ../cogs/cogs
    candidate = os.path.normpath(os.path.join(project_root, '..', 'cogs', 'cogs'))
    if not os.path.isdir(candidate):
        # بدل احتياطي: جرب ../cogs
        candidate = os.path.normpath(os.path.join(project_root, '..', 'cogs'))

    loaded = 0
    if os.path.isdir(candidate):
        for root, _, files in os.walk(candidate):
            for filename in files:
                if not filename.endswith('.py') or filename == '__init__.py':
                    continue
                file_path = os.path.join(root, filename)
                # احسب مسار الوحدة (module path) نسبةً إلى مجلد المشروع الأعلى (parent of discord-bot)
                rel = os.path.relpath(file_path, start=os.path.normpath(os.path.join(project_root, '..')))
                module = rel.replace(os.sep, '.')[:-3]  # remove .py
                try:
                    # In discord.py 2.x load_extension is a coroutine because extensions
                    # can define async `setup(bot)` functions. Await it to support both.
                    await bot.load_extension(module)
                    loaded += 1
                    print(f"✅ Loaded: {module}")
                except Exception as e:
                    print(f"⚠️ Failed to load {module}: {e}")

    print(f"📦 تم محاولة تحميل Cogs — محمَّلة: {loaded}")
    # Sync application commands (slash commands). If GUILD_ID set, sync to that guild for fast registration.
    guild_id = os.getenv('GUILD_ID')
    try:
        if guild_id:
            guild = discord.Object(id=int(guild_id))
            await bot.tree.sync(guild=guild)
            print(f"🔁 Synced app commands to guild {guild_id}")
        else:
            await bot.tree.sync()
            print("🔁 Synced app commands globally")
    except Exception as e:
        print(f"⚠️ Failed to sync app commands: {e}")

bot.run(os.getenv("TOKEN"))
