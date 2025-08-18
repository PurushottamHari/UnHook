# Newspaper Categories Feature

This document describes the newspaper categories functionality added to the UnHook frontend application.

## Overview

The newspaper categories feature allows users to see:
1. **Actual categories present in the newspaper** for a specific day with article counts and details
2. **Allowed categories based on user preferences** for that day (what categories the user has configured to receive)

This helps users understand what type of content is actually in their newspaper versus what they've configured to receive.

## Features

### 1. API Endpoints

#### GET `/api/categories`
Returns all available categories in the system.

**Response:**
```json
{
  "available_categories": [
    "TECHNOLOGY",
    "SCIENCE", 
    "BUSINESS",
    "HEALTH",
    "COMEDY",
    "SPORTS",
    "NEWS",
    "EDUCATION",
    "ENVIRONMENT",
    "CULTURE",
    "SPIRITUALITY",
    "MOVIES",
    "PERSPECTIVES",
    "GAMING",
    "MUSIC"
  ],
  "total_categories": 15
}
```

#### GET `/api/user/{user_id}/allowed-categories`
Returns both the actual categories in the newspaper and the allowed categories for a specific user on a given date.

**Parameters:**
- `date` (optional): Date in YYYY-MM-DD format. Defaults to today.

**Response:**
```json
{
  "user_id": "607d95f0-47ef-444c-89d2-d05f257d1265",
  "date": "2024-01-15",
  "weekday": "MONDAY",
  "allowed_categories": [
    {
      "category_name": "TECHNOLOGY",
      "category_definition": "Latest tech news and developments",
      "output_type": "MEDIUM",
      "weekdays": ["MONDAY", "WEDNESDAY", "FRIDAY"]
    },
    {
      "category_name": "SCIENCE",
      "category_definition": "Scientific discoveries and research",
      "output_type": "SHORT",
      "weekdays": ["TUESDAY", "THURSDAY"]
    }
  ],
  "newspaper_categories": [
    {
      "category_name": "TECHNOLOGY",
      "article_count": 3,
      "articles": [
        {
          "id": "article_id_1",
          "title": "Latest AI Developments",
          "summary": "Summary of AI news...",
          "external_id": "youtube_video_id",
          "reading_time_seconds": 180
        }
      ]
    },
    {
      "category_name": "BUSINESS",
      "article_count": 2,
      "articles": [...]
    }
  ],
  "total_allowed_categories": 2,
  "total_newspaper_categories": 2,
  "total_articles": 5
}
```

### 2. Web Interface

#### `/allowed-categories`
A web page that displays both actual newspaper categories and allowed categories for a specific date with a user-friendly interface.

**Features:**
- **Newspaper Categories Section**: Shows actual categories present in the newspaper with article counts and sample titles
- **Allowed Categories Section**: Shows categories allowed by user preferences with definitions and output types
- Displays which weekdays each category is active
- Allows testing different dates
- Shows all available categories for reference
- Links to user settings for configuration

**URL Parameters:**
- `user_id`: User ID to check categories for
- `date`: Date in YYYY-MM-DD format (optional, defaults to today)

### 3. Core Functions

#### `get_weekday_from_date(date: datetime) -> Weekday`
Converts a datetime object to the corresponding weekday enum, using Asia/Kolkata timezone.

#### `get_allowed_categories_for_date(user_id: str, for_date: datetime) -> List[dict]`
Determines which categories are allowed for a user on a specific date by:
1. Fetching the user's interests
2. Getting the weekday for the given date
3. Filtering interests that include the current weekday
4. Returning the matching categories with their details

#### `get_newspaper_categories_for_date(user_id: str, for_date: datetime) -> List[dict]`
Gets the actual categories present in the newspaper for a given date by:
1. Finding newspapers for the user on the given date
2. Extracting external_ids from the considered_content_list
3. Fetching generated articles with those external_ids
4. Grouping articles by category and counting them
5. Returning categories with article counts and sample titles

## How It Works

The allowed categories are determined by the user's `interested` field in the user model. Each interest contains:

- `category_name`: One of the 15 predefined categories
- `category_definition`: Custom description of the category
- `weekdays`: List of weekdays when this category should be included
- `output_type`: Content length preference (VERY_SHORT, SHORT, MEDIUM, LONG)

For a given date, the system:
1. Determines the weekday (Monday-Sunday)
2. Checks all user interests
3. Returns only those interests where the current weekday is in the `weekdays` list

## Usage Examples

### Using the API
```bash
# Get allowed categories for today
curl "http://localhost:5000/api/user/607d95f0-47ef-444c-89d2-d05f257d1265/allowed-categories"

# Get allowed categories for a specific date
curl "http://localhost:5000/api/user/607d95f0-47ef-444c-89d2-d05f257d1265/allowed-categories?date=2024-01-15"

# Get all available categories
curl "http://localhost:5000/api/categories"
```

### Using the Web Interface
```
http://localhost:5000/allowed-categories?user_id=607d95f0-47ef-444c-89d2-d05f257d1265&date=2024-01-15
```

### Using the Test Script
```bash
cd scrappy_frontend_app
python test_allowed_categories.py
```

## Integration with Newspaper Service

This functionality mirrors the logic used in the `newspaper_service` in the `_get_allowed_categories_for_date()` method. The frontend implementation provides the same filtering logic but exposes it through web APIs for user interface consumption.

## Future Enhancements

1. **Category Filtering**: Filter articles shown on the main page to only include content from allowed categories
2. **Notifications**: Alert users when no categories are allowed for a day
3. **Analytics**: Show statistics about category usage over time
4. **Quick Setup**: Provide templates for common category configurations
