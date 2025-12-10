#!/usr/bin/env python3
"""
Script to process articles and create daily disciple content.

This script:
1. Fetches an article by ID from generated_content collection
2. Creates a folder with the article's created_at date
3. Stores the article JSON in that folder
4. Fetches the newspaper for that date if available
5. Creates today's date directory with social_media.txt
6. Makes API calls to add article and newspaper
"""

import json
import os
import re
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from PIL import Image, ImageDraw, ImageFont

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from pymongo import MongoClient

from data_processing_service.models import ContentType
from data_processing_service.models.generated_content import (
    GeneratedContent, GeneratedContentStatus)
from data_processing_service.repositories.mongodb.adapters.generated_content_adapter import \
    GeneratedContentAdapter
from data_processing_service.repositories.mongodb.models.generated_content_db_model import \
    GeneratedContentDBModel
from user_service.models import OutputType


def extract_article_id(input_str: str) -> Optional[str]:
    """
    Extract article ID from URL or return the input if it's already an ID.
    
    Supports URLs like:
    - https://unhook-production.up.railway.app/article/{article_id}
    - https://www.teerth.xyz/article/{article_id}
    - Any URL ending with /article/{article_id}
    
    Args:
        input_str: Either a URL or an article ID
        
    Returns:
        The extracted article ID, or None if no valid ID found
    """
    # UUID pattern: 8-4-4-4-12 hexadecimal characters
    uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
    
    # Check if input is a URL (starts with http:// or https://)
    if input_str.startswith('http://') or input_str.startswith('https://'):
        # Extract UUID from the URL (should be the last segment after /article/)
        match = re.search(uuid_pattern, input_str, re.IGNORECASE)
        if match:
            return match.group(0)
        else:
            print(f"Warning: Could not extract article ID from URL: {input_str}")
            return None
    else:
        # Assume it's already an article ID
        # Validate it's a UUID format
        if re.match(f'^{uuid_pattern}$', input_str, re.IGNORECASE):
            return input_str
        else:
            print(f"Warning: Input does not appear to be a valid article ID: {input_str}")
            return input_str  # Return anyway, let MongoDB validation handle it


