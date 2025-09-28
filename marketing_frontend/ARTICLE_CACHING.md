# Article Caching System

This system allows you to fetch articles from the UnHook API and cache them locally for fast access.

## How it Works

1. **Cache Articles**: Use the `addArticle` endpoint to fetch and cache articles
2. **View Articles**: Access cached articles through the article page
3. **Local Storage**: Articles are stored as JSON files in `src/lib/cache/articles/`

## API Endpoints

### Add Article to Cache

```
GET /api/addArticle/{article_id}
POST /api/addArticle/{article_id}
```

**Example:**

```bash
curl -X GET "http://localhost:3000/api/addArticle/02003d04-5555-4b43-89f9-01fbdcf010cc"
```

**Response:**

```json
{
  "success": true,
  "message": "Article 02003d04-5555-4b43-89f9-01fbdcf010cc has been cached successfully",
  "article": {
    "id": "02003d04-5555-4b43-89f9-01fbdcf010cc",
    "title": "Smartphone Data Privacy Dangers and Chinese Market Dominance",
    "external_id": "1GpGqwXExYE",
    "youtube_channel": "ranveerallahbadia",
    "cached_at": "2025-09-16T06:50:08.232Z"
  }
}
```

### View Cached Article

```
GET /article/{article_id}
```

**Example:**

```
http://localhost:3000/article/02003d04-5555-4b43-89f9-01fbdcf010cc
```

## Cached Article Structure

Each cached article contains:

- `id`: Article ID
- `title`: Article title
- `content`: Full article content (cleaned HTML)
- `external_id`: YouTube video ID
- `youtube_channel`: YouTube channel name
- `cached_at`: Timestamp when article was cached

## Workflow

1. **First Time**: Call `/api/addArticle/{id}` to fetch and cache the article
2. **Subsequent Access**: Visit `/article/{id}` to view the cached article
3. **Not Cached**: If article isn't cached, you'll see a "Not Found" page

## Features

- ✅ Fetches from UnHook API: `https://unhook-production.up.railway.app/article/{id}`
- ✅ Extracts title, content, YouTube video ID, and channel name
- ✅ Local file-based caching in `src/lib/cache/articles/`
- ✅ Fast article loading from cache
- ✅ YouTube video integration
- ✅ Waitlist signup on article pages
- ✅ Responsive design with theme switching

## Example Usage

```bash
# 1. Cache an article
curl -X GET "http://localhost:3000/api/addArticle/02003d04-5555-4b43-89f9-01fbdcf010cc"

# 2. View the cached article
open "http://localhost:3000/article/02003d04-5555-4b43-89f9-01fbdcf010cc"
```

The system is now ready to use! Articles will be cached locally and served quickly from the file system.
