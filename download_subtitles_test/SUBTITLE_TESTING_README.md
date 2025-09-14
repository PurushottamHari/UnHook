# YouTube Subtitle Vendor Testing

This directory contains tools to test YouTube subtitle downloading capabilities across multiple vendors.

## Files

- `test_subtitle_vendors.py` - Main test script that tests all subtitle vendors
- `requirements-subtitle-test.txt` - Python dependencies for subtitle testing
- `SUBTITLE_TESTING_README.md` - This documentation file
- `../.github/workflows/test-subtitle-vendors.yml` - GitHub Action workflow for automated testing

## Tested Vendors

1. **yt-dlp** - Command-line tool for downloading YouTube videos and subtitles
2. **youtube-transcript-api** - Python API for fetching YouTube transcripts
3. **EasySubAPI** - Third-party API service for subtitle extraction

## Test Videos

- `1GpGqwXExYE` - Hindi auto-generated subtitles available
- `9uY6N2Bl0pU` - Hindi auto-generated subtitles available

## Usage

### Local Testing

```bash
# Navigate to the subtitle vendor test directory
cd download_subtitles_test

# Install dependencies
pip install -r requirements-subtitle-test.txt

# Run tests
python test_subtitle_vendors.py
```

### GitHub Actions

The workflow runs only when manually triggered via:
- **Manual trigger (workflow_dispatch)** - Go to Actions tab and click "Run workflow"

## Test Results

The script provides detailed results including:
- Success/failure status for each vendor
- Number of retry attempts
- Vendor-specific details (language, snippet count, etc.)
- Overall statistics and success rates

## Retry Logic

Each vendor is tested with up to 2 retry attempts per video, with a 1-second delay between retries.

## Output Format

The script outputs:
- Real-time progress for each test
- Detailed summary with vendor breakdown
- Overall statistics and success rates
- Exit code 0 for all tests passed, 1 for any failures
