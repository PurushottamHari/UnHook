import os
import sys
from datetime import datetime, timedelta
from typing import List, Optional

import markdown
import pytz
from flask import Flask, jsonify, render_template, request
from pymongo import MongoClient

# Add the parent directory to the path to import from the main project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_processing_service.models.generated_content import \
    GeneratedContentStatus
from user_service.models.enums import CategoryName, OutputType, Weekday

app = Flask(__name__)

# MongoDB connection
from config import CONFIG


def get_database():
    """Get MongoDB database connection."""
    client = MongoClient(CONFIG["MONGODB_URI"])
    return client[CONFIG["DATABASE_NAME"]]


class NewspaperCard:
    """Simple model for newspaper card display."""

    def __init__(
        self,
        id: str,
        user_id: str,
        status: str,
        created_at: datetime = None,
        updated_at: datetime = None,
        article_count: int = 0,
        reading_time_seconds: int = 0,
    ):
        self.id = id
        self.user_id = user_id
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at
        self.article_count = article_count
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


class NewspaperDetail:
    """Model for full newspaper details."""

    def __init__(
        self,
        id: str,
        user_id: str,
        status: str,
        created_at: datetime = None,
        updated_at: datetime = None,
        reading_time_seconds: int = 0,
        considered_content_list: List[dict] = None,
        final_content_list: List[str] = None,
    ):
        self.id = id
        self.user_id = user_id
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at
        self.reading_time_seconds = reading_time_seconds
        self.considered_content_list = considered_content_list or []
        self.final_content_list = final_content_list or []

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
        external_id: Optional[str] = None,
        channel_name: Optional[str] = None,
    ):
        self.id = id
        self.title = title
        self.summary = summary
        self.category = category
        self.created_at = created_at
        self.content_types = content_types or []
        self.reading_time_seconds = reading_time_seconds
        self.external_id = external_id
        self.channel_name = channel_name

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

    def get_youtube_url(self) -> Optional[str]:
        """Get YouTube URL if external_id is available."""
        if self.external_id:
            return f"https://www.youtube.com/watch?v={self.external_id}"
        return None


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
        channel_name: Optional[str] = None,
    ):
        self.id = id
        self.title = title
        self.content = content
        self.category = category
        self.created_at = created_at
        self.external_id = external_id
        self.reading_time_seconds = reading_time_seconds
        self.channel_name = channel_name

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


def fetch_newspapers(
    user_id: str, sort_by: str = "newest", target_date: Optional[datetime] = None
) -> List[NewspaperCard]:
    """Fetch newspapers for a user, optionally filtered by date."""
    db = get_database()
    collection = db.newspapers

    # Build query
    query = {"user_id": user_id}

    # Add date filter if target_date is provided
    if target_date:
        # Create start and end of day for the target date
        start_of_day = datetime(
            target_date.year, target_date.month, target_date.day, 0, 0, 0
        )
        end_of_day = datetime(
            target_date.year, target_date.month, target_date.day, 23, 59, 59
        )

        query["created_at"] = {
            "$gte": start_of_day.timestamp(),
            "$lte": end_of_day.timestamp(),
        }

    # Find newspapers for the user
    cursor = collection.find(query)

    newspapers = []
    for doc in cursor:
        # Get created_at and updated_at
        created_at = None
        if "created_at" in doc:
            created_at = datetime.fromtimestamp(doc["created_at"])

        updated_at = None
        if "updated_at" in doc:
            updated_at = datetime.fromtimestamp(doc["updated_at"])

        # Count articles in considered_content_list
        article_count = len(doc.get("considered_content_list", []))

        # Get reading time
        reading_time_seconds = doc.get("reading_time_in_seconds", 0)

        newspapers.append(
            NewspaperCard(
                id=doc["_id"],
                user_id=doc["user_id"],
                status=doc["status"],
                created_at=created_at,
                updated_at=updated_at,
                article_count=article_count,
                reading_time_seconds=reading_time_seconds,
            )
        )

    # Sort newspapers based on the sort_by parameter
    if sort_by == "newest":
        newspapers.sort(key=lambda x: x.created_at or datetime.min, reverse=True)
    elif sort_by == "oldest":
        newspapers.sort(key=lambda x: x.created_at or datetime.max)
    elif sort_by == "status":
        newspapers.sort(key=lambda x: x.status.lower())

    return newspapers


