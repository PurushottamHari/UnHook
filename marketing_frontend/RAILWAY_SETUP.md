# Railway Deployment Setup for UnHook Marketing Frontend

Since your repository is at the UnHook level and the marketing frontend app is in a subdirectory, here's how to configure Railway properly.

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

- Set **Root Directory** to: `marketing_frontend`
- This tells Railway to treat the `marketing_frontend` folder as the project root

#### **Build Method**

- Railway will automatically detect this as a Node.js project
- The `railway.json` file will configure the build and start commands
- Railway's current build system will handle the deployment

**Note**: The `railway.json` file in the `marketing_frontend` directory will automatically configure the build and start commands for you. You don't need to manually set them.

### Step 3: Set Environment Variables

In Railway dashboard, go to **Variables** tab and add:

```
MONGODB_URI=<uri>
DATABASE_NAME=youtube_newspaper
NEXT_PUBLIC_APP_URL=https://your-app-name.railway.app
NODE_ENV=production
```

**Note**: Railway automatically sets the `PORT` environment variable, so you don't need to set it manually.

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
railway variables set RAILWAY_ROOT_DIRECTORY=marketing_frontend

# Set environment variables
railway variables set MONGODB_URI="your_uri"
railway variables set DATABASE_NAME="youtube_newspaper"
railway variables set NEXT_PUBLIC_APP_URL="https://your-app-name.railway.app"
railway variables set NODE_ENV="production"

# Deploy
railway up
```

## 📁 Repository Structure

Your repository structure should look like this:

```
UnHook/
├── marketing_frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── api/
│   │   │   └── ...
│   │   └── components/
│   ├── package.json
│   ├── next.config.ts
│   ├── railway.json
│   └── env.example
├── scrappy_frontend_app/
├── data_collector_service/
├── data_processing_service/
└── other_folders...
```

## ⚠️ Important Notes

1. **Root Directory**: Make sure to set `marketing_frontend` as the root directory in Railway
2. **Node.js Version**: Railway will automatically detect Node.js from your `package.json`
3. **Environment Variables**: All sensitive data should be in Railway's environment variables, not in code
4. **Dependencies**: Railway will install from `marketing_frontend/package.json`
5. **Build Process**: Railway will run `npm ci && npm run build` then `npm start`

## 🐛 Troubleshooting

### If Build Fails:

- Check that the root directory is set to `marketing_frontend`
- Verify that `package.json` exists in the marketing_frontend folder
- Check Railway logs for specific error messages

### If Import Errors Occur:

- The app uses Next.js which handles its own module resolution
- Make sure all dependencies are listed in `package.json`
- Check that the build process completes successfully

### If MongoDB Connection Fails:

- Verify your MongoDB URI is correct
- Check that your MongoDB cluster allows connections from Railway's IP ranges
- Ensure the database name is correct
- Test the connection using the `/api/health` endpoint

### If Environment Variables Don't Work:

- Make sure variables are set in Railway dashboard
- Check that variable names match exactly (case-sensitive)
- Restart the deployment after adding new environment variables

## 🎯 Quick Setup Summary

1. **Repository**: Connect your UnHook repository to Railway
2. **Root Directory**: Set to `marketing_frontend`
3. **Configuration**: Railway will automatically use the `railway.json` file in the marketing_frontend directory
4. **Environment Variables**: Add all required variables
5. **Deploy**: Click deploy and wait for completion

**That's it!** Railway will automatically detect and use the configuration files in the `marketing_frontend` directory.

Your app will be available at a Railway-generated URL that you can access from anywhere!

## 🔍 Health Check

Once deployed, you can check if your app is running properly by visiting:

- `https://your-app-name.railway.app/api/health`

This endpoint will return the health status of your application.
