# User Settings Feature

This document describes the new user settings functionality added to the UnHook frontend application.

## Overview

The user settings feature allows users to view and edit their profile settings through a modal interface accessible via a settings icon in the top-right corner of the application.

## Features

### 1. Settings Icon
- Located in the top-right corner of the header
- Clicking the icon opens the user settings modal
- Styled with a gear icon and hover effects

### 2. User Settings Modal
The modal displays and allows editing of the following user properties:

#### Editable Fields:
- **Max Reading Time Per Day**: Number input (1-480 minutes)
- **Interests**: Array of interest objects with:
  - Category (dropdown with predefined options)
  - Category Definition (text area)
  - Weekdays (checkboxes for each day)
  - Output Type (dropdown: VERY_SHORT, SHORT, MEDIUM, LONG)
- **Not Interested**: Array of category definitions
- **Manual Configs**: YouTube configuration with:
  - Discover On (weekday checkboxes)
  - YouTube Channels (array of channel configurations)

#### Non-Editable Fields (Display Only):
- User ID
- Email
- Name
- Created At

### 3. Form Features
- **Add/Remove Items**: Buttons to add new interests, not interested items, and YouTube channels
- **Dynamic Form Updates**: Form re-renders when items are added/removed
- **Validation**: Basic input validation for required fields
- **Real-time Updates**: Changes are reflected immediately in the form

### 4. API Integration
- **GET /api/user/{user_id}**: Retrieves user details
- **PUT /api/user/{user_id}**: Updates user details
- **Field Filtering**: Only editable fields are allowed in update requests
- **Error Handling**: Proper error messages for failed operations

## Technical Implementation

### Backend Changes

#### User Service Updates
- Added `update_user` method to `UserService`
- Added `update_user` method to `UserRepository` interface
- Implemented MongoDB update logic in `MongoDBUserRepository`

#### API Endpoints
- Added `PUT /users/{user_id}` endpoint in user controller
- Added user API endpoints to frontend app:
  - `GET /api/user/{user_id}`
  - `PUT /api/user/{user_id}`

#### Data Validation
- Only specific fields are allowed for updates:
  - `max_reading_time_per_day_mins`
  - `interested`
  - `not_interested`
  - `manual_configs`

### Frontend Changes

#### UI Components
- **Settings Button**: Added to header with gear icon
- **Modal**: Full-screen modal with backdrop blur
- **Form**: Dynamic form with various input types
- **Responsive Design**: Mobile-friendly layout

#### JavaScript Features
- **Modal Management**: Open/close functionality
- **Data Loading**: Async loading of user data
- **Form Rendering**: Dynamic form generation
- **Data Updates**: Real-time form updates
- **API Communication**: Fetch-based API calls
- **Error Handling**: User-friendly error messages

#### Styling
- **Modern Design**: Clean, modern UI with gradients
- **Animations**: Smooth transitions and hover effects
- **Responsive**: Mobile-optimized layout
- **Accessibility**: Proper labels and keyboard navigation

## Usage

### Opening Settings
1. Click the settings icon (gear) in the top-right corner
2. The modal will open and load user details
3. Make changes to the form fields
4. Click "Save Changes" to update
5. Click "Cancel" or outside the modal to close

### Adding Items
- Click "Add Interest" to add a new interest
- Click "Add Not Interested" to add a new not interested item
- Click "Add Channel" to add a new YouTube channel

### Removing Items
- Click the "Remove" button next to any item to delete it

### Saving Changes
- Click "Save Changes" to submit the form
- Success/error messages will be displayed
- The modal will show a success message on successful save

## Data Structure

### User Model
```json
{
  "_id": "user-uuid",
  "email": "user@example.com",
  "name": "User Name",
  "created_at": "2024-01-01T00:00:00Z",
  "max_reading_time_per_day_mins": 30,
  "interested": [
    {
      "category_name": "TECHNOLOGY",
      "category_definition": "Tech news and updates",
      "weekdays": ["MONDAY", "WEDNESDAY", "FRIDAY"],
      "output_type": "MEDIUM"
    }
  ],
  "not_interested": [
    {
      "category_definition": "Sports content"
    }
  ],
  "manual_configs": {
    "youtube": {
      "discover_on": ["MONDAY", "TUESDAY"],
      "channels": [
        {
          "channel_id": "UC123456789",
          "max_videos_daily": 3,
          "output_type": "SHORT",
          "not_interested": []
        }
      ]
    }
  }
}
```

## Testing

### Manual Testing
1. Start the frontend application: `python3 run.py`
2. Navigate to the application in a browser
3. Click the settings icon
4. Test adding/removing items
5. Test saving changes
6. Verify data persistence

### API Testing
Run the test script to verify API endpoints:
```bash
python3 test_user_api.py
```

## Security Considerations

- Only editable fields are allowed in update requests
- Input validation on both frontend and backend
- Proper error handling and user feedback
- No sensitive data exposure in the UI

## Future Enhancements

- User authentication and authorization
- Form validation with better error messages
- Auto-save functionality
- Undo/redo changes
- Export/import user settings
- Settings templates/presets