def get_available_dates(user_id: str) -> List[datetime]:
    """Get all available dates for newspapers for a user."""
    db = get_database()
    collection = db.newspapers

    # Find all newspapers for the user and extract unique dates
    cursor = collection.find({"user_id": user_id})

    dates = set()
    for doc in cursor:
        if "created_at" in doc:
            created_at = datetime.fromtimestamp(doc["created_at"])
            # Convert to date only (remove time)
            date_only = datetime(created_at.year, created_at.month, created_at.day)
            dates.add(date_only)

    # Convert to list and sort
    dates_list = list(dates)
    dates_list.sort(reverse=True)  # Most recent first

    return dates_list


def fetch_newspaper_detail(newspaper_id: str) -> Optional[NewspaperDetail]:
    """Fetch full newspaper details by ID."""
    db = get_database()
    collection = db.newspapers

    doc = collection.find_one({"_id": newspaper_id})
    if not doc:
        return None

    # Get created_at and updated_at
    created_at = None
    if "created_at" in doc:
        created_at = datetime.fromtimestamp(doc["created_at"])

    updated_at = None
    if "updated_at" in doc:
        updated_at = datetime.fromtimestamp(doc["updated_at"])

    # Get reading time
    reading_time_seconds = doc.get("reading_time_in_seconds", 0)

    return NewspaperDetail(
        id=doc["_id"],
        user_id=doc["user_id"],
        status=doc["status"],
        created_at=created_at,
        updated_at=updated_at,
        reading_time_seconds=reading_time_seconds,
        considered_content_list=doc.get("considered_content_list", []),
        final_content_list=doc.get("final_content_list", []),
    )


def fetch_articles_for_newspaper(newspaper_id: str) -> List[ArticleCard]:
    """Fetch articles associated with a newspaper."""
    newspaper = fetch_newspaper_detail(newspaper_id)
    if not newspaper:
        return []

    # Get the considered content IDs from the newspaper
    considered_content_ids = []
    for item in newspaper.considered_content_list:
        if "user_collected_content_id" in item:
            considered_content_ids.append(item["user_collected_content_id"])

    if not considered_content_ids:
        return []

    # Get external_ids from the collected_content collection
    db = get_database()
    collected_content_collection = db.collected_content

    external_ids = []
    for content_id in considered_content_ids:
        collected_doc = collected_content_collection.find_one({"_id": content_id})
        if collected_doc and "external_id" in collected_doc:
            external_ids.append(collected_doc["external_id"])

    if not external_ids:
        return []

    # Fetch the generated articles using external_ids
    generated_content_collection = db.generated_content

    # Find articles with status ARTICLE_GENERATED that match the external_ids
    cursor = generated_content_collection.find(
        {
            "status": GeneratedContentStatus.ARTICLE_GENERATED,
            "external_id": {"$in": external_ids},
        }
    )

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

        # Get external_id for YouTube video link
        external_id = None
        if "external_id" in doc:
            external_id = doc["external_id"]

        articles.append(
            ArticleCard(
                id=doc["_id"],
                title=title,
                summary=summary,
                category=category,
                created_at=content_generated_at,
                content_types=content_types,
                reading_time_seconds=reading_time_seconds,
                external_id=external_id,
                channel_name=None,  # Don't fetch channel name for performance
            )
        )

    # Sort articles by creation date (newest first)
    articles.sort(key=lambda x: x.created_at or datetime.min, reverse=True)

    return articles


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


def get_weekday_from_date(date: datetime) -> Weekday:
    """Get the weekday enum from a datetime object."""
    weekday_map = {
        0: Weekday.MONDAY,
        1: Weekday.TUESDAY,
        2: Weekday.WEDNESDAY,
        3: Weekday.THURSDAY,
        4: Weekday.FRIDAY,
        5: Weekday.SATURDAY,
        6: Weekday.SUNDAY,
    }
    # Convert to local timezone if needed and get weekday (0=Monday, 6=Sunday)
    local_date = date.astimezone(pytz.timezone("Asia/Kolkata"))
    weekday_num = local_date.weekday()
    return weekday_map[weekday_num]


def get_allowed_categories_for_date(user_id: str, for_date: datetime) -> List[dict]:
    """Get categories that should be considered for the given date based on user interests and weekdays."""
    user = fetch_user(user_id)
    if not user:
        return []

    weekday = get_weekday_from_date(for_date)
    allowed_categories = []

    for interest in user.get("interested", []):
        # Check if the interest is defined for the current weekday
        if weekday.value in interest.get("weekdays", []):
            allowed_categories.append(
                {
                    "category_name": interest.get("category_name"),
                    "category_definition": interest.get("category_definition"),
                    "output_type": interest.get("output_type"),
                    "weekdays": interest.get("weekdays"),
                }
            )

    return allowed_categories


