# UnHook Scrappy Frontend App

A simple Flask-based frontend application to view and read AI-generated articles from the UnHook system.

## Features

- **Article Cards**: Display articles organized by date in a card format
- **Sleek Date Carousel**: Browse articles by date using a modern gradient carousel
- **Article Details**: Click on any article to view its full content
- **Markdown Rendering**: Articles are displayed in proper markdown format
- **Responsive Design**: Works on desktop and mobile devices
- **User Switching**: Change user ID to view different user's articles
- **Sorting**: Sort articles by newest, oldest, or category
- **Date Filtering**: Filter articles by specific dates
- **Keyboard Navigation**: Use arrow keys to navigate between dates
- **Modern UI**: Clean, modern interface with smooth animations

## Setup

### Prerequisites

- Python 3.8+
- MongoDB running with the UnHook database
- Access to the main UnHook project files (for imports)

### Installation

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables**:
   Create a `.env` file in the parent directory (UnHook root) with your MongoDB connection:
   ```env
   MONGODB_URI=mongodb://localhost:27017
   DATABASE_NAME=youtube_newspaper
   ```

3. **Ensure the main UnHook project is accessible**:
   The app imports from the main project's modules, so make sure the parent directory structure is intact.

## Usage

### Running the App

1. **Test the connection** (optional but recommended):
   ```bash
   python test_connection.py
   ```

2. **Start the Flask application**:
   ```bash
   python run.py
   ```
   Or alternatively:
   ```bash
   python app.py
   ```

3. **Access the application**:
   Open your browser and go to `http://localhost:5000`

### Using the Interface

1. **View Articles**: The main page shows articles organized by date
2. **Navigate Dates**: Use the sleek date carousel at the top to browse articles by date
   - Click the circular arrow buttons to move between dates
   - Use the dropdown to jump to a specific date
   - Use left/right arrow keys for keyboard navigation
3. **Change User**: Use the user ID input field to switch between different users
4. **Sort Articles**: Use the "Sort by" dropdown to sort by newest, oldest, or category
5. **Read Articles**: Click on any article card to view its full content
6. **Navigate**: Use the "Back to Articles" button to return to the main page

## API Endpoints

The app also provides REST API endpoints:

- `GET /api/newspapers?user_id=<user_id>&date=<YYYY-MM-DD>` - Get newspapers for a specific date as JSON
- `GET /api/dates?user_id=<user_id>` - Get all available dates for newspapers as JSON
- `GET /api/newspaper/<newspaper_id>` - Get specific newspaper details as JSON
- `GET /api/articles?user_id=<user_id>` - Get all articles as JSON (legacy)
- `GET /api/article/<article_id>` - Get specific article details as JSON

## Data Structure

The app fetches newspapers from the `newspapers` collection in MongoDB with the following structure:

- **Status**: Newspaper status (e.g., "COMPLETED", "PROCESSING")
- **Created Date**: From `created_at` timestamp (used for date filtering)
- **Article Count**: Number of articles in the newspaper
- **Reading Time**: Total reading time in seconds
- **Articles**: Associated articles from the `generated_content` collection

The app also fetches articles from the `generated_content` collection with the following structure:

- **Status**: Must be "ARTICLE_GENERATED"
- **Title**: Extracted from `generated.VERY_SHORT.string` or first sentence of summary
- **Summary**: From `generated.SHORT.string`
- **Content**: From `generated.LONG.markdown_string` (preferred) or `generated.MEDIUM.markdown_string`
- **Category**: From `category.category` if available
- **Content Types**: Determined by checking presence of `generated.MEDIUM` and `generated.LONG` fields
- **Created Date**: From `created_at` timestamp

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure the main UnHook project files are accessible
2. **MongoDB Connection**: Verify your MongoDB is running and the connection string is correct
3. **No Articles**: Ensure there are articles with status "ARTICLE_GENERATED" in your database

### Debug Mode

The app runs in debug mode by default. Check the console for any error messages or database connection issues.

## Development

This is a "scrappy" frontend meant for testing and reading articles. For production use, consider:

- Adding authentication
- Implementing proper error handling
- Adding pagination for large article lists
- Implementing search and filtering
- Adding article bookmarking/favorites
- Implementing proper markdown rendering with syntax highlighting

## License

This is part of the UnHook project. 