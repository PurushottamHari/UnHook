# UnHook Marketing Frontend - Deployment Guide

This guide provides multiple deployment options for the UnHook Marketing Frontend app.

## 🚨 Security Fix Applied

**IMPORTANT**: The MongoDB credentials have been moved to environment variables. Make sure to:

1. Create a `.env.local` file with your actual MongoDB credentials
2. Never commit the `.env.local` file to version control
3. Use the provided `env.example` as a template

## Quick Deployment Options

### Option 1: Railway (Recommended for Quick Deploy)

Railway is the fastest and easiest option for a prototype deployment.

**Steps:**
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Create a new project
4. Connect your GitHub repository
5. Set **Root Directory** to `marketing_frontend`
6. Set environment variables in Railway dashboard:
   ```
   MONGODB_URI=your_mongodb_connection_string
   DATABASE_NAME=youtube_newspaper
   NEXT_PUBLIC_APP_URL=https://your-app-name.railway.app
   NODE_ENV=production
   ```
7. Deploy!

**Pros:**
- ✅ Free tier available
- ✅ Automatic deployments from GitHub
- ✅ Built-in environment variable management
- ✅ Custom domains available
- ✅ SSL certificates included
- ✅ Optimized for Next.js

### Option 2: Vercel (Recommended for Next.js)

Vercel is the creator of Next.js and provides excellent Next.js optimization.

**Steps:**
1. Go to [vercel.com](https://vercel.com)
2. Connect your GitHub repository
3. Set **Root Directory** to `marketing_frontend`
4. Set environment variables in Vercel dashboard
5. Deploy!

**Pros:**
- ✅ Free tier available
- ✅ Optimized for Next.js
- ✅ Automatic SSL
- ✅ Global CDN
- ✅ Easy GitHub integration
- ✅ Preview deployments for PRs

### Option 3: Netlify

**Steps:**
1. Go to [netlify.com](https://netlify.com)
2. Connect your GitHub repository
3. Set **Base Directory** to `marketing_frontend`
4. Set **Build Command** to `npm run build`
5. Set **Publish Directory** to `out` (if using static export)
6. Set environment variables in Netlify dashboard
7. Deploy!

**Pros:**
- ✅ Free tier available
- ✅ Automatic SSL
- ✅ Easy GitHub integration
- ✅ Form handling
- ✅ Edge functions

### Option 4: Render

**Steps:**
1. Go to [render.com](https://render.com)
2. Connect your GitHub repository
3. Create a new Web Service
4. Use these settings:
   - **Root Directory**: `marketing_frontend`
   - **Build Command**: `npm ci && npm run build`
   - **Start Command**: `npm start`
   - **Environment**: Node.js
5. Set environment variables in Render dashboard
6. Deploy!

**Pros:**
- ✅ Free tier available
- ✅ Automatic SSL
- ✅ Easy GitHub integration
- ✅ Good performance

### Option 5: DigitalOcean App Platform

**Steps:**
1. Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
2. Create a new app from GitHub
3. Configure:
   - **Source**: Your GitHub repository
   - **Type**: Web Service
   - **Root Directory**: `marketing_frontend`
   - **Build Command**: `npm ci && npm run build`
   - **Run Command**: `npm start`
4. Set environment variables
5. Deploy!

**Pros:**
- ✅ Good performance
- ✅ Reasonable pricing
- ✅ Easy scaling
- ✅ Managed databases available

### Option 6: Docker Deployment (Any VPS)

If you have a VPS or server:

**Steps:**
1. Copy the entire project to your server
2. Create a `.env.local` file with your credentials
3. Run with Docker:
   ```bash
   cd marketing_frontend
   docker build -t unhook-marketing .
   docker run -p 3000:3000 --env-file .env.local unhook-marketing
   ```

**For manual deployment:**
```bash
# Install dependencies
npm ci

# Set environment variables
export MONGODB_URI="your_mongodb_connection_string"
export DATABASE_NAME="youtube_newspaper"
export NEXT_PUBLIC_APP_URL="https://your-domain.com"
export NODE_ENV="production"

# Build the application
npm run build

# Start the application
npm start
```

## Environment Variables Required

Create a `.env.local` file with these variables:

```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
DATABASE_NAME=youtube_newspaper
NEXT_PUBLIC_APP_URL=https://your-app-name.railway.app
NODE_ENV=production
```

## Pre-Deployment Checklist

- [ ] MongoDB credentials moved to environment variables ✅
- [ ] `.env.local` file created with actual credentials
- [ ] `.env.local` file added to `.gitignore`
- [ ] Dependencies listed in `package.json`
- [ ] App runs locally with environment variables
- [ ] No hardcoded secrets in code
- [ ] Health check endpoint available at `/api/health`

## Post-Deployment

1. Test the deployed app
2. Verify all features work
3. Check that waitlist form can save to MongoDB
4. Test article viewing functionality
5. Monitor logs for any errors
6. Test the health check endpoint: `/api/health`

## Recommended for Marketing Site: Vercel

For a marketing frontend, I recommend **Vercel** because:
- Built specifically for Next.js
- Excellent performance and SEO optimization
- Free tier is generous
- Automatic deployments
- Built-in environment variable management
- Custom domains available
- Global CDN for fast loading

## Next Steps for Production

When you're ready for a production deployment:
1. Add authentication/authorization
2. Implement proper caching
3. Add rate limiting
4. Set up monitoring and logging
5. Use a proper database connection pool
6. Add security headers
7. Implement proper error handling
8. Add analytics tracking
9. Set up backup strategies

## Troubleshooting

**Common Issues:**
1. **Build errors**: Make sure all dependencies are in `package.json`
2. **MongoDB connection**: Verify your connection string and network access
3. **Environment variables**: Double-check all required variables are set
4. **Port issues**: Next.js automatically handles port configuration

**Debug Commands:**
```bash
# Test local deployment
npm run dev

# Test production build locally
npm run build
npm start

# Check environment variables
echo $MONGODB_URI
```

**Health Check:**
Visit `/api/health` on your deployed app to verify it's running properly.

## Performance Optimization

For better performance in production:
1. Enable Next.js Image Optimization
2. Use Next.js built-in caching
3. Implement proper SEO meta tags
4. Use a CDN for static assets
5. Enable compression
6. Monitor Core Web Vitals
