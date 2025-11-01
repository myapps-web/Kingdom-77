# 💬 Dashboard Auto-Messages System - User Guide

**Version:** v4.0.0  
**Last Updated:** November 1, 2025  
**For:** Kingdom-77 Bot Dashboard

---

## 📚 Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Creating Auto-Messages](#creating-messages)
4. [Trigger Types](#trigger-types)
5. [Response Types](#response-types)
6. [Embed Builder](#embed-builder)
7. [Buttons & Dropdowns](#buttons-dropdowns)
8. [Variables System](#variables)
9. [Settings & Permissions](#settings)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)
12. [FAQ](#faq)

---

<a id="introduction"></a>
## 🎯 Introduction

The **Auto-Messages System** creates automatic responses to user triggers in your Discord server. Think of it as an advanced, customizable auto-responder!

### Perfect For:

- 🤖 FAQ responses
- 📚 Information pages
- 🎫 Support menus
- 🎮 Role assignment
- 📢 Announcements
- ✨ Interactive guides

### Key Features

- ✅ **3 Trigger Types** - keyword, button, dropdown
- ✅ **4 Response Types** - text, embed, both, reaction
- ✅ **Nova-Style Embed Builder** - Visual editor with live preview
- ✅ **Buttons** - Up to 25 buttons, 5 styles
- ✅ **Variables** - Dynamic content ({user}, {server}, etc.)
- ✅ **Cooldowns** - Prevent spam (per-user or global)
- ✅ **Permissions** - Role/permission requirements

---

<a id="getting-started"></a>
## 🚀 Getting Started

### Accessing the Auto-Messages Page

1. **Log in** to Kingdom-77 Dashboard
2. **Select your server**
3. **Navigate** to **Auto-Messages** in sidebar
4. You'll see the messages management interface

### Dashboard Overview

The Auto-Messages page displays:

- 📊 **Statistics Cards** (top)
  - Total Messages
  - Triggers Today
  - Responses Sent
  - Most Popular Message

- 💬 **Messages List** (cards view)
  - All your auto-messages
  - Status indicators (Enabled/Disabled)
  - Trigger type badges
  - Quick actions (Edit, Toggle, Delete, Test)

---

<a id="creating-messages"></a>
## 📝 Creating Auto-Messages

### Step-by-Step Guide

#### 1. Open Create Dialog

1. Click **"Create New Message"** button (top right)
2. A 4-tab dialog appears:
   - **Basic** - Core settings
   - **Embed** - Visual embed builder
   - **Buttons** - Add interactive buttons
   - **Settings** - Advanced options

#### 2. Basic Tab - Core Settings

**Message Name** (Required)
- Internal name for your reference
- Not visible to users
- Example: "Welcome FAQ", "Support Menu"

**Trigger Type** (Required)
Choose how users activate this message:

| Type | Description | Example |
|------|-------------|---------|
| 🔤 **Keyword** | Text in messages | "!help", "how to" |
| 🔘 **Button** | Click a button | Role selection menu |
| 📋 **Dropdown** | Select from menu | Support categories |

**Trigger Value** (Required)
- **For Keyword:** The word/phrase to detect
- **For Button:** Button custom_id from another message
- **For Dropdown:** Option value from dropdown

**Response Type** (Required)
Choose what to send when triggered:

| Type | Description | Best For |
|------|-------------|----------|
| 📝 **Text** | Plain text only | Simple responses |
| 🎨 **Embed** | Rich embed only | Beautiful formatted messages |
| ✨ **Both** | Text + Embed | Complex responses |
| 😀 **Reaction** | Add reaction | Acknowledgment |

**Text Response** (Conditional)
- Required if Response Type is Text or Both
- Supports variables (see Variables section)
- Max 2000 characters

**Example Basic Configuration:**
```yaml
Name: FAQ - How to Apply
Trigger Type: Keyword
Trigger Value: !apply
Response Type: Both
Text Response: Here's how to apply for our staff team! 👇
```

---

<a id="trigger-types"></a>
## 🎯 Trigger Types Explained

### 1️⃣ Keyword Triggers

Detects specific words or phrases in messages.

**Features:**
- Case sensitive (optional)
- Exact match (optional)
- Regex support (advanced)
- Multiple keywords (OR logic)

**Examples:**

**Simple Keyword:**
```
Trigger: hello
User types: "hello"
Bot responds: "Hello! 👋"
```

**Multiple Keywords (OR):**
```
Trigger: hello|hi|hey
User types: "hi there"
Bot responds: "Hello! 👋"
```

**Partial Match:**
```
Trigger: help
Exact Match: OFF
User types: "I need help"
Bot responds: "I'm here to help!"
```

**Regex (Advanced):**
```
Trigger: ^!apply\s+(.+)$
User types: "!apply moderator"
Bot responds: Application form for moderator position
```

### 2️⃣ Button Triggers

Responds when user clicks a button.

**How it works:**
1. Create a message with buttons
2. Set custom_id on buttons
3. Create auto-message with button trigger
4. Use same custom_id as trigger value

**Example:**
```yaml
Button custom_id: apply_staff
Trigger Type: Button
Trigger Value: apply_staff
Response: Opens application form
```

### 3️⃣ Dropdown Triggers

Responds when user selects dropdown option.

**How it works:**
1. Create a message with dropdown
2. Set values on dropdown options
3. Create auto-message with dropdown trigger
4. Use same value as trigger value

**Example:**
```yaml
Dropdown option value: support_billing
Trigger Type: Dropdown
Trigger Value: support_billing
Response: Billing support information
```

---

<a id="response-types"></a>
## 💬 Response Types Explained

### 1️⃣ Text Response

Simple plain text message.

**When to use:**
- Quick answers
- Simple information
- No formatting needed

**Example:**
```
To apply for staff, use /apply command in #applications channel!
```

### 2️⃣ Embed Response

Rich, formatted message with embed.

**When to use:**
- Beautiful presentation
- Structured information
- Professional look
- Need images/colors

**Example:**
```yaml
Title: How to Apply
Description: Follow these steps...
Color: Blue (#0099ff)
Fields:
  - Step 1: Go to #applications
  - Step 2: Use /apply command
  - Step 3: Fill out the form
Footer: Applications Team
```

### 3️⃣ Both (Text + Embed)

Combination of text and embed.

**When to use:**
- Text for mention/ping
- Embed for main content
- Maximum impact

**Example:**
```
Text: @User, here's what you asked for! 👇
Embed: [Detailed information with formatting]
```

### 4️⃣ Reaction Response

Adds reaction emoji to user's message.

**When to use:**
- Acknowledgment
- Confirmation
- No text needed

**Example:**
```
User: "I agree to rules"
Bot: ✅ (reaction added)
```

---

<a id="embed-builder"></a>
## 🎨 Embed Builder (Nova-Style)

### Accessing Embed Builder

1. In create/edit dialog, go to **Embed** tab
2. Visual editor with live preview appears

### Embed Components

#### Title
- **What:** Main heading of embed
- **Max Length:** 256 characters
- **Supports:** Plain text and variables
- **Example:** `Welcome to {server}!`

#### Description
- **What:** Main content area
- **Max Length:** 4096 characters
- **Supports:** Text, variables, markdown
- **Example:**
  ```
  Welcome {user.mention}!
  
  Here are the server rules:
  1. Be respectful
  2. No spam
  3. Have fun!
  ```

#### Color
- **What:** Left border color
- **Options:**
  - Color picker (hex codes)
  - Preset colors (Primary, Success, Warning, Danger)
  - Custom hex input
- **Format:** #RRGGBB (e.g., #0099ff)
- **Example:** `#5865F2` (Discord Blurple)

**Preset Colors:**
| Preset | Hex | Use Case |
|--------|-----|----------|
| Primary | #5865F2 | General info |
| Success | #57F287 | Positive messages |
| Warning | #FEE75C | Warnings |
| Danger | #ED4245 | Errors/alerts |
| Dark | #23272A | Dark theme |

#### Thumbnail
- **What:** Small image (top right)
- **Format:** URL to image
- **Size:** Max 80x80 pixels display
- **Example:** User avatar URL

#### Image
- **What:** Large image (bottom)
- **Format:** URL to image
- **Size:** Max 400x300 pixels display
- **Example:** Server banner

#### Author
- **Components:**
  - Author Name (max 256 chars)
  - Author Icon URL (optional)
  - Author URL (optional, makes clickable)
- **Example:**
  ```yaml
  Name: Kingdom-77 Bot
  Icon: https://bot-avatar.png
  URL: https://kingdom77.com
  ```

#### Fields
- **What:** Columns of information
- **Max:** 25 fields per embed
- **Components:**
  - Name (max 256 chars, bold)
  - Value (max 1024 chars)
  - Inline (true = 3 columns, false = full width)
- **Example:**
  ```yaml
  Field 1:
    Name: 📚 Commands
    Value: Use /help to see all commands
    Inline: true
  
  Field 2:
    Name: 🆘 Support
    Value: Join our support server
    Inline: true
  ```

#### Footer
- **Components:**
  - Footer Text (max 2048 chars)
  - Footer Icon URL (optional)
- **Example:**
  ```yaml
  Text: Kingdom-77 Bot • v4.0
  Icon: https://bot-icon.png
  ```

#### Timestamp
- **What:** Shows date/time
- **Options:**
  - Now (current time)
  - Custom (ISO 8601 format)
- **Example:** `2025-11-01T15:30:00Z`

### Live Preview

The **Live Preview** panel shows your embed in real-time!

**Features:**
- ✅ Updates as you type
- ✅ Shows exact Discord appearance
- ✅ Variables replaced with examples
- ✅ Colors rendered accurately
- ✅ Responsive preview

**Tips:**
- Check preview frequently
- Test with different content lengths
- Verify colors look good
- Ensure images load

---

### Example: Complete Embed

```yaml
Title: 🎉 Welcome to Kingdom-77!
Description: |
  Hello {user.mention}! Welcome to our server.
  
  We're glad to have you here. Please take a moment to:
  • Read our rules in #rules
  • Get roles in #roles
  • Introduce yourself in #introductions

Color: #5865F2 (Blurple)

Thumbnail: {user.avatar}

Fields:
  1. Name: 📊 Server Stats
     Value: |
       Members: {membercount}
       Channels: 50+
       Bots: 5
     Inline: true
  
  2. Name: 🔗 Useful Links
     Value: |
       [Website](https://kingdom77.com)
       [Support](https://discord.gg/support)
     Inline: true
  
  3. Name: 🎮 Get Started
     Value: Check out #getting-started for your first steps!
     Inline: false

Footer:
  Text: Joined on {date}
  Icon: Server icon

Timestamp: Now
```

---

<a id="buttons-dropdowns"></a>
## 🔘 Buttons & Dropdowns

### Adding Buttons

Go to **Buttons** tab in create/edit dialog.

#### Button Properties

**Label** (Required)
- Text shown on button
- Max 80 characters
- Example: "Apply Now", "Get Role"

**Custom ID** (Required)
- Unique identifier
- Used for triggering other auto-messages
- Max 100 characters
- Example: "apply_staff", "role_gamer"

**Style** (Required)
Choose from 5 styles:

| Style | Color | Use Case |
|-------|-------|----------|
| Primary | Blurple | Main actions |
| Secondary | Gray | Secondary actions |
| Success | Green | Positive actions |
| Danger | Red | Destructive actions |
| Link | Blue | External URLs |

**URL** (For Link style only)
- External URL to open
- Example: "https://kingdom77.com/apply"

**Emoji** (Optional)
- Unicode emoji or custom emoji ID
- Example: "✅", "🎮", "<:custom:123456>"

**Disabled** (Optional)
- Makes button unclickable
- Shows as grayed out

#### Button Limits

- **Maximum:** 25 buttons per message
- **Per Row:** 5 buttons max
- **Rows:** 5 rows max

#### Button Layout

Buttons auto-arrange in rows:
- 1-5 buttons: 1 row
- 6-10 buttons: 2 rows
- 11-15 buttons: 3 rows
- Etc.

#### Example: Button Row

```yaml
Button 1:
  Label: Apply for Staff
  Custom ID: apply_staff
  Style: Primary
  Emoji: 📝

Button 2:
  Label: Server Rules
  Custom ID: view_rules
  Style: Secondary
  Emoji: 📚

Button 3:
  Label: Get Roles
  Custom ID: role_menu
  Style: Success
  Emoji: 🎭

Button 4:
  Label: Support Server
  Style: Link
  URL: https://discord.gg/support
  Emoji: 🆘
```

---

### Adding Dropdowns

Dropdowns allow users to select from multiple options.

#### Creating a Dropdown

1. Enable dropdown in settings
2. Set placeholder text
3. Add options (min 1, max 25)

#### Dropdown Option Properties

**Label** (Required)
- Text shown in dropdown
- Max 100 characters
- Example: "Billing Support"

**Value** (Required)
- Unique identifier
- Used for triggering
- Max 100 characters
- Example: "support_billing"

**Description** (Optional)
- Additional info shown
- Max 100 characters
- Example: "Help with payments and subscriptions"

**Emoji** (Optional)
- Icon for the option
- Example: "💳"

**Default** (Optional)
- Pre-selected option

#### Example: Support Dropdown

```yaml
Placeholder: Select a support category

Options:
  1. Label: 💳 Billing Support
     Value: support_billing
     Description: Help with payments and subscriptions
  
  2. Label: 🔧 Technical Support
     Value: support_technical
     Description: Bot not working? Get help here
  
  3. Label: 👥 Account Issues
     Value: support_account
     Description: Problems with your account
  
  4. Label: 💡 Feature Request
     Value: support_feature
     Description: Suggest a new feature
  
  5. Label: 🐛 Bug Report
     Value: support_bug
     Description: Report a bug you found
```

---

<a id="variables"></a>
## 🔢 Variables System

Variables are dynamic placeholders replaced with real data.

### Available Variables

| Variable | Replaces With | Example |
|----------|---------------|---------|
| `{user}` | Username | `JohnDoe` |
| `{user.mention}` | User mention | `@JohnDoe` |
| `{user.id}` | User ID | `123456789` |
| `{user.tag}` | Username#discriminator | `JohnDoe#1234` |
| `{user.avatar}` | User avatar URL | `https://...` |
| `{server}` | Server name | `Kingdom-77` |
| `{server.id}` | Server ID | `987654321` |
| `{server.icon}` | Server icon URL | `https://...` |
| `{server.owner}` | Owner name | `OwnerName` |
| `{channel}` | Channel name | `general` |
| `{channel.mention}` | Channel mention | `#general` |
| `{channel.id}` | Channel ID | `111222333` |
| `{membercount}` | Member count | `1,234` |
| `{date}` | Current date | `Nov 1, 2025` |
| `{time}` | Current time | `3:30 PM` |
| `{datetime}` | Date and time | `Nov 1, 2025 3:30 PM` |

### Using Variables

Simply type the variable in text or embed fields:

**Text Example:**
```
Welcome {user.mention} to {server}!
We now have {membercount} members! 🎉
```

**Result:**
```
Welcome @JohnDoe to Kingdom-77!
We now have 1,234 members! 🎉
```

**Embed Example:**
```yaml
Title: User Info for {user.tag}
Description: |
  User ID: {user.id}
  Joined: {date}
  Server: {server}
```

### Variable Tips

- ✅ Use `{user.mention}` to ping users
- ✅ Use `{channel.mention}` to link channels
- ✅ Use `{membercount}` for dynamic stats
- ✅ Test variables with `/automsg test` command
- ❌ Don't use invalid variable names
- ❌ Variables are case-sensitive

---

<a id="settings"></a>
## ⚙️ Settings & Permissions

### Advanced Settings (Settings Tab)

#### Case Sensitive
- **What:** Match trigger case exactly
- **Default:** OFF
- **Example:**
  - ON: "Hello" ≠ "hello"
  - OFF: "Hello" = "hello"

#### Exact Match
- **What:** Trigger must be exact message
- **Default:** OFF
- **Example:**
  - ON: "!help" only (not "!help me")
  - OFF: "!help" matches anywhere in message

#### Delete Trigger Message
- **What:** Delete user's message after trigger
- **Default:** OFF
- **Use Case:** Keep channel clean

#### DM Response
- **What:** Send response in DM instead of channel
- **Default:** OFF
- **Use Case:** Private information

#### Cooldown
- **What:** Time before user can trigger again
- **Options:**
  - None (no cooldown)
  - Per User (individual cooldowns)
  - Global (server-wide cooldown)
- **Duration:** Seconds (1-3600)
- **Example:** 60 seconds = 1 minute

#### Required Roles
- **What:** User must have one of these roles
- **Format:** Select from role list
- **Logic:** OR (user needs any one role)
- **Example:** @Staff OR @Moderator

#### Required Permissions
- **What:** User must have these permissions
- **Format:** Select from permission list
- **Logic:** AND (user needs all permissions)
- **Example:** Manage Messages AND Ban Members

### Permission Checks

The bot checks permissions in this order:
1. ✅ Does user have required roles? (if set)
2. ✅ Does user have required permissions? (if set)
3. ✅ Is cooldown expired? (if set)
4. ✅ Trigger all checks passed → Send response

If any check fails:
- ❌ No response sent
- ❌ Optional: Send error message

---

<a id="best-practices"></a>
## ✨ Best Practices

### Message Design

1. **Keep It Simple**
   - One message = one purpose
   - Clear, concise text
   - Easy to understand

2. **Use Embeds Wisely**
   - Embeds for formatted content
   - Plain text for simple responses
   - Don't over-design

3. **Test Everything**
   - Use `/automsg test` command
   - Test all trigger scenarios
   - Check variable replacements

### Trigger Setup

1. **Choose Appropriate Type**
   - Keywords for FAQs
   - Buttons for interactions
   - Dropdowns for menus

2. **Avoid Conflicts**
   - Don't overlap triggers
   - Use unique custom_ids
   - Test similar keywords

3. **Use Cooldowns**
   - Prevent spam
   - 30-60 seconds recommended
   - Per-user for most cases

### Organization

1. **Naming Convention**
   - Clear, descriptive names
   - Category prefixes
   - Example: "FAQ - Rules", "Support - Billing"

2. **Categories**
   - Group related messages
   - FAQ category
   - Support category
   - Info category

3. **Regular Review**
   - Update outdated info
   - Remove unused messages
   - Check trigger statistics

### Performance

1. **Optimize Triggers**
   - Use exact match when possible
   - Avoid complex regex
   - Limit multiple keywords

2. **Manage Count**
   - Don't create 100s of messages
   - Combine similar messages
   - Archive old messages

---

<a id="troubleshooting"></a>
## 🔧 Troubleshooting

### Common Issues

#### ❌ "Message not triggering"

**Possible Causes:**
- Message is disabled
- Trigger doesn't match
- User doesn't have required role
- Cooldown not expired

**Solutions:**
- Check enabled status (toggle)
- Verify trigger value spelling
- Check required roles/permissions
- Wait for cooldown to expire
- Use `/automsg test` to debug

---

#### ❌ "Variables not replacing"

**Possible Causes:**
- Typo in variable name
- Variable not supported
- Wrong syntax

**Solutions:**
- Check spelling: `{user}` not `{User}`
- Use `/automsg variables` to see list
- Use correct braces: `{}` not `()`

---

#### ❌ "Buttons not working"

**Possible Causes:**
- Custom ID mismatch
- Button trigger message not created
- Bot restarted (interactions expired)

**Solutions:**
- Verify custom_id matches exactly
- Create auto-message for button trigger
- Resend message with buttons after bot restart

---

#### ❌ "Embed not displaying"

**Possible Causes:**
- Missing required fields
- Embed too large
- Invalid URLs

**Solutions:**
- Check title or description is set
- Reduce text length
- Verify image/icon URLs work

---

#### ❌ "Cooldown not working"

**Possible Causes:**
- Cooldown set to 0
- Wrong cooldown type selected

**Solutions:**
- Set cooldown > 0 seconds
- Choose Per User or Global type

---

### Need More Help?

- 📚 Check [Bot Commands Guide](./BOT_COMMANDS.md)
- 💬 Join [Support Server](https://discord.gg/kingdom77)
- 🐛 Report bugs on [GitHub](https://github.com/myapps-web/Kingdom-77/issues)

---

<a id="faq"></a>
## ❓ FAQ

### General Questions

**Q: How many auto-messages can I create?**
A: Depends on your tier:
- Free: 10 messages
- Pro: 50 messages
- Premium: Unlimited

**Q: Can one trigger activate multiple responses?**
A: No, one trigger = one response. Create separate messages for different triggers.

**Q: Do variables work in embeds?**
A: Yes! Variables work in all text fields (title, description, fields, footer).

**Q: Can I edit messages after creation?**
A: Yes! Click Edit button and modify any field.

### Triggers

**Q: Can I use regex in keywords?**
A: Yes, but disable "Exact Match" setting.

**Q: How do button triggers work?**
A: Set custom_id on button, create auto-message with same custom_id as trigger value.

**Q: Can dropdowns have more than 25 options?**
A: No, Discord limit is 25 options per dropdown.

### Responses

**Q: Can I send multiple embeds?**
A: No, one response = one embed. Use fields for multiple sections.

**Q: What's the character limit?**
A: 
- Text: 2000 characters
- Embed description: 4096 characters
- Total embed: 6000 characters

**Q: Can I attach files?**
A: Not yet. Coming in Phase 6!

### Buttons

**Q: How many buttons can I have?**
A: Maximum 25 buttons per message (5 rows × 5 buttons).

**Q: Can buttons have images?**
A: No, only emojis (Unicode or custom).

**Q: What happens when button expires?**
A: Buttons expire after bot restart. Resend the message.

### Technical

**Q: Are responses sent instantly?**
A: Yes, usually < 1 second after trigger.

**Q: Can I see trigger statistics?**
A: Yes! Use `/automsg stats` command or check dashboard.

**Q: Is there a rate limit?**
A: Yes, cooldowns prevent spam. Set per-message cooldowns.

---

## 📋 Quick Reference Card

### Creating a Message
1. Click Create New Message
2. Basic tab: name, trigger, response
3. Embed tab: build embed (optional)
4. Buttons tab: add buttons (optional)
5. Settings tab: configure options
6. Save message

### Trigger Types
- 🔤 Keyword (text in messages)
- 🔘 Button (click button)
- 📋 Dropdown (select option)

### Response Types
- 📝 Text (plain text)
- 🎨 Embed (rich format)
- ✨ Both (text + embed)
- 😀 Reaction (emoji)

### Popular Variables
- `{user}` - Username
- `{user.mention}` - @mention
- `{server}` - Server name
- `{membercount}` - Member count
- `{date}` - Current date

### Button Styles
- Primary (Blurple)
- Secondary (Gray)
- Success (Green)
- Danger (Red)
- Link (Blue, external URL)

---

**🎉 You're now ready to create amazing auto-messages!**

For more guides, check out:
- [Applications Guide](./DASHBOARD_APPLICATIONS_GUIDE.md)
- [Social Integration Guide](./DASHBOARD_SOCIAL_GUIDE.md)
- [API Documentation](./API_DOCUMENTATION.md)

---

*Made with ❤️ by Kingdom-77 Team*  
*Last Updated: November 1, 2025*
