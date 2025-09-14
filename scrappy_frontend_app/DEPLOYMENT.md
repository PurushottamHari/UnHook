# UnHook Scrappy Frontend - Deployment Guide

This guide provides multiple deployment options for the UnHook Scrappy Frontend app.

## 🚨 Security Fix Applied

**IMPORTANT**: The MongoDB credentials have been moved to environment variables. Make sure to:

1. Create a `.env` file with your actual MongoDB credentials
2. Never commit the `.env` file to version control
3. Use the provided `env.example` as a template

## Quick Deployment Options

### Option 1: Railway (Recommended for Quick Deploy)

Railway is the fastest and easiest option for a prototype deployment.

**Steps:**
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Create a new project
4. Connect your GitHub repository
5. Set environment variables in Railway dashboard:
   ```
   MONGODB_URI=your_mongodb_connection_string
   DATABASE_NAME=youtube_newspaper
   FLASK_DEBUG=False
   FLASK_HOST=0.0.0.0
   FLASK_PORT=5001
   ```
6. Deploy!

**Pros:**
- ✅ Free tier available
- ✅ Automatic deployments from GitHub
- ✅ Built-in environment variable management
- ✅ Custom domains available
- ✅ SSL certificates included

### Option 2: Render

**Steps:**
1. Go to [render.com](https://render.com)
2. Connect your GitHub repository
3. Create a new Web Service
4. Use these settings:
   - **Build Command**: `pip install -r scrappy_frontend_app/requirements.txt`
   - **Start Command**: `cd scrappy_frontend_app && python run.py`
   - **Environment**: Python 3
5. Set environment variables in Render dashboard
6. Deploy!

**Pros:**
- ✅ Free tier available
- ✅ Automatic SSL
- ✅ Easy GitHub integration

### Option 3: Heroku

**Steps:**
1. Install Heroku CLI
2. Create a Heroku app:
   ```bash
   heroku create your-app-name
   ```
3. Set environment variables:
   ```bash
   heroku config:set MONGODB_URI="your_mongodb_connection_string"
   heroku config:set DATABASE_NAME="youtube_newspaper"
   heroku config:set FLASK_DEBUG="False"
   ```
4. Deploy:
   ```bash
   git push heroku main
   ```

**Pros:**
- ✅ Well-established platform
- ✅ Good documentation
- ✅ Add-ons available

### Option 4: DigitalOcean App Platform

**Steps:**
1. Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
2. Create a new app from GitHub
3. Configure:
   - **Source**: Your GitHub repository
   - **Type**: Web Service
   - **Build Command**: `pip install -r scrappy_frontend_app/requirements.txt`
   - **Run Command**: `cd scrappy_frontend_app && python run.py`
4. Set environment variables
5. Deploy!

**Pros:**
- ✅ Good performance
- ✅ Reasonable pricing
- ✅ Easy scaling

### Option 5: Docker Deployment (Any VPS)

If you have a VPS or server:

**Steps:**
1. Copy the entire project to your server
2. Create a `.env` file with your credentials
3. Run with Docker:
   ```bash
   cd scrappy_frontend_app
   docker-compose up -d
   ```

**For manual deployment:**
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export MONGODB_URI="your_mongodb_connection_string"
export DATABASE_NAME="youtube_newspaper"
export FLASK_DEBUG="False"

# Run the app
python run.py
```

## Environment Variables Required

Create a `.env` file with these variables:

```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
DATABASE_NAME=youtube_newspaper
FLASK_DEBUG=False
FLASK_HOST=0.0.0.0
FLASK_PORT=5001
```

## Pre-Deployment Checklist

- [ ] MongoDB credentials moved to environment variables ✅
- [ ] `.env` file created with actual credentials
- [ ] `.env` file added to `.gitignore`
- [ ] Dependencies listed in `requirements.txt`
- [ ] App runs locally with environment variables
- [ ] No hardcoded secrets in code

## Post-Deployment

1. Test the deployed app
2. Verify all features work
3. Check that user settings can be saved
4. Test article viewing functionality
5. Monitor logs for any errors

## Recommended for Prototype: Railway

For a quick prototype deployment, I recommend **Railway** because:
- Fastest setup (5 minutes)
- Free tier is generous
- Automatic deployments
- Built-in environment variable management
- Custom domains available
- Good performance

## Next Steps for Production

When you're ready for a production deployment:
1. Add authentication/authorization
2. Implement proper caching
3. Add rate limiting
4. Set up monitoring and logging
5. Use a proper database connection pool
6. Add health checks
7. Implement proper error handling
8. Add security headers

## Troubleshooting

**Common Issues:**
1. **Import errors**: Make sure the parent directory structure is preserved
2. **MongoDB connection**: Verify your connection string and network access
3. **Port issues**: Ensure the port is properly exposed and not blocked
4. **Environment variables**: Double-check all required variables are set

**Debug Commands:**
```bash
# Test local deployment
python run.py

# Test with Docker
docker-compose up

# Check environment variables
echo $MONGODB_URI
```
