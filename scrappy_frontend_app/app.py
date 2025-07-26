import os
import sys
from datetime import datetime
from typing import List, Optional

import markdown
from flask import Flask, jsonify, render_template, request
from pymongo import MongoClient

# Add the parent directory to the path to import from the main project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_processing_service.models.generated_content import \
    GeneratedContentStatus
from user_service.models.enums import OutputType

app = Flask(__name__)

# MongoDB connection
from config import CONFIG


def get_database():
    """Get MongoDB database connection."""
    client = MongoClient(CONFIG["MONGODB_URI"])
    return client[CONFIG["DATABASE_NAME"]]


class ArticleCard:
    """Simple model for article card display."""

    def __init__(
        self,
        id: str,
        title: str,
        summary: str,
        category: Optional[str] = None,
        created_at: datetime = None,
        content_types: List[str] = None,
        reading_time_seconds: int = 0,
    ):
        self.id = id
        self.title = title
        self.summary = summary
        self.category = category
        self.created_at = created_at
        self.content_types = content_types or []
        self.reading_time_seconds = reading_time_seconds

    def get_time_ago(self) -> str:
        """Get a human-readable time ago string."""
        if not self.created_at:
            return ""

        now = datetime.now()
        diff = now - self.created_at

        if diff.days > 0:
            if diff.days == 1:
                return "1 day ago"
            elif diff.days < 7:
                return f"{diff.days} days ago"
            else:
                return self.created_at.strftime("%b %d, %Y")
        elif diff.seconds >= 3600:
            hours = diff.seconds // 3600
            if hours == 1:
                return "1 hour ago"
            else:
                return f"{hours} hours ago"
        elif diff.seconds >= 60:
            minutes = diff.seconds // 60
            if minutes == 1:
                return "1 minute ago"
            else:
                return f"{minutes} minutes ago"
        else:
            return "Just now"

    def get_reading_time(self) -> str:
        """Get reading time in a human-readable format."""
        if not self.reading_time_seconds:
            return ""

        minutes = self.reading_time_seconds // 60
        if minutes < 1:
            return "Less than 1 min read"
        elif minutes == 1:
            return "1 min read"
        else:
            return f"{minutes} min read"


class ArticleDetail:
    """Model for full article details."""

    def __init__(
        self,
        id: str,
        title: str,
        content: str,
        category: Optional[str] = None,
        created_at: datetime = None,
        external_id: Optional[str] = None,
        reading_time_seconds: int = 0,
    ):
        self.id = id
        self.title = title
        self.content = content
        self.category = category
        self.created_at = created_at
        self.external_id = external_id
        self.reading_time_seconds = reading_time_seconds

    def get_youtube_url(self) -> Optional[str]:
        """Get YouTube URL if external_id is available."""
        if self.external_id:
            return f"https://www.youtube.com/watch?v={self.external_id}"
        return None

    def get_reading_time(self) -> str:
        """Get reading time in a human-readable format."""
        if not self.reading_time_seconds:
            return ""

        minutes = self.reading_time_seconds // 60
        if minutes < 1:
            return "Less than 1 min read"
        elif minutes == 1:
            return "1 min read"
        else:
            return f"{minutes} min read"


def get_unique_categories() -> List[str]:
    """Get all unique categories from the database."""
    db = get_database()
    collection = db.generated_content

    # Find articles with status ARTICLE_GENERATED
    cursor = collection.find({"status": GeneratedContentStatus.ARTICLE_GENERATED})

    categories = set()
    for doc in cursor:
        if "category" in doc and doc["category"]:
            category = doc["category"].get("category", "")
            if category:
                categories.add(category)

    return sorted(list(categories))


def fetch_articles(
    user_id: str,
    sort_by: str = "newest",
    category_filter: str = None,
    content_type_filter: str = None,
) -> List[ArticleCard]:
    """Fetch articles with status ARTICLE_GENERATED for a user."""
    db = get_database()
    collection = db.generated_content

    # Find articles with status ARTICLE_GENERATED
    cursor = collection.find({"status": GeneratedContentStatus.ARTICLE_GENERATED})

    articles = []
    for doc in cursor:
        # Get title from VERY_SHORT or SHORT content
        title = ""
        summary = ""

        generated = doc.get("generated", {})

        # Try to get title from VERY_SHORT
        if OutputType.VERY_SHORT in generated:
            title = generated[OutputType.VERY_SHORT].get("string", "")

        # Get summary from SHORT
        if OutputType.SHORT in generated:
            summary = generated[OutputType.SHORT].get("string", "")

        # If no title from VERY_SHORT, try to extract from SHORT
        if not title and summary:
            title = (
                summary.split(".")[0][:50] + "..."
                if len(summary.split(".")[0]) > 50
                else summary.split(".")[0]
            )

        # Get category if available
        category = None
        if "category" in doc and doc["category"]:
            category = doc["category"].get("category", "")

        # Get content types available (MEDIUM, LONG)
        content_types = []
        if OutputType.MEDIUM in generated:
            content_types.append("MEDIUM")
        if OutputType.LONG in generated:
            content_types.append("LONG")

        # Get content generated date (when the content was actually published/generated)
        content_generated_at = None
        if "content_generated_at" in doc:
            content_generated_at = datetime.fromtimestamp(doc["content_generated_at"])
        elif "created_at" in doc:
            # Fallback to created_at if content_generated_at is not available
            content_generated_at = datetime.fromtimestamp(doc["created_at"])

        # Get reading time in seconds
        reading_time_seconds = 0
        if "reading_time_seconds" in doc:
            reading_time_seconds = doc["reading_time_seconds"]

        # Apply filters
        if category_filter and category != category_filter:
            continue

        if content_type_filter and content_type_filter not in content_types:
            continue

        articles.append(
            ArticleCard(
                id=doc["_id"],
                title=title,
                summary=summary,
                category=category,
                created_at=content_generated_at,
                content_types=content_types,
                reading_time_seconds=reading_time_seconds,
            )
        )

    # Sort articles based on the sort_by parameter
    if sort_by == "newest":
        articles.sort(key=lambda x: x.created_at or datetime.min, reverse=True)
    elif sort_by == "oldest":
        articles.sort(key=lambda x: x.created_at or datetime.max)
    elif sort_by == "title":
        articles.sort(key=lambda x: x.title.lower())

    return articles


