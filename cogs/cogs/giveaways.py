"""
Giveaway Commands - Kingdom-77 Bot
Slash commands for giveaway system.
"""

import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, Literal
from datetime import datetime, timedelta
try:
    import parsedatetime
except ImportError:
    parsedatetime = None

from giveaways.giveaway_system import GiveawaySystem


class GiveawayCommands(commands.Cog):
    """Giveaway System Slash Commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.giveaway_system = GiveawaySystem(bot.db, bot)
        
        # Start auto-end task
        self.giveaway_system.start_auto_end_task()
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """Handle giveaway entry via reaction"""
        if payload.user_id == self.bot.user.id:
            return
        
        result = await self.giveaway_system.handle_reaction_add(payload)
        
        # Notify user if there's an issue
        if result and result != "success":
            try:
                user = self.bot.get_user(payload.user_id)
                if user:
                    messages = {
                        "already_entered": "⚠️ You've already entered this giveaway!",
                        "host_cannot_enter": "⚠️ As the host, you cannot enter your own giveaway!",
                        "need_role": "⚠️ You don't have the required role to enter this giveaway!",
                    }
                    
                    # Handle dynamic messages
                    if result.startswith("need_level_"):
                        level = result.split("_")[2]
                        message = f"⚠️ You need to be level {level} or higher to enter this giveaway!"
                    elif result.startswith("account_too_new_"):
                        days = result.split("_")[3]
                        message = f"⚠️ Your account must be at least {days} days old to enter!"
                    elif result.startswith("server_too_new_"):
                        days = result.split("_")[3]
                        message = f"⚠️ You must be in the server for at least {days} days to enter!"
                    else:
                        message = messages.get(result, "⚠️ You cannot enter this giveaway!")
                    
                    await user.send(message)
            except:
                pass
    
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        """Handle giveaway leave via reaction removal"""
        await self.giveaway_system.handle_reaction_remove(payload)
    
    # Giveaway Command Group
    giveaway_group = app_commands.Group(name="giveaway", description="Giveaway system commands")
    
    @giveaway_group.command(name="create", description="Create a new giveaway")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.describe(
        prize="What are you giving away?",
        duration="Duration (e.g., 1h, 2d, 1w)",
        winners="Number of winners",
        channel="Channel to host the giveaway (optional)",
        description="Additional description (optional)"
    )
    async def giveaway_create(
        self,
        interaction: discord.Interaction,
        prize: str,
        duration: str,
        winners: int = 1,
        channel: Optional[discord.TextChannel] = None,
        description: Optional[str] = None
    ):
        """Create a new giveaway"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Parse duration
            cal = parsedatetime.Calendar()
            time_struct, parse_status = cal.parse(duration)
            
            if parse_status == 0:
                await interaction.followup.send(
                    "❌ Invalid duration format! Use formats like: 1h, 2d, 1w, 30m",
                    ephemeral=True
                )
                return
            
            end_time = datetime(*time_struct[:6])
            duration_delta = end_time - datetime.now()
            
            if duration_delta.total_seconds() < 60:
                await interaction.followup.send(
                    "❌ Duration must be at least 1 minute!",
                    ephemeral=True
                )
                return
            
            # Validate winners count
            if winners < 1:
                await interaction.followup.send(
                    "❌ Number of winners must be at least 1!",
                    ephemeral=True
                )
                return
            
            if winners > 20:
                await interaction.followup.send(
                    "❌ Maximum 20 winners allowed!",
                    ephemeral=True
                )
                return
            
            # Use current channel if none specified
            target_channel = channel or interaction.channel
            
            # Create giveaway
            result = await self.giveaway_system.create_giveaway(
                interaction.guild,
                target_channel,
                interaction.user,
                prize,
                winners,
                duration_delta,
                description=description
            )
            
            if result["success"]:
                embed = discord.Embed(
                    title="✅ Giveaway Created!",
                    description=f"**Prize:** {prize}\n"
                               f"**Channel:** {target_channel.mention}\n"
                               f"**Winners:** {winners}\n"
                               f"**Ends:** <t:{int(result['end_time'].timestamp())}:R>",
                    color=discord.Color.green()
                )
                
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.followup.send(
                    f"❌ Error: {result.get('error', 'Unknown error')}",
                    ephemeral=True
                )
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)
    
    @giveaway_group.command(name="end", description="End a giveaway early")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.describe(message_id="Message ID of the giveaway")
    async def giveaway_end(
        self,
        interaction: discord.Interaction,
        message_id: str
    ):
        """End giveaway early"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            msg_id = int(message_id)
            
            result = await self.giveaway_system.end_giveaway(
                interaction.guild.id,
                msg_id
            )
            
            if result["success"]:
                winners = result.get("winners", [])
                
                embed = discord.Embed(
                    title="✅ Giveaway Ended",
                    description=f"**Winners:** {len(winners)}\n"
                               f"**Entries:** {result.get('entries', 0)}",
                    color=discord.Color.green()
                )
                
                if winners:
                    winner_mentions = [f"<@{w}>" for w in winners]
                    embed.add_field(
                        name="🏆 Winners",
                        value="\n".join(winner_mentions),
                        inline=False
                    )
                
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.followup.send(
                    f"❌ Error: {result.get('error', 'Unknown error')}",
                    ephemeral=True
                )
            
        except ValueError:
            await interaction.followup.send("❌ Invalid message ID!", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)
    
    @giveaway_group.command(name="reroll", description="Reroll giveaway winners")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.describe(
        message_id="Message ID of the giveaway",
        count="Number of new winners to select"
    )
    async def giveaway_reroll(
        self,
        interaction: discord.Interaction,
        message_id: str,
        count: int = 1
    ):
        """Reroll giveaway winners"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            msg_id = int(message_id)
            
            if count < 1 or count > 10:
                await interaction.followup.send(
                    "❌ Count must be between 1 and 10!",
                    ephemeral=True
                )
                return
            
            result = await self.giveaway_system.reroll_giveaway(
                interaction.guild.id,
                msg_id,
                count
            )
            
            if result["success"]:
                winners = result.get("winners", [])
                winner_mentions = [f"<@{w}>" for w in winners]
                
                embed = discord.Embed(
                    title="✅ Giveaway Rerolled",
                    description="New winners have been selected!",
                    color=discord.Color.blue()
                )
                
                embed.add_field(
                    name="🏆 New Winners",
                    value="\n".join(winner_mentions),
                    inline=False
                )
                
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.followup.send(
                    f"❌ Error: {result.get('error', 'Unknown error')}",
                    ephemeral=True
                )
            
        except ValueError:
            await interaction.followup.send("❌ Invalid message ID!", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)
    
    @giveaway_group.command(name="list", description="List active giveaways")
    async def giveaway_list(self, interaction: discord.Interaction):
        """List all active giveaways"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            giveaways = await self.giveaway_system.schema.get_active_giveaways(
                interaction.guild.id
            )
            
            if not giveaways:
                await interaction.followup.send(
                    "📭 No active giveaways in this server.",
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title="🎉 Active Giveaways",
                description=f"Found {len(giveaways)} active giveaway(s)",
                color=discord.Color.gold(),
                timestamp=datetime.now()
            )
            
            for giveaway in giveaways[:10]:  # Limit to 10
                channel = interaction.guild.get_channel(giveaway["channel_id"])
                channel_mention = channel.mention if channel else "Unknown"
                
                embed.add_field(
                    name=f"🎁 {giveaway['prize']}",
                    value=f"**Channel:** {channel_mention}\n"
                          f"**Winners:** {giveaway['winners_count']}\n"
                          f"**Entries:** {giveaway['entries_count']}\n"
                          f"**Ends:** <t:{int(giveaway['end_time'].timestamp())}:R>\n"
                          f"**ID:** `{giveaway['message_id']}`",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)
    
    @giveaway_group.command(name="delete", description="Delete/cancel a giveaway")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.describe(message_id="Message ID of the giveaway")
    async def giveaway_delete(
        self,
        interaction: discord.Interaction,
        message_id: str
    ):
        """Delete giveaway"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            msg_id = int(message_id)
            
            result = await self.giveaway_system.cancel_giveaway(
                interaction.guild.id,
                msg_id
            )
            
            if result["success"]:
                await interaction.followup.send(
                    "✅ Giveaway has been cancelled and deleted.",
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    f"❌ Error: {result.get('error', 'Unknown error')}",
                    ephemeral=True
                )
            
        except ValueError:
            await interaction.followup.send("❌ Invalid message ID!", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)
    
    @giveaway_group.command(name="entries", description="View giveaway entries")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.describe(message_id="Message ID of the giveaway")
    async def giveaway_entries(
        self,
        interaction: discord.Interaction,
        message_id: str
    ):
        """View giveaway entries"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            msg_id = int(message_id)
            
            entries = await self.giveaway_system.schema.get_entries(
                interaction.guild.id,
                msg_id
            )
            
            if not entries:
                await interaction.followup.send(
                    "📭 No entries for this giveaway yet.",
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title="📋 Giveaway Entries",
                description=f"Total Entries: **{len(entries)}**",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            # Show first 25 entries
            entry_list = []
            for i, entry in enumerate(entries[:25], 1):
                user_id = entry["user_id"]
                entered_at = entry["entered_at"]
                entry_list.append(
                    f"{i}. <@{user_id}> - <t:{int(entered_at.timestamp())}:R>"
                )
            
            embed.add_field(
                name="👥 Participants",
                value="\n".join(entry_list) if entry_list else "None",
                inline=False
            )
            
            if len(entries) > 25:
                embed.set_footer(text=f"Showing 25 of {len(entries)} entries")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except ValueError:
            await interaction.followup.send("❌ Invalid message ID!", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)
    
    @giveaway_group.command(name="stats", description="View giveaway statistics")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.describe(days="Number of days to show stats for")
    async def giveaway_stats(
        self,
        interaction: discord.Interaction,
        days: int = 30
    ):
        """View giveaway statistics"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            stats = await self.giveaway_system.schema.get_guild_statistics(
                interaction.guild.id,
                days
            )
            
            embed = discord.Embed(
                title=f"📊 Giveaway Statistics (Last {days} days)",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="🎉 Giveaways",
                value=f"Total: **{stats['total_giveaways']}**\n"
                      f"Active: **{stats['active_giveaways']}**\n"
                      f"Ended: **{stats['ended_giveaways']}**\n"
                      f"Cancelled: **{stats['cancelled_giveaways']}**",
                inline=True
            )
            
            embed.add_field(
                name="👥 Participation",
                value=f"Total Entries: **{stats['total_entries']}**\n"
                      f"Total Winners: **{stats['total_winners']}**\n"
                      f"Avg Entries: **{stats['avg_entries_per_giveaway']:.1f}**",
                inline=True
            )
            
            # Top participants
            if stats['top_participants']:
                top_list = []
                for i, participant in enumerate(stats['top_participants'][:5], 1):
                    user_id = participant['user_id']
                    entries = participant['entries']
                    top_list.append(f"{i}. <@{user_id}> - {entries} entries")
                
                embed.add_field(
                    name="🏆 Top Participants",
                    value="\n".join(top_list),
                    inline=False
                )
            
            embed.set_footer(text=f"Requested by {interaction.user.name}")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)
    
    @giveaway_group.command(name="requirements", description="Set giveaway requirements")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.describe(
        message_id="Message ID of the giveaway",
        min_level="Minimum level required (optional)",
        min_account_age="Minimum account age in days (optional)",
        min_server_age="Minimum server member age in days (optional)",
        required_role="Required role (optional)"
    )
    async def giveaway_requirements(
        self,
        interaction: discord.Interaction,
        message_id: str,
        min_level: Optional[int] = None,
        min_account_age: Optional[int] = None,
        min_server_age: Optional[int] = None,
        required_role: Optional[discord.Role] = None
    ):
        """Set requirements for giveaway"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            msg_id = int(message_id)
            
            # Build requirements dict
            requirements = {}
            
            if min_level is not None:
                requirements["min_level"] = min_level
            
            if min_account_age is not None:
                requirements["min_account_age"] = min_account_age
            
            if min_server_age is not None:
                requirements["min_server_age"] = min_server_age
            
            if required_role is not None:
                requirements["required_roles"] = [required_role.id]
            
            # Update giveaway
            await self.giveaway_system.schema.update_giveaway(
                interaction.guild.id,
                msg_id,
                {"requirements": requirements}
            )
            
            embed = discord.Embed(
                title="✅ Requirements Updated",
                description="Giveaway requirements have been set!",
                color=discord.Color.green()
            )
            
            req_text = []
            if min_level:
                req_text.append(f"• Minimum Level: {min_level}")
            if min_account_age:
                req_text.append(f"• Account Age: {min_account_age} days")
            if min_server_age:
                req_text.append(f"• Server Age: {min_server_age} days")
            if required_role:
                req_text.append(f"• Required Role: {required_role.mention}")
            
            if req_text:
                embed.add_field(
                    name="📋 Requirements",
                    value="\n".join(req_text),
                    inline=False
                )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except ValueError:
            await interaction.followup.send("❌ Invalid message ID!", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)


async def setup(bot):
    await bot.add_cog(GiveawayCommands(bot))
