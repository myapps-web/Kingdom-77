# 🧪 Phase 5.7 Testing Guide - Kingdom-77 Bot v4.0

**Testing Phase:** Pre-Launch Quality Assurance  
**Systems Under Test:** 4 Major Systems (Applications, Auto-Messages, Social Integration, Giveaway)  
**Date:** November 1, 2025

---

## 📋 Testing Overview

### Systems to Test:
1. **Applications System** (2,150 lines, 8 commands, 9 APIs)
2. **Auto-Messages System** (3,700 lines, 12 commands, 9 APIs)
3. **Social Integration** (1,909 lines, 9 commands, 10 APIs)
4. **Giveaway System** (2,200 lines, 10+ commands)
5. **Dashboard Integration** (28 APIs, 3 UI pages)

### Testing Types:
- ✅ Unit Testing (individual functions)
- ✅ Integration Testing (system interactions)
- ✅ End-to-End Testing (full workflows)
- ✅ UI/UX Testing (dashboard pages)
- ✅ Performance Testing (load & speed)

---

## 1️⃣ Applications System Testing

### 🎯 Discord Commands Testing (8 commands)

#### `/application create`
- [ ] **Basic Creation:**
  - [ ] Create form with required fields only
  - [ ] Create form with all optional fields
  - [ ] Test form name validation (length limits)
  - [ ] Test description validation
  
- [ ] **Question Types:**
  - [ ] Add text question (short answer)
  - [ ] Add textarea question (long answer)
  - [ ] Add number question (numeric input)
  - [ ] Add select question (single choice with options)
  - [ ] Add multiselect question (multiple choice)
  - [ ] Add yes_no question (boolean)
  - [ ] Test required vs optional questions
  - [ ] Test question limits (if any)
  
- [ ] **Configuration:**
  - [ ] Set channel ID (valid channel)
  - [ ] Set role ID (valid role for approval)
  - [ ] Set cooldown hours (0, 24, 168)
  - [ ] Set max submissions (0 = unlimited, 1, 10, 100)
  
- [ ] **Validation:**
  - [ ] Missing required fields → Error message
  - [ ] Invalid channel ID → Error message
  - [ ] Invalid role ID → Error message
  - [ ] Duplicate form name → Error message

#### `/application edit`
- [ ] Edit form name
- [ ] Edit description
- [ ] Edit channel ID
- [ ] Edit role ID
- [ ] Edit cooldown
- [ ] Edit max submissions
- [ ] Add new questions
- [ ] Remove existing questions
- [ ] Modify question properties
- [ ] Test validation on edits

#### `/application delete`
- [ ] Delete existing form
- [ ] Confirmation prompt appears
- [ ] Cancel deletion
- [ ] Confirm deletion
- [ ] Verify form removed from database
- [ ] Test deleting non-existent form → Error

#### `/application list`
- [ ] List all forms when multiple exist
- [ ] List when no forms exist → Empty message
- [ ] Verify form details displayed correctly:
  - [ ] Form name
  - [ ] Status (enabled/disabled)
  - [ ] Number of questions
  - [ ] Submission count
  - [ ] Channel mention
  - [ ] Role mention

#### `/application view`
- [ ] View specific form details
- [ ] Display all questions with types
- [ ] Show configuration (cooldown, max submissions)
- [ ] Show statistics (pending, approved, rejected)
- [ ] Test viewing non-existent form → Error

#### `/application toggle`
- [ ] Enable disabled form
- [ ] Disable enabled form
- [ ] Verify status change in list
- [ ] Test disabled form can't receive submissions

#### `/application submit`
- [ ] **Submission Process:**
  - [ ] Modal appears with all questions
  - [ ] Answer all required questions
  - [ ] Submit modal
  - [ ] Confirmation message
  
- [ ] **Validation:**
  - [ ] Missing required answers → Error
  - [ ] Number question with non-numeric input → Error
  - [ ] Select question with invalid option → Error
  
