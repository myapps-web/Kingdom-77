"""
Kingdom-77 Bot - Custom Commands Cog
Discord slash commands for managing custom commands and auto-responses
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional, Literal
import json

from database.custom_commands_schema import CustomCommandsSchema
from custom_commands.commands_system import CommandsSystem
from custom_commands.command_parser import CommandParser


class EmbedBuilderModal(discord.ui.Modal):
    """Modal for building custom embeds"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(title="Embed Builder", *args, **kwargs)
        
        self.add_item(discord.ui.InputText(
            label="Title",
            placeholder="Embed title (optional)",
            required=False,
            max_length=256
        ))
        
        self.add_item(discord.ui.InputText(
            label="Description",
            placeholder="Embed description",
            style=discord.InputTextStyle.long,
            required=False,
            max_length=4000
        ))
        
        self.add_item(discord.ui.InputText(
            label="Color (Hex)",
            placeholder="#FF0000",
            required=False,
            max_length=7
        ))
        
        self.add_item(discord.ui.InputText(
            label="Footer Text",
            placeholder="Footer text (optional)",
            required=False,
            max_length=2048
        ))
        
        self.add_item(discord.ui.InputText(
            label="Image URL",
            placeholder="https://example.com/image.png",
            required=False,
            max_length=500
        ))
    
    async def callback(self, interaction: discord.Interaction):
        """Handle modal submission"""
        embed_data = {}
        
        if self.children[0].value:
            embed_data["title"] = self.children[0].value
        if self.children[1].value:
            embed_data["description"] = self.children[1].value
        if self.children[2].value:
            embed_data["color"] = self.children[2].value
        if self.children[3].value:
            embed_data["footer"] = {"text": self.children[3].value}
        if self.children[4].value:
            embed_data["image"] = self.children[4].value
        
        self.embed_data = embed_data
        await interaction.response.defer()


