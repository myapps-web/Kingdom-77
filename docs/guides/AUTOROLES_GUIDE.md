# 🎭 Auto-Roles System - Complete Guide

The Auto-Roles System provides three powerful ways to automatically manage roles in your Discord server:

1. **Reaction Roles** - Users get roles by reacting to messages
2. **Level Roles** - Users get roles automatically when reaching specific levels
3. **Join Roles** - Users get roles automatically when joining the server

---

## 📋 Table of Contents

- [Reaction Roles](#-reaction-roles)
  - [Creating Reaction Roles](#creating-reaction-roles)
  - [Managing Reaction Roles](#managing-reaction-roles)
  - [Modes Explained](#modes-explained)
- [Level Roles](#-level-roles)
  - [Setting Up Level Roles](#setting-up-level-roles)
  - [Managing Level Roles](#managing-level-roles)
- [Join Roles](#-join-roles)
  - [Setting Up Join Roles](#setting-up-join-roles)
  - [Managing Join Roles](#managing-join-roles)
- [Configuration](#-configuration)
- [Emoji Guide](#-emoji-guide)
- [Permissions](#-permissions)
- [Troubleshooting](#-troubleshooting)

---

## 🎯 Reaction Roles

Reaction roles allow members to self-assign roles by reacting to a message with specific emojis.

### Creating Reaction Roles

#### Step 1: Create the Reaction Role Message

```
/reactionrole create
```

This opens a modal where you can configure:
- **Title**: The title of the embed (e.g., "Select Your Roles")
- **Description**: Description text (e.g., "React to get your roles!")
- **Mode**: How roles should be assigned
  - `toggle`: Users can add/remove roles by reacting (on/off)
  - `unique`: Users can only have ONE role from this message at a time
  - `multiple`: Users can have multiple roles simultaneously

**Example:**
```
Title: 🎮 Game Roles
Description: React with your favorite games to get the corresponding role!
Mode: multiple
```

#### Step 2: Add Emojis and Roles

After creating the message, add emoji-role pairs:

```
/reactionrole add message_id:<message_id> emoji:<emoji> role:<@role>
```

**Parameters:**
- `message_id`: The ID of the reaction role message
- `emoji`: The emoji to use (see [Emoji Guide](#-emoji-guide))
- `role`: The role to assign (@mention or role ID)

**Example:**
```
/reactionrole add message_id:123456789 emoji:🎮 role:@Gamer
/reactionrole add message_id:123456789 emoji:🎵 role:@Music Lover
/reactionrole add message_id:123456789 emoji:🎨 role:@Artist
```

### Managing Reaction Roles

#### View All Reaction Roles

```
/reactionrole list
```

Shows all reaction role messages with:
- Message ID and channel
- Title and description
- Mode (toggle/unique/multiple)
- Number of roles
- Enabled status

#### Remove an Emoji-Role Pair

```
/reactionrole remove message_id:<message_id> emoji:<emoji>
```

Removes a specific emoji-role combination from a reaction role message.

**Example:**
```
/reactionrole remove message_id:123456789 emoji:🎮
```

#### Refresh a Reaction Role Message

```
/reactionrole refresh message_id:<message_id>
```

Updates the message embed and re-adds all reactions. Useful if:
- Reactions were manually cleared
- The message was edited
- Roles were renamed

#### Delete a Reaction Role

```
/reactionrole delete message_id:<message_id>
```

Completely removes a reaction role message from the database. **Note:** This does not delete the Discord message itself.

### Modes Explained

#### Toggle Mode (`toggle`)
- Users can click emoji to **add** role
- Click again to **remove** role
- Can have multiple roles at once
- **Best for:** Interest roles, notification roles

**Example Use Case:**
```
🔔 Announcements
📰 News Updates
🎉 Events
```

#### Unique Mode (`unique`)
- Users can only have **ONE** role from the message
- Adding a new role **automatically removes** the old one
- **Best for:** Team selection, faction roles, exclusive groups

**Example Use Case:**
```
🔴 Team Red
🔵 Team Blue
🟢 Team Green
```

#### Multiple Mode (`multiple`)
- Users can have **several roles** at once
- Reactions are permanent (click to add, click again to remove)
- **Best for:** Game roles, hobby roles, language roles

**Example Use Case:**
```
🎮 Minecraft
🎯 Valorant
⚔️ League of Legends
🔫 CS:GO
```

---

## 📊 Level Roles

Level roles are automatically assigned when users reach specific levels in the server's leveling system.

### Setting Up Level Roles

#### Add a Level Role

```
/levelrole add level:<number> role:<@role> remove_previous:<true/false>
```

**Parameters:**
- `level`: The level required (e.g., 5, 10, 25)
- `role`: The role to assign (@mention or ID)
- `remove_previous`: Whether to remove the previous level role
  - `true`: Removes lower level roles (e.g., Level 10 removes Level 5 role)
  - `false`: Keeps all level roles (stacking)

**Example (Stacking Roles):**
```
/levelrole add level:5 role:@Bronze remove_previous:false
/levelrole add level:10 role:@Silver remove_previous:false
/levelrole add level:25 role:@Gold remove_previous:false
/levelrole add level:50 role:@Platinum remove_previous:false
```
*User at level 50 will have: Bronze, Silver, Gold, Platinum*

**Example (Replacing Roles):**
```
/levelrole add level:5 role:@Beginner remove_previous:true
/levelrole add level:10 role:@Intermediate remove_previous:true
/levelrole add level:25 role:@Advanced remove_previous:true
/levelrole add level:50 role:@Expert remove_previous:true
```
*User at level 50 will have: Expert only*

### Managing Level Roles

#### View All Level Roles

```
/levelrole list
```

Shows all configured level roles:
- Required level
- Role name
- Remove previous setting
- Enabled status

#### Remove a Level Role

```
/levelrole remove level:<number>
```

Removes the level role configuration for a specific level.

**Example:**
```
/levelrole remove level:10
```

### Integration with Leveling System

Level roles work seamlessly with the existing leveling system:

1. **Automatic Assignment**: When a user levels up, roles are automatically assigned
2. **Error Handling**: If role assignment fails (missing permissions, role deleted), it's logged but doesn't break leveling
3. **Previous Role Removal**: If `remove_previous` is true, the system finds the previous level role and removes it
4. **Performance**: Uses async operations to avoid slowing down the bot

**Example Flow:**
```
User at Level 9 → Gains XP → Levels up to 10 → Level 10 role automatically assigned
```

---

## 👋 Join Roles

Join roles are automatically assigned to new members when they join the server.

### Setting Up Join Roles

#### Add a Join Role

```
/joinrole add role:<@role> target:<all/humans/bots> delay:<seconds>
```

**Parameters:**
- `role`: The role to assign (@mention or ID)
- `target`: Who should get this role
  - `all`: Everyone who joins
  - `humans`: Only human members (not bots)
  - `bots`: Only bot accounts
- `delay`: Seconds to wait before assigning (0 = instant, max 3600)

**Example (Welcome Role):**
```
/joinrole add role:@Member target:humans delay:0
```

**Example (Verification Role with Delay):**
```
/joinrole add role:@Unverified target:humans delay:5
```

**Example (Bot Role):**
```
/joinrole add role:@Bot target:bots delay:0
```

### Managing Join Roles

#### View All Join Roles

```
/joinrole list
```

Shows all configured join roles:
- Role name
- Target type (all/humans/bots)
- Delay in seconds
- Enabled status

#### Remove a Join Role

```
/joinrole remove role:<@role>
```

Removes a join role configuration.

**Example:**
```
/joinrole remove role:@Member
```

### Use Cases

1. **Welcome Roles**: Instant role for all new members
   ```
   /joinrole add role:@Newcomer target:humans delay:0
   ```

2. **Verification System**: Role assigned after a delay
   ```
   /joinrole add role:@Unverified target:humans delay:60
   # (User has 60 seconds to verify before getting Unverified role)
   ```

3. **Bot Identification**: Automatic role for bots
   ```
   /joinrole add role:@Bot target:bots delay:0
   ```

4. **Multiple Roles**: Add several roles to new members
   ```
   /joinrole add role:@Member target:humans delay:0
   /joinrole add role:@Level 0 target:humans delay:0
   ```

---

## ⚙️ Configuration

View the current Auto-Roles configuration and statistics:

```
/autoroles config
```

This shows:
- **Reaction Roles**: Total count, enabled messages, total roles
- **Level Roles**: Total count, enabled roles
- **Join Roles**: Total count, enabled roles
- **Statistics**:
  - Total roles managed
  - Enabled systems
  - Active reaction role messages

**Example Output:**
```
📊 Auto-Roles Configuration for Server Name

🎯 Reaction Roles
Enabled: ✅ Yes
Messages: 5
Total Roles: 23

📊 Level Roles
Enabled: ✅ Yes
Configured Levels: 8
Total Roles: 8

👋 Join Roles
Enabled: ✅ Yes
Configured Roles: 2

📈 Statistics
Total Roles Managed: 33
Active Systems: 3
```

---

## 🎨 Emoji Guide

The Auto-Roles system supports both **Unicode emojis** and **custom Discord emojis**.

### Unicode Emojis

Unicode emojis work directly - just use them as-is:

```
✅ ❌ ⭐ 🎮 🎵 🎨 🎯 🔔 📰 🎉
🔴 🔵 🟢 🟡 🟠 🟣 ⚫ ⚪ 🟤
😀 😃 😄 😁 😆 😅 😂 🤣 😊 😇
```

**Example:**
```
/reactionrole add message_id:123456789 emoji:🎮 role:@Gamer
```

### Custom Discord Emojis

For custom server emojis, you need the emoji's **ID**.

#### Finding Emoji ID (Method 1: Send emoji with backslash)
1. In Discord, type `\:emoji_name:`
2. Send the message
3. Copy the output: `<:emoji_name:123456789012345678>`
4. The number at the end is the emoji ID

**Example:**
```
Type: \:custom_emoji:
Output: <:custom_emoji:987654321012345678>
Use: 987654321012345678
```

#### Finding Emoji ID (Method 2: Developer Mode)
1. Enable Developer Mode in Discord settings
2. Right-click the emoji in emoji picker
3. Click "Copy ID"

#### Using Custom Emojis

**Format 1: Full emoji format**
```
/reactionrole add message_id:123456789 emoji:<:name:123456789> role:@Role
```

**Format 2: Just the ID**
```
/reactionrole add message_id:123456789 emoji:123456789 role:@Role
```

**Format 3: Animated emojis**
```
/reactionrole add message_id:123456789 emoji:<a:name:123456789> role:@Role
```

### Emoji Best Practices

1. **Keep it simple**: Use recognizable emojis that represent the role
2. **Avoid duplicates**: Don't use the same emoji twice in one message
3. **Test custom emojis**: Make sure the emoji is from YOUR server or a server the bot is in
4. **Color coding**: Use colored emojis for team/faction roles (🔴🔵🟢)
5. **Theme consistency**: Use similar emoji styles for a cohesive look

---

## 🔒 Permissions

### Required Bot Permissions

The bot needs these permissions to manage auto-roles:

- **Manage Roles**: To assign/remove roles
- **View Channels**: To read messages and reactions
- **Read Message History**: To fetch reaction role messages
- **Add Reactions**: To add reactions to reaction role messages
- **Send Messages**: To send error messages (optional)
- **Embed Links**: To create reaction role embeds

### Required User Permissions

Users need these permissions to manage auto-roles:

- **Manage Roles**: Required for all auto-roles commands
- **Administrator**: OR administrator permission

### Role Hierarchy

**IMPORTANT**: The bot can only manage roles **below** its highest role in the hierarchy.

**Example:**
```
Server Hierarchy:
1. Owner (Top)
2. Admin
3. Kingdom-77 Bot  ← Bot's highest role
4. Moderator
5. Member
6. Gamer  ← Bot CAN manage
7. @everyone
```

The bot can manage roles 4-7, but **cannot** manage roles 1-2.

**Solution**: Move the bot's role higher in the server settings → Roles.

---

## 🔧 Troubleshooting

### Reaction Roles Not Working

**Problem**: User reacts but doesn't get the role

**Solutions**:
1. **Check bot permissions**: Ensure bot has "Manage Roles" permission
2. **Check role hierarchy**: Bot's role must be higher than the role it's assigning
3. **Check emoji format**: For custom emojis, verify the emoji ID is correct
4. **Check if enabled**: Use `/reactionrole list` to verify the message is enabled
5. **Refresh the message**: Use `/reactionrole refresh` to reset reactions

**Problem**: Reactions disappear from the message

**Solutions**:
1. Use `/reactionrole refresh message_id:<id>` to re-add all reactions
2. Check if someone manually cleared reactions
3. Verify bot has "Add Reactions" permission

### Level Roles Not Working

**Problem**: User levels up but doesn't get the role

**Solutions**:
1. **Check leveling system**: Verify leveling is enabled with `/level settings`
2. **Check role hierarchy**: Bot's role must be higher than level roles
3. **Check bot permissions**: Ensure bot has "Manage Roles" permission
4. **Check level configuration**: Use `/levelrole list` to verify the level role exists
5. **Check logs**: Look for error messages in the bot's console

**Problem**: Previous role not removed with `remove_previous:true`

**Solutions**:
1. Verify that lower level roles are configured correctly
2. Check that the bot has permission to remove the old role
3. Manual roles won't be removed - only level roles the bot assigned

### Join Roles Not Working

**Problem**: New members don't get roles

**Solutions**:
1. **Check bot permissions**: Ensure bot has "Manage Roles" permission
2. **Check role hierarchy**: Bot's role must be higher than join roles
3. **Check target type**: Verify `target` is set correctly (all/humans/bots)
4. **Check delay**: If using a delay, wait for the specified time
5. **Check if enabled**: Use `/joinrole list` to verify the role is enabled

**Problem**: Join role applies to wrong members

**Solutions**:
1. Check the `target` setting: `humans` for users, `bots` for bots, `all` for both
2. Verify you don't have conflicting join roles

### General Issues

**Problem**: Commands don't appear

**Solutions**:
1. Wait a few minutes - slash commands take time to sync
2. Check bot permissions in the channel
3. Try using the command in a different channel
4. Re-invite the bot with proper permissions

**Problem**: "Database connection error"

**Solutions**:
1. Check MongoDB connection in the bot console
2. Verify MongoDB credentials in `.env` file
3. Restart the bot
4. Contact server administrator

**Problem**: "Missing permissions"

**Solutions**:
1. Check both bot AND user permissions
2. Verify role hierarchy
3. Try in a different channel with proper permissions

---

## 📝 Examples & Use Cases

### Example 1: Gaming Community

**Reaction Roles (Multiple Mode):**
```
/reactionrole create
Title: 🎮 Select Your Games
Description: React to get roles for games you play!
Mode: multiple

/reactionrole add message_id:XXX emoji:⛏️ role:@Minecraft
/reactionrole add message_id:XXX emoji:🎯 role:@Valorant
/reactionrole add message_id:XXX emoji:⚔️ role:@League of Legends
/reactionrole add message_id:XXX emoji:🔫 role:@CS:GO
```

**Level Roles (Stacking):**
```
/levelrole add level:5 role:@Newbie remove_previous:false
/levelrole add level:15 role:@Regular remove_previous:false
/levelrole add level:30 role:@Veteran remove_previous:false
/levelrole add level:50 role:@Legend remove_previous:false
```

**Join Role:**
```
/joinrole add role:@Member target:humans delay:0
```

### Example 2: Support Server

**Reaction Roles (Unique Mode):**
```
/reactionrole create
Title: 🎫 Create a Ticket
Description: Select your issue type
Mode: unique

/reactionrole add message_id:XXX emoji:💻 role:@Tech Support Needed
/reactionrole add message_id:XXX emoji:💰 role:@Billing Support Needed
/reactionrole add message_id:XXX emoji:❓ role:@General Question
```

**Join Roles:**
```
/joinrole add role:@User target:humans delay:0
/joinrole add role:@Awaiting Verification target:humans delay:30
```

### Example 3: Role-Play Server

**Reaction Roles (Unique Mode for Factions):**
```
/reactionrole create
Title: ⚔️ Choose Your Faction
Description: You can only be in one faction!
Mode: unique

/reactionrole add message_id:XXX emoji:🔴 role:@Red Kingdom
/reactionrole add message_id:XXX emoji:🔵 role:@Blue Empire
/reactionrole add message_id:XXX emoji:🟢 role:@Green Alliance
```

**Level Roles (Replacing - Ranks):**
```
/levelrole add level:5 role:@Peasant remove_previous:true
/levelrole add level:15 role:@Knight remove_previous:true
/levelrole add level:30 role:@Lord remove_previous:true
/levelrole add level:50 role:@King remove_previous:true
```

**Join Role:**
```
/joinrole add role:@Newcomer target:humans delay:0
```

---

## 📚 Quick Reference

### All Commands

| Command | Description |
|---------|-------------|
| `/reactionrole create` | Create a new reaction role message |
| `/reactionrole add` | Add emoji-role pair to message |
| `/reactionrole remove` | Remove emoji-role pair from message |
| `/reactionrole list` | View all reaction roles |
| `/reactionrole delete` | Delete a reaction role message |
| `/reactionrole refresh` | Refresh message and reactions |
| `/levelrole add` | Add a level role |
| `/levelrole remove` | Remove a level role |
| `/levelrole list` | View all level roles |
| `/joinrole add` | Add a join role |
| `/joinrole remove` | Remove a join role |
| `/joinrole list` | View all join roles |
| `/autoroles config` | View configuration and statistics |

### Reaction Role Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `toggle` | Click to add, click again to remove | Notification roles |
| `unique` | Only one role at a time | Team selection, factions |
| `multiple` | Can have multiple roles | Interest roles, games |

### Join Role Targets

| Target | Description |
|--------|-------------|
| `all` | Everyone who joins (humans + bots) |
| `humans` | Only human members |
| `bots` | Only bot accounts |

---

## 🆘 Support

If you encounter issues not covered in this guide:

1. Check the bot's console logs for detailed error messages
2. Verify all permissions are correctly set
3. Try the `/autoroles config` command to see current settings
4. Contact server administrators or bot support

---

## 📖 Additional Resources

- **Leveling System Guide**: See `LEVELING_GUIDE.md` for leveling system details
- **Moderation Guide**: See `MODERATION_GUIDE.md` for moderation commands
- **Tickets Guide**: See `TICKETS_GUIDE.md` for ticket system setup

---

**Version**: Kingdom-77 Bot v3.6  
**Last Updated**: October 2025  
**Auto-Roles System**: Phase 2.5
