# 🌐 Dashboard Social Integration - User Guide

**Version:** v4.0.0  
**Last Updated:** November 1, 2025  
**For:** Kingdom-77 Bot Dashboard

---

## 📚 Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Supported Platforms](#platforms)
4. [Adding Social Links](#adding-links)
5. [Managing Links](#managing-links)
6. [Link Limits & Purchasing](#limits-purchasing)
7. [Recent Posts Timeline](#recent-posts)
8. [Platform-Specific Guides](#platform-guides)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)
11. [FAQ](#faq)

---

<a id="introduction"></a>
## 🎯 Introduction

The **Social Integration System** automatically posts updates from your social media accounts to your Discord server. Stay connected with your community across all platforms!

### Perfect For:

- 📺 Content creators (YouTube, Twitch, TikTok)
- 🎮 Streamers and gamers
- 📱 Social media influencers
- 🎨 Artists and designers
- 📢 Community announcements
- 🔔 Multi-platform notifications

### Key Features

- ✅ **7 Platforms Supported** - YouTube, Twitch, Kick, Twitter, Instagram, TikTok, Snapchat
- ✅ **Auto-Posting** - New content automatically posted to Discord
- ✅ **Custom Messages** - Personalize each link's announcement
- ✅ **Link Limits** - Manage multiple links per platform
- ✅ **Purchase System** - Buy additional link slots with credits
- ✅ **Recent Posts** - View timeline of all posts
- ✅ **Toggle On/Off** - Enable/disable links individually

---

<a id="getting-started"></a>
## 🚀 Getting Started

### Accessing the Social Integration Page

1. **Log in** to Kingdom-77 Dashboard
2. **Select your server**
3. **Navigate** to **Social Integration** in sidebar
4. You'll see the social management interface

### Dashboard Overview

The Social Integration page displays:

- 📊 **Link Limits Overview** (top cards)
  - Used Links
  - Purchased Slots
  - Active Links
  - Posts Today

- 🎴 **7 Platform Cards** (main area)
  - YouTube 📺
  - Twitch 🎮
  - Kick ⚡
  - Twitter 🐦
  - Instagram 📷
  - TikTok 🎵
  - Snapchat 👻

- 📰 **Recent Posts Timeline** (bottom)
  - Last 10 posts from all platforms
  - Platform icons
  - External links
  - Timestamps

---

<a id="platforms"></a>
## 🌐 Supported Platforms

### Platform Comparison

| Platform | Content Type | Update Frequency | Link Format |
|----------|-------------|------------------|-------------|
| 📺 **YouTube** | Videos, Shorts, Streams | Every 5 minutes | Channel URL or ID |
| 🎮 **Twitch** | Live Streams | Every 2 minutes | Channel username |
| ⚡ **Kick** | Live Streams | Every 2 minutes | Channel username |
| 🐦 **Twitter** | Tweets, Retweets | Every 3 minutes | @username or profile URL |
| 📷 **Instagram** | Posts, Stories, Reels | Every 10 minutes | Username or profile URL |
| 🎵 **TikTok** | Videos | Every 10 minutes | @username or profile URL |
| 👻 **Snapchat** | Public Stories | Every 15 minutes | Username or profile URL |

### Default Link Limits

| Tier | Links Per Platform | Total Links |
|------|-------------------|-------------|
| **Free** | 1 per platform | 7 max |
| **Pro** | 3 per platform | 21 max |
| **Premium** | 10 per platform | 70 max |

**💡 Tip:** You can purchase additional link slots with credits (200 ❄️ per link)!

---

<a id="adding-links"></a>
## ➕ Adding Social Links

### Step-by-Step Guide

#### 1. Choose Platform

1. Find the platform card you want to add
2. Check remaining links badge
3. Click **"Add Link"** button

#### 2. Fill Link Information

**Platform** (Auto-selected)
- Already selected based on card clicked
- Can change if needed

**Link URL or Username** (Required)
- Enter the URL or username for the account
- See platform-specific formats below

**Discord Channel** (Required)
- Select where to post notifications
- Must have Send Messages permission

**Custom Message** (Optional)
- Personalized text to include with posts
- Supports variables: {platform}, {author}, {title}, {url}
- Max 500 characters

**Role to Mention** (Optional)
- Select a role to ping with posts
- Example: @Everyone, @Notifications, @Subscribers

#### 3. Validate & Save

1. Click **"Validate Link"** to test URL
2. Bot checks if link is valid and accessible
3. If valid, click **"Add Link"**
4. Success message appears
5. Link added to platform card

---

### Platform-Specific Link Formats

#### 📺 YouTube

**Accepted Formats:**
```
Channel URL: https://youtube.com/@channelname
Channel URL: https://youtube.com/c/channelname
Channel ID: https://youtube.com/channel/UCxxxxxxxxx
Direct ID: UCxxxxxxxxx
@Handle: @channelname
```

**Example:**
```
URL: https://youtube.com/@MrBeast
Channel: #announcements
Message: 🎥 New video from {author}: {title}
Role: @Subscribers
```

**What Gets Posted:**
- ✅ New video uploads
- ✅ YouTube Shorts
- ✅ Live streams (when started)
- ✅ Premiere videos

---

#### 🎮 Twitch

**Accepted Formats:**
```
Channel URL: https://twitch.tv/username
Username: username
```

**Example:**
```
URL: https://twitch.tv/ninja
Channel: #streams
Message: 🔴 {author} is now LIVE! {title}
Role: @Live Notifications
```

**What Gets Posted:**
- ✅ Stream goes live
- ✅ Stream title
- ✅ Game/category
- ✅ Viewer count
- ❌ Not posted: Stream ends, offline streams

---

#### ⚡ Kick

**Accepted Formats:**
```
Channel URL: https://kick.com/username
Username: username
```

**Example:**
```
URL: https://kick.com/xqc
Channel: #streams
Message: ⚡ {author} is streaming on Kick!
Role: @Everyone
```

**What Gets Posted:**
- ✅ Stream goes live
- ✅ Stream title
- ✅ Category
- ✅ Thumbnail

---

#### 🐦 Twitter (X)

**Accepted Formats:**
```
Profile URL: https://twitter.com/username
Username: @username
Username: username
```

**Example:**
```
URL: https://twitter.com/elonmusk
Channel: #tweets
Message: 🐦 New tweet from {author}
Role: None
```

**What Gets Posted:**
- ✅ New tweets
- ✅ Retweets (optional)
- ✅ Quote tweets
- ✅ Replies (optional)
- ❌ Not posted: Likes, follows

---

#### 📷 Instagram

**Accepted Formats:**
```
Profile URL: https://instagram.com/username
Username: @username
Username: username
```

**Example:**
```
URL: https://instagram.com/cristiano
Channel: #social
Message: 📷 New post from {author} on Instagram!
Role: @Followers
```

**What Gets Posted:**
- ✅ New posts (photos/videos)
- ✅ Reels
- ✅ Stories (if public account)
- ❌ Not posted: IGTV, Lives

---

#### 🎵 TikTok

**Accepted Formats:**
```
Profile URL: https://tiktok.com/@username
Username: @username
Username: username
```

**Example:**
```
URL: https://tiktok.com/@charlidamelio
Channel: #videos
Message: 🎵 New TikTok from {author}!
Role: None
```

**What Gets Posted:**
- ✅ New video uploads
- ✅ Video title/caption
- ✅ Thumbnail
- ✅ Direct link

---

#### 👻 Snapchat

**Accepted Formats:**
```
Profile URL: https://snapchat.com/add/username
Username: username
```

**Example:**
```
URL: https://snapchat.com/add/djkhaled
Channel: #stories
Message: 👻 New Snap Story from {author}
Role: None
```

**What Gets Posted:**
- ✅ Public Stories
- ✅ Spotlight videos (if public)
- ❌ Not posted: Private snaps, messages

---

<a id="managing-links"></a>
## 🔧 Managing Links

### Viewing Your Links

Each platform card shows:
- **Platform Icon** - Visual identifier
- **Remaining Badge** - Links left (e.g., "2/3 remaining")
- **Links List** - All your links for this platform

### Link Card Information

Each link displays:
- **Author/Channel Name** - Who it's tracking
- **Status Badge** - Active 🟢 or Disabled 🔴
- **Channel** - Where posts go (#channel-name)
- **Actions** - Toggle, Edit, Delete buttons

### Editing a Link

1. Find the link to edit
2. Click **✏️ Edit** button
3. Modify any field:
   - URL/Username
   - Discord channel
   - Custom message
   - Role to mention
4. Click **"Save Changes"**

### Toggling Links

**Enable/Disable** links without deleting:

1. Find the link
2. Click the **Toggle Switch** (on/off)
3. Status changes immediately:
   - 🟢 **Active** - Posts are sent
   - 🔴 **Disabled** - Posts are paused

**Use Cases:**
- Temporarily pause notifications
- Test other links
- Keep link but stop posts

### Deleting Links

**Permanently remove** a link:

1. Click **🗑️ Delete** button
2. Confirmation dialog appears
3. Confirm deletion
4. Link removed from platform
5. Link slot freed up

**⚠️ Warning:** Deletion is permanent and cannot be undone!

---

<a id="limits-purchasing"></a>
## 💰 Link Limits & Purchasing

### Understanding Link Limits

**Link Limits** control how many links you can add per platform.

**Your Current Limits:**
- Check **"Link Limits Overview"** cards at top
- See per-platform limits on each card

### Purchasing Additional Links

**Cost:** 200 ❄️ Credits per link slot

#### How to Purchase

1. **Check Your Balance**
   - View credits in top right corner
   - Need 200 ❄️ per link

2. **Choose Platform**
   - Go to platform card
   - Click **"Purchase Link Slot"** button

3. **Confirm Purchase**
   - Confirmation dialog shows:
     - Current balance
     - Cost (200 ❄️)
     - New balance after purchase
   - Click **"Confirm Purchase"**

4. **Slot Added**
   - 200 ❄️ deducted from balance
   - Limit increased by 1
   - Can now add another link

#### Purchase Examples

**Example 1: YouTube**
```
Current YouTube Links: 3/3 (max reached)
Action: Purchase 1 slot
Cost: 200 ❄️
New Limit: 4 links
Result: Can add 1 more YouTube channel
```

**Example 2: Multiple Platforms**
```
Balance: 1,000 ❄️
Purchase: 2 YouTube + 1 Twitch + 2 Instagram = 5 slots
Cost: 5 × 200 = 1,000 ❄️
New Balance: 0 ❄️
```

### Earning Credits

**Ways to earn credits:**
- 💰 Daily claim (/credits daily)
- 🎁 Giveaways
- 💳 Purchase credit packages
- 🎮 Server activities
- 🏆 Achievements

**Tip:** Save credits for important link slots!

---

<a id="recent-posts"></a>
## 📰 Recent Posts Timeline

### Viewing Recent Posts

The **Recent Posts** section (bottom of page) shows your last 10 posts from all platforms.

### Post Card Information

Each post displays:
- **Platform Icon** - Which platform (📺🎮🐦📷)
- **Author Name** - Who posted
- **Post Title** - Content title/caption
- **Timestamp** - When posted (e.g., "2 hours ago")
- **External Link** - 🔗 Opens original post

### Filtering Posts

**Filter by Platform:**
- Click platform filter dropdown
- Select specific platform or "All"
- Timeline updates instantly

**Filter by Date:**
- Last 24 hours
- Last 7 days
- Last 30 days
- All time

### Post Actions

**Open Original:**
- Click 🔗 **"View Original"** button
- Opens post in new tab on original platform

**Re-post:**
- Click **"Re-post"** button
- Manually send to Discord again

**Delete Post Record:**
- Click **"Delete"** button
- Removes from timeline (doesn't delete original)

---

<a id="platform-guides"></a>
## 📖 Platform-Specific Guides

### 📺 YouTube Setup Guide

1. **Find Channel URL**
   - Go to your YouTube channel
   - Copy URL from address bar
   - Or use @handle from YouTube

2. **Add to Bot**
   - Paste URL in "Add Link" dialog
   - Select notification channel
   - Customize message

3. **What to Expect**
   - New videos posted within 5 minutes
   - Includes video title, thumbnail, description
   - Direct link to video

**Tips:**
- Use @Everyone for important uploads
- Create dedicated #youtube channel
- Test with an upload

---

### 🎮 Twitch Setup Guide

1. **Find Username**
   - Your Twitch username (twitch.tv/USERNAME)
   - Don't include @ symbol

2. **Add to Bot**
   - Enter username or full URL
   - Select #streams channel
   - Add "🔴 LIVE NOW!" message

3. **What to Expect**
   - Live notification within 2 minutes of going live
   - Shows stream title, game, viewer count
   - Direct link to stream

**Tips:**
- Create @Live role for notifications
- Use separate channel for streams
- Test by going live briefly

---

### 🐦 Twitter Setup Guide

1. **Find Profile**
   - Your Twitter handle (@username)
   - Or profile URL

2. **Add to Bot**
   - Enter @username or URL
   - Select #tweets channel
   - Decide if you want retweets included

3. **What to Expect**
   - New tweets posted within 3 minutes
   - Includes tweet text and images
   - Direct link to tweet

**Tips:**
- Disable retweets for cleaner feed
- Use for important announcements only
- Consider rate limits (high-volume accounts)

---

### 📷 Instagram Setup Guide

1. **Find Profile**
   - Your Instagram username
   - Must be public account

2. **Add to Bot**
   - Enter username or profile URL
   - Select #instagram channel
   - Add custom caption

3. **What to Expect**
   - New posts within 10 minutes
   - Includes images and caption
   - Direct link to post

**⚠️ Important:** Account must be public! Private accounts won't work.

---

### 🎵 TikTok Setup Guide

1. **Find Profile**
   - Your TikTok handle (@username)
   - Must be public account

2. **Add to Bot**
   - Enter @username or profile URL
   - Select #tiktok channel
   - Add engaging message

3. **What to Expect**
   - New videos within 10 minutes
   - Includes thumbnail and caption
   - Direct link to video

**Tips:**
- Great for viral content sharing
- Use for clips and highlights
- Engage community with reactions

---

<a id="best-practices"></a>
## ✨ Best Practices

### Channel Organization

1. **Dedicated Channels**
   - Create separate channel for each platform
   - Examples: #youtube, #streams, #tweets
   - Keeps content organized

2. **Channel Permissions**
   - Bot needs Send Messages permission
   - Bot needs Embed Links permission
   - Bot needs Attach Files permission (for images)

3. **Channel Categories**
   - Group social channels together
   - Example: "Social Media" category

### Message Customization

1. **Use Variables**
   - `{author}` - Channel/username
   - `{title}` - Post title
   - `{platform}` - Platform name
   - `{url}` - Direct link

2. **Add Emojis**
   - Match platform theme
   - Make posts visually appealing
   - Example: "🎥 New video from {author}!"

3. **Keep It Short**
   - Brief, exciting messages
   - Let the content speak
   - Don't clutter with too much text

### Role Management

1. **Notification Roles**
   - Create @Live for stream notifications
   - Create @NewVideo for uploads
   - Let users opt-in/out

2. **Don't Spam @Everyone**
   - Use sparingly for important content
   - Consider creating notification roles instead
   - Respect your community

### Performance

1. **Limit Links**
   - Don't add too many (max 3-5 per platform)
   - Quality over quantity
   - Remove inactive accounts

2. **Monitor Posts**
   - Check Recent Posts regularly
   - Ensure notifications are working
   - Fix broken links promptly

3. **Test Before Publishing**
   - Add link to test channel first
   - Verify it works correctly
   - Move to main channel after testing

---

<a id="troubleshooting"></a>
## 🔧 Troubleshooting

### Common Issues

#### ❌ "Link validation failed"

**Possible Causes:**
- Invalid URL format
- Private account (must be public)
- Account doesn't exist
- Platform API issue

**Solutions:**
- Check URL spelling
- Make account public
- Verify account exists
- Try again later

---

#### ❌ "Posts not appearing in Discord"

**Possible Causes:**
- Link is disabled (toggle off)
- Bot doesn't have channel permissions
- No new content posted
- API rate limit reached

**Solutions:**
- Check toggle is ON (🟢)
- Verify bot permissions in channel
- Wait for new content from account
- Check bot status

---

#### ❌ "Cannot purchase link slot"

**Possible Causes:**
- Insufficient credits (need 200 ❄️)
- Already at maximum limit
- Premium tier limit reached

**Solutions:**
- Earn/buy more credits
- Delete unused links
- Upgrade Premium tier

---

#### ❌ "Delay in posting notifications"

**Possible Causes:**
- Normal delay (2-15 minutes depending on platform)
- High server load
- API rate limits

**Solutions:**
- Wait up to 15 minutes for post
- This is normal behavior
- Contact support if >1 hour delay

---

#### ❌ "Duplicate posts"

**Possible Causes:**
- Multiple links for same account
- Bot restarted mid-post
- Platform API issue

**Solutions:**
- Remove duplicate links
- This should auto-resolve
- Report if persistent

---

### Platform-Specific Issues

#### YouTube
- ❌ **Not detecting uploads:** Wait up to 5 minutes, check channel ID
- ❌ **Missing Shorts:** Shorts support may vary by region
- ❌ **Live stream missed:** Live notifications work, but may delay

#### Twitch
- ❌ **Not detecting streams:** Check username spelling, ensure public
- ❌ **False positives:** May post if stream briefly flickers

#### Twitter
- ❌ **Too many tweets:** Consider disabling retweets
- ❌ **Rate limited:** Twitter has strict limits, reduce frequency

#### Instagram
- ❌ **Private account:** Must be public!
- ❌ **Stories not posting:** Stories support limited
- ❌ **Missing reels:** Reel detection may be delayed

---

### Need More Help?

- 📚 Check [Bot Commands Guide](./BOT_COMMANDS.md)
- 💬 Join [Support Server](https://discord.gg/kingdom77)
- 🐛 Report bugs on [GitHub](https://github.com/myapps-web/Kingdom-77/issues)
- 📧 Email: support@kingdom77.com

---

<a id="faq"></a>
## ❓ FAQ

### General Questions

**Q: How many platforms can I connect?**
A: All 7 platforms! Limits are per-platform (e.g., 3 YouTube channels).

**Q: Do I need API keys?**
A: No! We handle all API connections. Just provide URLs.

**Q: What's the update frequency?**
A: Varies by platform:
- Twitch/Kick: 2 minutes
- YouTube/Twitter: 3-5 minutes
- Instagram/TikTok: 10 minutes
- Snapchat: 15 minutes

**Q: Can I use multiple servers?**
A: Yes! Each server has its own links and limits.

### Link Management

**Q: Can I have multiple links for one account?**
A: No, each unique account can only be added once per server.

**Q: What happens if I delete a link?**
A: Posts stop immediately. Link slot is freed. No refund for purchased slots.

**Q: Can I transfer link slots between platforms?**
A: No, purchased slots are platform-specific.

### Posts & Notifications

**Q: Can I customize the embed appearance?**
A: Not yet. Embeds use platform-default design. Coming in Phase 6!

**Q: Can I filter what gets posted?**
A: Limited filtering available (e.g., disable retweets). More options coming.

**Q: Why was my post delayed?**
A: Normal delays vary by platform (2-15 minutes). API rate limits may add delay.

### Credits & Purchasing

**Q: How much does a link slot cost?**
A: 200 ❄️ Credits per slot, any platform.

**Q: Do purchased slots expire?**
A: No! Once purchased, slots are permanent.

**Q: Can I get a refund?**
A: No refunds on link slot purchases.

### Technical

**Q: What if a platform changes their API?**
A: We monitor all platforms and update integration ASAP.

**Q: Are there rate limits?**
A: Yes, platform-specific. Bot handles limits automatically.

**Q: Can I see post history?**
A: Yes! Recent Posts shows last 10 posts. Export coming soon.

---

## 📋 Quick Reference Card

### Adding a Link
1. Choose platform card
2. Click "Add Link"
3. Enter URL/username
4. Select Discord channel
5. Customize message (optional)
6. Add role mention (optional)
7. Save link

### Link Limits
- Free: 1 per platform (7 total)
- Pro: 3 per platform (21 total)
- Premium: 10 per platform (70 total)
- Purchase: 200 ❄️ per additional slot

### Supported Platforms
- 📺 YouTube (videos, streams)
- 🎮 Twitch (streams)
- ⚡ Kick (streams)
- 🐦 Twitter (tweets)
- 📷 Instagram (posts, reels)
- 🎵 TikTok (videos)
- 👻 Snapchat (stories)

### Update Frequencies
- Fast: Twitch, Kick (2 min)
- Medium: YouTube, Twitter (3-5 min)
- Slow: Instagram, TikTok (10 min)
- Very Slow: Snapchat (15 min)

### Variables for Messages
- `{author}` - Channel name
- `{title}` - Post title
- `{platform}` - Platform name
- `{url}` - Direct link

---

**🎉 You're now ready to connect all your social platforms!**

For more guides, check out:
- [Applications Guide](./DASHBOARD_APPLICATIONS_GUIDE.md)
- [Auto-Messages Guide](./DASHBOARD_AUTOMESSAGES_GUIDE.md)
- [API Documentation](./API_DOCUMENTATION.md)

---

*Made with ❤️ by Kingdom-77 Team*  
*Last Updated: November 1, 2025*