class ArticleProcessor:
    """Processes articles and creates daily disciple content."""
    
    def __init__(self):
        """Initialize the processor with MongoDB connections."""
        # Hardcoded MongoDB connections as requested
        self.mongodb_uri = "mongodb+srv://purushottam:test12345@cluster0.xv0gfbm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        self.database_name = "youtube_newspaper"
        
        # Connect to MongoDB
        self.client = MongoClient(self.mongodb_uri)
        self.db = self.client[self.database_name]
        
        # Collections
        self.generated_content_collection = self.db.generated_content
        self.newspaper_collection = self.db.newspaper
        
        # Base directory for daily disciple (script is already in daily_disciple folder)
        self.daily_disciple_dir = Path(__file__).parent
        self.daily_disciple_dir.mkdir(exist_ok=True)
        
        # Marketing frontend paths
        self.project_root = Path(__file__).parent.parent.parent
        self.marketing_frontend_dir = self.project_root / "marketing_frontend"
        self.local_app_process = None
        self.local_app_port = 3000
        
        # Store processed articles for summary at the end
        self.processed_articles = []
    
    def fetch_article(self, article_id: str) -> Optional[GeneratedContent]:
        """Fetch article from generated_content collection by ID."""
        try:
            # Find the document by ID
            doc = self.generated_content_collection.find_one({"_id": article_id})
            if not doc:
                print(f"Article with ID {article_id} not found")
                return None
            
            # Convert to internal model
            db_model = GeneratedContentDBModel(**doc)
            article = GeneratedContentAdapter.from_generated_content_db_model(db_model)
            return article
            
        except Exception as e:
            print(f"Error fetching article {article_id}: {e}")
            return None
    
    def create_today_folder(self) -> Path:
        """Create folder with today's date."""
        # Get today's date
        today = datetime.now().date()
        today_folder = self.daily_disciple_dir / today.strftime("%Y-%m-%d")
        today_folder.mkdir(exist_ok=True)
        
        print(f"Created/verified today's folder: {today_folder}")
        return today_folder
    
    def store_article_json(self, article: GeneratedContent, date_folder: Path) -> None:
        """Store article JSON in the date folder."""
        # Convert article to dict for JSON serialization
        article_dict = {
            "id": article.id,
            "external_id": article.external_id,
            "content_type": article.content_type,
            "status": article.status,
            "content_generated_at": article.content_generated_at.isoformat(),
            "created_at": article.created_at.isoformat(),
            "updated_at": article.updated_at.isoformat(),
            "reading_time_seconds": article.reading_time_seconds,
            "category": {
                "category": article.category.category if article.category else None,
                "shelf_life": article.category.shelf_life if article.category else None,
                "geography": article.category.geography if article.category else None
            } if article.category else None,
            "generated": {
                output_type: {
                    "markdown_string": data.markdown_string,
                    "string": data.string
                }
                for output_type, data in article.generated.items()
            },
            "status_details": [
                {
                    "status": detail.status,
                    "created_at": detail.created_at.isoformat(),
                    "reason": detail.reason
                }
                for detail in article.status_details
            ]
        }
        
        # Save to JSON file
        article_file = date_folder / f"article_{article.id}.json"
        with open(article_file, 'w', encoding='utf-8') as f:
            json.dump(article_dict, f, indent=2, ensure_ascii=False)
        
        print(f"Stored article JSON: {article_file}")
    
    def fetch_newspaper_for_today(self) -> Optional[Dict[str, Any]]:
        """Fetch newspaper for today's date."""
        try:
            # Get today's date
            today = datetime.now().date()
            
            # Convert date to start and end of day for comparison
            start_of_day = datetime.combine(today, datetime.min.time())
            end_of_day = datetime.combine(today, datetime.max.time())
            
            # Find newspaper for today (assuming we want any user's newspaper for today)
            newspaper_doc = self.newspaper_collection.find_one({
                "created_at": {"$gte": start_of_day, "$lte": end_of_day}
            })
            
            if newspaper_doc:
                print(f"Found newspaper for today ({today})")
                return newspaper_doc
            else:
                print(f"No newspaper found for today ({today})")
                return None
                
        except Exception as e:
            print(f"Error fetching newspaper for today ({today}): {e}")
            return None
    
    def add_newspaper_to_date_folder(self, newspaper: Dict[str, Any], date_folder: Path) -> None:
        """Add newspaper JSON to the date directory."""
        newspaper_file = date_folder / f"newspaper_{newspaper['_id']}.json"
        with open(newspaper_file, 'w', encoding='utf-8') as f:
            json.dump(newspaper, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"Stored newspaper JSON: {newspaper_file}")
    
    def create_social_media_file(self, article: GeneratedContent, today_folder: Path) -> None:
        """Create or append to social_media.txt file in today's folder."""
        # Extract content for social media
        very_short_content = ""
        short_content = ""
        
        if OutputType.VERY_SHORT in article.generated:
            very_short_content = article.generated[OutputType.VERY_SHORT].string
        if OutputType.SHORT in article.generated:
            short_content = article.generated[OutputType.SHORT].string
        
        # Truncate summary if it's too long (aim for ~700 words total)
        max_summary_length = 500  # Leave room for title and link
        if len(short_content) > max_summary_length:
            short_content = short_content[:max_summary_length].rsplit(' ', 1)[0] + "....."
        
        # Create social media content with WhatsApp/Instagram story formatting
        social_media_content = f"""📰 *{very_short_content}*

{short_content}

🔗 Read more: www.teerth.xyz/article/{article.id}

---
Generated on: {datetime.now().isoformat()}

"""
        
        # Append social media content to file
        social_media_file = today_folder / "social_media.txt"
        with open(social_media_file, 'a', encoding='utf-8') as f:
            f.write(social_media_content)
        
        print(f"Appended to social media file: {social_media_file}")
        
        # Print the social media content to console for easy copying
        print("\n" + "="*60)
        print("📱 SOCIAL MEDIA CONTENT (Copy from here):")
        print("="*60)
        print(social_media_content.strip())
        print("="*60)
    
    def generate_social_media_card(self, article: GeneratedContent, today_folder: Path) -> None:
        """Generate a social media card image instead of text file."""
        try:
            # Extract content for social media
            very_short_content = ""
            short_content = ""
            
            if OutputType.VERY_SHORT in article.generated:
                very_short_content = article.generated[OutputType.VERY_SHORT].string
            if OutputType.SHORT in article.generated:
                short_content = article.generated[OutputType.SHORT].string
            
            # Apply text constraints from data processing service
            # TITLE: under 12 words, SUMMARY: under 175 words
            title_words = very_short_content.split()
            if len(title_words) > 12:
                very_short_content = ' '.join(title_words[:12]) + "..."
            
            # Truncate content to 175 words max
            content_words = short_content.split()
            if len(content_words) > 175:
                short_content = ' '.join(content_words[:175]) + "..."
            
            # Card dimensions (Instagram square format)
            card_width = 1080
            card_height = 1080
            corner_radius = 40  # For rounded corners
            
            # Create image with gradient background (matching marketing frontend amber theme)
            image = Image.new('RGB', (card_width, card_height), color='white')
            draw = ImageDraw.Draw(image)
            
            # Create gradient background
            for y in range(card_height):
                # Amber gradient: from #fef7e0 to #f4e4bc (matching marketing frontend)
                ratio = y / card_height
                r = int(254 + (244 - 254) * ratio)  # 254 to 244
                g = int(247 + (228 - 247) * ratio)  # 247 to 228  
                b = int(224 + (188 - 224) * ratio)  # 224 to 188
                draw.line([(0, y), (card_width, y)], fill=(r, g, b))
            
            # Try to load fonts, fallback to default if not available
            try:
                title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 52)
                content_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
                small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22)
                tiny_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
            except:
                try:
                    title_font = ImageFont.truetype("arial.ttf", 52)
                    content_font = ImageFont.truetype("arial.ttf", 28)
                    small_font = ImageFont.truetype("arial.ttf", 22)
                    tiny_font = ImageFont.truetype("arial.ttf", 18)
                except:
                    title_font = ImageFont.load_default()
                    content_font = ImageFont.load_default()
                    small_font = ImageFont.load_default()
                    tiny_font = ImageFont.load_default()
            
            # Colors (matching marketing frontend theme exactly)
            title_color = (139, 69, 19)  # #8b4513 (amber-900)
            content_color = (160, 82, 45)  # #a0522d (amber-800)
            accent_color = (184, 134, 11)  # #b8860b (amber-600)
            category_bg_color = (254, 243, 199)  # #fef3c7 (amber-200/50)
            category_text_color = (146, 64, 14)  # #92400e (amber-800)
            reading_time_color = (180, 83, 9)  # #b45309 (amber-600)
            
            # Padding and layout
            padding = 80
            content_width = card_width - (padding * 2)
            
            # Draw title first
            title_y = padding
            title_lines = self._wrap_text(very_short_content, title_font, content_width)
            for line in title_lines:
                bbox = draw.textbbox((0, 0), line, font=title_font)
                text_width = bbox[2] - bbox[0]
                x = (card_width - text_width) // 2
                draw.text((x, title_y), line, fill=title_color, font=title_font)
                title_y += 65
            
            # Draw category and reading time below title (matching marketing frontend styling)
            category_text = ""
            if article.category and article.category.category:
                category_text = article.category.category.upper()
            
            reading_time_minutes = article.reading_time_seconds // 60
            reading_time_text = f"{reading_time_minutes} min read"
            
            meta_y = title_y + 20  # Start below title
            
            # Draw category as a pill (matching marketing frontend)
            if category_text:
                # Calculate category pill dimensions
                cat_bbox = draw.textbbox((0, 0), category_text, font=tiny_font)
                cat_text_width = cat_bbox[2] - cat_bbox[0]
                cat_pill_width = cat_text_width + 24  # 12px padding on each side
                cat_pill_height = 32
                cat_pill_x = (card_width - cat_pill_width) // 2
                cat_pill_y = meta_y
                
                # Draw category pill background
                draw.rounded_rectangle(
                    [(cat_pill_x, cat_pill_y), (cat_pill_x + cat_pill_width, cat_pill_y + cat_pill_height)],
                    radius=16,
                    fill=category_bg_color
                )
                
                # Draw category text
                cat_text_x = (card_width - cat_text_width) // 2
                cat_text_y = cat_pill_y + (cat_pill_height - 18) // 2  # Center vertically
                draw.text((cat_text_x, cat_text_y), category_text, fill=category_text_color, font=tiny_font)
                
                meta_y += cat_pill_height + 15
            
            # Draw reading time with clock icon (matching marketing frontend)
            clock_text = f"🕐 {reading_time_text}"
            bbox = draw.textbbox((0, 0), clock_text, font=tiny_font)
            text_width = bbox[2] - bbox[0]
            x = (card_width - text_width) // 2
            draw.text((x, meta_y), clock_text, fill=reading_time_color, font=tiny_font)
            
            # Draw content below metadata
            content_y = meta_y + 40
            content_lines = self._wrap_text(short_content, content_font, content_width)
            for line in content_lines:
                bbox = draw.textbbox((0, 0), line, font=content_font)
                text_width = bbox[2] - bbox[0]
                x = (card_width - text_width) // 2
                draw.text((x, content_y), line, fill=content_color, font=content_font)
                content_y += 35
            
            # Add call-to-action above logo (generic for all platforms)
            cta_text = "Full read in bio/link"
            bbox = draw.textbbox((0, 0), cta_text, font=small_font)
            text_width = bbox[2] - bbox[0]
            cta_x = (card_width - text_width) // 2
            cta_y = card_height - padding - 160  # Increased distance from logo
            draw.text((cta_x, cta_y), cta_text, fill=accent_color, font=small_font)
            
            # Load and place logo with correct aspect ratio (matching TeerthLogoIcon.tsx)
            logo_path = Path(__file__).parent / "logo_without_text.png"
            if logo_path.exists():
                try:
                    logo = Image.open(logo_path)
                    
                    # Use correct aspect ratio from TeerthLogoIcon.tsx: 220px width / 135px height ≈ 1.63:1
                    logo_aspect_ratio = 220 / 135  # ≈ 1.63
                    
                    # Set logo height and calculate width to maintain aspect ratio
                    logo_height = 60  # Smaller height for better proportion
                    logo_width = int(logo_height * logo_aspect_ratio)  # ≈ 98px
                    
                    logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
                    
                    # Place logo closer to bottom
                    logo_x = (card_width - logo_width) // 2
                    logo_y = card_height - logo_height - padding - 10  # Closer to bottom
                    
                    # Paste logo with transparency
                    if logo.mode == 'RGBA':
                        image.paste(logo, (logo_x, logo_y), logo)
                    else:
                        image.paste(logo, (logo_x, logo_y))
                except Exception as e:
                    print(f"Warning: Could not load logo: {e}")
            
            # Create rounded corners
            rounded_image = self._create_rounded_corners(image, corner_radius)
            
            # Create filename from title (replace spaces and special chars with underscores)
            title_filename = very_short_content.replace(' ', '_').replace(':', '').replace(',', '').replace('.', '').replace('!', '').replace('?', '').replace('(', '').replace(')', '').replace('-', '_')
            # Limit filename length to avoid filesystem issues
            if len(title_filename) > 50:
                title_filename = title_filename[:50]
            
            # Save the image
            card_file = today_folder / f"social_media_card_{title_filename}.png"
            rounded_image.save(card_file, 'PNG', quality=95)
            
            print(f"Generated social media card: {card_file}")
            
            # Print the content to console for easy copying
            print("\n" + "="*60)
            print("📱 SOCIAL MEDIA CARD GENERATED:")
            print("="*60)
            print(f"Title: {very_short_content}")
            print(f"URL: www.teerth.xyz/article/{article.id}")
            print("="*60)
            
            # Store for summary at the end
            self.processed_articles.append({
                'title': very_short_content,
                'url': f"www.teerth.xyz/article/{article.id}"
            })
            
        except Exception as e:
            print(f"Error generating social media card: {e}")
            # Fallback to text file if image generation fails
            self.create_social_media_file(article, today_folder)
            
            # Still store for summary even if image generation failed
            very_short_content = ""
            if OutputType.VERY_SHORT in article.generated:
                very_short_content = article.generated[OutputType.VERY_SHORT].string
            self.processed_articles.append({
                'title': very_short_content,
                'url': f"www.teerth.xyz/article/{article.id}"
            })
    
    def _wrap_text(self, text: str, font: ImageFont.ImageFont, max_width: int) -> list:
        """Wrap text to fit within max_width."""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = ImageDraw.Draw(Image.new('RGB', (1, 1))).textbbox((0, 0), test_line, font=font)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Single word is too long, add it anyway
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _create_rounded_corners(self, image: Image.Image, radius: int) -> Image.Image:
        """Create rounded corners for the image."""
        # Create a mask for rounded corners
        mask = Image.new('L', image.size, 0)
        mask_draw = ImageDraw.Draw(mask)
        
        # Draw rounded rectangle mask
        mask_draw.rounded_rectangle(
            [(0, 0), image.size], 
            radius=radius, 
            fill=255
        )
        
        # Create output image with transparency
        output = Image.new('RGBA', image.size, (0, 0, 0, 0))
        output.paste(image, (0, 0))
        output.putalpha(mask)
        
        return output
    
    def test_image_generation(self, article_id: str) -> None:
        """Test function to generate only the image without running the full script."""
        print(f"Testing image generation for article: {article_id}")
        
        # Step 1: Fetch article
        article = self.fetch_article(article_id)
        if not article:
            print("Failed to fetch article")
            return
        
        print(f"Successfully fetched article: {article.id}")
        
        # Step 2: Create today's folder
        today_folder = self.create_today_folder()
        
        # Step 3: Generate only the social media card
        self.generate_social_media_card(article, today_folder)
        
        print("Image generation test completed!")
    
    def start_local_marketing_frontend(self) -> bool:
        """Start the local marketing frontend app."""
        try:
            print("Starting local marketing frontend app...")
            
            # Check if marketing frontend directory exists
            if not self.marketing_frontend_dir.exists():
                print(f"❌ Marketing frontend directory not found: {self.marketing_frontend_dir}")
                return False
            
            # Check if node_modules exists, if not install dependencies
            node_modules_path = self.marketing_frontend_dir / "node_modules"
            if not node_modules_path.exists():
                print("Installing marketing frontend dependencies...")
                install_result = subprocess.run(
                    ["npm", "install"],
                    cwd=self.marketing_frontend_dir,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutes timeout
                )
                if install_result.returncode != 0:
                    print(f"❌ Failed to install dependencies: {install_result.stderr}")
                    return False
                print("✅ Dependencies installed successfully")
            
            # Start the Next.js app in development mode
            self.local_app_process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=self.marketing_frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for the app to start (check if port is available)
            max_wait_time = 60  # 60 seconds
            wait_interval = 2   # Check every 2 seconds
            waited = 0
            
            while waited < max_wait_time:
                try:
                    # Try to make a request to the local app
                    response = requests.get(f"http://localhost:{self.local_app_port}", timeout=5)
                    if response.status_code in [200, 404]:  # 404 is fine, means app is running
                        print(f"✅ Local marketing frontend started successfully on port {self.local_app_port}")
                        return True
                except requests.exceptions.RequestException:
                    pass
                
                time.sleep(wait_interval)
                waited += wait_interval
                
                # Check if process is still running
                if self.local_app_process.poll() is not None:
                    stdout, stderr = self.local_app_process.communicate()
                    print(f"❌ Local app failed to start. stdout: {stdout}, stderr: {stderr}")
                    return False
            
            print(f"❌ Local app failed to start within {max_wait_time} seconds")
            return False
            
        except Exception as e:
            print(f"❌ Error starting local marketing frontend: {e}")
            return False
    
    def stop_local_marketing_frontend(self) -> None:
        """Stop the local marketing frontend app."""
        try:
            if self.local_app_process and self.local_app_process.poll() is None:
                print("Stopping local marketing frontend app...")
                
                # Try graceful shutdown first
                self.local_app_process.terminate()
                
                # Wait for graceful shutdown
                try:
                    self.local_app_process.wait(timeout=10)
                    print("✅ Local marketing frontend stopped gracefully")
                except subprocess.TimeoutExpired:
                    # Force kill if graceful shutdown fails
                    print("Force killing local marketing frontend...")
                    self.local_app_process.kill()
                    self.local_app_process.wait()
                    print("✅ Local marketing frontend force stopped")
                
                self.local_app_process = None
            else:
                print("Local marketing frontend was not running")
                
        except Exception as e:
            print(f"❌ Error stopping local marketing frontend: {e}")
    
    def make_api_calls(self, article_id: str) -> None:
        """Make API calls to add article and newspaper (both remote and local)."""
        try:
            # Start local marketing frontend
            local_app_started = self.start_local_marketing_frontend()
            
            # API call 1: Add article (POST request) - Remote
            article_url = f"https://www.teerth.xyz/api/addArticle/{article_id}"
            print(f"Making POST API call (remote): {article_url}")
            
            article_response = requests.post(article_url, timeout=30)
            print(f"Remote Article API response: {article_response.status_code}")
            
            if article_response.status_code == 200:
                print(f"✅ Remote Article API call successful!")
            elif article_response.status_code == 404:
                print(f"❌ Article not found in database (404)")
            else:
                print(f"⚠️ Unexpected response: {article_response.status_code}")
                if article_response.text:
                    print(f"Response body: {article_response.text[:200]}...")
            
            # API call 1: Add article (POST request) - Local
            if local_app_started:
                local_article_url = f"http://localhost:{self.local_app_port}/api/addArticle/{article_id}"
                print(f"Making POST API call (local): {local_article_url}")
                
                try:
                    local_article_response = requests.post(local_article_url, timeout=30)
                    print(f"Local Article API response: {local_article_response.status_code}")
                    
                    if local_article_response.status_code == 200:
                        print(f"✅ Local Article API call successful!")
                    elif local_article_response.status_code == 404:
                        print(f"❌ Article not found in local database (404)")
                    else:
                        print(f"⚠️ Unexpected local response: {local_article_response.status_code}")
                        if local_article_response.text:
                            print(f"Local response body: {local_article_response.text[:200]}...")
                except Exception as e:
                    print(f"❌ Error making local article API call: {e}")
            
            # API call 2: Add newspaper articles for today - Remote
            today = datetime.now().date()
            newspaper_date_str = today.strftime("%Y-%m-%d")
            newspaper_url = f"https://www.teerth.xyz/api/add_newspaper_articles?date={newspaper_date_str}"
            print(f"Making GET API call (remote): {newspaper_url}")
            
            newspaper_response = requests.get(newspaper_url, timeout=30)
            print(f"Remote Newspaper API response: {newspaper_response.status_code}")
            
            if newspaper_response.status_code == 200:
                print(f"✅ Remote Newspaper API call successful!")
            else:
                print(f"⚠️ Unexpected response: {newspaper_response.status_code}")
                if newspaper_response.text:
                    print(f"Response body: {newspaper_response.text[:200]}...")
            
            # API call 2: Add newspaper articles for today - Local
            if local_app_started:
                local_newspaper_url = f"http://localhost:{self.local_app_port}/api/add_newspaper_articles?date={newspaper_date_str}"
                print(f"Making GET API call (local): {local_newspaper_url}")
                
                try:
                    local_newspaper_response = requests.get(local_newspaper_url, timeout=30)
                    print(f"Local Newspaper API response: {local_newspaper_response.status_code}")
                    
                    if local_newspaper_response.status_code == 200:
                        print(f"✅ Local Newspaper API call successful!")
                    else:
                        print(f"⚠️ Unexpected local response: {local_newspaper_response.status_code}")
                        if local_newspaper_response.text:
                            print(f"Local response body: {local_newspaper_response.text[:200]}...")
                except Exception as e:
                    print(f"❌ Error making local newspaper API call: {e}")
            
        except Exception as e:
            print(f"Error making API calls: {e}")
        finally:
            # Always stop the local app
            self.stop_local_marketing_frontend()
    
    def process_article(self, article_id: str) -> None:
        """Main method to process an article."""
        print(f"Processing article: {article_id}")
        
        # Step 1: Fetch article
        article = self.fetch_article(article_id)
        if not article:
            print("Failed to fetch article")
            return
        
        print(f"Successfully fetched article: {article.id}")
        
        # Step 2: Create today's folder
        today_folder = self.create_today_folder()
        
        # Step 3: Store article JSON in today's folder
        self.store_article_json(article, today_folder)
        
        # Step 4: Fetch and store newspaper for today
        newspaper = self.fetch_newspaper_for_today()
        if newspaper:
            self.add_newspaper_to_date_folder(newspaper, today_folder)
        
        # Step 5: Generate social media card image in today's folder
        self.generate_social_media_card(article, today_folder)
        
        # Step 6: Make API calls
        self.make_api_calls(article_id)
        
        print("Article processing completed successfully!")
    
    def print_processed_articles_summary(self):
        """Print summary of all processed articles for easy copy-pasting."""
        if not self.processed_articles:
            return
            
        print("\n" + "="*80)
        print("📋 SUMMARY OF ALL PROCESSED ARTICLES (Copy from here):")
        print("="*80)
        
        for i, article in enumerate(self.processed_articles, 1):
            print(f"{i}. Title: {article['title']}")
            print(f"   URL: {article['url']}")
            if i < len(self.processed_articles):
                print()  # Add blank line between articles except for the last one
        
        print("="*80)
    
    def close_connections(self):
        """Close MongoDB connections and stop local app."""
        self.client.close()
        self.stop_local_marketing_frontend()