class CustomCommandsCog(commands.Cog):
    """Custom Commands Management"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.schema = CustomCommandsSchema(bot.db)
        self.system = bot.get_cog("CommandsSystem")
        self.parser = CommandParser()
        
        # Create command groups using app_commands
        self.command_group = app_commands.Group(name="command", description="Manage custom commands")
        self.autoresponse_group = app_commands.Group(name="autoresponse", description="Manage auto-responses")
    
    # ==================== Command Management ====================
    
    @commands.command(description="Create a new custom command")
    @discord.default_permissions(manage_guild=True)
    async def create(
        self,
        ctx: discord.ApplicationContext,
        name: str = Option(description="Command name (letters, numbers, - and _ only)"),
        response: str = Option(description="Response text (use {variables})"),
        cooldown: int = Option(default=0, description="Cooldown in seconds"),
        delete_trigger: bool = Option(default=False, description="Delete command message")
    ):
        """Create a custom command"""
        await ctx.defer()
        
        # Check premium limits
        is_premium = await self.bot.premium_system.check_premium(ctx.guild.id)
        limit_info = await self.schema.check_command_limit(ctx.guild.id, is_premium)
        
        if not limit_info["can_create"]:
            embed = discord.Embed(
                title="❌ Command Limit Reached",
                description=f"You have reached the maximum of {limit_info['limit']} commands.\n"
                           f"Upgrade to Premium for unlimited commands!",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return
        
        # Create command
        success, message = await self.system.create_command(
            guild_id=ctx.guild.id,
            creator_id=ctx.author.id,
            name=name,
            response_type="text",
            response_content=response,
            cooldown=cooldown,
            delete_trigger=delete_trigger
        )
        
        if success:
            embed = discord.Embed(
                title="✅ Command Created",
                description=f"{message}\n\n**Usage:** `/command_run {name}`\n"
                           f"**Remaining:** {limit_info['remaining'] - 1 if limit_info['remaining'] != float('inf') else '∞'}",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="❌ Error",
                description=message,
                color=discord.Color.red()
            )
        
        await ctx.respond(embed=embed)
    
    @commands.command(description="Create a command with custom embed")
    @discord.default_permissions(manage_guild=True)
    async def create_embed(
        self,
        ctx: discord.ApplicationContext,
        name: str = Option(description="Command name"),
        text: Optional[str] = Option(default=None, description="Optional text with embed")
    ):
        """Create a command with embed builder"""
        # Check premium limits
        is_premium = await self.bot.premium_system.check_premium(ctx.guild.id)
        limit_info = await self.schema.check_command_limit(ctx.guild.id, is_premium)
        
        if not limit_info["can_create"]:
            embed = discord.Embed(
                title="❌ Command Limit Reached",
                description=f"Maximum {limit_info['limit']} commands reached. Upgrade to Premium!",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return
        
        # Show embed builder modal
        modal = EmbedBuilderModal()
        await ctx.send_modal(modal)
        await modal.wait()
        
        # Validate embed data
        is_valid, error_msg = self.parser.validate_embed_data(modal.embed_data)
        if not is_valid:
            await ctx.respond(
                embed=discord.Embed(
                    title="❌ Invalid Embed",
                    description=error_msg,
                    color=discord.Color.red()
                ),
                ephemeral=True
            )
            return
        
        # Determine response type
        response_type = "both" if text else "embed"
        
        # Create command
        success, message = await self.system.create_command(
            guild_id=ctx.guild.id,
            creator_id=ctx.author.id,
            name=name,
            response_type=response_type,
            response_content=text,
            embed_data=modal.embed_data
        )
        
        if success:
            embed = discord.Embed(
                title="✅ Embed Command Created",
                description=message,
                color=discord.Color.green()
            )
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(
                title="❌ Error",
                description=message,
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed, ephemeral=True)
    
    @commands.command(description="Delete a custom command")
    @discord.default_permissions(manage_guild=True)
    async def delete(
        self,
        ctx: discord.ApplicationContext,
        name: str = Option(description="Command name to delete")
    ):
        """Delete a custom command"""
        success, message = await self.system.delete_command(ctx.guild.id, name)
        
        if success:
            embed = discord.Embed(
                title="✅ Command Deleted",
                description=message,
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="❌ Error",
                description=message,
                color=discord.Color.red()
            )
        
        await ctx.respond(embed=embed)
    
    @commands.command(description="List all custom commands")
    async def list(
        self,
        ctx: discord.ApplicationContext,
        creator: Optional[discord.Member] = Option(default=None, description="Filter by creator")
    ):
        """List all custom commands"""
        await ctx.defer()
        
        if creator:
            commands_list = await self.schema.get_commands_by_creator(ctx.guild.id, creator.id)
        else:
            commands_list = await self.schema.get_all_commands(ctx.guild.id, enabled_only=False)
        
        if not commands_list:
            embed = discord.Embed(
                title="📝 Custom Commands",
                description="No custom commands found.",
                color=discord.Color.blue()
            )
            await ctx.respond(embed=embed)
            return
        
        # Build command list
        embed = discord.Embed(
            title=f"📝 Custom Commands ({len(commands_list)})",
            description=f"Total commands in {ctx.guild.name}",
            color=discord.Color.blue()
        )
        
        for cmd in commands_list[:25]:  # Max 25 per page
            status = "✅" if cmd.get("enabled", True) else "❌"
            creator_id = cmd.get("creator_id", "Unknown")
            uses = cmd.get("use_count", 0)
            
            embed.add_field(
                name=f"{status} {cmd['name']}",
                value=f"Creator: <@{creator_id}>\nUses: {uses}\nType: {cmd.get('response_type', 'text')}",
                inline=True
            )
        
        if len(commands_list) > 25:
            embed.set_footer(text=f"Showing 25 of {len(commands_list)} commands")
        
        await ctx.respond(embed=embed)
    
    @commands.command(description="Get information about a command")
    async def info(
        self,
        ctx: discord.ApplicationContext,
        name: str = Option(description="Command name")
    ):
        """Get detailed command information"""
        command = await self.schema.get_command(ctx.guild.id, name)
        
        if not command:
            embed = discord.Embed(
                title="❌ Command Not Found",
                description=f"No command named `{name}` exists.",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"ℹ️ Command Info: {command['name']}",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="Creator", value=f"<@{command['creator_id']}>", inline=True)
        embed.add_field(name="Type", value=command.get('response_type', 'text'), inline=True)
        embed.add_field(name="Status", value="✅ Enabled" if command.get('enabled', True) else "❌ Disabled", inline=True)
        embed.add_field(name="Uses", value=str(command.get('use_count', 0)), inline=True)
        embed.add_field(name="Cooldown", value=f"{command.get('cooldown', 0)}s", inline=True)
        embed.add_field(name="Delete Trigger", value="Yes" if command.get('delete_trigger', False) else "No", inline=True)
        
        if command.get('aliases'):
            embed.add_field(name="Aliases", value=", ".join(command['aliases']), inline=False)
        
        if command.get('response_content'):
            content = command['response_content'][:200]
            if len(command['response_content']) > 200:
                content += "..."
            embed.add_field(name="Response", value=f"```{content}```", inline=False)
        
        created = command.get('created_at')
        if created:
            embed.timestamp = created
            embed.set_footer(text="Created")
        
        await ctx.respond(embed=embed)
    
    @commands.command(description="Test a command execution")
    async def test(
        self,
        ctx: discord.ApplicationContext,
        name: str = Option(description="Command name to test"),
        args: Optional[str] = Option(default=None, description="Test arguments")
    ):
        """Test command execution"""
        await ctx.defer()
        
        command = await self.schema.get_command(ctx.guild.id, name)
        if not command:
            await ctx.respond(
                embed=discord.Embed(
                    title="❌ Command Not Found",
                    description=f"No command named `{name}` exists.",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )
            return
        
        # Execute command
        executed = await self.system.execute_command(ctx, name, args)
        
        if not executed:
            await ctx.respond(
                embed=discord.Embed(
                    title="❌ Execution Failed",
                    description="Failed to execute command. Check the logs.",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )
    
    @commands.command(description="Toggle command enabled status")
    @discord.default_permissions(manage_guild=True)
    async def toggle(
        self,
        ctx: discord.ApplicationContext,
        name: str = Option(description="Command name"),
        enabled: bool = Option(description="Enable or disable")
    ):
        """Enable or disable a command"""
        success = await self.schema.toggle_command(ctx.guild.id, name, enabled)
        
        if success:
            status = "enabled" if enabled else "disabled"
            embed = discord.Embed(
                title="✅ Success",
                description=f"Command `{name}` has been {status}.",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Command `{name}` not found.",
                color=discord.Color.red()
            )
        
        await ctx.respond(embed=embed)
    
    @commands.command(description="Get command statistics")
    async def stats(
        self,
        ctx: discord.ApplicationContext,
        days: int = Option(default=7, description="Number of days to analyze")
    ):
        """View command usage statistics"""
        await ctx.defer()
        
        stats = await self.system.get_guild_stats(ctx.guild.id, days)
        
        embed = discord.Embed(
            title=f"📊 Command Statistics ({days} days)",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="Total Commands", value=str(stats['total_commands']), inline=True)
        embed.add_field(name="Total Usage", value=str(stats['total_usage']), inline=True)
        embed.add_field(name="Success Rate", value=f"{stats['success_rate']}%", inline=True)
        
        if stats['most_used_commands']:
            top_commands = "\n".join([
                f"{i+1}. **{cmd['_id']}** ({cmd['count']} uses)"
                for i, cmd in enumerate(stats['most_used_commands'][:5])
            ])
            embed.add_field(name="🔥 Most Used", value=top_commands, inline=False)
        
        if stats['most_active_users']:
            top_users = "\n".join([
                f"{i+1}. <@{user['_id']}> ({user['count']} uses)"
                for i, user in enumerate(stats['most_active_users'][:5])
            ])
            embed.add_field(name="👥 Most Active", value=top_users, inline=False)
        
        await ctx.respond(embed=embed)
    
    # ==================== Auto-Response Management ====================
    
    @autoresponse.command(description="Create an auto-response")
    @discord.default_permissions(manage_guild=True)
    async def add(
        self,
        ctx: discord.ApplicationContext,
        trigger: str = Option(description="Trigger word/phrase"),
        response: str = Option(description="Response message"),
        match_type: str = Option(
            choices=["exact", "contains", "starts_with", "ends_with"],
            default="contains",
            description="How to match the trigger"
        ),
        case_sensitive: bool = Option(default=False, description="Case sensitive matching")
    ):
        """Create an auto-response"""
        success, message = await self.system.create_auto_response(
            guild_id=ctx.guild.id,
            creator_id=ctx.author.id,
            trigger=trigger,
            response=response,
            match_type=match_type,
            case_sensitive=case_sensitive
        )
        
        if success:
            embed = discord.Embed(
                title="✅ Auto-Response Created",
                description=message,
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="❌ Error",
                description=message,
                color=discord.Color.red()
            )
        
        await ctx.respond(embed=embed)
    
    @autoresponse.command(description="List all auto-responses")
    async def list(self, ctx: discord.ApplicationContext):
        """List all auto-responses"""
        auto_responses = await self.schema.get_all_auto_responses(ctx.guild.id, enabled_only=False)
        
        if not auto_responses:
            embed = discord.Embed(
                title="🤖 Auto-Responses",
                description="No auto-responses configured.",
                color=discord.Color.blue()
            )
            await ctx.respond(embed=embed)
            return
        
        embed = discord.Embed(
            title=f"🤖 Auto-Responses ({len(auto_responses)})",
            color=discord.Color.blue()
        )
        
        for ar in auto_responses[:25]:
            status = "✅" if ar.get("enabled", True) else "❌"
            match_type = ar.get("match_type", "contains")
            uses = ar.get("use_count", 0)
            
            embed.add_field(
                name=f"{status} {ar['trigger']}",
                value=f"Type: {match_type}\nUses: {uses}",
                inline=True
            )
        
        await ctx.respond(embed=embed)
    
    @autoresponse.command(description="Delete an auto-response")
    @discord.default_permissions(manage_guild=True)
    async def remove(
        self,
        ctx: discord.ApplicationContext,
        trigger: str = Option(description="Trigger to remove")
    ):
        """Delete an auto-response"""
        success = await self.schema.delete_auto_response(ctx.guild.id, trigger)
        
        if success:
            embed = discord.Embed(
                title="✅ Auto-Response Removed",
                description=f"Auto-response for `{trigger}` has been removed.",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Auto-response for `{trigger}` not found.",
                color=discord.Color.red()
            )
        
        await ctx.respond(embed=embed)
    
    # ==================== Variable Documentation ====================
    
    @commands.command(description="View available variables")
    async def variables(self, ctx: discord.ApplicationContext):
        """Show all available variables"""
        var_list = self.parser.format_variable_list()
        
        embed = discord.Embed(
            title="📝 Command Variables",
            description=var_list,
            color=discord.Color.blue()
        )
        embed.set_footer(text="Use these in your command responses!")
        
        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(CustomCommandsCog(bot))
