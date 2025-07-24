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
    ):
        self.id = id
        self.title = title
        self.summary = summary
        self.category = category
        self.created_at = created_at


class ArticleDetail:
    """Model for full article details."""

    def __init__(
        self,
        id: str,
        title: str,
        content: str,
        category: Optional[str] = None,
        created_at: datetime = None,
    ):
        self.id = id
        self.title = title
        self.content = content
        self.category = category
        self.created_at = created_at


def fetch_articles(user_id: str) -> List[ArticleCard]:
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

        # Get content generated date (when the content was actually published/generated)
        content_generated_at = None
        if "content_generated_at" in doc:
            content_generated_at = datetime.fromtimestamp(doc["content_generated_at"])
        elif "created_at" in doc:
            # Fallback to created_at if content_generated_at is not available
            content_generated_at = datetime.fromtimestamp(doc["created_at"])

        articles.append(
            ArticleCard(
                id=doc["_id"],
                title=title,
                summary=summary,
                category=category,
                created_at=content_generated_at,
            )
        )

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

    return ArticleDetail(
        id=doc["_id"],
        title=title,
        content=content,
        category=category,
        created_at=content_generated_at,
    )


@app.route("/")
def index():
    """Main page showing article cards."""
    # For now, we'll use a default user_id. In a real app, this would come from authentication
    user_id = request.args.get("user_id", "default_user")
    articles = fetch_articles(user_id)
    return render_template("index.html", articles=articles, user_id=user_id)


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
    articles = fetch_articles(user_id)

    # Convert to dict for JSON serialization
    articles_data = []
    for article in articles:
        articles_data.append(
            {
                "id": article.id,
                "title": article.title,
                "summary": article.summary,
                "category": article.category,
                "created_at": (
                    article.created_at.isoformat() if article.created_at else None
                ),
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
        }
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
