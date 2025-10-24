import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()  # لتحميل المتغيرات من ملف .env

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"✅ تم تسجيل الدخول كبوت: {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong! 🏓")

bot.run(os.getenv("TOKEN"))