- [ ] **Restrictions:**
  - [ ] Cooldown enforcement (can't submit within cooldown)
  - [ ] Max submissions limit (can't exceed limit)
  - [ ] Disabled form (can't submit)
  
- [ ] **Edge Cases:**
  - [ ] Submit to non-existent form → Error
  - [ ] Multiple submissions (test cooldown)
  - [ ] Exactly at max submissions limit

#### `/application review`
- [ ] **Approval:**
  - [ ] Approve pending submission
  - [ ] Approve with custom reason
  - [ ] Verify role assigned to user
  - [ ] Verify DM sent to user (if configured)
  - [ ] Verify status changed to "approved"
  
- [ ] **Rejection:**
  - [ ] Reject pending submission
  - [ ] Reject with custom reason
  - [ ] Verify DM sent to user
  - [ ] Verify status changed to "rejected"
  
- [ ] **Validation:**
  - [ ] Review non-existent submission → Error
  - [ ] Review already-reviewed submission → Error
  - [ ] Non-admin trying to review → Permission error

#### `/application stats`
- [ ] Display correct counts:
  - [ ] Total submissions
  - [ ] Pending submissions
  - [ ] Approved submissions
  - [ ] Rejected submissions
- [ ] Display per-form breakdown
- [ ] Test with no submissions → Show zeros
- [ ] Verify statistics accuracy

---

### 🔌 API Endpoints Testing (9 endpoints)

#### `GET /api/applications/guilds/{guild_id}/forms`
- [ ] List all forms for guild
- [ ] Filter by status (enabled/disabled)
- [ ] Empty result when no forms
- [ ] Invalid guild_id → 404
- [ ] Missing API key → 401
- [ ] Response format correct (JSON)

#### `POST /api/applications/guilds/{guild_id}/forms`
- [ ] Create form with valid data
- [ ] Validate required fields (name, questions)
- [ ] Invalid data → 400 with error details
- [ ] Duplicate name → 400
- [ ] Created form returned in response
- [ ] Verify in database

#### `PUT /api/applications/guilds/{guild_id}/forms/{form_id}`
- [ ] Update form name
- [ ] Update questions
- [ ] Update configuration
- [ ] Partial update (only some fields)
- [ ] Invalid form_id → 404
- [ ] Invalid data → 400

#### `DELETE /api/applications/guilds/{guild_id}/forms/{form_id}`
- [ ] Delete existing form
- [ ] Form removed from database
- [ ] Associated submissions handling
- [ ] Invalid form_id → 404
- [ ] Already deleted → 404

#### `PATCH /api/applications/guilds/{guild_id}/forms/{form_id}/toggle`
- [ ] Toggle enabled → disabled
- [ ] Toggle disabled → enabled
- [ ] Response includes new status
- [ ] Verify in database

#### `GET /api/applications/guilds/{guild_id}/submissions`
- [ ] List all submissions
- [ ] Filter by status (pending/approved/rejected)
- [ ] Filter by form_id
- [ ] Pagination works (if implemented)
- [ ] Sort by submission date

#### `PATCH /api/applications/submissions/{submission_id}/review`
- [ ] Approve submission (status: approved)
- [ ] Reject submission (status: rejected)
- [ ] Optional reason field
- [ ] Update timestamp
- [ ] Invalid submission_id → 404

#### `GET /api/applications/guilds/{guild_id}/stats`
- [ ] Return accurate statistics:
  - [ ] Total forms
  - [ ] Total submissions
  - [ ] Pending count
  - [ ] Approved count
  - [ ] Rejected count
- [ ] Per-form breakdown
- [ ] Response format correct

#### `GET /api/applications/guilds/{guild_id}/forms/{form_id}`
- [ ] Get single form details
- [ ] Include questions array
- [ ] Include configuration
- [ ] Include statistics
- [ ] Invalid form_id → 404

---

### 🎨 Dashboard UI Testing (`applications/page.tsx` - 683 lines)

#### Page Load
- [ ] Page loads without errors
- [ ] Loading spinner appears during fetch
- [ ] Forms list displayed after load
- [ ] Empty state shown when no forms
- [ ] Responsive design (mobile/tablet/desktop)

#### Forms Tab
- [ ] **Forms Grid:**
  - [ ] All forms displayed as cards
  - [ ] Form name, description visible
  - [ ] Status badge (Active/Disabled)
  - [ ] Statistics (pending, approved, rejected)
  - [ ] Action buttons (View, Edit, Delete, Toggle)
  
- [ ] **Create Form Dialog:**
  - [ ] Click "Create Form" button
  - [ ] Modal opens
  - [ ] Form builder interface loads
  - [ ] Add questions of each type
  - [ ] Question preview updates
  - [ ] Remove question works
  - [ ] Submit form → API call
  - [ ] Success → Form appears in list
  - [ ] Error handling → Error message displayed

#### Submissions Tab
- [ ] **Submissions Table:**
  - [ ] All submissions listed
  - [ ] Filter by status works (pending/all)
  - [ ] User ID, form name, status visible
  - [ ] Submission date formatted correctly
  - [ ] Review button appears for pending
  
- [ ] **Review Dialog:**
  - [ ] Click "Review" button
  - [ ] Dialog opens with submission details
  - [ ] All questions and answers displayed
  - [ ] Approve button works
  - [ ] Reject button works
  - [ ] Reason field (optional)
  - [ ] Success → Submission updated
  - [ ] Table refreshes

#### Interactions
- [ ] **Toggle Form:**
  - [ ] Click toggle button
  - [ ] Status changes immediately
  - [ ] API called
  - [ ] Badge updates (Active ↔ Disabled)
  
- [ ] **Delete Form:**
  - [ ] Click delete button
  - [ ] Confirmation appears
  - [ ] Cancel → No action
  - [ ] Confirm → Form deleted
  - [ ] Form removed from list
  
- [ ] **View Form:**
  - [ ] Click view/edit button
  - [ ] Form details displayed
  - [ ] Questions listed
  - [ ] Configuration shown

#### Error Handling
- [ ] API failure → Error toast/message
- [ ] Network error → Retry option
- [ ] Validation errors → Field highlights
- [ ] Loading states during operations
- [ ] Disable buttons during actions

---

## 2️⃣ Auto-Messages System Testing

### 🎯 Discord Commands Testing (12 commands)

#### `/automessage create`
- [ ] **Basic Setup:**
  - [ ] Message name validation
  - [ ] Trigger type selection (keyword/button/dropdown)
  - [ ] Trigger value input
  - [ ] Response type (text/embed/both)
  
- [ ] **Text Response:**
  - [ ] Set text content
  - [ ] Test message length limits
  - [ ] Special characters handling
  - [ ] Mentions formatting
  
- [ ] **Embed Response:**
  - [ ] Set title
  - [ ] Set description
  - [ ] Set color (hex or int)
  - [ ] Set footer
  - [ ] Set thumbnail URL
  - [ ] Set image URL
  - [ ] Set author name/icon
  - [ ] Set timestamp (true/false)
  
- [ ] **Settings:**
  - [ ] Case sensitive toggle
  - [ ] Exact match toggle
  - [ ] Delete trigger toggle
  - [ ] DM response toggle

#### `/automessage edit`
- [ ] Edit message name
- [ ] Edit trigger type/value
- [ ] Edit response type
- [ ] Edit text content
- [ ] Edit embed fields
- [ ] Edit settings
- [ ] Test validation on changes

#### `/automessage delete`
- [ ] Delete message
- [ ] Confirmation prompt
- [ ] Verify removal from database
- [ ] Test with active triggers

#### `/automessage list`
- [ ] List all messages
- [ ] Show trigger type
- [ ] Show enabled status
- [ ] Show trigger count
- [ ] Empty list handling

#### `/automessage toggle`
- [ ] Enable message
- [ ] Disable message
- [ ] Verify status change
- [ ] Disabled message doesn't trigger

#### `/automessage test`
- [ ] Send test trigger
- [ ] Verify response received
- [ ] Test all trigger types
- [ ] Test all response types

#### `/automessage addbutton`
- [ ] **Add Button:**
  - [ ] Set custom_id
  - [ ] Set label
  - [ ] Set style (primary/secondary/success/danger/link)
  - [ ] Set emoji (optional)
  - [ ] Set URL (for link style)
  - [ ] Set disabled (true/false)
  
- [ ] **Validation:**
  - [ ] Max 25 buttons per message
  - [ ] Duplicate custom_id → Error
  - [ ] Link style requires URL
  - [ ] Non-link style cannot have URL

#### `/automessage removebutton`
- [ ] Remove button by custom_id
- [ ] Verify button removed
- [ ] Test removing non-existent button → Error

#### `/automessage adddropdown`
- [ ] **Add Dropdown:**
  - [ ] Set custom_id
  - [ ] Set placeholder
  - [ ] Set min_values (1-25)
  - [ ] Set max_values (1-25)
  
- [ ] **Add Options:**
  - [ ] Set value
  - [ ] Set label
  - [ ] Set description (optional)
  - [ ] Set emoji (optional)
  - [ ] Set default (true/false)
  - [ ] Max 25 options per dropdown
  
- [ ] **Validation:**
  - [ ] Max 5 dropdowns per message
  - [ ] min_values ≤ max_values
  - [ ] At least 1 option

#### `/automessage removedropdown`
- [ ] Remove dropdown by custom_id
- [ ] Verify dropdown removed
- [ ] Test removing non-existent → Error

#### `/automessage settings`
- [ ] View current settings
- [ ] Update cooldown
- [ ] Update auto-delete timer
- [ ] Update max triggers per user
- [ ] Verify settings applied

#### `/automessage stats`
- [ ] Display total messages
- [ ] Display total triggers
- [ ] Display per-message statistics
- [ ] Display most used messages
- [ ] Test with no data → Show zeros

---

### 🔌 API Endpoints Testing (9 endpoints)

#### `GET /api/automessages/guilds/{guild_id}/messages`
- [ ] List all messages
- [ ] Filter by trigger_type
- [ ] Filter by enabled status
- [ ] Response includes buttons/dropdowns
- [ ] Empty list handling

#### `POST /api/automessages/guilds/{guild_id}/messages`
- [ ] Create message with text response
- [ ] Create message with embed response
- [ ] Create message with both
- [ ] Include buttons
- [ ] Include dropdowns
- [ ] Validate Pydantic models
- [ ] Invalid data → 400

#### `PUT /api/automessages/guilds/{guild_id}/messages/{message_id}`
- [ ] Update message name
- [ ] Update trigger
- [ ] Update response
- [ ] Update buttons array
- [ ] Update dropdowns array
- [ ] Partial updates work

#### `DELETE /api/automessages/guilds/{guild_id}/messages/{message_id}`
- [ ] Delete message
- [ ] Associated triggers cleaned up
- [ ] Invalid message_id → 404

#### `PATCH /api/automessages/guilds/{guild_id}/messages/{message_id}/toggle`
- [ ] Toggle enabled status
- [ ] Response includes new status
- [ ] Verify in database

#### `GET /api/automessages/guilds/{guild_id}/settings`
- [ ] Get current settings
- [ ] Response format correct
- [ ] Default values if not set

#### `PUT /api/automessages/guilds/{guild_id}/settings`
- [ ] Update cooldown
- [ ] Update auto_delete_delay
- [ ] Update max_triggers_per_user
- [ ] Update enabled status
- [ ] Validate settings values

#### `GET /api/automessages/guilds/{guild_id}/stats`
- [ ] Return statistics
- [ ] Total messages
- [ ] Total triggers today/week/month
- [ ] Per-message breakdown
- [ ] Most popular messages

#### `GET /api/automessages/guilds/{guild_id}/messages/{message_id}`
- [ ] Get single message
- [ ] Include full details
- [ ] Include buttons/dropdowns
- [ ] Include statistics
- [ ] Invalid message_id → 404

---

### 🎨 Dashboard UI Testing (`automessages/page.tsx` - 763 lines)

#### Page Load
- [ ] Page loads successfully
- [ ] Messages list fetched
- [ ] Loading state displayed
- [ ] Empty state when no messages
- [ ] Responsive layout

#### Create Message Dialog (4 Tabs)
- [ ] **Basic Tab:**
  - [ ] Message name input
  - [ ] Trigger type selector
  - [ ] Trigger value input
  - [ ] Response type selector
  - [ ] Text response textarea
  - [ ] All fields work correctly
  
- [ ] **Embed Tab:**
  - [ ] Title input
  - [ ] Description textarea
  - [ ] Color picker works
  - [ ] Hex color displays correctly
  - [ ] Thumbnail URL input
  - [ ] Author name input
  - [ ] Footer text input
  - [ ] **Live Preview:**
    - [ ] Preview updates in real-time
    - [ ] Color applies to border
    - [ ] All fields visible in preview
    - [ ] Matches Discord embed style
  
- [ ] **Buttons Tab:**
  - [ ] Add button form
  - [ ] Button label input (max 80 chars)
  - [ ] Custom ID input (max 100 chars)
  - [ ] Style selector (5 options)
  - [ ] "Add Button" creates button
  - [ ] **Button List:**
    - [ ] Shows all added buttons (0/25)
    - [ ] Button style preview correct colors
    - [ ] Remove button works
    - [ ] Buttons persist during dialog
  - [ ] Max 25 buttons enforced
  
- [ ] **Settings Tab:**
  - [ ] Case sensitive toggle
  - [ ] Exact match toggle
  - [ ] Delete trigger toggle
  - [ ] DM response toggle
  - [ ] All toggles work

#### Messages List
- [ ] All messages displayed as cards
- [ ] Message name, trigger type visible
- [ ] Status badge (Active/Disabled)
- [ ] Trigger count statistic
- [ ] Button count (if any)
- [ ] Action buttons work

#### Interactions
- [ ] Toggle message enable/disable
- [ ] Delete message with confirmation
- [ ] View message details
- [ ] Edit message (opens dialog)

#### Error Handling
- [ ] Validation errors displayed
- [ ] API errors shown
- [ ] Loading states during saves
- [ ] Disable submit during processing

---

## 3️⃣ Social Integration Testing

### 🎯 Discord Commands Testing (9 commands)

#### `/social add`
- [ ] **Platform Selection:**
  - [ ] YouTube (RSS feed URL)
  - [ ] Twitch (channel name)
  - [ ] Kick (channel name)
  - [ ] Twitter (username)
  - [ ] Instagram (username)
  - [ ] TikTok (username)
  - [ ] Snapchat (username)
  
- [ ] **Configuration:**
  - [ ] Set notification channel
  - [ ] Set mention role
  - [ ] Set custom message template
  - [ ] Variables: {creator}, {title}, {url}
  
- [ ] **Link Limits:**
  - [ ] Free links available → Success
  - [ ] No free links → Error with purchase option
  - [ ] Verify limit check before adding

#### `/social remove`
- [ ] Remove link by platform + URL
- [ ] Confirmation prompt
- [ ] Link removed from database
- [ ] Free link count restored
- [ ] Test removing non-existent → Error

#### `/social list`
- [ ] List all connected platforms
- [ ] Show platform, URL, status
- [ ] Show channel and role
- [ ] Show post count
- [ ] Empty list → Helpful message

#### `/social toggle`
- [ ] Enable disabled link
- [ ] Disable enabled link
- [ ] Status change confirmed
- [ ] Disabled links don't check posts

#### `/social purchase`
- [ ] **Purchase Flow:**
  - [ ] Select platform
  - [ ] Confirm purchase (200 credits)
  - [ ] Check credits balance first
  - [ ] Insufficient credits → Error
  - [ ] Success → Credits deducted
  - [ ] Purchased link count increased
  
- [ ] **Verification:**
  - [ ] Verify credits deducted in database
  - [ ] Verify limit increased
  - [ ] Transaction logged

#### `/social settings`
- [ ] View current settings
- [ ] Update check interval (minutes)
- [ ] Update max posts per check
- [ ] Update post cooldown
- [ ] Enable/disable entire system

#### `/social stats`
- [ ] Total connected platforms
- [ ] Total posts detected
- [ ] Posts per platform breakdown
- [ ] Recent activity
- [ ] Link limits overview

#### `/social posts`
- [ ] **Recent Posts List:**
  - [ ] Last 10 posts from all platforms
  - [ ] Post title, platform, date
  - [ ] Click to view original post
  - [ ] Sorted by date (newest first)
  
- [ ] **Filter Options:**
  - [ ] Filter by platform
  - [ ] Filter by date range
  - [ ] Pagination (if > 10)

#### `/social limits`
- [ ] **Display for Each Platform:**
  - [ ] Free links available
  - [ ] Purchased links
  - [ ] Used links
  - [ ] Remaining links
  - [ ] Total capacity
  
- [ ] Purchase button if at limit

---

### 🔌 API Endpoints Testing (10 endpoints)

#### `GET /api/social/guilds/{guild_id}/links`
- [ ] List all links
- [ ] Filter by platform
- [ ] Filter by enabled status
- [ ] Response includes statistics
- [ ] Empty array when no links

#### `POST /api/social/guilds/{guild_id}/links`
- [ ] Create link with valid data
- [ ] Check link limits before creation
- [ ] At limit → 400 error
- [ ] Invalid platform → 400
- [ ] Invalid URL → 400
- [ ] Success → Link created

#### `PUT /api/social/guilds/{guild_id}/links/{link_id}`
- [ ] Update URL
- [ ] Update channel_id
- [ ] Update role_id
- [ ] Update custom_message
- [ ] Partial updates work
- [ ] Invalid link_id → 404

#### `DELETE /api/social/guilds/{guild_id}/links/{link_id}`
- [ ] Delete link
- [ ] Restore free link count
- [ ] Link removed from database
- [ ] Invalid link_id → 404

#### `PATCH /api/social/guilds/{guild_id}/links/{link_id}/toggle`
- [ ] Toggle enabled status
- [ ] Response includes new status
- [ ] Verify in database

#### `GET /api/social/guilds/{guild_id}/limits`
- [ ] **Returns for each platform:**
  - [ ] free_links
  - [ ] purchased_links
  - [ ] used_links
  - [ ] remaining_links
- [ ] Accurate calculations
- [ ] Response format correct

#### `POST /api/social/guilds/{guild_id}/purchase`
- [ ] **Purchase Link:**
  - [ ] Specify platform
  - [ ] Check credits (200 required)
  - [ ] Insufficient → 400 error
  - [ ] Success → Credits deducted
  - [ ] purchased_links incremented
  
- [ ] **Verification:**
  - [ ] Credits transaction recorded
  - [ ] Limits updated correctly

#### `GET /api/social/guilds/{guild_id}/posts`
- [ ] List recent posts
- [ ] Limit parameter works (default 10)
- [ ] Platform filter works
- [ ] Sorted by posted_at (desc)
- [ ] Response includes:
  - [ ] platform, title, url
  - [ ] posted_at, channel_name

#### `GET /api/social/guilds/{guild_id}/stats`
- [ ] Total links
- [ ] Total posts
- [ ] Posts per platform
- [ ] Last check timestamp
- [ ] Response format correct

#### `GET /api/social/guilds/{guild_id}/links/{link_id}`
- [ ] Get single link details
- [ ] Include statistics
- [ ] Include recent posts
- [ ] Invalid link_id → 404

---

### 🎨 Dashboard UI Testing (`social/page.tsx` - 596 lines)

#### Page Load
- [ ] Page loads successfully
- [ ] Links fetched
- [ ] Limits fetched
- [ ] Recent posts fetched
- [ ] Loading states shown
- [ ] Responsive design

#### Limits Overview Card
- [ ] Total used displayed
- [ ] Total purchased displayed
- [ ] Active links count
- [ ] Recent posts count
- [ ] Cards with colors (blue, green, purple, orange)

#### Add Link Dialog
- [ ] **Platform Selector:**
  - [ ] All 7 platforms listed
  - [ ] Platform icons and colors correct
  - [ ] Remaining links shown (X remaining)
  - [ ] Platforms with 0 remaining disabled
  
- [ ] **Form Fields:**
  - [ ] URL input (required)
  - [ ] Channel ID input (optional)
  - [ ] Role ID input (optional)
  - [ ] Custom message textarea (optional)
  - [ ] Placeholder shows variable examples
  
- [ ] **Validation:**
  - [ ] URL required → Error
  - [ ] Invalid URL format → Error (optional)
  - [ ] Success → Link added, dialog closes
  - [ ] List refreshes

#### Platform Cards (7 cards)
- [ ] **Card for Each Platform:**
  - [ ] Platform name and icon
  - [ ] Icon color matches platform
  - [ ] Remaining links badge
  - [ ] Used/Total display (X/Y links used)
  - [ ] Links listed if any exist
  
- [ ] **Link Display:**
  - [ ] URL with external link icon
  - [ ] URL truncated if too long
  - [ ] Status badge (Active/Disabled)
  - [ ] Post count shown
  - [ ] Toggle button
  - [ ] Delete button
  
- [ ] **No Links:**
  - [ ] "No links added yet" message
  - [ ] Centered in card
  
- [ ] **Purchase Button:**
  - [ ] Shown only when remaining = 0
  - [ ] "Buy Link (200 Credits)" text
  - [ ] Click → Confirmation dialog
  - [ ] Success → Limits update

#### Recent Posts Card
- [ ] All recent posts listed
- [ ] Platform icon and color
- [ ] Post title with external link
- [ ] Channel/creator name
- [ ] Posted date formatted
- [ ] Click → Opens in new tab
- [ ] Sorted newest first

#### Interactions
- [ ] **Toggle Link:**
  - [ ] Click toggle button
  - [ ] Status changes
  - [ ] Badge updates
  - [ ] API called
  
- [ ] **Delete Link:**
  - [ ] Click delete button
  - [ ] Confirmation prompt
  - [ ] Confirm → Link deleted
  - [ ] Card updates
  - [ ] Limits refresh
  
- [ ] **Purchase Link:**
  - [ ] Click purchase button
  - [ ] Confirmation dialog
  - [ ] Shows cost (200 credits)
  - [ ] Confirm → API call
  - [ ] Success → Limits update
  - [ ] Error if insufficient credits

#### Empty State
- [ ] Shown when no links exist
- [ ] External link icon
- [ ] Message: "No social media links connected yet"
- [ ] "Add Your First Link" button
- [ ] Click → Opens add dialog

#### Error Handling
- [ ] API errors displayed
- [ ] Validation errors shown
- [ ] Loading states during operations
- [ ] Network error handling

---

## 4️⃣ Integration Testing

### Bot ↔ Dashboard Integration
- [ ] **Data Sync:**
  - [ ] Create form in dashboard → Available in bot
  - [ ] Create message in dashboard → Triggers in bot
  - [ ] Add social link in dashboard → Bot monitors it
  - [ ] Changes in dashboard reflect immediately in bot
  
- [ ] **Bi-directional:**
  - [ ] Submit application in bot → Appears in dashboard
  - [ ] Trigger message in bot → Stats update in dashboard
  - [ ] Social post detected by bot → Appears in dashboard

### Database Operations
- [ ] **CRUD Operations:**
  - [ ] Create records via both bot and API
  - [ ] Read records from both interfaces
  - [ ] Update records via both interfaces
  - [ ] Delete records cleanly
  
- [ ] **Data Integrity:**
  - [ ] No orphaned records
  - [ ] Relationships maintained
  - [ ] Cascading deletes work
  - [ ] Validation enforced

### Credits System
- [ ] **Purchase Flow:**
  - [ ] Check credits balance
  - [ ] Deduct 200 credits for social link
  - [ ] Transaction recorded
  - [ ] Balance updates everywhere
  
- [ ] **Insufficient Credits:**
  - [ ] Purchase blocked
  - [ ] Error message displayed
  - [ ] No partial deduction

### Permissions & Security
- [ ] **Discord Permissions:**
  - [ ] Admin commands require admin role
  - [ ] Regular users can't access admin commands
  - [ ] Permission errors handled gracefully
  
- [ ] **API Authentication:**
  - [ ] Missing API key → 401
  - [ ] Invalid API key → 401
  - [ ] Valid key → Access granted
  
- [ ] **Guild Isolation:**
  - [ ] Guild A can't see Guild B's data
  - [ ] Guild IDs validated on all endpoints

---

## 5️⃣ Performance Testing

### Load Testing
- [ ] **High Volume:**
  - [ ] 100+ application forms
  - [ ] 500+ submissions
  - [ ] 100+ auto-messages
  - [ ] 50+ social links
  - [ ] Monitor response times
  
- [ ] **Concurrent Users:**
  - [ ] Multiple users accessing dashboard
  - [ ] Multiple bot commands simultaneously
  - [ ] No race conditions
  - [ ] No deadlocks

### Response Time Benchmarks
- [ ] **API Endpoints:**
  - [ ] List endpoints < 200ms
  - [ ] Create endpoints < 500ms
  - [ ] Update endpoints < 300ms
  - [ ] Delete endpoints < 200ms
  
- [ ] **Dashboard Pages:**
  - [ ] Initial page load < 2s
  - [ ] Subsequent loads < 1s (cached)
  - [ ] Dialog opens < 100ms
  - [ ] Form submissions < 1s
  
- [ ] **Discord Commands:**
  - [ ] Command response < 3s
  - [ ] Defer if needed for long operations
  - [ ] No timeout errors

### Database Performance
- [ ] **Query Optimization:**
  - [ ] Indexes used effectively
  - [ ] Complex queries < 100ms
  - [ ] Aggregation queries < 500ms
  
- [ ] **Connection Pooling:**
  - [ ] Connections reused
  - [ ] No connection leaks
  - [ ] Max connections not exceeded

### Memory & CPU
- [ ] **Resource Usage:**
  - [ ] Memory stable over time
  - [ ] No memory leaks
  - [ ] CPU usage reasonable
  - [ ] Cache working effectively

---

## 6️⃣ User Experience Testing

### Ease of Use
- [ ] **First-Time Setup:**
  - [ ] Clear instructions
  - [ ] Intuitive navigation
  - [ ] Helpful tooltips/hints
  
- [ ] **Common Tasks:**
  - [ ] Create form in < 2 minutes
  - [ ] Create auto-message in < 3 minutes
  - [ ] Add social link in < 1 minute

### Error Messages
- [ ] **User-Friendly:**
  - [ ] Clear error descriptions
  - [ ] Actionable suggestions
  - [ ] No technical jargon
  
- [ ] **Examples:**
  - [ ] "Form name is required" ✅
  - [ ] Not: "ValidationError: field cannot be null" ❌

### Visual Design
- [ ] **Consistency:**
  - [ ] Colors match theme
  - [ ] Icons appropriate
  - [ ] Spacing uniform
  
- [ ] **Accessibility:**
  - [ ] Text readable
  - [ ] Contrast sufficient
  - [ ] Interactive elements clear

---

## 📊 Testing Metrics

### Success Criteria:
- ✅ **0 Critical Bugs** (system-breaking)
- ✅ **< 5 High Priority Bugs** (major features broken)
- ✅ **< 10 Medium Priority Bugs** (minor issues)
- ✅ **< 20 Low Priority Bugs** (cosmetic/edge cases)

### Performance Targets:
- ✅ **API Response:** < 500ms (95th percentile)
- ✅ **Page Load:** < 2s (initial), < 1s (cached)
- ✅ **Command Response:** < 3s
- ✅ **Database Queries:** < 100ms (simple), < 500ms (complex)

### Coverage Goals:
- ✅ **Command Coverage:** 100% (all 40+ commands tested)
- ✅ **API Coverage:** 100% (all 28 endpoints tested)
- ✅ **UI Coverage:** 100% (all 3 pages tested)
- ✅ **Integration Scenarios:** 100% (all workflows tested)

---

## 🐛 Bug Tracking

### Bug Report Template:
```
**Title:** Brief description
**Severity:** Critical / High / Medium / Low
**Component:** Applications / Auto-Messages / Social / Giveaway / Dashboard
**Steps to Reproduce:**
1. Step 1
2. Step 2
3. Step 3

**Expected:** What should happen
**Actual:** What actually happens
**Screenshots:** (if applicable)
**Environment:** Production / Staging / Development
**Fixed:** Yes / No
```

---

## ✅ Testing Completion Checklist

### Before Declaring "Testing Complete":
- [ ] All commands tested (40+)
- [ ] All API endpoints tested (28)
- [ ] All UI pages tested (3)
- [ ] Integration scenarios tested
- [ ] Performance benchmarks met
- [ ] No critical bugs remaining
- [ ] High priority bugs addressed
- [ ] Test results documented
- [ ] Bug fixes verified
- [ ] Regression testing completed

---

## 🚀 Ready for Launch When:
- ✅ Testing 100% complete
- ✅ < 5 non-critical bugs remaining
- ✅ Performance targets met
- ✅ Documentation complete
- ✅ Team sign-off received

---

**Kingdom-77 Bot v4.0 - Quality Assured! 🧪✅**