def get_newspaper_categories_for_date(user_id: str, for_date: datetime) -> List[dict]:
    """Get actual categories present in the newspaper for a given date."""
    db = get_database()

    # Create start and end of day for the target date
    start_of_day = datetime(for_date.year, for_date.month, for_date.day, 0, 0, 0)
    end_of_day = datetime(for_date.year, for_date.month, for_date.day, 23, 59, 59)

    # Find newspapers for the user on the given date
    newspapers_collection = db.newspapers
    newspapers = newspapers_collection.find(
        {
            "user_id": user_id,
            "created_at": {
                "$gte": start_of_day.timestamp(),
                "$lte": end_of_day.timestamp(),
            },
        }
    )

    # Collect all external_ids from considered_content_list
    all_external_ids = set()
    newspaper_ids = []

    for newspaper in newspapers:
        newspaper_ids.append(newspaper["_id"])
        considered_content = newspaper.get("considered_content_list", [])
        for content in considered_content:
            if "external_id" in content:
                all_external_ids.add(content["external_id"])

    if not all_external_ids:
        return []

    # Fetch the generated articles using external_ids
    generated_content_collection = db.generated_content

    # Find articles with status ARTICLE_GENERATED that match the external_ids
    cursor = generated_content_collection.find(
        {
            "status": GeneratedContentStatus.ARTICLE_GENERATED,
            "external_id": {"$in": list(all_external_ids)},
        }
    )

    # Collect unique categories with their details
    categories = {}

    for doc in cursor:
        if "category" in doc and doc["category"]:
            category_name = doc["category"].get("category", "")
            if category_name:
                if category_name not in categories:
                    categories[category_name] = {
                        "category_name": category_name,
                        "article_count": 0,
                        "articles": [],
                    }

                # Get article details
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

                categories[category_name]["article_count"] += 1
                categories[category_name]["articles"].append(
                    {
                        "id": doc["_id"],
                        "title": title,
                        "summary": summary,
                        "external_id": doc.get("external_id"),
                        "reading_time_seconds": doc.get("reading_time_seconds", 0),
                    }
                )

    # Convert to list and sort by article count
    categories_list = list(categories.values())
    categories_list.sort(key=lambda x: x["article_count"], reverse=True)

    return categories_list


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

        # Get external_id for YouTube video link (but don't fetch channel name for performance)
        external_id = None
        if "external_id" in doc:
            external_id = doc["external_id"]

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
                external_id=external_id,
                channel_name=None,  # Don't fetch channel name for homepage performance
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

    # Fetch channel name from collected_content collection
    channel_name = None
    if external_id:
        collected_content_collection = db.collected_content
        collected_doc = collected_content_collection.find_one(
            {"external_id": external_id}
        )
        if collected_doc and "data" in collected_doc:
            # The data field contains the YouTube video details with YOUTUBE_VIDEO as key
            data = collected_doc["data"]
            if "YOUTUBE_VIDEO" in data:
                video_details = data["YOUTUBE_VIDEO"]
                if isinstance(video_details, dict) and "channel_name" in video_details:
                    channel_name = video_details["channel_name"]

    return ArticleDetail(
        id=doc["_id"],
        title=title,
        content=content,
        category=category,
        created_at=content_generated_at,
        external_id=external_id,
        reading_time_seconds=reading_time_seconds,
        channel_name=channel_name,
    )


def fetch_user(user_id: str) -> Optional[dict]:
    """Fetch user details by ID."""
    db = get_database()
    collection = db["users"]

    user_dict = collection.find_one({"_id": user_id})
    if not user_dict:
        return None

    return user_dict


def update_user(user_id: str, user_data: dict) -> Optional[dict]:
    """Update user details by ID."""
    db = get_database()
    collection = db["users"]

    # Only allow updating specific fields
    allowed_fields = {
        "max_reading_time_per_day_mins",
        "interested",
        "not_interested",
        "manual_configs",
    }

    # Filter out non-editable fields
    filtered_data = {k: v for k, v in user_data.items() if k in allowed_fields}

    if not filtered_data:
        raise Exception("No valid fields to update")

    result = collection.update_one({"_id": user_id}, {"$set": filtered_data})

    if result.modified_count > 0:
        return fetch_user(user_id)
    return None


