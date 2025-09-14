# Railway Deployment Setup for UnHook Repository

Since your repository is at the UnHook level and the scrappy frontend app is in a subdirectory, here's how to configure Railway properly.

## 🚀 Railway Deployment Steps

### Step 1: Connect Repository to Railway

1. Go to [railway.app](https://railway.app)
2. Sign up/Login with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your **UnHook** repository

### Step 2: Configure Railway Settings

In the Railway dashboard, you need to configure the following:

#### **Root Directory**
- Set **Root Directory** to: `scrappy_frontend_app`
- This tells Railway to treat the `scrappy_frontend_app` folder as the project root

#### **Build Method**
- Make sure Railway uses **Nixpacks** (not Docker)
- The `railway.json` file will automatically configure this
- If Railway tries to use Docker, you can force Nixpacks in the settings

**Note**: The `railway.json` file in the `scrappy_frontend_app` directory will automatically configure the build and start commands for you. You don't need to manually set them.

### Step 3: Set Environment Variables

In Railway dashboard, go to **Variables** tab and add:

```
MONGODB_URI=mongodb+srv://purushottam:test12345@cluster0.xv0gfbm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
DATABASE_NAME=youtube_newspaper
FLASK_DEBUG=False
FLASK_HOST=0.0.0.0
```

**Note**: Railway automatically sets the `PORT` environment variable, so you don't need to set `FLASK_PORT`.

### Step 4: Deploy

1. Click **Deploy** button
2. Railway will automatically detect the `railway.json` configuration
3. Railway will build and deploy your app using the settings from the config file
4. You'll get a public URL like: `https://your-app-name.railway.app`

## 🔧 Alternative: Using Railway CLI

If you prefer using the Railway CLI:

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize in your UnHook repository root
railway init

# Set the root directory
railway variables set RAILWAY_ROOT_DIRECTORY=scrappy_frontend_app

# Set environment variables
railway variables set MONGODB_URI="mongodb+srv://purushottam:test12345@cluster0.xv0gfbm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
railway variables set DATABASE_NAME="youtube_newspaper"
railway variables set FLASK_DEBUG="False"
railway variables set FLASK_HOST="0.0.0.0"
railway variables set FLASK_PORT="5001"

# Deploy
railway up
```

## 📁 Repository Structure

Your repository structure should look like this:
```
UnHook/
├── scrappy_frontend_app/
│   ├── app.py
│   ├── run.py
│   ├── requirements.txt
│   ├── config.py
│   ├── railway.json
│   ├── Procfile
│   └── templates/
├── data_collector_service/
├── data_processing_service/
└── other_folders...
```

## ⚠️ Important Notes

1. **Root Directory**: Make sure to set `scrappy_frontend_app` as the root directory in Railway
2. **Python Path**: The app imports from parent directories, so Railway needs access to the full repository
3. **Environment Variables**: All sensitive data should be in Railway's environment variables, not in code
4. **Dependencies**: Railway will install from `scrappy_frontend_app/requirements.txt`

## 🐛 Troubleshooting

### If Build Fails:
- Check that the root directory is set to `scrappy_frontend_app`
- Verify that `requirements.txt` exists in the scrappy_frontend_app folder
- **Make sure Railway is using Nixpacks, not Docker** (check the build logs)
- If Railway is using Docker, go to Settings → Build and change to Nixpacks
- Check Railway logs for specific error messages

### If Import Errors Occur:
- The app imports from parent directories (`sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))`)
- Railway needs the full repository structure
- Make sure you're deploying from the main UnHook repository, not just the scrappy_frontend_app folder

### If MongoDB Connection Fails:
- Verify your MongoDB URI is correct
- Check that your MongoDB cluster allows connections from Railway's IP ranges
- Ensure the database name is correct

## 🎯 Quick Setup Summary

1. **Repository**: Connect your UnHook repository to Railway
2. **Root Directory**: Set to `scrappy_frontend_app`
3. **Configuration**: Railway will automatically use the `railway.json` file in the scrappy_frontend_app directory
4. **Environment Variables**: Add all required variables
5. **Deploy**: Click deploy and wait for completion

**That's it!** Railway will automatically detect and use the configuration files in the `scrappy_frontend_app` directory.

Your app will be available at a Railway-generated URL that you can access from anywhere!
