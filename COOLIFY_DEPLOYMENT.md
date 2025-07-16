# Coolify Deployment Guide

## Overview
This guide explains how to deploy the Betting Analytics API and Frontend to Coolify.

## Project Structure
```
├── api_server.py          # FastAPI server
├── betting_database.py    # Database creation script
├── json_query.py          # Analytics logic
├── Dockerfile            # Multi-stage Docker build
├── docker-compose.yml    # Local development
├── requirements.txt      # Python dependencies
├── new/                 # Next.js frontend
│   ├── app/
│   ├── components/
│   └── package.json
└── betting_transactions.db  # SQLite database (will be mounted)
```

## Coolify Configuration

### 1. Repository Setup
- Push your code to a Git repository (GitHub, GitLab, etc.)
- Ensure all files are committed

### 2. Coolify Service Configuration

#### Basic Settings:
- **Name**: `betting-analytics`
- **Repository**: Your Git repo URL
- **Branch**: `main` (or your preferred branch)

#### Build Settings:
- **Build Pack**: `Dockerfile`
- **Dockerfile Path**: `Dockerfile`
- **Port**: `8000`

#### Environment Variables:
```env
MONAD_HYPERSYNC_URL=https://monad-testnet.hypersync.xyz
HYPERSYNC_BEARER_TOKEN=your_token_here
NEXT_PUBLIC_API_URL=http://your-domain.com
```

#### Volumes:
- **Source**: `/app/betting_transactions.db`
- **Destination**: `/path/to/your/database/betting_transactions.db`

### 3. Database Setup

#### Option A: Upload Existing Database
1. Upload your `betting_transactions.db` file to the server
2. Mount it as a volume in Coolify
3. Set the volume path to `/app/betting_transactions.db`

#### Option B: Generate Database on Server
1. Add a build step to run `betting_database.py`
2. Ensure environment variables are set for blockchain access

### 4. Domain Configuration
- **Domain**: Your custom domain (e.g., `analytics.yourdomain.com`)
- **SSL**: Enable Let's Encrypt SSL
- **Proxy**: Coolify will handle this automatically

## Deployment Steps

### 1. Prepare Your Repository
```bash
# Ensure all files are committed
git add .
git commit -m "Add Coolify deployment files"
git push origin main
```

### 2. Create Coolify Service
1. Go to your Coolify dashboard
2. Click "New Service" → "Application"
3. Select your repository
4. Configure as described above

### 3. Deploy
1. Click "Deploy" in Coolify
2. Monitor the build logs
3. Wait for deployment to complete

### 4. Verify Deployment
- Visit your domain
- Check API endpoints: `https://your-domain.com/api/analytics`
- Check API docs: `https://your-domain.com/docs`

## Local Testing (Before Coolify)

### Test Docker Build:
```bash
docker build -t betting-analytics .
docker run -p 8000:8000 -v $(pwd)/betting_transactions.db:/app/betting_transactions.db betting-analytics
```

### Test with Docker Compose:
```bash
docker-compose up --build
```

## Troubleshooting

### Common Issues:

1. **Database Not Found**
   - Ensure the database file is mounted correctly
   - Check volume paths in Coolify

2. **Build Failures**
   - Check Docker logs in Coolify
   - Verify all dependencies are in requirements.txt

3. **API Errors**
   - Check environment variables
   - Verify database connectivity

4. **Frontend Not Loading**
   - Check if Next.js build completed
   - Verify static file serving

### Logs:
- Check Coolify logs for build issues
- Check application logs for runtime errors
- Use `docker logs` for container debugging

## Maintenance

### Database Updates:
1. Run `betting_database.py` locally
2. Upload new database file
3. Restart the service in Coolify

### Code Updates:
1. Push changes to Git
2. Coolify will auto-deploy (if configured)
3. Or manually trigger deployment

### Monitoring:
- Use Coolify's built-in monitoring
- Set up health checks
- Monitor API response times

## Security Notes

1. **Environment Variables**: Never commit sensitive data
2. **Database**: Keep database file secure
3. **SSL**: Always enable SSL in production
4. **CORS**: Configure CORS properly for production

## Performance Optimization

1. **Database**: Consider SQLite to PostgreSQL migration for high traffic
2. **Caching**: Add Redis for API response caching
3. **CDN**: Use CDN for static assets
4. **Scaling**: Configure auto-scaling in Coolify if needed 