@app.route("/health")
def health_check():
    """Health check endpoint for Railway."""
    return (
        jsonify({"status": "healthy", "message": "UnHook Scrappy Frontend is running"}),
        200,
    )


@app.route("/")
def index():
    """Main page showing articles for a specific date."""
    # For now, we'll use a default user_id. In a real app, this would come from authentication
    user_id = request.args.get("user_id", "607d95f0-47ef-444c-89d2-d05f257d1265")
    sort_by = request.args.get("sort", "newest")

    # Handle date parameter
    target_date = None
    date_str = request.args.get("date")
    if date_str:
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            # If date parsing fails, ignore the date parameter
            pass

    # If no date specified, default to today
    if not target_date:
        target_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    # Get newspapers for the date to extract article IDs
    newspapers = fetch_newspapers(user_id, sort_by, target_date)

    # Extract all article IDs from newspapers
    all_articles = []
    for newspaper in newspapers:
        articles = fetch_articles_for_newspaper(newspaper.id)
        all_articles.extend(articles)

    # Sort articles based on the sort_by parameter
    if sort_by == "newest":
        all_articles.sort(key=lambda x: x.created_at or datetime.min, reverse=True)
    elif sort_by == "oldest":
        all_articles.sort(key=lambda x: x.created_at or datetime.max)
    elif sort_by == "status":
        all_articles.sort(key=lambda x: x.category or "")

    available_dates = get_available_dates(user_id)

    # Get allowed categories for the current date
    allowed_categories = get_allowed_categories_for_date(user_id, target_date)

    return render_template(
        "index.html",
        articles=all_articles,
        user_id=user_id,
        sort_by=sort_by,
        target_date=target_date,
        available_dates=available_dates,
        allowed_categories=allowed_categories,
    )


@app.route("/newspaper/<newspaper_id>")
def newspaper_detail(newspaper_id):
    """Newspaper detail page showing articles."""
    newspaper = fetch_newspaper_detail(newspaper_id)
    if not newspaper:
        return "Newspaper not found", 404

    articles = fetch_articles_for_newspaper(newspaper_id)

    return render_template(
        "newspaper_detail.html", newspaper=newspaper, articles=articles
    )


@app.route("/articles")
def articles():
    """Legacy articles page showing all articles."""
    # For now, we'll use a default user_id. In a real app, this would come from authentication
    user_id = request.args.get("user_id", "607d95f0-47ef-444c-89d2-d05f257d1265")
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
        "articles.html",
        articles=articles,
        user_id=user_id,
        sort_by=sort_by,
        category_filter=category_filter,
        content_type_filter=content_type_filter,
        available_categories=available_categories,
        date_range=date_range,
    )


@app.route("/test-summary")
def test_summary():
    """Test route for summary functionality."""
    return render_template("test_summary.html")


@app.route("/debug-summary")
def debug_summary():
    """Debug route for summary functionality."""
    return render_template("debug_summary.html")


@app.route("/grid-test")
def grid_test():
    """Grid test route for summary functionality."""
    return render_template("grid_test.html")


@app.route("/article/<article_id>")
def article_detail(article_id):
    """Article detail page."""
    article = fetch_article_detail(article_id)
    if not article:
        return "Article not found", 404
    return render_template("article_detail.html", article=article)


@app.route("/settings")
def user_settings():
    """User settings page."""
    return render_template("user_settings.html")


@app.route("/api/newspapers")
def api_newspapers():
    """API endpoint to get newspapers as JSON."""
    user_id = request.args.get("user_id", "607d95f0-47ef-444c-89d2-d05f257d1265")
    sort_by = request.args.get("sort", "newest")

    # Handle date parameter
    target_date = None
    date_str = request.args.get("date")
    if date_str:
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            # If date parsing fails, ignore the date parameter
            pass

    newspapers = fetch_newspapers(user_id, sort_by, target_date)

    # Convert to dict for JSON serialization
    newspapers_data = []
    for newspaper in newspapers:
        newspapers_data.append(
            {
                "id": newspaper.id,
                "user_id": newspaper.user_id,
                "status": newspaper.status,
                "created_at": (
                    newspaper.created_at.isoformat() if newspaper.created_at else None
                ),
                "updated_at": (
                    newspaper.updated_at.isoformat() if newspaper.updated_at else None
                ),
                "article_count": newspaper.article_count,
                "reading_time_seconds": newspaper.reading_time_seconds,
            }
        )

    return jsonify(newspapers_data)


