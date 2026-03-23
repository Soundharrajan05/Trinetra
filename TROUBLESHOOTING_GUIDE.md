# 🔧 TRINETRA AI - Comprehensive Troubleshooting Guide

> Complete troubleshooting reference for the TRINETRA AI Trade Fraud Intelligence System

**Version:** 1.0  
**Last Updated:** 2024  
**Audience:** Developers, System Administrators, Demo Presenters

---

## 📋 Table of Contents

1. [Quick Diagnostics](#quick-diagnostics)
2. [Installation & Setup Issues](#installation--setup-issues)
3. [Data Loading Problems](#data-loading-problems)
4. [ML Model Issues](#ml-model-issues)
5. [API Connectivity Problems](#api-connectivity-problems)
6. [Gemini API Integration Issues](#gemini-api-integration-issues)
7. [Dashboard Rendering Problems](#dashboard-rendering-problems)
8. [Performance Issues](#performance-issues)
9. [Environment & Dependency Issues](#environment--dependency-issues)
10. [Testing & CI/CD Issues](#testing--cicd-issues)
11. [Demo & Presentation Issues](#demo--presentation-issues)
12. [Advanced Debugging](#advanced-debugging)
13. [Log Analysis](#log-analysis)
14. [Recovery Procedures](#recovery-procedures)

---

## Quick Diagnostics

### System Health Check

Run this quick diagnostic script to identify common issues:

```bash
# Check Python version
python --version  # Should be 3.8+

# Check if virtual environment is activated
which python  # Should point to venv

# Verify dataset exists
ls -la data/trinetra_trade_fraud_dataset_1000_rows_complex.csv

# Check if ports are available
netstat -an | grep 8000  # API port
netstat -an | grep 8501  # Dashboard port

# Verify dependencies
pip list | grep -E "fastapi|streamlit|scikit-learn|google-generativeai"

# Check logs for errors
tail -n 50 logs/trinetra_main.log
```

### Quick Status Indicators

| Indicator | Meaning | Action |
|-----------|---------|--------|
| ✅ Green checkmarks in startup | System healthy | Proceed normally |
| ⚠️ Yellow warnings | Non-critical issues | Review warnings, system may work |
| ❌ Red errors | Critical failures | Check specific error section below |
| 🛑 Shutdown messages | Graceful termination | Normal if you pressed Ctrl+C |

---

## Installation & Setup Issues

### Issue 1: Python Version Incompatibility

**Symptoms:**
```
ERROR: This package requires Python 3.8 or higher
SyntaxError: invalid syntax
```

**Diagnosis:**
```bash
python --version
python3 --version
```

**Solutions:**

**Option A: Install Python 3.8+**
- Windows: Download from [python.org](https://www.python.org/downloads/)
- macOS: `brew install python@3.11`
- Linux: `sudo apt install python3.11`

**Option B: Use pyenv for version management**
```bash
# Install pyenv
curl https://pyenv.run | bash

# Install Python 3.11
pyenv install 3.11.0
pyenv local 3.11.0
```


### Issue 2: Virtual Environment Creation Fails

**Symptoms:**
```
Error: Command 'python -m venv trinetra_env' failed
The virtual environment was not created successfully
```

**Solutions:**

**Windows:**
```bash
# Install venv module
python -m pip install --upgrade pip
python -m pip install virtualenv

# Create environment with virtualenv
virtualenv trinetra_env

# If PowerShell execution policy blocks activation
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**macOS/Linux:**
```bash
# Install python3-venv
sudo apt install python3-venv  # Ubuntu/Debian
sudo yum install python3-venv  # CentOS/RHEL

# Create environment
python3 -m venv trinetra_env

# Fix permissions if needed
chmod +x trinetra_env/bin/activate
```

### Issue 3: Dependency Installation Failures

**Symptoms:**
```
ERROR: Could not find a version that satisfies the requirement
ERROR: Failed building wheel for package
```

**Diagnosis:**
```bash
# Check pip version
pip --version  # Should be 20.0+

# Check available disk space
df -h  # Linux/macOS
wmic logicaldisk get size,freespace,caption  # Windows
```

**Solutions:**

**Solution A: Upgrade pip and setuptools**
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

**Solution B: Install dependencies one by one**
```bash
# Core dependencies first
pip install fastapi uvicorn streamlit pandas numpy scikit-learn

# Then visualization
pip install plotly networkx

# Then AI integration
pip install google-generativeai

# Finally testing tools
pip install pytest hypothesis pytest-cov
```

**Solution C: Use conda (alternative)**
```bash
conda create -n trinetra python=3.11
conda activate trinetra
pip install -r requirements.txt
```


### Issue 4: Port Already in Use

**Symptoms:**
```
OSError: [Errno 48] Address already in use
ERROR: [Errno 98] Address already in use
uvicorn.error: Can't bind to port 8000
```

**Diagnosis:**
```bash
# Windows
netstat -ano | findstr :8000
netstat -ano | findstr :8501

# macOS/Linux
lsof -i :8000
lsof -i :8501
netstat -tulpn | grep 8000
```

**Solutions:**

**Solution A: Kill existing processes**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# macOS/Linux
lsof -ti:8000 | xargs kill -9
lsof -ti:8501 | xargs kill -9

# Or kill by name
pkill -f uvicorn
pkill -f streamlit
```

**Solution B: Change ports**

Edit `main.py`:
```python
API_PORT = 8001  # Change from 8000
DASHBOARD_PORT = 8502  # Change from 8501
```

Or use environment variables:
```bash
export API_PORT=8001
export STREAMLIT_PORT=8502
python main.py
```

**Solution C: Use different network interface**
```python
# In main.py, change:
API_HOST = "127.0.0.1"  # Instead of "0.0.0.0"
```

---

## Data Loading Problems

### Issue 5: Dataset Not Found

**Symptoms:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'data/trinetra_trade_fraud_dataset_1000_rows_complex.csv'
❌ Dataset not found: data/trinetra_trade_fraud_dataset_1000_rows_complex.csv
```

**Diagnosis:**
```bash
# Check current directory
pwd

# List data directory
ls -la data/

# Check if file exists
test -f data/trinetra_trade_fraud_dataset_1000_rows_complex.csv && echo "File exists" || echo "File missing"
```

**Solutions:**

**Solution A: Verify file location**
```bash
# Ensure you're in project root
cd /path/to/trinetra-ai-fraud-detection

# Check file exists
ls data/trinetra_trade_fraud_dataset_1000_rows_complex.csv
```

**Solution B: Check file permissions**
```bash
# Linux/macOS
chmod 644 data/trinetra_trade_fraud_dataset_1000_rows_complex.csv

# Windows - Right-click file → Properties → Security → Edit permissions
```

**Solution C: Verify file integrity**
```bash
# Check file size (should be ~500KB)
ls -lh data/trinetra_trade_fraud_dataset_1000_rows_complex.csv

# Check first few lines
head -n 5 data/trinetra_trade_fraud_dataset_1000_rows_complex.csv
```


### Issue 6: CSV Parsing Errors

**Symptoms:**
```
ParserError: Error tokenizing data
ValueError: could not convert string to float
pandas.errors.EmptyDataError: No columns to parse from file
```

**Diagnosis:**
```bash
# Check file encoding
file -I data/trinetra_trade_fraud_dataset_1000_rows_complex.csv

# Check for special characters
head -n 1 data/trinetra_trade_fraud_dataset_1000_rows_complex.csv | od -c

# Validate CSV structure
python -c "import pandas as pd; df = pd.read_csv('data/trinetra_trade_fraud_dataset_1000_rows_complex.csv', nrows=5); print(df.head())"
```

**Solutions:**

**Solution A: Fix encoding issues**
```python
# In backend/data_loader.py, modify load_dataset():
df = pd.read_csv(
    file_path,
    encoding='utf-8-sig',  # Handle BOM
    parse_dates=['date', 'shipment_date', 'arrival_date'],
    on_bad_lines='skip'  # Skip problematic lines
)
```

**Solution B: Handle missing values**
```python
# Add to data_loader.py
df = df.fillna({
    'price_deviation': 0,
    'route_anomaly': 0,
    'company_risk_score': 0,
    'port_activity_index': 1.0
})
```

**Solution C: Validate schema**
```python
# Check required columns
required_columns = [
    'transaction_id', 'product', 'unit_price', 'market_price',
    'price_deviation', 'route_anomaly', 'company_risk_score'
]

missing_cols = set(required_columns) - set(df.columns)
if missing_cols:
    raise ValueError(f"Missing required columns: {missing_cols}")
```

### Issue 7: Date Parsing Failures

**Symptoms:**
```
ValueError: time data '2023-01-01' does not match format
ParserError: Unable to parse date column
```

**Solutions:**

```python
# In backend/data_loader.py
import pandas as pd
from datetime import datetime

# Flexible date parsing
df = pd.read_csv(
    file_path,
    parse_dates=['date', 'shipment_date', 'arrival_date'],
    date_parser=lambda x: pd.to_datetime(x, errors='coerce')
)

# Handle invalid dates
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df = df.dropna(subset=['date'])  # Remove rows with invalid dates
```

---

## ML Model Issues

### Issue 8: Model Training Fails

**Symptoms:**
```
ValueError: Input contains NaN, infinity or a value too large
sklearn.exceptions.NotFittedError: This IsolationForest instance is not fitted yet
MemoryError: Unable to allocate array
```

**Diagnosis:**
```python
# Check for NaN values
import pandas as pd
df = pd.read_csv('data/trinetra_trade_fraud_dataset_1000_rows_complex.csv')
print(df.isnull().sum())

# Check for infinite values
print(df.select_dtypes(include=['float64', 'int64']).apply(lambda x: np.isinf(x).sum()))

# Check data types
print(df.dtypes)
```

**Solutions:**

**Solution A: Clean data before training**
```python
# In backend/model.py
def train_model(df: pd.DataFrame) -> IsolationForest:
    # Select feature columns
    feature_cols = [
        'price_anomaly_score', 'route_risk_score',
        'company_network_risk', 'port_congestion_score',
        'shipment_duration_risk', 'volume_spike_score'
    ]
    
    X = df[feature_cols].copy()
    
    # Handle NaN values
    X = X.fillna(0)
    
    # Handle infinite values
    X = X.replace([np.inf, -np.inf], 0)
    
    # Verify no NaN or inf remain
    assert not X.isnull().any().any(), "NaN values still present"
    assert not np.isinf(X).any().any(), "Infinite values still present"
    
    # Train model
    model = IsolationForest(
        n_estimators=100,
        contamination=0.1,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X)
    return model
```


**Solution B: Reduce memory usage**
```python
# For large datasets, use smaller n_estimators
model = IsolationForest(
    n_estimators=50,  # Reduced from 100
    contamination=0.1,
    max_samples=256,  # Limit samples per tree
    random_state=42
)
```

**Solution C: Debug feature engineering**
```python
# In backend/feature_engineering.py
def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    
    # Safe division with zero handling
    df['shipment_duration_risk'] = np.where(
        df['distance_km'] > 0,
        df['shipment_duration_days'] / df['distance_km'],
        0
    )
    
    df['volume_spike_score'] = np.where(
        df['quantity'] > 0,
        df['cargo_volume'] / df['quantity'],
        0
    )
    
    # Clip extreme values
    df['price_anomaly_score'] = df['price_deviation'].abs().clip(0, 10)
    
    return df
```

### Issue 9: Model Loading Fails

**Symptoms:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'models/isolation_forest.pkl'
EOFError: Ran out of input
pickle.UnpicklingError: invalid load key
```

**Solutions:**

**Solution A: Retrain model**
```bash
# Delete corrupted model
rm models/isolation_forest.pkl

# Restart application (will retrain)
python main.py
```

**Solution B: Check model file integrity**
```bash
# Check file size (should be ~100KB)
ls -lh models/isolation_forest.pkl

# Verify it's a valid pickle file
python -c "import joblib; model = joblib.load('models/isolation_forest.pkl'); print(type(model))"
```

**Solution C: Version compatibility**
```python
# In backend/model.py
import joblib
import sklearn

def save_model(model, path: str):
    """Save model with version info"""
    joblib.dump({
        'model': model,
        'sklearn_version': sklearn.__version__,
        'timestamp': datetime.now().isoformat()
    }, path)

def load_model(path: str):
    """Load model with version check"""
    data = joblib.load(path)
    
    if isinstance(data, dict):
        model = data['model']
        saved_version = data.get('sklearn_version')
        
        if saved_version != sklearn.__version__:
            logger.warning(f"Model trained with sklearn {saved_version}, "
                         f"current version is {sklearn.__version__}")
    else:
        model = data
    
    return model
```

### Issue 10: Incorrect Risk Scores

**Symptoms:**
- All transactions classified as SAFE or FRAUD
- Risk scores not distributed properly
- Suspicious category empty

**Diagnosis:**
```python
# Check risk score distribution
import pandas as pd
df = pd.read_csv('data/trinetra_trade_fraud_dataset_1000_rows_complex.csv')
# After scoring
print(df['risk_score'].describe())
print(df['risk_category'].value_counts())
```

**Solutions:**

**Solution A: Adjust thresholds**
```python
# In backend/fraud_detection.py
def classify_risk(df: pd.DataFrame) -> pd.DataFrame:
    """Classify risk with adjusted thresholds"""
    
    # Calculate percentiles for dynamic thresholds
    p33 = df['risk_score'].quantile(0.33)
    p67 = df['risk_score'].quantile(0.67)
    
    def get_risk_category(score):
        if score < p33:
            return "SAFE"
        elif score < p67:
            return "SUSPICIOUS"
        else:
            return "FRAUD"
    
    df['risk_category'] = df['risk_score'].apply(get_risk_category)
    return df
```

**Solution B: Retrain with different contamination**
```python
# In backend/model.py
model = IsolationForest(
    n_estimators=100,
    contamination=0.15,  # Increase from 0.1 if too few frauds detected
    random_state=42
)
```


---

## API Connectivity Problems

### Issue 11: FastAPI Server Won't Start

**Symptoms:**
```
❌ FastAPI server failed to start
ImportError: cannot import name 'app' from 'backend.api'
ModuleNotFoundError: No module named 'backend'
```

**Diagnosis:**
```bash
# Check if backend directory exists
ls -la backend/

# Verify api.py exists
ls -la backend/api.py

# Test import manually
python -c "from backend.api import app; print('Import successful')"
```

**Solutions:**

**Solution A: Fix Python path**
```python
# In main.py, ensure this is at the top:
import sys
from pathlib import Path

backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))
```

**Solution B: Start API manually**
```bash
# Navigate to project root
cd /path/to/trinetra-ai-fraud-detection

# Start uvicorn directly
python -m uvicorn backend.api:app --host 0.0.0.0 --port 8000 --reload
```

**Solution C: Check for syntax errors**
```bash
# Validate Python syntax
python -m py_compile backend/api.py

# Check for import errors
python -c "import backend.api"
```

### Issue 12: API Returns 500 Internal Server Error

**Symptoms:**
```
HTTP 500 Internal Server Error
{"detail": "Internal Server Error"}
```

**Diagnosis:**
```bash
# Check API logs
tail -f logs/trinetra_main.log

# Test API endpoint directly
curl http://localhost:8000/transactions

# Check FastAPI docs
open http://localhost:8000/docs
```

**Solutions:**

**Solution A: Check data availability**
```python
# In backend/api.py, add error handling
from fastapi import HTTPException

@app.get("/transactions")
async def get_all_transactions():
    try:
        if df_global is None or df_global.empty:
            raise HTTPException(status_code=503, detail="Data not loaded")
        
        return {
            "status": "success",
            "data": df_global.to_dict('records')
        }
    except Exception as e:
        logger.error(f"Error in /transactions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

**Solution B: Enable debug mode**
```python
# In backend/api.py
import traceback

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {str(exc)}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "traceback": traceback.format_exc()}
    )
```

### Issue 13: CORS Errors

**Symptoms:**
```
Access to fetch at 'http://localhost:8000/transactions' from origin 'http://localhost:8501' has been blocked by CORS policy
```

**Solutions:**

```python
# In backend/api.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Gemini API Integration Issues

### Issue 14: Gemini API Key Invalid

**Symptoms:**
```
google.api_core.exceptions.PermissionDenied: 403 API key not valid
google.api_core.exceptions.Unauthenticated: 401 Request is missing required authentication credential
```

**Diagnosis:**
```bash
# Check if API key is set
echo $GEMINI_API_KEY

# Check .env file
cat .env | grep GEMINI_API_KEY

# Test API key manually
python -c "import google.generativeai as genai; genai.configure(api_key='YOUR_KEY'); print('API key valid')"
```

**Solutions:**

**Solution A: Get new API key**
1. Visit https://makersuite.google.com/app/apikey
2. Create new API key
3. Add to `.env` file:
```bash
GEMINI_API_KEY=your_new_api_key_here
```

**Solution B: Use fallback system**
```python
# System automatically falls back to rule-based explanations
# Check logs for:
# ⚠️ Gemini API initialization failed: [error]
# Fallback explanations will be used
```

**Solution C: Verify environment loading**
```python
# In backend/ai_explainer.py
from dotenv import load_dotenv
import os

load_dotenv()  # Load .env file

api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    logger.warning("GEMINI_API_KEY not found in environment")
    # Use fallback
```


### Issue 15: Gemini API Rate Limiting

**Symptoms:**
```
google.api_core.exceptions.ResourceExhausted: 429 Quota exceeded
Too many requests to Gemini API
```

**Solutions:**

**Solution A: Implement rate limiting**
```python
# In backend/ai_explainer.py
import time
from functools import wraps

def rate_limit(max_calls=50, time_window=60):
    """Rate limiter decorator"""
    calls = []
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            # Remove old calls outside time window
            calls[:] = [c for c in calls if now - c < time_window]
            
            if len(calls) >= max_calls:
                wait_time = time_window - (now - calls[0])
                logger.warning(f"Rate limit reached, waiting {wait_time:.1f}s")
                time.sleep(wait_time)
                calls[:] = []
            
            calls.append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator

@rate_limit(max_calls=50, time_window=60)
def explain_transaction(transaction: dict) -> str:
    # Gemini API call
    pass
```

**Solution B: Use quota tracking**
```python
# Track API usage
class GeminiQuotaManager:
    def __init__(self, max_calls=50):
        self.max_calls = max_calls
        self.calls_made = 0
        self.reset_time = time.time() + 3600  # Reset hourly
    
    def can_make_call(self):
        if time.time() > self.reset_time:
            self.calls_made = 0
            self.reset_time = time.time() + 3600
        
        return self.calls_made < self.max_calls
    
    def record_call(self):
        self.calls_made += 1
    
    def get_remaining(self):
        return self.max_calls - self.calls_made
```

**Solution C: Use fallback explanations**
```python
# Automatically switch to fallback when quota exceeded
def get_explanation(transaction: dict) -> str:
    try:
        if quota_manager.can_make_call():
            explanation = gemini_explain(transaction)
            quota_manager.record_call()
            return explanation
        else:
            logger.warning("Quota exceeded, using fallback")
            return fallback_explain(transaction)
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return fallback_explain(transaction)
```

### Issue 16: Gemini API Timeout

**Symptoms:**
```
TimeoutError: Request timed out after 10 seconds
google.api_core.exceptions.DeadlineExceeded: Deadline exceeded
```

**Solutions:**

```python
# In backend/ai_explainer.py
import google.generativeai as genai

def explain_transaction(transaction: dict, timeout: int = 15) -> str:
    """Generate explanation with timeout"""
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        # Set timeout in generation config
        response = model.generate_content(
            prompt,
            request_options={'timeout': timeout}
        )
        
        return response.text
        
    except TimeoutError:
        logger.warning(f"Gemini API timeout after {timeout}s")
        return fallback_explain(transaction)
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return fallback_explain(transaction)
```

---

## Dashboard Rendering Problems

### Issue 17: Streamlit Dashboard Won't Start

**Symptoms:**
```
❌ Streamlit dashboard failed to start
ModuleNotFoundError: No module named 'streamlit'
streamlit: command not found
```

**Solutions:**

**Solution A: Reinstall Streamlit**
```bash
pip uninstall streamlit
pip install streamlit==1.28.2

# Verify installation
streamlit --version
```

**Solution B: Start dashboard manually**
```bash
# From project root
streamlit run frontend/dashboard.py --server.port 8501
```

**Solution C: Check Python path**
```bash
# Ensure virtual environment is activated
which python
which streamlit

# Should both point to venv directory
```

### Issue 18: Dashboard Shows "Connection Error"

**Symptoms:**
- Dashboard loads but shows "Unable to connect to backend"
- API calls fail with network errors
- Empty data tables

**Diagnosis:**
```bash
# Check if API is running
curl http://localhost:8000/transactions

# Check API health
curl http://localhost:8000/

# Test from dashboard
python -c "import requests; r = requests.get('http://localhost:8000/transactions'); print(r.status_code)"
```

**Solutions:**

**Solution A: Verify API URL**
```python
# In frontend/dashboard.py
API_BASE_URL = "http://localhost:8000"  # Ensure correct

# Test connection
try:
    response = requests.get(f"{API_BASE_URL}/transactions", timeout=5)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    st.error(f"Cannot connect to API: {e}")
```

**Solution B: Add retry logic**
```python
# In frontend/dashboard.py
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def get_session_with_retries():
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    return session

# Use in API calls
session = get_session_with_retries()
response = session.get(f"{API_BASE_URL}/transactions")
```


### Issue 19: Visualizations Not Rendering

**Symptoms:**
- Blank charts or maps
- "Plotly chart failed to render"
- JavaScript errors in browser console

**Solutions:**

**Solution A: Clear Streamlit cache**
```bash
# Clear cache directory
rm -rf ~/.streamlit/cache

# Or use Streamlit command
streamlit cache clear
```

**Solution B: Update Plotly**
```bash
pip install --upgrade plotly==5.18.0
```

**Solution C: Check data format**
```python
# In frontend/dashboard.py
import plotly.express as px

# Ensure data is not empty
if df is not None and not df.empty:
    fig = px.scatter_geo(
        df,
        lat='export_port_lat',
        lon='export_port_lon',
        # ... other parameters
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No data available for visualization")
```

### Issue 20: Dashboard Performance Issues

**Symptoms:**
- Slow page loads (>10 seconds)
- Unresponsive UI
- High CPU/memory usage

**Solutions:**

**Solution A: Enable caching**
```python
# In frontend/dashboard.py
import streamlit as st

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_transactions():
    response = requests.get(f"{API_BASE_URL}/transactions")
    return response.json()

@st.cache_data(ttl=300)
def load_suspicious_transactions():
    response = requests.get(f"{API_BASE_URL}/suspicious")
    return response.json()
```

**Solution B: Paginate large tables**
```python
# Display only first 100 rows
df_display = df.head(100)
st.dataframe(df_display)

st.info(f"Showing 100 of {len(df)} transactions")
```

**Solution C: Lazy load visualizations**
```python
# Use expanders for heavy visualizations
with st.expander("Route Intelligence Map", expanded=False):
    # Only render when expanded
    fig = create_route_map(df)
    st.plotly_chart(fig)
```

---

## Performance Issues

### Issue 21: Slow Startup Time

**Symptoms:**
- Application takes >60 seconds to start
- "Training model..." takes too long
- High CPU usage during startup

**Diagnosis:**
```bash
# Profile startup time
time python main.py

# Check system resources
top  # Linux/macOS
taskmgr  # Windows
```

**Solutions:**

**Solution A: Use pre-trained model**
```bash
# Ensure model exists before starting
ls -la models/isolation_forest.pkl

# If missing, train once and reuse
python -c "from backend.model import train_model, save_model; from backend.data_loader import load_dataset; from backend.feature_engineering import engineer_features; df = load_dataset('data/trinetra_trade_fraud_dataset_1000_rows_complex.csv'); df = engineer_features(df); model = train_model(df); save_model(model, 'models/isolation_forest.pkl')"
```

**Solution B: Optimize model parameters**
```python
# In backend/model.py
model = IsolationForest(
    n_estimators=50,  # Reduce from 100
    max_samples=256,  # Limit samples
    n_jobs=-1,  # Use all CPU cores
    random_state=42
)
```

**Solution C: Reduce dataset size for testing**
```python
# In backend/data_loader.py
def load_dataset(file_path: str, sample_size: int = None):
    df = pd.read_csv(file_path, ...)
    
    if sample_size:
        df = df.sample(n=sample_size, random_state=42)
        logger.info(f"Using sample of {sample_size} rows")
    
    return df

# Use in main.py for testing
df = load_dataset(DATASET_PATH, sample_size=500)
```

### Issue 22: High Memory Usage

**Symptoms:**
```
MemoryError: Unable to allocate array
System becomes unresponsive
Process killed by OS (OOM)
```

**Diagnosis:**
```bash
# Monitor memory usage
# Linux
free -h
ps aux | grep python

# macOS
vm_stat
top -o mem

# Windows
tasklist /FI "IMAGENAME eq python.exe"
```

**Solutions:**

**Solution A: Optimize data loading**
```python
# In backend/data_loader.py
def load_dataset(file_path: str):
    # Load only required columns
    usecols = [
        'transaction_id', 'product', 'unit_price', 'market_price',
        'price_deviation', 'route_anomaly', 'company_risk_score',
        'port_activity_index', 'distance_km', 'shipment_duration_days',
        'cargo_volume', 'quantity'
    ]
    
    df = pd.read_csv(
        file_path,
        usecols=usecols,
        dtype={
            'transaction_id': 'string',
            'product': 'category',  # Use category for strings
            'unit_price': 'float32',  # Use float32 instead of float64
            'market_price': 'float32',
        }
    )
    
    return df
```

**Solution B: Process in chunks**
```python
# For very large datasets
def load_dataset_chunked(file_path: str, chunksize: int = 10000):
    chunks = []
    for chunk in pd.read_csv(file_path, chunksize=chunksize):
        # Process chunk
        chunk = engineer_features(chunk)
        chunks.append(chunk)
    
    return pd.concat(chunks, ignore_index=True)
```


---

## Environment & Dependency Issues

### Issue 23: Conflicting Dependencies

**Symptoms:**
```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed
ERROR: Cannot install package-a and package-b because these package versions have conflicting dependencies
```

**Solutions:**

**Solution A: Create fresh environment**
```bash
# Deactivate current environment
deactivate

# Remove old environment
rm -rf trinetra_env

# Create new environment
python -m venv trinetra_env
source trinetra_env/bin/activate  # Linux/macOS
trinetra_env\Scripts\activate  # Windows

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

**Solution B: Use pip-tools**
```bash
# Install pip-tools
pip install pip-tools

# Compile requirements
pip-compile requirements.txt

# Install compiled requirements
pip-sync
```

**Solution C: Pin specific versions**
```txt
# In requirements.txt, ensure exact versions
fastapi==0.104.1
uvicorn==0.24.0
streamlit==1.28.2
pandas==2.1.3
scikit-learn==1.3.2
```

### Issue 24: SSL Certificate Errors

**Symptoms:**
```
SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
urllib.error.URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED]>
```

**Solutions:**

**Solution A: Update certificates**
```bash
# macOS
/Applications/Python\ 3.11/Install\ Certificates.command

# Linux
sudo apt-get install ca-certificates
sudo update-ca-certificates

# Windows - Download and install certificates from python.org
```

**Solution B: Use pip with trusted host (temporary)**
```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

**Solution C: Configure pip**
```bash
# Create/edit ~/.pip/pip.conf (Linux/macOS) or %APPDATA%\pip\pip.ini (Windows)
[global]
trusted-host = pypi.python.org
               pypi.org
               files.pythonhosted.org
```

### Issue 25: Permission Denied Errors

**Symptoms:**
```
PermissionError: [Errno 13] Permission denied: 'models/isolation_forest.pkl'
OSError: [Errno 13] Permission denied: 'logs/trinetra_main.log'
```

**Solutions:**

**Solution A: Fix file permissions**
```bash
# Linux/macOS
chmod -R 755 models/
chmod -R 755 logs/
chmod -R 755 data/

# Change ownership if needed
sudo chown -R $USER:$USER .
```

**Solution B: Run without sudo**
```bash
# Never run with sudo
# Instead, fix permissions or use user-writable directories
```

**Solution C: Check directory permissions**
```bash
# Ensure directories are writable
mkdir -p models logs data
chmod 755 models logs data
```

---

## Testing & CI/CD Issues

### Issue 26: Property Tests Failing

**Symptoms:**
```
hypothesis.errors.Flaky: Hypothesis test is flaky
AssertionError in property test
Falsifying example found
```

**Diagnosis:**
```bash
# Run specific property test
pytest backend/test_data_integrity_property.py -v

# Run with hypothesis verbosity
pytest backend/test_data_integrity_property.py -v --hypothesis-verbosity=verbose

# Check hypothesis database
ls -la .hypothesis/
```

**Solutions:**

**Solution A: Review falsifying example**
```python
# Hypothesis will show the failing example
# Example output:
# Falsifying example: test_data_integrity(
#     row_index=42
# )

# Debug the specific case
import pandas as pd
df = pd.read_csv('data/trinetra_trade_fraud_dataset_1000_rows_complex.csv')
row = df.iloc[42]
print(row)
# Check what's wrong with this row
```

**Solution B: Fix test assumptions**
```python
# In test file
from hypothesis import given, strategies as st, assume

@given(row_index=st.integers(min_value=0, max_value=999))
def test_data_integrity(row_index):
    df = load_dataset(DATASET_PATH)
    
    # Add assumption to skip invalid cases
    assume(row_index < len(df))
    
    row = df.iloc[row_index]
    
    # Test assertions
    assert pd.notna(row['transaction_id'])
    assert pd.notna(row['date'])
```

**Solution C: Increase test examples**
```python
# Run more examples to find edge cases
from hypothesis import settings

@settings(max_examples=1000)  # Default is 100
@given(row_index=st.integers(min_value=0, max_value=999))
def test_data_integrity(row_index):
    # Test code
    pass
```


### Issue 27: CI Pipeline Failures

**Symptoms:**
- GitHub Actions workflow fails
- Tests pass locally but fail in CI
- Timeout errors in CI

**Solutions:**

**Solution A: Check CI logs**
```bash
# View workflow logs in GitHub Actions tab
# Look for specific error messages

# Common issues:
# - Missing environment variables
# - Different Python version
# - Missing dependencies
```

**Solution B: Reproduce CI environment locally**
```bash
# Use same Python version as CI
pyenv install 3.11.0
pyenv local 3.11.0

# Install exact dependencies
pip install -r requirements.txt

# Run tests as CI does
pytest --cov=backend --cov-report=term-missing
```

**Solution C: Fix CI configuration**
```yaml
# In .github/workflows/ci.yml
name: CI Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        pytest --cov=backend --cov-report=xml
      env:
        GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
```

---

## Demo & Presentation Issues

### Issue 28: Demo Crashes During Presentation

**Prevention Checklist:**

```bash
# Pre-demo checklist
□ Test complete startup: python main.py
□ Verify both services running (API + Dashboard)
□ Test all dashboard sections
□ Prepare backup explanations (in case Gemini fails)
□ Have sample queries ready
□ Test on presentation laptop/network
□ Close unnecessary applications
□ Disable system updates
□ Have backup dataset ready
```

**Emergency Recovery:**

```bash
# If system crashes during demo:

# 1. Quick restart
Ctrl+C  # Stop current process
python main.py  # Restart

# 2. If that fails, use pre-trained model
ls models/isolation_forest.pkl  # Verify exists
python main.py  # Will load existing model

# 3. If API fails, show dashboard with cached data
streamlit run frontend/dashboard.py

# 4. Have screenshots ready as backup
```

### Issue 29: Slow Demo Performance

**Optimization for Demos:**

```python
# In main.py, add demo mode
DEMO_MODE = True

if DEMO_MODE:
    # Use smaller dataset
    df = load_dataset(DATASET_PATH, sample_size=500)
    
    # Reduce model complexity
    model = IsolationForest(
        n_estimators=50,
        max_samples=128,
        n_jobs=-1
    )
    
    # Pre-cache common queries
    cache_demo_data()
```

**Pre-demo Setup:**

```bash
# 1. Pre-train model
python -c "from backend.model import train_model, save_model; from backend.data_loader import load_dataset; from backend.feature_engineering import engineer_features; df = load_dataset('data/trinetra_trade_fraud_dataset_1000_rows_complex.csv'); df = engineer_features(df); model = train_model(df); save_model(model, 'models/isolation_forest.pkl')"

# 2. Clear caches
rm -rf ~/.streamlit/cache
rm -rf .hypothesis/

# 3. Test startup time
time python main.py

# 4. Warm up services
curl http://localhost:8000/transactions
curl http://localhost:8501/
```

### Issue 30: Network Issues During Demo

**Offline Demo Mode:**

```python
# In backend/ai_explainer.py
OFFLINE_MODE = True  # Set for offline demos

def explain_transaction(transaction: dict) -> str:
    if OFFLINE_MODE:
        # Use fallback explanations (no API calls)
        return fallback_explain(transaction)
    else:
        # Try Gemini API
        try:
            return gemini_explain(transaction)
        except Exception:
            return fallback_explain(transaction)
```

**Prepare Offline Resources:**

```bash
# 1. Pre-generate explanations for demo transactions
python scripts/pregenerate_explanations.py

# 2. Save demo data locally
python scripts/cache_demo_data.py

# 3. Test without internet
# Disconnect network and run:
python main.py
```

---

## Advanced Debugging

### Debug Mode Activation

```python
# In main.py, enable debug mode
import logging

LOG_LEVEL = logging.DEBUG  # Change from INFO

# Add detailed logging
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler('logs/trinetra_debug.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
```

### Interactive Debugging

```python
# Add breakpoints for debugging
import pdb

def problematic_function():
    # Code here
    pdb.set_trace()  # Debugger will stop here
    # More code
```

### Performance Profiling

```bash
# Profile application startup
python -m cProfile -o profile.stats main.py

# Analyze profile
python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative'); p.print_stats(20)"

# Profile specific function
python -m cProfile -o profile.stats -s cumulative backend/model.py
```

### Memory Profiling

```bash
# Install memory profiler
pip install memory-profiler

# Profile memory usage
python -m memory_profiler main.py

# Add decorator to specific functions
from memory_profiler import profile

@profile
def load_dataset(file_path: str):
    # Function code
    pass
```


---

## Log Analysis

### Log File Locations

```
logs/
├── trinetra_main.log          # Main application logs
├── trinetra_data_loader.log   # Data loading logs
├── trinetra_model.log         # ML model logs
└── trinetra_debug.log         # Debug logs (if enabled)
```

### Reading Logs

```bash
# View recent logs
tail -f logs/trinetra_main.log

# Search for errors
grep -i error logs/trinetra_main.log

# Search for warnings
grep -i warning logs/trinetra_main.log

# View logs from specific time
grep "2024-01-15 10:" logs/trinetra_main.log

# Count error types
grep -i error logs/trinetra_main.log | sort | uniq -c
```

### Common Log Patterns

**Successful Startup:**
```
[INFO] Loading dataset from data/trinetra_trade_fraud_dataset_1000_rows_complex.csv
[INFO] Dataset loaded successfully: 1000 transactions
[INFO] Engineering features...
[INFO] Features engineered successfully
[INFO] Loading existing model from: models/isolation_forest.pkl
[INFO] Scoring transactions for fraud risk...
[INFO] Scoring completed: 125 fraud, 250 suspicious, 625 safe
[INFO] ✅ FastAPI server started on http://localhost:8000
[INFO] ✅ Streamlit dashboard started on http://localhost:8501
```

**Data Loading Issues:**
```
[ERROR] ❌ Dataset not found: data/trinetra_trade_fraud_dataset_1000_rows_complex.csv
[ERROR] Failed to load dataset or dataset is empty
[ERROR] Dataset schema validation failed
```

**Model Issues:**
```
[ERROR] ❌ ML model setup failed: Input contains NaN
[WARNING] Model trained with sklearn 1.3.0, current version is 1.3.2
[ERROR] Failed to load model: [Errno 2] No such file or directory
```

**API Issues:**
```
[ERROR] ❌ FastAPI server failed to start
[ERROR] Error in /transactions: 'NoneType' object has no attribute 'to_dict'
[WARNING] API server not responding, but continuing...
```

**Gemini API Issues:**
```
[WARNING] ⚠️ Gemini API initialization failed: API key not valid
[INFO] Fallback explanations will be used
[WARNING] Quota exceeded, using fallback
```

### Log Rotation

```python
# In main.py, add log rotation
from logging.handlers import RotatingFileHandler

def setup_logging():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Rotating file handler (10MB max, keep 5 backups)
    file_handler = RotatingFileHandler(
        log_dir / 'trinetra_main.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    
    logging.basicConfig(
        level=LOG_LEVEL,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            file_handler,
            logging.StreamHandler(sys.stdout)
        ]
    )
```

---

## Recovery Procedures

### Complete System Reset

```bash
# 1. Stop all processes
pkill -f uvicorn
pkill -f streamlit
pkill -f python

# 2. Clean up
rm -rf models/*.pkl
rm -rf logs/*.log
rm -rf .hypothesis/
rm -rf __pycache__/
rm -rf backend/__pycache__/
rm -rf frontend/__pycache__/

# 3. Recreate virtual environment
deactivate
rm -rf trinetra_env
python -m venv trinetra_env
source trinetra_env/bin/activate

# 4. Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 5. Restart system
python main.py
```

### Model Reset

```bash
# Delete corrupted model
rm models/isolation_forest.pkl

# Retrain from scratch
python main.py
# System will automatically train new model
```

### Data Reset

```bash
# Verify dataset integrity
md5sum data/trinetra_trade_fraud_dataset_1000_rows_complex.csv

# If corrupted, restore from backup or repository
git checkout data/trinetra_trade_fraud_dataset_1000_rows_complex.csv
```

### Configuration Reset

```bash
# Reset to default configuration
cp .env.example .env

# Edit with your settings
nano .env
```

---

## Platform-Specific Issues

### Windows-Specific Issues

**Issue: PowerShell Execution Policy**
```powershell
# Error: cannot be loaded because running scripts is disabled
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Activate environment
.\trinetra_env\Scripts\Activate.ps1
```

**Issue: Long Path Names**
```powershell
# Enable long paths in Windows
# Run as Administrator
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

**Issue: Windows Defender Blocking**
```
# Add Python to exclusions
# Windows Security → Virus & threat protection → Manage settings → Exclusions
# Add: C:\Users\YourName\trinetra-ai-fraud-detection\
```

### macOS-Specific Issues

**Issue: SSL Certificate Errors**
```bash
# Install certificates
/Applications/Python\ 3.11/Install\ Certificates.command

# Or manually
pip install --upgrade certifi
```

**Issue: Port Binding on macOS**
```bash
# macOS may require sudo for ports < 1024
# Use ports > 1024 (8000, 8501 are fine)

# If still issues, check firewall
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
```

### Linux-Specific Issues

**Issue: Missing System Dependencies**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3-dev python3-pip python3-venv build-essential

# CentOS/RHEL
sudo yum install python3-devel python3-pip gcc gcc-c++ make

# Arch Linux
sudo pacman -S python python-pip base-devel
```

**Issue: Port Permissions**
```bash
# Allow non-root user to bind to ports
sudo setcap 'cap_net_bind_service=+ep' $(which python3)

# Or use ports > 1024 (recommended)
```

---

## Getting Help

### Self-Help Resources

1. **Check Logs First**
   ```bash
   tail -n 100 logs/trinetra_main.log
   ```

2. **Search This Guide**
   - Use Ctrl+F to search for error messages
   - Check relevant sections based on symptoms

3. **Review Documentation**
   - README.md - General usage
   - API_DOCUMENTATION.md - API details
   - USER_GUIDE.md - Dashboard usage

### Reporting Issues

When reporting issues, include:

```
**Environment:**
- OS: [Windows 11 / macOS 13 / Ubuntu 22.04]
- Python Version: [output of `python --version`]
- Virtual Environment: [Yes/No]

**Issue Description:**
[Clear description of the problem]

**Steps to Reproduce:**
1. [First step]
2. [Second step]
3. [...]

**Expected Behavior:**
[What should happen]

**Actual Behavior:**
[What actually happens]

**Error Messages:**
```
[Paste error messages here]
```

**Logs:**
```
[Paste relevant log entries]
```

**Screenshots:**
[If applicable]
```

### Contact Information

- **GitHub Issues**: [Create new issue](https://github.com/your-repo/issues)
- **Documentation**: Check README.md and other docs
- **Community**: [Discussion forum link]

---

## Appendix: Useful Commands

### Quick Reference

```bash
# System Status
python --version                    # Check Python version
pip list                           # List installed packages
which python                       # Check Python path
df -h                             # Check disk space
free -h                           # Check memory (Linux)

# Environment Management
python -m venv trinetra_env       # Create environment
source trinetra_env/bin/activate  # Activate (Linux/macOS)
trinetra_env\Scripts\activate     # Activate (Windows)
deactivate                        # Deactivate environment

# Dependency Management
pip install -r requirements.txt   # Install dependencies
pip freeze > requirements.txt     # Save current dependencies
pip list --outdated              # Check for updates

# Application Management
python main.py                    # Start application
Ctrl+C                           # Stop application
pkill -f uvicorn                 # Kill API server
pkill -f streamlit               # Kill dashboard

# Testing
pytest                           # Run all tests
pytest -v                        # Verbose output
pytest --cov=backend            # With coverage
pytest -k test_name             # Run specific test

# Debugging
tail -f logs/trinetra_main.log  # Follow logs
grep -i error logs/*.log        # Search for errors
python -m pdb main.py           # Debug mode

# Cleanup
rm -rf __pycache__/             # Remove cache
rm -rf .hypothesis/             # Remove hypothesis cache
rm models/*.pkl                 # Remove models
rm logs/*.log                   # Remove logs
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024 | Initial comprehensive troubleshooting guide |

---

**End of Troubleshooting Guide**

For additional help, refer to:
- [README.md](README.md) - Main documentation
- [USER_GUIDE.md](USER_GUIDE.md) - Dashboard usage guide
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - API reference
