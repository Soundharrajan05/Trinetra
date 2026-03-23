# TRINETRA AI - Deployment Guide

## Render Deployment (Recommended)

### Option 1: Using render.yaml (Automatic)

1. **Push to GitHub**: Ensure your code is in a GitHub repository
2. **Connect to Render**: 
   - Go to [render.com](https://render.com)
   - Connect your GitHub repository
   - Render will automatically detect `render.yaml`
3. **Deploy**: Render will create both API and Dashboard services automatically

### Option 2: Manual Render Deployment

#### Deploy API Service:
1. **Create Web Service** on Render
2. **Configuration**:
   - **Build Command**: `pip install --upgrade pip && pip install -r requirements-deploy.txt`
   - **Start Command**: `python deploy_api.py`
   - **Environment**: `Python 3.11`
   - **Plan**: Starter (Free)

#### Deploy Dashboard Service:
1. **Create Web Service** on Render
2. **Configuration**:
   - **Build Command**: `pip install --upgrade pip && pip install -r requirements-deploy.txt`
   - **Start Command**: `streamlit run deploy_dashboard.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`
   - **Environment Variables**:
     - `API_BASE_URL`: `https://your-api-service.onrender.com`
   - **Plan**: Starter (Free)

## Alternative Deployment Options

### Docker Deployment

```bash
# Build the image
docker build -t trinetra-ai .

# Run the container
docker run -p 8000:8000 trinetra-ai
```

### Heroku Deployment

1. **Create Procfile**:
```
web: python deploy_api.py
```

2. **Deploy**:
```bash
heroku create your-app-name
git push heroku main
```

## Troubleshooting Render Build Issues

### Common Issues and Solutions:

#### 1. Pandas Installation Error
**Error**: `metadata-generation-failed × Encountered error while generating package metadata pandas`

**Solution**: Use `requirements-deploy.txt` with fixed pandas version:
```
pandas==2.0.3
numpy==1.24.4
```

#### 2. Python Version Issues
**Solution**: Add to render.yaml:
```yaml
envVars:
  - key: PYTHON_VERSION
    value: 3.11.0
```

#### 3. Build Timeout
**Solution**: Reduce dependencies in `requirements-deploy.txt` (remove optional packages)

#### 4. Memory Issues
**Solution**: Use Render's paid plans or optimize code for lower memory usage

## Environment Variables

### Required for Dashboard:
- `API_BASE_URL`: URL of your deployed API service

### Optional:
- `PORT`: Port number (automatically set by Render)
- `PYTHON_VERSION`: Python version (3.11.0 recommended)

## File Structure for Deployment

```
trinetra-ai/
├── deploy_api.py              # Deployment-ready API
├── deploy_dashboard.py        # Deployment-ready Dashboard  
├── requirements-deploy.txt    # Minimal dependencies
├── render.yaml               # Render configuration
├── Dockerfile               # Docker configuration
└── DEPLOYMENT_GUIDE.md      # This guide
```

## Testing Deployment

### Local Testing:
```bash
# Test API
python deploy_api.py

# Test Dashboard (in another terminal)
streamlit run deploy_dashboard.py
```

### Production Testing:
1. **API Health Check**: `https://your-api.onrender.com/health`
2. **Dashboard**: `https://your-dashboard.onrender.com`

## Performance Optimization

### For Free Tier:
1. **Use sample data** (included in deploy_api.py)
2. **Minimal dependencies** (requirements-deploy.txt)
3. **Efficient caching** (built into deployment version)
4. **Reduced features** (no heavy ML training)

### For Paid Tier:
1. **Full feature set** (use original files)
2. **Real data integration** (add database connections)
3. **Advanced ML models** (include full scikit-learn features)

## Support

If you encounter deployment issues:
1. Check Render build logs
2. Verify all files are committed to Git
3. Ensure requirements-deploy.txt is used
4. Test locally first with deploy_api.py

## Success Indicators

✅ **API Deployed Successfully**:
- Health check returns `{"status": "ok"}`
- `/transactions` returns sample data
- All endpoints respond within 30 seconds

✅ **Dashboard Deployed Successfully**:
- Streamlit interface loads
- KPI metrics display
- Transaction table shows data
- Explanations work without errors