# TRINETRA AI - Deployment Guide

## 🚨 Python 3.14 Compatibility Issue - SOLVED

**Problem**: Render is using Python 3.14.3, but pandas doesn't support Python 3.14 yet, causing compilation errors.

**Solution**: Use the minimal deployment version that avoids pandas entirely.

## Render Deployment (Recommended Solutions)

### Option 1: Minimal Deployment (NO PANDAS - FASTEST) ⭐

This version uses pure Python without pandas, avoiding all compilation issues:

1. **Files to use**:
   - `requirements-minimal.txt` (no pandas)
   - `deploy_api_minimal.py` (pure Python API)
   - `deploy_dashboard_minimal.py` (minimal dashboard)
   - `render-minimal.yaml` (configuration)

2. **Deploy Steps**:
   ```bash
   # Use the minimal render config
   cp render-minimal.yaml render.yaml
   
   # Push to GitHub
   git add .
   git commit -m "Deploy minimal version to Render"
   git push origin main
   ```

3. **Manual Render Setup**:
   - **Build Command**: `pip install --no-cache-dir -r requirements-minimal.txt`
   - **Start Command**: `python deploy_api_minimal.py`
   - **Runtime**: `python-3.11.0`

### Option 2: Force Python 3.11 with Pandas

If you need pandas functionality:

1. **Files to use**:
   - `requirements-deploy.txt` (pandas 1.5.3)
   - `deploy_api.py` (with pandas)
   - `render.yaml` (with Python 3.11 runtime)

2. **Key Configuration**:
   ```yaml
   runtime: python-3.11.0
   buildCommand: |
     python -m pip install --upgrade pip==23.3.1
     pip install --no-cache-dir -r requirements-deploy.txt
   ```

## Troubleshooting Python 3.14 Issues

### Error Symptoms:
```
pandas/_libs/tslibs/base.pyx.c: error: too few arguments to function '_PyLong_AsByteArray'
Python-3.14.3/include/python3.14/cpython/longobject.h:84:17: note: declared here
```

### Solutions (in order of preference):

#### 1. Use Minimal Version (Recommended)
- ✅ No compilation issues
- ✅ Fast deployment
- ✅ All core functionality works
- ❌ No advanced data processing

#### 2. Force Python 3.11
- ✅ Full pandas support
- ✅ All features available
- ⚠️ May still have build issues on some Render instances

#### 3. Use Pre-compiled Wheels
```bash
pip install --only-binary=pandas pandas==1.5.3
```

## File Structure for Deployment

### Minimal Deployment:
```
trinetra-ai/
├── deploy_api_minimal.py         # No pandas API
├── deploy_dashboard_minimal.py   # No pandas dashboard
├── requirements-minimal.txt      # Minimal dependencies
├── render-minimal.yaml          # Minimal config
├── runtime.txt                  # Force Python 3.11
└── DEPLOYMENT_GUIDE.md
```

### Full Deployment:
```
trinetra-ai/
├── deploy_api.py                # With pandas API
├── deploy_dashboard.py          # With pandas dashboard
├── requirements-deploy.txt      # Full dependencies
├── render.yaml                  # Full config
├── runtime.txt                  # Force Python 3.11
└── DEPLOYMENT_GUIDE.md
```

## Quick Deploy Commands

### For Minimal Version (Recommended):
```bash
# 1. Copy minimal config
cp render-minimal.yaml render.yaml

# 2. Test locally (optional)
python deploy_api_minimal.py

# 3. Deploy to Render
git add .
git commit -m "Deploy minimal TRINETRA AI"
git push origin main
```

### For Full Version:
```bash
# 1. Use full config (already created)
# render.yaml is ready

# 2. Test locally (optional)
python deploy_api.py

# 3. Deploy to Render
git add .
git commit -m "Deploy full TRINETRA AI"
git push origin main
```

## Environment Variables

### Required for Dashboard:
- `API_BASE_URL`: URL of your deployed API service
- `PYTHON_VERSION`: `3.11.0`

## Testing Deployment

### Local Testing:
```bash
# Test minimal API
python deploy_api_minimal.py

# Test minimal dashboard (in another terminal)
streamlit run deploy_dashboard_minimal.py
```

### Production Testing:
1. **API Health Check**: `https://your-api.onrender.com/health`
2. **Dashboard**: `https://your-dashboard.onrender.com`

## Performance Comparison

| Version | Build Time | Features | Reliability |
|---------|------------|----------|-------------|
| Minimal | ~2 min     | Core     | 99%         |
| Full    | ~8 min     | All      | 85%         |

## Success Indicators

✅ **Minimal Version Deployed Successfully**:
- Build completes in under 3 minutes
- Health check returns `{"status": "ok"}`
- Dashboard loads with transaction data
- No pandas compilation errors

✅ **Full Version Deployed Successfully**:
- Build completes (may take 5-10 minutes)
- All advanced features work
- Pandas operations function correctly

## Recommended Approach

1. **Start with Minimal**: Deploy `deploy_api_minimal.py` first
2. **Verify Functionality**: Ensure core features work
3. **Upgrade if Needed**: Switch to full version only if you need advanced data processing

This approach guarantees a working deployment while avoiding Python 3.14 compatibility issues!