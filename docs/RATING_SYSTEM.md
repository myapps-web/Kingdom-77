# Bot Rating System Documentation

## Overview
The bot now includes a complete rating system that allows users to rate their overall experience with the bot using a star-based system (1-5 stars).

## Features

### 1. User Rating (`/rate`)
- **Description**: Allows users to rate the bot with 1-5 stars
- **UI**: Interactive button interface with star labels
- **Functionality**:
  - Users can rate the bot by clicking star buttons (⭐ to ⭐⭐⭐⭐⭐)
  - Each user can only have one rating (updates replace previous rating)
  - Rating is saved immediately with timestamp and username
  - Ephemeral response (only visible to the user)
  - 3-minute timeout for the rating UI

### 2. Rating Statistics (`/ratings`)
- **Description**: Displays comprehensive bot rating statistics
- **Functionality**:
  - Shows average rating with star visualization
  - Displays total number of ratings
  - Shows distribution of ratings (5⭐ to 1⭐)
  - Visual bars showing percentage distribution
  - Public response (visible to all users in channel)

### 3. Data Persistence
- **Storage**: Ratings are stored in `ratings.json`
- **Format**: 
  ```json
  {
    "user_id": {
      "rating": 5,
      "timestamp": "2024-01-01T12:00:00.000000",
      "username": "User#1234"
    }
  }
  ```
- **Loading**: Ratings loaded on bot startup
- **Saving**: Asynchronous saving using thread pool to avoid blocking

## Implementation Details

### Files Modified
- `main.py`:
  - Added `RATINGS_FILE` constant for file path
  - Added `bot_ratings` global dictionary
  - Added `load_ratings()` function
  - Added `save_ratings()` async function
  - Added `RatingView` UI class with 5 star buttons
  - Added `/rate` slash command
  - Added `/ratings` slash command
  - Updated `/help` command to include new rating commands
  - Updated `on_ready()` to load ratings on startup

### Classes

#### RatingView
- **Type**: `discord.ui.View`
- **Purpose**: Interactive UI for rating submission
- **Buttons**: 5 buttons (1-5 stars)
- **Handler**: `_handle_rating()` method processes the rating
- **Features**:
  - Detects if rating is new or update
  - Saves rating with timestamp
  - Provides user feedback
  - Logs rating activity

### Commands

#### `/rate`
- **Permission**: All users
- **Response Type**: Ephemeral (private)
- **Features**:
  - Shows rating prompt with star descriptions
  - Displays RatingView UI
  - Includes footer with helpful text

#### `/ratings`
- **Permission**: All users
- **Response Type**: Public
- **Display**:
  - Average rating (stars + numeric)
  - Total ratings count
  - Distribution bars (using █ and ░ characters)
  - Percentage for each star level
  - Thank you message

## Usage Examples

### Rating the Bot
1. User types `/rate`
2. Bot shows rating prompt with 5 star buttons
3. User clicks their desired rating (e.g., ⭐⭐⭐⭐)
4. Bot confirms rating submission
5. Rating is saved to `ratings.json`

### Viewing Statistics
1. User types `/ratings`
2. Bot shows:
   ```
   Average Rating: ⭐⭐⭐⭐ (4.20/5.00)
   Total Ratings: 10

   Distribution:
   ⭐⭐⭐⭐⭐: ████████████░░░░░░░░ 6 (60.0%)
   ⭐⭐⭐⭐: ████░░░░░░░░░░░░░░░░ 2 (20.0%)
   ⭐⭐⭐: ██░░░░░░░░░░░░░░░░░░ 1 (10.0%)
   ⭐⭐: ██░░░░░░░░░░░░░░░░░░ 1 (10.0%)
   ⭐: ░░░░░░░░░░░░░░░░░░░░ 0 (0.0%)
   ```

## Technical Notes

- **Thread Safety**: Uses `asyncio.run_in_executor()` for non-blocking file I/O
- **Data Validation**: Ratings are integers 1-5
- **User Identification**: Uses Discord user ID as unique key
- **Error Handling**: Comprehensive try-except blocks for file operations
- **Logging**: All rating operations are logged for debugging
- **Performance**: Async operations ensure UI remains responsive

## Future Enhancements (Optional)
- Add optional comment/feedback field
- Export ratings to CSV
- Show recent ratings
- Add admin command to view detailed statistics
- Rating leaderboard for most active raters
- Periodic rating reminders
