import discord
from discord.ext import commands


class Debug(commands.Cog):
    """Debug cog: small utilities to check prefix commands and app command registration."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='ping')
    async def ping(self, ctx: commands.Context):
        """Simple ping to verify prefix commands."""
        await ctx.send('Pong!')

    @commands.command(name='listappcommands')
    async def list_app_commands(self, ctx: commands.Context):
        """List application (slash) commands currently in bot.tree."""
        try:
            cmds = [c.name for c in self.bot.tree.walk_commands()]
            if not cmds:
                await ctx.send('No application commands are currently registered in bot.tree.')
                return
            await ctx.send(f"App commands: {', '.join(cmds[:25])}{'...' if len(cmds) > 25 else ''}")
        except Exception as e:
            await ctx.send(f"Error listing app commands: {e}")

    @commands.command(name='sync')
    async def sync(self, ctx: commands.Context, guild_id: int = None):
        """Force sync application commands. Requires Manage Guild or bot owner."""
        # Permission check
        is_owner = False
        try:
            is_owner = await self.bot.is_owner(ctx.author)
        except Exception:
            is_owner = False

        if not (ctx.author.guild_permissions.manage_guild or is_owner):
            await ctx.send('⚠️ You need Manage Server permission or be bot owner to run this command.', ephemeral=False)
            return

        try:
            if guild_id:
                guild = discord.Object(id=guild_id)
                await self.bot.tree.sync(guild=guild)
                await ctx.send(f'✅ Synced app commands to guild {guild_id}')
            else:
                await self.bot.tree.sync()
                await ctx.send('✅ Synced app commands globally')
        except Exception as e:
            await ctx.send(f'⚠️ Failed to sync app commands: {e}')


async def setup(bot: commands.Bot):
    await bot.add_cog(Debug(bot))
