"""
Giveaway System Core - Kingdom-77 Bot
Advanced giveaway system with requirements and auto-end.
"""

import discord
from discord import Member, Guild, TextChannel, Message
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
import random
import asyncio
from motor.motor_asyncio import AsyncIOMotorDatabase

from database.giveaways_schema import GiveawaysSchema


class GiveawaySystem:
    """Advanced Giveaway System"""
    
    def __init__(self, db: AsyncIOMotorDatabase, bot):
        self.db = db
        self.bot = bot
        self.schema = GiveawaysSchema(db)
        self._task = None
    
    def start_auto_end_task(self):
        """Start background task to auto-end giveaways"""
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._auto_end_loop())
    
    async def _auto_end_loop(self):
        """Background loop to check and end giveaways"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                # Get giveaways that need to end
                giveaways = await self.schema.get_ended_giveaways()
                
                for giveaway in giveaways:
                    try:
                        await self.end_giveaway(
                            giveaway["guild_id"],
                            giveaway["message_id"],
                            auto_end=True
                        )
                    except Exception as e:
                        print(f"Error auto-ending giveaway: {e}")
                        
            except Exception as e:
                print(f"Error in auto-end loop: {e}")
    
    async def create_giveaway(
        self,
        guild: Guild,
        channel: TextChannel,
        host: Member,
        prize: str,
        winners_count: int,
        duration: timedelta,
        requirements: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new giveaway"""
        try:
            end_time = datetime.now() + duration
            
            # Create embed
            embed = self._create_giveaway_embed(
                prize,
                host,
                end_time,
                winners_count,
                0,  # initial entries
                requirements,
                description
            )
            
            # Send message
            message = await channel.send("🎉 **GIVEAWAY** 🎉", embed=embed)
            
            # Add reaction
            await message.add_reaction("🎉")
            
            # Save to database
            await self.schema.create_giveaway(
                guild.id,
                channel.id,
                message.id,
                host.id,
                prize,
                winners_count,
                end_time,
                requirements
            )
            
            return {
                "success": True,
                "message_id": message.id,
                "channel_id": channel.id,
                "end_time": end_time
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _create_giveaway_embed(
        self,
        prize: str,
        host: Member,
        end_time: datetime,
        winners_count: int,
        entries_count: int,
        requirements: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None
    ) -> discord.Embed:
        """Create giveaway embed"""
        embed = discord.Embed(
            title=f"🎁 {prize}",
            description=description or f"React with 🎉 to enter!",
            color=discord.Color.gold(),
            timestamp=end_time
        )
        
        # Requirements
        if requirements:
            req_text = []
            
            if requirements.get("min_level"):
                req_text.append(f"• Level {requirements['min_level']}+")
            
            if requirements.get("required_roles"):
                roles = requirements['required_roles']
                if roles:
                    role_mentions = [f"<@&{role_id}>" for role_id in roles]
                    req_text.append(f"• Roles: {', '.join(role_mentions)}")
            
            if requirements.get("min_account_age"):
                days = requirements['min_account_age']
                req_text.append(f"• Account age: {days}+ days")
            
            if requirements.get("min_server_age"):
                days = requirements['min_server_age']
                req_text.append(f"• Server member: {days}+ days")
            
            if req_text:
                embed.add_field(
                    name="📋 Requirements",
                    value="\n".join(req_text),
                    inline=False
                )
        
        # Info
        embed.add_field(
            name="⏰ Ends",
            value=f"<t:{int(end_time.timestamp())}:R>",
            inline=True
        )
        
        embed.add_field(
            name="🏆 Winners",
            value=str(winners_count),
            inline=True
        )
        
        embed.add_field(
            name="👥 Entries",
            value=str(entries_count),
            inline=True
        )
        
        embed.set_footer(text=f"Hosted by {host.name}", icon_url=host.display_avatar.url)
        
        return embed
    
    async def handle_reaction_add(
        self,
        payload: discord.RawReactionActionEvent
    ) -> Optional[str]:
        """Handle reaction add (entry)"""
        try:
            # Check if it's giveaway reaction
            if str(payload.emoji) != "🎉":
                return None
            
            # Get giveaway
            giveaway = await self.schema.get_giveaway(
                payload.guild_id,
                payload.message_id
            )
            
            if not giveaway or giveaway["status"] != "active":
                return None
            
            # Check if already entered
            if await self.schema.has_entered(
                payload.guild_id,
                payload.message_id,
                payload.user_id
            ):
                return "already_entered"
            
            # Get member
            guild = self.bot.get_guild(payload.guild_id)
            if not guild:
                return None
            
            member = guild.get_member(payload.user_id)
            if not member or member.bot:
                return None
            
            # Check if host can enter
            if member.id == giveaway["host_id"]:
                if not giveaway.get("settings", {}).get("allow_host", False):
                    return "host_cannot_enter"
            
            # Check requirements
            requirements = giveaway.get("requirements", {})
            if requirements:
                meets_req, reason = await self._check_requirements(
                    member,
                    requirements
                )
                
                if not meets_req:
                    return reason
            
            # Add entry
            await self.schema.add_entry(
                payload.guild_id,
                payload.message_id,
                payload.user_id
            )
            
            # Update message
            await self._update_giveaway_message(giveaway)
            
            return "success"
            
        except Exception as e:
            print(f"Error handling reaction add: {e}")
            return None
    
    async def handle_reaction_remove(
        self,
        payload: discord.RawReactionActionEvent
    ) -> bool:
        """Handle reaction remove (leave giveaway)"""
        try:
            if str(payload.emoji) != "🎉":
                return False
            
            # Get giveaway
            giveaway = await self.schema.get_giveaway(
                payload.guild_id,
                payload.message_id
            )
            
            if not giveaway or giveaway["status"] != "active":
                return False
            
            # Remove entry
            await self.schema.remove_entry(
                payload.guild_id,
                payload.message_id,
                payload.user_id
            )
            
            # Update message
            await self._update_giveaway_message(giveaway)
            
            return True
            
        except Exception as e:
            print(f"Error handling reaction remove: {e}")
            return False
    
    async def _check_requirements(
        self,
        member: Member,
        requirements: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """Check if member meets giveaway requirements"""
        try:
            # Check level requirement
            if requirements.get("min_level"):
                from database.leveling_schema import LevelingSchema
                level_schema = LevelingSchema(self.db)
                user_data = await level_schema.get_user(member.guild.id, member.id)
                
                if not user_data or user_data.get("level", 0) < requirements["min_level"]:
                    return False, f"need_level_{requirements['min_level']}"
            
            # Check role requirement
            if requirements.get("required_roles"):
                required_role_ids = requirements["required_roles"]
                user_role_ids = [role.id for role in member.roles]
                
                if not any(role_id in user_role_ids for role_id in required_role_ids):
                    return False, "need_role"
            
            # Check account age
            if requirements.get("min_account_age"):
                min_days = requirements["min_account_age"]
                account_age = (datetime.now() - member.created_at.replace(tzinfo=None)).days
                
                if account_age < min_days:
                    return False, f"account_too_new_{min_days}"
            
            # Check server age
            if requirements.get("min_server_age"):
                min_days = requirements["min_server_age"]
                if member.joined_at:
                    server_age = (datetime.now() - member.joined_at.replace(tzinfo=None)).days
                    
                    if server_age < min_days:
                        return False, f"server_too_new_{min_days}"
            
            return True, None
            
        except Exception as e:
            print(f"Error checking requirements: {e}")
            return False, "error"
    
    async def _update_giveaway_message(self, giveaway: Dict[str, Any]) -> None:
        """Update giveaway message"""
        try:
            guild = self.bot.get_guild(giveaway["guild_id"])
            if not guild:
                return
            
            channel = guild.get_channel(giveaway["channel_id"])
            if not channel:
                return
            
            try:
                message = await channel.fetch_message(giveaway["message_id"])
            except discord.NotFound:
                return
            
            # Get host
            host = guild.get_member(giveaway["host_id"])
            if not host:
                host = await self.bot.fetch_user(giveaway["host_id"])
            
            # Get entries count
            entries_count = await self.schema.get_entries_count(
                giveaway["guild_id"],
                giveaway["message_id"]
            )
            
            # Create updated embed
            embed = self._create_giveaway_embed(
                giveaway["prize"],
                host,
                giveaway["end_time"],
                giveaway["winners_count"],
                entries_count,
                giveaway.get("requirements"),
                giveaway.get("description")
            )
            
            await message.edit(embed=embed)
            
        except Exception as e:
            print(f"Error updating giveaway message: {e}")
    
    async def end_giveaway(
        self,
        guild_id: int,
        message_id: int,
        auto_end: bool = False
    ) -> Dict[str, Any]:
        """End giveaway and select winners"""
        try:
            # Get giveaway
            giveaway = await self.schema.get_giveaway(guild_id, message_id)
            
            if not giveaway:
                return {"success": False, "error": "Giveaway not found"}
            
            if giveaway["status"] != "active":
                return {"success": False, "error": "Giveaway already ended"}
            
            # Get entries
            entries = await self.schema.get_entries(guild_id, message_id)
            
            if not entries:
                # No entries
                await self.schema.end_giveaway(guild_id, message_id, [])
                await self._announce_no_winners(giveaway)
                return {"success": True, "winners": [], "message": "No entries"}
            
            # Select winners
            winners_count = min(giveaway["winners_count"], len(entries))
            winner_entries = random.sample(entries, winners_count)
            winner_ids = [entry["user_id"] for entry in winner_entries]
            
            # Save winners
            for winner_id in winner_ids:
                await self.schema.add_winner(
                    guild_id,
                    message_id,
                    winner_id,
                    giveaway["prize"]
                )
            
            # Mark giveaway as ended
            await self.schema.end_giveaway(guild_id, message_id, winner_ids)
            
            # Announce winners
            await self._announce_winners(giveaway, winner_ids)
            
            # Notify winners via DM
            if giveaway.get("settings", {}).get("dm_winners", True):
                await self._notify_winners(giveaway, winner_ids)
            
            return {
                "success": True,
                "winners": winner_ids,
                "entries": len(entries)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _announce_winners(
        self,
        giveaway: Dict[str, Any],
        winner_ids: List[int]
    ) -> None:
        """Announce winners in channel"""
        try:
            guild = self.bot.get_guild(giveaway["guild_id"])
            if not guild:
                return
            
            channel = guild.get_channel(giveaway["channel_id"])
            if not channel:
                return
            
            # Get message
            try:
                message = await channel.fetch_message(giveaway["message_id"])
            except discord.NotFound:
                return
            
            # Create winner embed
            embed = discord.Embed(
                title="🎉 Giveaway Ended! 🎉",
                description=f"**Prize:** {giveaway['prize']}",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            
            # Winners
            winner_mentions = [f"<@{winner_id}>" for winner_id in winner_ids]
            embed.add_field(
                name="🏆 Winners",
                value="\n".join(winner_mentions),
                inline=False
            )
            
            # Update original message
            await message.edit(content="🎉 **GIVEAWAY ENDED** 🎉", embed=embed)
            
            # Send announcement
            ping_winners = giveaway.get("settings", {}).get("ping_winners", True)
            
            if ping_winners and winner_ids:
                winner_pings = " ".join([f"<@{winner_id}>" for winner_id in winner_ids])
                await channel.send(
                    f"🎊 Congratulations {winner_pings}! You won **{giveaway['prize']}**!"
                )
            else:
                await channel.send(
                    f"🎊 Giveaway for **{giveaway['prize']}** has ended!"
                )
                
        except Exception as e:
            print(f"Error announcing winners: {e}")
    
    async def _announce_no_winners(self, giveaway: Dict[str, Any]) -> None:
        """Announce giveaway ended with no winners"""
        try:
            guild = self.bot.get_guild(giveaway["guild_id"])
            if not guild:
                return
            
            channel = guild.get_channel(giveaway["channel_id"])
            if not channel:
                return
            
            try:
                message = await channel.fetch_message(giveaway["message_id"])
            except discord.NotFound:
                return
            
            embed = discord.Embed(
                title="🎉 Giveaway Ended",
                description=f"**Prize:** {giveaway['prize']}\n\nNo one entered the giveaway! 😢",
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
            
            await message.edit(content="🎉 **GIVEAWAY ENDED** 🎉", embed=embed)
            await channel.send("😢 The giveaway ended with no entries.")
            
        except Exception as e:
            print(f"Error announcing no winners: {e}")
    
    async def _notify_winners(
        self,
        giveaway: Dict[str, Any],
        winner_ids: List[int]
    ) -> None:
        """Send DM to winners"""
        try:
            guild = self.bot.get_guild(giveaway["guild_id"])
            if not guild:
                return
            
            for winner_id in winner_ids:
                try:
                    winner = guild.get_member(winner_id)
                    if not winner:
                        winner = await self.bot.fetch_user(winner_id)
                    
                    embed = discord.Embed(
                        title="🎉 You Won a Giveaway! 🎉",
                        description=f"**Prize:** {giveaway['prize']}\n"
                                   f"**Server:** {guild.name}",
                        color=discord.Color.gold()
                    )
                    
                    embed.add_field(
                        name="What's Next?",
                        value="Contact the server moderators to claim your prize!",
                        inline=False
                    )
                    
                    await winner.send(embed=embed)
                    
                    # Mark as notified
                    await self.schema.mark_winner_notified(
                        giveaway["guild_id"],
                        giveaway["message_id"],
                        winner_id
                    )
                    
                except discord.Forbidden:
                    # User has DMs disabled
                    pass
                except Exception as e:
                    print(f"Error notifying winner {winner_id}: {e}")
                    
        except Exception as e:
            print(f"Error in notify winners: {e}")
    
    async def reroll_giveaway(
        self,
        guild_id: int,
        message_id: int,
        count: int = 1
    ) -> Dict[str, Any]:
        """Reroll giveaway winners"""
        try:
            # Get giveaway
            giveaway = await self.schema.get_giveaway(guild_id, message_id)
            
            if not giveaway:
                return {"success": False, "error": "Giveaway not found"}
            
            if giveaway["status"] != "ended":
                return {"success": False, "error": "Giveaway not ended yet"}
            
            # Get entries
            entries = await self.schema.get_entries(guild_id, message_id)
            
            # Get previous winners
            previous_winners = await self.schema.get_winners(guild_id, message_id)
            previous_winner_ids = [w["user_id"] for w in previous_winners]
            
            # Filter out previous winners
            available_entries = [
                e for e in entries 
                if e["user_id"] not in previous_winner_ids
            ]
            
            if not available_entries:
                return {
                    "success": False,
                    "error": "No more eligible participants"
                }
            
            # Select new winners
            new_winners_count = min(count, len(available_entries))
            new_winner_entries = random.sample(available_entries, new_winners_count)
            new_winner_ids = [entry["user_id"] for entry in new_winner_entries]
            
            # Save new winners
            for winner_id in new_winner_ids:
                await self.schema.add_winner(
                    guild_id,
                    message_id,
                    winner_id,
                    giveaway["prize"]
                )
            
            # Announce reroll
            await self._announce_reroll(giveaway, new_winner_ids)
            
            return {
                "success": True,
                "winners": new_winner_ids
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _announce_reroll(
        self,
        giveaway: Dict[str, Any],
        winner_ids: List[int]
    ) -> None:
        """Announce rerolled winners"""
        try:
            guild = self.bot.get_guild(giveaway["guild_id"])
            if not guild:
                return
            
            channel = guild.get_channel(giveaway["channel_id"])
            if not channel:
                return
            
            winner_mentions = [f"<@{winner_id}>" for winner_id in winner_ids]
            
            embed = discord.Embed(
                title="🔄 Giveaway Rerolled!",
                description=f"**Prize:** {giveaway['prize']}",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="🏆 New Winners",
                value="\n".join(winner_mentions),
                inline=False
            )
            
            await channel.send(embed=embed)
            
        except Exception as e:
            print(f"Error announcing reroll: {e}")
    
    async def cancel_giveaway(self, guild_id: int, message_id: int) -> Dict[str, Any]:
        """Cancel active giveaway"""
        try:
            giveaway = await self.schema.get_giveaway(guild_id, message_id)
            
            if not giveaway:
                return {"success": False, "error": "Giveaway not found"}
            
            if giveaway["status"] != "active":
                return {"success": False, "error": "Giveaway not active"}
            
            # Mark as cancelled
            await self.schema.cancel_giveaway(guild_id, message_id)
            
            # Update message
            guild = self.bot.get_guild(guild_id)
            if guild:
                channel = guild.get_channel(giveaway["channel_id"])
                if channel:
                    try:
                        message = await channel.fetch_message(message_id)
                        
                        embed = discord.Embed(
                            title="❌ Giveaway Cancelled",
                            description=f"**Prize:** {giveaway['prize']}\n\n"
                                       "This giveaway has been cancelled.",
                            color=discord.Color.red()
                        )
                        
                        await message.edit(content="❌ **GIVEAWAY CANCELLED** ❌", embed=embed)
                    except:
                        pass
            
            return {"success": True}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
