# UnHook

## Setup

Follow these steps to set up the development environment for this project:

1. **Create and activate a Python virtual environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Update local dependency paths in `pyproject.toml` files:**
   - Ensure that the local dependency paths in the `pyproject.toml` files for each service reflect your local directory structure. For example, update lines like:
     ```toml
     user-service @ file:///Users/puru/Workspace/UnHook/user_service
     data-collector-service @ file:///Users/puru/Workspace/UnHook/data_collector_service
     ```
     to match your actual local path if it differs.

3. **Install each service in editable mode:**
   - From the root of your project, run the following commands for each service:

   ```bash
   cd user_service
   python3 -m pip install -e .
   cd ../data_collector_service
   python3 -m pip install -e .
   cd ../data_processing_service
   python3 -m pip install -e .
   cd ..
   ```

4. **Create a `.env` file in each module:**
   - In each of the following directories: `user_service`, `data_collector_service`, and `data_processing_service`, create a `.env` file with the following content:
     ```env
     MONGODB_URI=your_mongodb_connection_string
     ```
   - Replace `your_mongodb_connection_string` with your actual MongoDB URI.

This will ensure all dependencies are installed and local packages are linked in editable mode for development.

## YouTube Cookie Configuration for GitHub Actions

YouTube has implemented strict bot detection that blocks GitHub Actions IP addresses. To avoid this issue, you need to configure YouTube cookies for authentication.

### Option 1: Using the Cookie Export Script (Recommended)

1. **Activate your virtual environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Run the cookie export script:**
   ```bash
   python scripts/export_youtube_cookies.py chrome
   ```

3. **Follow the instructions** provided by the script to add cookies to GitHub Secrets

### Option 2: Manual yt-dlp Export

1. **Install yt-dlp locally:**
   ```bash
   pip install yt-dlp
   ```

2. **Export cookies from your browser:**
   ```bash
   # For Chrome/Chromium
   yt-dlp --cookies-from-browser chrome --cookies youtube_cookies.txt
   
   # For Firefox
   yt-dlp --cookies-from-browser firefox --cookies youtube_cookies.txt
   
   # For Safari (macOS)
   yt-dlp --cookies-from-browser safari --cookies youtube_cookies.txt
   ```

3. **The workflow will automatically use the cookies** from the `cookies/` folder.

### Testing Cookie Configuration

To test if your cookies work:

1. **Test the cookie export script:**
   ```bash
   source venv/bin/activate
   python scripts/export_youtube_cookies.py chrome
   ```

2. **Test locally with cookies:**
   ```bash
   source venv/bin/activate
   export YOUTUBE_COOKIES=./youtube_cookies.txt
   python -c "from data_collector_service.collectors.youtube.tools.clients.yt_dlp_client import YtDlpClient; client = YtDlpClient(); print('Cookies loaded successfully')"
   ```

3. **Test with a YouTube video:**
   ```bash
   yt-dlp --cookies youtube_cookies.txt "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --skip-download --write-sub
   ```

4. **Test subtitle download:**
   ```bash
   python -c "
   from data_collector_service.collectors.youtube.tools.clients.yt_dlp_client import YtDlpClient
   client = YtDlpClient()
   result = client.download_subtitles('dQw4w9WgXcQ', 'en', 'vtt', 'automatic')
   print('Subtitle download successful' if result else 'Subtitle download failed')
   "
   ```

5. **Run comprehensive test:**
   ```bash
   source venv/bin/activate
   export YOUTUBE_COOKIES=./youtube_cookies.txt
   python scripts/test_youtube_cookies.py dQw4w9WgXcQ
   ```

### Important Notes

- **Cookie Expiration:** YouTube cookies typically expire after a few weeks. You'll need to refresh them periodically.
- **Security:** Never commit cookie files to your repository. Always use GitHub Secrets.
- **Multiple Accounts:** If you have multiple YouTube accounts, make sure to export cookies from the correct account.
- **Legal Compliance:** Ensure you comply with YouTube's Terms of Service when using automated tools.

## Code Formatting

This project uses **Black** and **isort** for automatic code formatting and import sorting. Configuration for both tools is included in each service's `pyproject.toml` file.

To format your code, run the following commands from the root of each service:

```bash
black . && isort .
```

This will ensure your code is consistently formatted and imports are properly organized.

## Running the Data Collector Service

To start the data collector service, run the following command from the root of your project:

```bash
python3 -m data_collector_service.service
```

# Moderation (Content Rejection) Step

To run the content moderation (rejection) step, use the following command from the project root:

```sh
python3 -m data_processing_service.services.rejection.reject_content_service
```

# Processing Moderated Content Step

To process the moderated content, use the following command from the project root:

```sh
python3 -m data_processing_service.services.processing.process_moderated_content_service
```

# Generating the required data for Youtube Video
```sh
python3 -m data_processing_service.services.processing.youtube.generate_required_content.generate_required_youtube_content_service
```

# Categorizing the generated content
```sh
python3 -m data_processing_service.services.processing.youtube.categorize_content.categorize_youtube_content_service
```

# Generating the Final Article
```sh
python3 -m data_processing_service.services.processing.youtube.generate_complete_content.generate_complete_youtube_content_service
```

# Create the newspaper for the day
```sh
python -m newspaper_service.services.create_newspaper_service
```

