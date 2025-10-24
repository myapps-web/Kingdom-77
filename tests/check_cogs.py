import sys
import os
import asyncio

print('Python:', sys.version.splitlines()[0])

try:
    import discord
    from discord.ext import commands
    print('discord.py version:', getattr(discord, '__version__', 'unknown'))
except Exception as e:
    print('ERROR: cannot import discord.py:', e)
    print('Please install dependencies: pip install -r discord-bot/requirements.txt')
    raise SystemExit(1)


async def main():
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix='!', intents=intents)

    project_root = os.path.dirname(os.path.dirname(__file__))
    # Ensure the project root is on sys.path so 'cogs' package can be imported
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    cogs_dir = os.path.join(project_root, 'cogs', 'cogs')
    if not os.path.isdir(cogs_dir):
        print('No cogs directory found at', cogs_dir)
        raise SystemExit(1)

    loaded = 0
    for filename in os.listdir(cogs_dir):
        if not filename.endswith('.py') or filename == '__init__.py':
            continue
        rel = os.path.relpath(os.path.join(cogs_dir, filename), start=project_root)
        module = rel.replace(os.sep, '.')[:-3]
        try:
            # await load_extension to support async setup
            await bot.load_extension(module)
            print('Loaded cog:', module)
            loaded += 1
        except Exception as e:
            print('Failed loading', module, '->', e)

    print('Total cogs loaded:', loaded)
    print('Registered cogs on bot:', list(bot.cogs.keys()))
    # Check for common commands
    ping_cmd = bot.get_command('ping')
    print('ping command registered?:', bool(ping_cmd))


if __name__ == '__main__':
    asyncio.run(main())