def main():
    """Main function to run the script."""
    if len(sys.argv) < 2:
        print("Usage: python article_processor.py <article_id_or_url1> [article_id_or_url2] ... [--test]")
        print("  --test: Generate only the image without running full script")
        print("  You can provide multiple article IDs or URLs to process them sequentially")
        print("  Examples:")
        print("    python article_processor.py 79bc5706-23e0-4fad-b797-ec0467f7e713")
        print("    python article_processor.py https://unhook-production.up.railway.app/article/79bc5706-23e0-4fad-b797-ec0467f7e713")
        sys.exit(1)
    
    # Parse arguments - collect article IDs/URLs and check for test mode
    article_ids = []
    test_mode = False
    
    for arg in sys.argv[1:]:
        if arg == "--test":
            test_mode = True
        else:
            # Extract article ID from URL or use as-is if it's already an ID
            extracted_id = extract_article_id(arg)
            if extracted_id:
                article_ids.append(extracted_id)
            else:
                print(f"⚠️ Skipping invalid input: {arg}")
    
    if not article_ids:
        print("Error: No valid article IDs or URLs provided")
        print("Usage: python article_processor.py <article_id_or_url1> [article_id_or_url2] ... [--test]")
        sys.exit(1)
    
    processor = ArticleProcessor()
    try:
        # Process each article
        for i, article_id in enumerate(article_ids, 1):
            print(f"\n{'='*80}")
            print(f"Processing article {i}/{len(article_ids)}: {article_id}")
            print(f"{'='*80}")
            
            try:
                if test_mode:
                    processor.test_image_generation(article_id)
                else:
                    processor.process_article(article_id)
                print(f"✅ Successfully processed article {i}/{len(article_ids)}: {article_id}")
            except Exception as e:
                print(f"❌ Error processing article {i}/{len(article_ids)} ({article_id}): {e}")
                # Continue with next article instead of stopping
                continue
        
        print(f"\n{'='*80}")
        print(f"Completed processing {len(article_ids)} article(s)")
        print(f"{'='*80}")
        
        # Print summary of all processed articles
        processor.print_processed_articles_summary()
        
    finally:
        processor.close_connections()


if __name__ == "__main__":
    main()