def fetch_article_detail(article_id: str) -> Optional[ArticleDetail]:
    """Fetch full article details by ID."""
    db = get_database()
    collection = db.generated_content

    doc = collection.find_one({"_id": article_id})
    if not doc:
        return None

    # Get title
    title = ""
    generated = doc.get("generated", {})

    if OutputType.VERY_SHORT in generated:
        title = generated[OutputType.VERY_SHORT].get("string", "")

    # Get content - prefer LONG, then MEDIUM, then SHORT
    content = ""
    if OutputType.LONG in generated:
        content = generated[OutputType.LONG].get(
            "markdown_string", generated[OutputType.LONG].get("string", "")
        )
    elif OutputType.MEDIUM in generated:
        content = generated[OutputType.MEDIUM].get(
            "markdown_string", generated[OutputType.MEDIUM].get("string", "")
        )
    elif OutputType.SHORT in generated:
        content = generated[OutputType.SHORT].get("string", "")

    # Convert markdown to HTML
    if content:
        # Configure markdown extensions for better rendering
        md = markdown.Markdown(
            extensions=[
                "markdown.extensions.tables",
                "markdown.extensions.fenced_code",
                "markdown.extensions.codehilite",
                "markdown.extensions.toc",
                "markdown.extensions.nl2br",
                "markdown.extensions.sane_lists",
            ]
        )
        content = md.convert(content)

    # If no title, extract from content
    if not title and content:
        title = content.split("\n")[0].replace("#", "").strip()

    # Get category
    category = None
    if "category" in doc and doc["category"]:
        category = doc["category"].get("category", "")

    # Get content generated date (when the content was actually published/generated)
    content_generated_at = None
    if "content_generated_at" in doc:
        content_generated_at = datetime.fromtimestamp(doc["content_generated_at"])
    elif "created_at" in doc:
        # Fallback to created_at if content_generated_at is not available
        content_generated_at = datetime.fromtimestamp(doc["created_at"])

    # Get external_id for YouTube video link
    external_id = None
    if "external_id" in doc:
        external_id = doc["external_id"]

    # Get reading time in seconds
    reading_time_seconds = 0
    if "reading_time_seconds" in doc:
        reading_time_seconds = doc["reading_time_seconds"]

    return ArticleDetail(
        id=doc["_id"],
        title=title,
        content=content,
        category=category,
        created_at=content_generated_at,
        external_id=external_id,
        reading_time_seconds=reading_time_seconds,
    )


@app.route("/")
def index():
    """Main page showing article cards."""
    # For now, we'll use a default user_id. In a real app, this would come from authentication
    user_id = request.args.get("user_id", "default_user")
    sort_by = request.args.get("sort", "newest")
    category_filter = request.args.get("category", "")
    content_type_filter = request.args.get("content_type", "")
    articles = fetch_articles(user_id, sort_by, category_filter, content_type_filter)

    # Get available categories for filter dropdown
    available_categories = get_unique_categories()

    # Calculate date range for articles with dates
    articles_with_dates = [a for a in articles if a.created_at]
    date_range = None
    if articles_with_dates:
        dates = [a.created_at for a in articles_with_dates]
        date_range = {"earliest": min(dates), "latest": max(dates)}

    return render_template(
        "index.html",
        articles=articles,
        user_id=user_id,
        sort_by=sort_by,
        category_filter=category_filter,
        content_type_filter=content_type_filter,
        available_categories=available_categories,
        date_range=date_range,
    )


@app.route("/article/<article_id>")
def article_detail(article_id):
    """Article detail page."""
    article = fetch_article_detail(article_id)
    if not article:
        return "Article not found", 404
    return render_template("article_detail.html", article=article)


@app.route("/api/articles")
def api_articles():
    """API endpoint to get articles as JSON."""
    user_id = request.args.get("user_id", "default_user")
    sort_by = request.args.get("sort", "newest")
    category_filter = request.args.get("category", "")
    content_type_filter = request.args.get("content_type", "")
    articles = fetch_articles(user_id, sort_by, category_filter, content_type_filter)

    # Convert to dict for JSON serialization
    articles_data = []
    for article in articles:
        articles_data.append(
            {
                "id": article.id,
                "title": article.title,
                "summary": article.summary,
                "category": article.category,
                "content_types": article.content_types,
                "created_at": (
                    article.created_at.isoformat() if article.created_at else None
                ),
                "reading_time_seconds": article.reading_time_seconds,
            }
        )

    return jsonify(articles_data)


@app.route("/api/article/<article_id>")
def api_article_detail(article_id):
    """API endpoint to get article details as JSON."""
    article = fetch_article_detail(article_id)
    if not article:
        return jsonify({"error": "Article not found"}), 404

    return jsonify(
        {
            "id": article.id,
            "title": article.title,
            "content": article.content,
            "category": article.category,
            "created_at": (
                article.created_at.isoformat() if article.created_at else None
            ),
            "external_id": article.external_id,
            "youtube_url": article.get_youtube_url(),
            "reading_time_seconds": article.reading_time_seconds,
        }
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