@app.route("/api/dates")
def api_dates():
    """API endpoint to get available dates as JSON."""
    user_id = request.args.get("user_id", "607d95f0-47ef-444c-89d2-d05f257d1265")
    available_dates = get_available_dates(user_id)

    # Convert to list of date strings for JSON serialization
    dates_data = [date.strftime("%Y-%m-%d") for date in available_dates]

    return jsonify(dates_data)


@app.route("/api/newspaper/<newspaper_id>")
def api_newspaper_detail(newspaper_id):
    """API endpoint to get newspaper details as JSON."""
    newspaper = fetch_newspaper_detail(newspaper_id)
    if not newspaper:
        return jsonify({"error": "Newspaper not found"}), 404

    return jsonify(
        {
            "id": newspaper.id,
            "user_id": newspaper.user_id,
            "status": newspaper.status,
            "created_at": (
                newspaper.created_at.isoformat() if newspaper.created_at else None
            ),
            "updated_at": (
                newspaper.updated_at.isoformat() if newspaper.updated_at else None
            ),
            "reading_time_seconds": newspaper.reading_time_seconds,
            "considered_content_list": newspaper.considered_content_list,
            "final_content_list": newspaper.final_content_list,
        }
    )


@app.route("/api/articles")
def api_articles():
    """API endpoint to get articles as JSON."""
    user_id = request.args.get("user_id", "607d95f0-47ef-444c-89d2-d05f257d1265")
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
                "external_id": article.external_id,
                "youtube_url": article.get_youtube_url(),
                # channel_name not included for performance (only fetched on detail pages)
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
            "channel_name": article.channel_name,
        }
    )


@app.route("/api/user/<user_id>")
def api_user_detail(user_id):
    """API endpoint to get user details as JSON."""
    user = fetch_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user)


@app.route("/api/user/<user_id>", methods=["PUT"])
def api_update_user(user_id):
    """API endpoint to update user details."""
    try:
        user_data = request.get_json()
        if not user_data:
            return jsonify({"error": "No data provided"}), 400

        updated_user = update_user(user_id, user_data)
        if not updated_user:
            return jsonify({"error": "User not found"}), 404

        return jsonify(updated_user)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/user/<user_id>/allowed-categories")
def api_allowed_categories(user_id):
    """API endpoint to get allowed categories for a specific date."""
    try:
        # Get date parameter, default to today
        date_str = request.args.get("date")
        if date_str:
            try:
                target_date = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
        else:
            target_date = datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            )

        allowed_categories = get_allowed_categories_for_date(user_id, target_date)
        newspaper_categories = get_newspaper_categories_for_date(user_id, target_date)

        return jsonify(
            {
                "user_id": user_id,
                "date": target_date.strftime("%Y-%m-%d"),
                "weekday": get_weekday_from_date(target_date).value,
                "allowed_categories": allowed_categories,
                "newspaper_categories": newspaper_categories,
                "total_allowed_categories": len(allowed_categories),
                "total_newspaper_categories": len(newspaper_categories),
                "total_articles": sum(
                    cat["article_count"] for cat in newspaper_categories
                ),
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/categories")
def api_all_categories():
    """API endpoint to get all available categories."""
    try:
        all_categories = [category.value for category in CategoryName]
        return jsonify(
            {
                "available_categories": all_categories,
                "total_categories": len(all_categories),
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/allowed-categories")
def allowed_categories_page():
    """Page to display allowed categories for a specific date."""
    user_id = request.args.get("user_id", "607d95f0-47ef-444c-89d2-d05f257d1265")

    # Get date parameter, default to today
    date_str = request.args.get("date")
    if date_str:
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            target_date = datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
    else:
        target_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    # Get allowed categories for the date
    allowed_categories = get_allowed_categories_for_date(user_id, target_date)

    # Get actual newspaper categories for the date
    newspaper_categories = get_newspaper_categories_for_date(user_id, target_date)

    # Get all available categories
    all_categories = [category.value for category in CategoryName]

    # Generate test dates for the next 7 days
    test_dates = []
    for i in range(7):
        test_date = target_date + timedelta(days=i)
        test_dates.append(
            {
                "date": test_date.strftime("%Y-%m-%d"),
                "day_name": test_date.strftime("%A"),
            }
        )

    return render_template(
        "allowed_categories.html",
        user_id=user_id,
        date=target_date.strftime("%Y-%m-%d"),
        weekday=get_weekday_from_date(target_date).value,
        allowed_categories=allowed_categories,
        newspaper_categories=newspaper_categories,
        all_categories=all_categories,
        test_dates=test_dates,
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
