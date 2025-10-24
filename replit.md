# Discord Bot Project

## Overview
This is a Discord bot built with discord.py that uses a modular cog system for organizing commands. The bot is currently configured to run on Replit and includes a basic "ping" command as an example.

## Project Structure
```
.
├── discord-bot/
│   ├── Main.py              # Main bot entry point
│   └── requirements.txt     # Python dependencies
├── cogs/
│   └── cogs/
│       ├── __init__.py
│       └── general.py       # General commands cog (includes !ping)
└── replit.md               # This file
```

## Current State
- **Status**: ✅ Running successfully
- **Bot Name**: K77 translator#8977
- **Python Version**: 3.11
- **Dependencies**: discord.py 2.6.4, python-dotenv 1.1.1
- **Loaded Cogs**: 1 (cogs.cogs.general)

## Recent Changes (October 24, 2025)
- Added Python 3.11 support
- Installed discord.py and python-dotenv via UV package manager
- Fixed module path issue by adding project root to sys.path in Main.py
- Successfully loaded the general cog with ping command
- Updated .gitignore to include .pythonlibs/ directory
- Created workflow configuration for running the bot

## Features
- **Command Prefix**: `!`
- **Message Content Intent**: Enabled
- **Auto-loading Cogs**: The bot automatically discovers and loads all cogs from the `cogs/cogs/` directory

## Available Commands
- `!ping` - Responds with "Pong! 🏓"

## Configuration
The bot requires the following environment variable:
- `TOKEN` - Discord bot token (stored in Replit Secrets)

## How to Use
The bot runs automatically when you start the Replit project. The workflow is configured to:
1. Navigate to the `discord-bot` directory
2. Run `python Main.py`

## Adding New Commands
To add new commands:
1. Create a new cog file in `cogs/cogs/` directory
2. Follow the pattern in `general.py`:
   ```python
   from discord.ext import commands

   class YourCog(commands.Cog):
       def __init__(self, bot):
           self.bot = bot

       @commands.command()
       async def your_command(self, ctx):
           await ctx.send("Response")

   async def setup(bot):
       await bot.add_cog(YourCog(bot))
   ```
3. The bot will automatically load it on restart

## Technical Notes
- The bot uses discord.py 2.x with async/await syntax
- Cogs are loaded dynamically from the file system
- The project root is added to sys.path to enable proper module imports
- Virtual environment is managed by UV in `.pythonlibs/` directory

## User Preferences
None specified yet.
