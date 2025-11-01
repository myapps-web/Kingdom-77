# 📝 Dashboard Applications System - User Guide

**Version:** v4.0.0  
**Last Updated:** November 1, 2025  
**For:** Kingdom-77 Bot Dashboard

---

## 📚 Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Creating Application Forms](#creating-forms)
4. [Managing Questions](#managing-questions)
5. [Reviewing Submissions](#reviewing-submissions)
6. [Statistics & Analytics](#statistics)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#faq)

---

<a id="introduction"></a>
## 🎯 Introduction

The **Applications System** allows you to create custom application forms for your Discord server. Perfect for:

- 📋 Staff applications
- 🎮 Team recruitment
- 🎫 Event registration
- 👥 Community applications
- 📝 Any custom forms you need!

### Key Features

- ✅ **6 Question Types** - text, textarea, number, select, multiselect, yes/no
- ✅ **Auto-Role Assignment** - Automatically assign roles on approval
- ✅ **Review System** - Approve/reject with reasons
- ✅ **Notifications** - Auto-DM applicants on status changes
- ✅ **Statistics** - Track approval rates and response times
- ✅ **Easy Management** - Create, edit, and delete forms easily

---

<a id="getting-started"></a>
## 🚀 Getting Started

### Accessing the Applications Page

1. **Log in** to the Kingdom-77 Dashboard
2. **Select your server** from the server selector
3. **Navigate** to **Applications** in the sidebar
4. You'll see two tabs:
   - **Forms** - Manage your application forms
   - **Submissions** - Review user submissions

### Dashboard Overview

The Applications page displays:

- 📊 **Statistics Cards** (top)
  - Total Submissions
  - Pending Reviews
  - Approved Applications
  - Rejected Applications

- 📋 **Forms List** (Forms tab)
  - All your application forms
  - Status indicators (Open/Closed)
  - Quick actions (Edit, Delete)

- 📥 **Submissions Table** (Submissions tab)
  - All received submissions
  - Filter by status
  - Review actions

---

<a id="creating-forms"></a>
## 📝 Creating Application Forms

### Step-by-Step Guide

#### 1. Open Create Form Dialog

1. Go to the **Forms** tab
2. Click **"Create New Form"** button (top right)
3. A dialog with form builder will appear

#### 2. Fill Basic Information

**Form Title** (Required)
- Enter a clear, descriptive title
- Example: "Staff Application", "Event Registration"
- Max 100 characters

**Form Description** (Optional)
- Describe the purpose of the application
- Provide instructions for applicants
- Max 500 characters

**Auto-Role on Approval** (Optional)
- Select a role to assign automatically when approved
- Useful for staff positions or member tiers

**Example:**
```
Title: Staff Application
Description: Apply to join our staff team! Please answer all questions honestly.
Auto-Role: @Staff Member
```

#### 3. Add Questions

Click **"Add Question"** to add a new question to your form.

For each question, configure:

- **Question Text** - The question to ask (required)
- **Question Type** - Choose from 6 types (required)
- **Required** - Toggle if answer is mandatory

**Available Question Types:**

| Type | Description | Best For |
|------|-------------|----------|
| 📝 **Text** | Short text input (1 line) | Name, Discord tag, short answers |
| 📄 **Textarea** | Long text input (multiple lines) | Detailed answers, experience, bio |
| 🔢 **Number** | Numeric input only | Age, hours available, years of experience |
| 📋 **Select** | Dropdown (single choice) | Timezone, position applying for |
| ☑️ **Multiselect** | Multiple checkboxes | Skills, languages spoken, interests |
| ✅ **Yes/No** | Boolean choice | Agreement, availability, eligibility |

#### 4. Configure Question Options

**For Select & Multiselect types:**

- Click **"Add Option"**
- Enter option text
- Add multiple options (min 2, max 10)

**Example Select Question:**
```
Question: Which position are you applying for?
Type: Select
Options:
  - Moderator
  - Admin
  - Developer
  - Designer
```

**Example Multiselect Question:**
```
Question: Which languages do you speak?
Type: Multiselect
Options:
  - English
  - Arabic
  - French
  - Spanish
  - Other
```

#### 5. Reorder Questions

- Use **↑ Up** and **↓ Down** arrows to reorder
- Or drag and drop questions (if enabled)
- Questions appear in this order to applicants

#### 6. Remove Questions

- Click **🗑️ Delete** icon next to question
- Confirmation dialog will appear
- This cannot be undone

#### 7. Save Your Form

1. Review all questions and settings
2. Click **"Save Form"** button
3. Success message will appear
4. Form is now live and accepting submissions!

---

### 📋 Example: Complete Staff Application Form

```yaml
Form Title: Staff Application 2025
Description: |
  Apply to join our moderation team!
  Requirements:
  - Must be 16+ years old
  - Active in server for 30+ days
  - Available at least 10 hours/week

Auto-Role: @Staff Applicant

Questions:
  1. What is your full Discord username?
     Type: Text
     Required: Yes

  2. How old are you?
     Type: Number
     Required: Yes

  3. What position are you applying for?
     Type: Select
     Options: [Moderator, Admin, Support]
     Required: Yes

  4. Why do you want to join our staff team?
     Type: Textarea
     Required: Yes

  5. How many hours per week can you dedicate?
     Type: Number
     Required: Yes

  6. Which languages do you speak fluently?
     Type: Multiselect
     Options: [English, Arabic, French, Spanish, Other]
     Required: Yes

  7. Do you have previous moderation experience?
     Type: Yes/No
     Required: Yes

  8. If yes, please describe your experience:
     Type: Textarea
     Required: No

  9. Are you available for voice interviews?
     Type: Yes/No
     Required: Yes

  10. Do you agree to our staff guidelines?
      Type: Yes/No
      Required: Yes
```

---

<a id="managing-questions"></a>
## 🔧 Managing Questions

### Editing Existing Questions

1. Click **Edit** button on the form
2. Find the question to edit
3. Modify question text, type, or settings
4. Click **"Update Question"**
5. Save the form

**Note:** Changing question type will reset any existing answers for that question.

### Question Validation

The system automatically validates:

- ✅ Question text is not empty
- ✅ Select/Multiselect have at least 2 options
- ✅ No duplicate option texts
- ✅ Required questions are marked

### Question Limits

- **Maximum Questions:** 20 per form
- **Maximum Options:** 10 per Select/Multiselect
- **Question Text:** Max 500 characters
- **Option Text:** Max 100 characters

---

<a id="reviewing-submissions"></a>
## 📥 Reviewing Submissions

### Viewing Submissions

1. Go to **Submissions** tab
2. See all submissions in a table format

**Table Columns:**
- **Applicant** - Discord username
- **Form** - Which form they submitted
- **Submitted** - Date and time
- **Status** - Pending/Approved/Rejected
- **Actions** - View/Review buttons

### Filtering Submissions

Use the filter dropdown to show:
- **All** - Show all submissions
- **Pending** - Only pending reviews
- **Approved** - Only approved applications
- **Rejected** - Only rejected applications

### Reviewing a Submission

#### 1. Open Submission

1. Click **"View"** or **"Review"** button
2. Review dialog opens showing:
   - Applicant information
   - All questions and answers
   - Submission timestamp
   - Current status

#### 2. Review Answers

Carefully read through all answers:
- Check for completeness
- Verify requirements are met
- Assess quality of responses

#### 3. Make a Decision

**To Approve:**
1. Click **"Approve"** button (green)
2. Optional: Add approval note
3. Confirm approval
4. Applicant receives DM notification
5. Auto-role assigned (if configured)

**To Reject:**
1. Click **"Reject"** button (red)
2. **Required:** Enter rejection reason
3. Confirm rejection
4. Applicant receives DM with reason

#### 4. Submission Status Updates

After review, submission status changes:
- **Pending** → **Approved** ✅
- **Pending** → **Rejected** ❌

### Notifications

Applicants automatically receive DM notifications:

**Approval DM:**
```
✅ Application Approved

Your application for "Staff Application" has been approved!

Approved by: @ModeratorName
Note: Welcome to the team!

You have been assigned the @Staff Member role.
```

**Rejection DM:**
```
❌ Application Rejected

Your application for "Staff Application" has been rejected.

Reason: We require at least 6 months of moderation experience.

Reviewed by: @ModeratorName

You may re-apply after 30 days.
```

---

<a id="statistics"></a>
## 📊 Statistics & Analytics

### Dashboard Statistics

**Statistics Cards** (top of page):

1. **Total Submissions**
   - Count of all submissions received
   - All time total

2. **Pending Reviews**
   - Submissions awaiting review
   - Action needed

3. **Approved Applications**
   - Successfully approved submissions
   - Percentage of total

4. **Rejected Applications**
   - Rejected submissions
   - Percentage of total

### Form Statistics

View detailed stats for each form:

1. Click **"Stats"** button on form
2. See form-specific metrics:
   - Total submissions
   - Approval rate (%)
   - Rejection rate (%)
   - Average response time
   - Most common answers
   - Submission timeline

### Approval Rate Calculation

```
Approval Rate = (Approved / Total Reviewed) × 100%

Example:
- Total Submissions: 100
- Approved: 60
- Rejected: 30
- Pending: 10
- Approval Rate: 60 / (60 + 30) = 66.7%
```

### Export Data

Export submissions to:
- **CSV** - For spreadsheet analysis
- **JSON** - For custom processing
- **PDF** - For reports

---

<a id="best-practices"></a>
## ✨ Best Practices

### Form Design

1. **Keep it Focused**
   - Only ask necessary questions
   - 5-10 questions is optimal
   - Too many questions discourage applicants

2. **Clear Questions**
   - Be specific and unambiguous
   - Avoid double-barreled questions
   - Use simple language

3. **Logical Order**
   - Start with basic information
   - Group related questions
   - Save complex questions for later

4. **Use Appropriate Types**
   - Text for short answers
   - Textarea for detailed responses
   - Select for limited choices
   - Yes/No for binary decisions

### Review Process

1. **Review Promptly**
   - Aim to review within 24-48 hours
   - Set up review notifications
   - Consider multiple reviewers

2. **Be Consistent**
   - Use same criteria for all applicants
   - Document your requirements
   - Train your review team

3. **Provide Feedback**
   - Always explain rejections
   - Be constructive and helpful
   - Encourage re-application if appropriate

4. **Track Metrics**
   - Monitor approval rates
   - Review response times
   - Identify bottlenecks

### Security & Privacy

1. **Sensitive Data**
   - Don't ask for passwords
   - Avoid unnecessary personal info
   - Comply with privacy laws

2. **Access Control**
   - Limit who can review submissions
   - Use role permissions
   - Audit review actions

3. **Data Retention**
   - Archive old submissions
   - Delete expired data
   - Backup important data

---

<a id="troubleshooting"></a>
## 🔧 Troubleshooting

### Common Issues

#### ❌ "Cannot create form"

**Possible Causes:**
- Reached form limit (check Premium tier)
- Missing required fields
- Invalid question configuration

**Solutions:**
- Delete unused forms
- Upgrade Premium tier
- Check all required fields filled
- Ensure Select questions have options

---

#### ❌ "Submission not appearing"

**Possible Causes:**
- Form is closed
- User doesn't have permission
- Network issue

**Solutions:**
- Check form status (Open/Closed)
- Verify user permissions
- Refresh dashboard
- Check bot is online

---

#### ❌ "Cannot review submission"

**Possible Causes:**
- Insufficient permissions
- Submission already reviewed
- Network issue

**Solutions:**
- Check your role permissions
- Refresh page
- Check if already approved/rejected
- Contact admin

---

#### ❌ "Auto-role not assigned"

**Possible Causes:**
- Bot doesn't have Manage Roles permission
- Role is higher than bot's role
- Role no longer exists

**Solutions:**
- Give bot Manage Roles permission
- Move bot's role higher in hierarchy
- Update form with valid role
- Check role still exists

---

#### ❌ "DM notification not sent"

**Possible Causes:**
- User has DMs disabled
- User blocked the bot
- User left the server

**Solutions:**
- Inform users to enable DMs
- Post announcement in channel
- Cannot send if DMs disabled

---

### Need More Help?

- 📚 Check [Bot Commands Guide](./BOT_COMMANDS.md)
- 💬 Join our [Support Server](https://discord.gg/kingdom77)
- 🐛 Report bugs on [GitHub](https://github.com/myapps-web/Kingdom-77/issues)
- 📧 Email: support@kingdom77.com

---

<a id="faq"></a>
## ❓ FAQ

### General Questions

**Q: How many forms can I create?**
A: Depends on your tier:
- Free: 3 forms
- Pro: 10 forms
- Premium: Unlimited

**Q: Can users submit multiple times?**
A: No, each user can only submit once per form. They must wait for review before re-applying.

**Q: How long are submissions stored?**
A: Permanently, unless you delete the form or manually delete submissions.

**Q: Can I edit a form after submissions?**
A: Yes, but changing question types may affect existing submissions.

### Question Types

**Q: What's the difference between Text and Textarea?**
A: 
- **Text** = Single line, short answers (e.g., name)
- **Textarea** = Multiple lines, long answers (e.g., essay)

**Q: How many options can Select have?**
A: Minimum 2, maximum 10 options.

**Q: Can I have conditional questions?**
A: Not yet. This feature is planned for Phase 6.

### Review Process

**Q: Can I have multiple reviewers?**
A: Yes! Any user with review permissions can review submissions.

**Q: Can I unreview a submission?**
A: No, reviews are final. Consider carefully before approving/rejecting.

**Q: Can applicants appeal rejections?**
A: Not automatically. Set up a manual appeal process if needed.

### Technical

**Q: Is data encrypted?**
A: Yes, all data is encrypted in transit (HTTPS) and at rest (MongoDB encryption).

**Q: Can I export all submissions?**
A: Yes, use the Export feature to download as CSV, JSON, or PDF.

**Q: Does this work with Discord modals?**
A: Yes! Users submit via Discord's native modal interface.

---

## 📋 Quick Reference Card

### Creating a Form
1. Forms tab → Create New Form
2. Add title & description
3. Add questions (6 types available)
4. Configure auto-role (optional)
5. Save form

### Reviewing Submissions
1. Submissions tab → Filter by status
2. Click View on submission
3. Review answers
4. Approve or Reject (with reason)
5. Applicant receives DM

### Question Types
- 📝 Text (short)
- 📄 Textarea (long)
- 🔢 Number
- 📋 Select (dropdown)
- ☑️ Multiselect (checkboxes)
- ✅ Yes/No (boolean)

### Limits
- Questions: Max 20 per form
- Options: Max 10 per Select/Multiselect
- Forms: 3/10/Unlimited (Free/Pro/Premium)

---

**🎉 You're now ready to create amazing application forms!**

For more guides, check out:
- [Auto-Messages Guide](./DASHBOARD_AUTOMESSAGES_GUIDE.md)
- [Social Integration Guide](./DASHBOARD_SOCIAL_GUIDE.md)
- [API Documentation](./API_DOCUMENTATION.md)

---

*Made with ❤️ by Kingdom-77 Team*  
*Last Updated: November 1, 2025*
