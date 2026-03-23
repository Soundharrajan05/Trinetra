# TRINETRA AI - Configuration Guide

## Overview

This document provides comprehensive documentation for all configurable options in the TRINETRA AI Trade Fraud Intelligence System. Use this guide to customize the system for your specific needs.

---

## Table of Contents

1. [Environment Variables](#environment-variables)
2. [Model Hyperparameters](#model-hyperparameters)
3. [API Settings](#api-settings)
4. [Dashboard Configuration](#dashboard-configuration)
5. [Alert Thresholds](#alert-thresholds)
6. [Performance Tuning](#performance-tuning)
7. [Quick Start Examples](#quick-start-examples)

---

## Environment Variables

Environment variables are configured in the `.env` file. Copy `.env.example` to `.env` and customize as needed.

### AI/ML Configuration

#### `GEMINI_API_KEY` (Required)
- **Description**: API key for Google Gemini AI service used for fraud explanations
- **Default**: None (must be provided)
- **Example**: `GEMINI_API_KEY=AIzaSyC0jXIwaSAiPGuOFBXvN0ofK0rivEflShA`
- **How to obtain**: Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

#### `GEMINI_MODEL`
- **Description**: Gemini model version to use
- **Default**: `models/gemini-2.5-flash`
- **Options**: 
  - `models/gemini-2.5-flash` (faster, recommended)
  - `models/gemini-pro` (more capable)
- **Example**: `GEMINI_MODEL=models/gemini-2.5-flash`

#### `GEMINI_TIMEOUT`
- **Description**: Timeout in seconds for Gemini API calls
- **Default**: `10`
- **Range**: 5-60 seconds
- **Example**: `GEMINI_TIMEOUT=15`

### API Configuration

#### `API_HOST`
- **Description**: Host address for FastAPI backend
- **Default**: `localhost`
- **Options**: `localhost`, `0.0.0.0` (for external access), specific IP
- **Example**: `API_HOST=0.0.0.0`

#### `API_PORT`
- **Description**: Port number for FastAPI backend
- **Default**: `8000`
- **Range**: 1024-65535
- **Example**: `API_PORT=8000`

#### `API_RELOAD`
- **Description**: Enable auto-reload for development
- **Default**: `true`
- **Options**: `true`, `false`
- **Example**: `API_RELOAD=false`
- **Note**: Set to `false` in production

### CORS Settings

#### `CORS_ORIGINS`
- **Description**: Allowed origins for CORS
- **Default**: `*` (all origins)
- **Example**: `CORS_ORIGINS=http://localhost:8501,https://yourdomain.com`
- **Security Note**: Restrict in production

#### `CORS_METHODS`
- **Description**: Allowed HTTP methods
- **Default**: `*` (all methods)
- **Example**: `CORS_METHODS=GET,POST,PUT,DELETE`

#### `CORS_HEADERS`
- **Description**: Allowed HTTP headers
- **Default**: `*` (all headers)
- **Example**: `CORS_HEADERS=Content-Type,Authorization`

### Application Settings

#### `DATASET_PATH`
- **Description**: Path to the trade transaction CSV dataset
- **Default**: `data/trinetra_trade_fraud_dataset_1000_rows_complex.csv`
- **Example**: `DATASET_PATH=data/my_custom_dataset.csv`
- **Note**: Dataset must have required columns (see schema below)

#### `MODEL_PATH`
- **Description**: Path to save/load the trained ML model
- **Default**: `models/isolation_forest.pkl`
- **Example**: `MODEL_PATH=models/my_model.pkl`

#### `LOG_LEVEL`
- **Description**: Logging verbosity level
- **Default**: `INFO`
- **Options**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **Example**: `LOG_LEVEL=DEBUG`

#### `LOG_FILE`
- **Description**: Path to log file
- **Default**: `trinetra.log`
- **Example**: `LOG_FILE=logs/trinetra.log`

### Dashboard Configuration

#### `STREAMLIT_HOST`
- **Description**: Host address for Streamlit dashboard
- **Default**: `localhost`
- **Example**: `STREAMLIT_HOST=0.0.0.0`

#### `STREAMLIT_PORT`
- **Description**: Port number for Streamlit dashboard
- **Default**: `8501`
- **Range**: 1024-65535
- **Example**: `STREAMLIT_PORT=8501`

#### `STREAMLIT_THEME`
- **Description**: Dashboard color theme
- **Default**: `dark`
- **Options**: `dark`, `light`
- **Example**: `STREAMLIT_THEME=dark`

#### `DASHBOARD_REFRESH_INTERVAL`
- **Description**: Auto-refresh interval in seconds
- **Default**: `30`
- **Range**: 10-300 seconds
- **Example**: `DASHBOARD_REFRESH_INTERVAL=60`

### Development Settings

#### `ENVIRONMENT`
- **Description**: Environment mode
- **Default**: `development`
- **Options**: `development`, `production`, `testing`
- **Example**: `ENVIRONMENT=production`

#### `DEBUG`
- **Description**: Enable debug mode
- **Default**: `true`
- **Options**: `true`, `false`
- **Example**: `DEBUG=false`
- **Note**: Disable in production

#### `ENABLE_AI_EXPLANATIONS`
- **Description**: Enable/disable AI-powered explanations
- **Default**: `true`
- **Options**: `true`, `false`
- **Example**: `ENABLE_AI_EXPLANATIONS=true`
- **Note**: Requires valid Gemini API key

#### `ENABLE_ALERTS`
- **Description**: Enable/disable alert system
- **Default**: `true`
- **Options**: `true`, `false`
- **Example**: `ENABLE_ALERTS=true`

#### `ENABLE_CACHING`
- **Description**: Enable/disable response caching
- **Default**: `true`
- **Options**: `true`, `false`
- **Example**: `ENABLE_CACHING=true`

---

## Model Hyperparameters

Configure ML model parameters in `.env` or directly in `backend/model.py`.

### IsolationForest Parameters

#### `ISOLATION_FOREST_N_ESTIMATORS`
- **Description**: Number of trees in the forest
- **Default**: `100`
- **Range**: 50-500
- **Impact**: 
  - Higher = Better accuracy, slower training
  - Lower = Faster training, less accurate
- **Example**: `ISOLATION_FOREST_N_ESTIMATORS=150`
- **Recommendation**: 100-200 for most use cases

#### `ISOLATION_FOREST_CONTAMINATION`
- **Description**: Expected proportion of fraud in dataset
- **Default**: `0.1` (10%)
- **Range**: 0.01-0.5 (1%-50%)
- **Impact**: 
  - Higher = More transactions flagged as fraud
  - Lower = Fewer fraud detections
- **Example**: `ISOLATION_FOREST_CONTAMINATION=0.15`
- **Recommendation**: Adjust based on your actual fraud rate

#### `ISOLATION_FOREST_RANDOM_STATE`
- **Description**: Random seed for reproducibility
- **Default**: `42`
- **Range**: Any integer
- **Example**: `ISOLATION_FOREST_RANDOM_STATE=42`
- **Note**: Keep constant for reproducible results

### Risk Classification Thresholds

#### `RISK_THRESHOLD_SAFE`
- **Description**: Upper bound for SAFE classification
- **Default**: `-0.2`
- **Range**: -1.0 to 0.0
- **Impact**: Scores below this are classified as SAFE
- **Example**: `RISK_THRESHOLD_SAFE=-0.3`

#### `RISK_THRESHOLD_FRAUD`
- **Description**: Lower bound for FRAUD classification
- **Default**: `0.2`
- **Range**: 0.0 to 1.0
- **Impact**: Scores above this are classified as FRAUD
- **Example**: `RISK_THRESHOLD_FRAUD=0.25`

**Risk Category Logic:**
```
score < RISK_THRESHOLD_SAFE        → SAFE
RISK_THRESHOLD_SAFE ≤ score < RISK_THRESHOLD_FRAUD → SUSPICIOUS
score ≥ RISK_THRESHOLD_FRAUD       → FRAUD
```

---

## API Settings

### Endpoint Configuration

All API endpoints are accessible at `http://{API_HOST}:{API_PORT}/`

#### Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API health check |
| `/transactions` | GET | Get all transactions with pagination |
| `/suspicious` | GET | Get suspicious transactions |
| `/fraud` | GET | Get fraud transactions |
| `/explain/{transaction_id}` | POST | Get AI explanation for transaction |
| `/query` | POST | Natural language query |
| `/stats` | GET | Dashboard statistics |
| `/alerts` | GET | Get all alerts |
| `/alerts/priority/{priority}` | GET | Get alerts by priority |
| `/session/reset` | POST | Reset AI explanation session |

### Pagination Settings

Configure in API calls using query parameters:

```python
# Example: Get 50 transactions, skip first 100
GET /transactions?limit=50&offset=100
```

- **limit**: Number of records to return (1-1000)
- **offset**: Number of records to skip (0+)

### Response Format

All API responses follow this structure:

```json
{
  "status": "success",
  "data": { ... },
  "message": "Optional message"
}
```

---

## Dashboard Configuration

### Page Configuration

Configure in `frontend/dashboard.py`:

```python
st.set_page_config(
    page_title="TRINETRA AI",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)
```

### Theme Customization

#### Dark Theme (Default)

```python
# Custom CSS for dark theme
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stMetric { 
        background-color: #1e2130; 
        padding: 20px; 
        border-radius: 10px; 
    }
    .stAlert { background-color: #ff4b4b; }
</style>
""", unsafe_allow_html=True)
```

#### Light Theme

Set `STREAMLIT_THEME=light` in `.env` and modify CSS:

```python
st.markdown("""
<style>
    .main { background-color: #ffffff; }
    .stMetric { 
        background-color: #f0f2f6; 
        padding: 20px; 
        border-radius: 10px; 
    }
</style>
""", unsafe_allow_html=True)
```

### Visualization Settings

#### Chart Colors

```python
# Risk category colors
COLORS = {
    'SAFE': '#00ff00',      # Green
    'SUSPICIOUS': '#ffaa00', # Orange
    'FRAUD': '#ff0000'       # Red
}
```

#### Map Configuration

```python
# Plotly map settings
fig = px.scatter_geo(
    projection="natural earth",
    color_discrete_map=COLORS,
    height=600,
    width=1200
)
```

### Layout Options

#### Column Widths

```python
# Two-column layout
col1, col2 = st.columns([2, 1])  # 2:1 ratio

# Three-column layout
col1, col2, col3 = st.columns(3)  # Equal width
```

#### Sidebar Configuration

```python
# Sidebar filters
with st.sidebar:
    st.header("Filters")
    risk_filter = st.multiselect(
        "Risk Category",
        options=['SAFE', 'SUSPICIOUS', 'FRAUD']
    )
```

---

## Alert Thresholds

Configure alert triggers in `.env` or `backend/alerts.py`.

### Alert Trigger Conditions

#### `ALERT_PRICE_DEVIATION_THRESHOLD`
- **Description**: Trigger alert when price deviation exceeds threshold
- **Default**: `0.5` (50%)
- **Range**: 0.1-2.0 (10%-200%)
- **Example**: `ALERT_PRICE_DEVIATION_THRESHOLD=0.6`
- **Alert Type**: PRICE_ANOMALY

#### `ALERT_COMPANY_RISK_THRESHOLD`
- **Description**: Trigger alert when company risk score exceeds threshold
- **Default**: `0.8` (80%)
- **Range**: 0.5-1.0 (50%-100%)
- **Example**: `ALERT_COMPANY_RISK_THRESHOLD=0.75`
- **Alert Type**: HIGH_RISK_COMPANY

#### `ALERT_PORT_ACTIVITY_THRESHOLD`
- **Description**: Trigger alert when port activity index exceeds threshold
- **Default**: `1.5`
- **Range**: 1.0-3.0
- **Example**: `ALERT_PORT_ACTIVITY_THRESHOLD=1.8`
- **Alert Type**: PORT_CONGESTION

### Alert Logic

```python
def check_alerts(transaction: dict) -> List[str]:
    alerts = []
    
    if transaction['price_deviation'] > ALERT_PRICE_DEVIATION_THRESHOLD:
        alerts.append("PRICE_ANOMALY")
    
    if transaction['route_anomaly'] == 1:
        alerts.append("ROUTE_ANOMALY")
    
    if transaction['company_risk_score'] > ALERT_COMPANY_RISK_THRESHOLD:
        alerts.append("HIGH_RISK_COMPANY")
    
    if transaction['port_activity_index'] > ALERT_PORT_ACTIVITY_THRESHOLD:
        alerts.append("PORT_CONGESTION")
    
    return alerts
```

### Alert Priority Levels

| Priority | Conditions | Color |
|----------|-----------|-------|
| CRITICAL | risk_category = FRAUD + multiple alerts | Red |
| HIGH | risk_category = FRAUD OR 3+ alerts | Orange |
| MEDIUM | risk_category = SUSPICIOUS + alerts | Yellow |
| LOW | Single alert, SAFE category | Blue |

---

## Performance Tuning

### Model Training Performance

#### Optimize Training Speed

```python
# Reduce estimators for faster training
ISOLATION_FOREST_N_ESTIMATORS=50

# Use fewer CPU cores
n_jobs=2  # Instead of -1 (all cores)
```

#### Optimize Accuracy

```python
# Increase estimators for better accuracy
ISOLATION_FOREST_N_ESTIMATORS=200

# Use all available cores
n_jobs=-1
```

### API Performance

#### Enable Caching

```python
# In .env
ENABLE_CACHING=true

# Cache duration (seconds)
CACHE_TTL=300  # 5 minutes
```

#### Pagination

```python
# Limit large responses
GET /transactions?limit=100  # Instead of all records
```

#### Async Processing

```python
# Use async endpoints in api.py
@app.get("/transactions")
async def get_transactions():
    # Async implementation
    pass
```

### Dashboard Performance

#### Lazy Loading

```python
# Load data only when needed
@st.cache_data(ttl=60)
def load_transactions():
    return fetch_from_api()
```

#### Reduce Refresh Rate

```python
# In .env
DASHBOARD_REFRESH_INTERVAL=60  # Refresh every 60 seconds
```

#### Optimize Visualizations

```python
# Limit data points in charts
df_sample = df.sample(n=1000)  # Plot 1000 points instead of all

# Use simpler chart types
st.bar_chart(data)  # Instead of complex Plotly charts
```

### Database Optimization (Future)

```python
# Index frequently queried columns
CREATE INDEX idx_risk_category ON transactions(risk_category);
CREATE INDEX idx_transaction_id ON transactions(transaction_id);

# Use connection pooling
SQLALCHEMY_POOL_SIZE=10
SQLALCHEMY_MAX_OVERFLOW=20
```

---

## Quick Start Examples

### Example 1: High-Security Configuration

```env
# .env for high-security deployment
ENVIRONMENT=production
DEBUG=false

# Strict CORS
CORS_ORIGINS=https://yourdomain.com
CORS_METHODS=GET,POST
CORS_HEADERS=Content-Type,Authorization

# Conservative fraud detection
ISOLATION_FOREST_CONTAMINATION=0.05
RISK_THRESHOLD_FRAUD=0.15

# Strict alert thresholds
ALERT_PRICE_DEVIATION_THRESHOLD=0.3
ALERT_COMPANY_RISK_THRESHOLD=0.7
ALERT_PORT_ACTIVITY_THRESHOLD=1.2
```

### Example 2: Development Configuration

```env
# .env for development
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# Permissive CORS
CORS_ORIGINS=*

# Fast training
ISOLATION_FOREST_N_ESTIMATORS=50

# Frequent refresh
DASHBOARD_REFRESH_INTERVAL=10
```

### Example 3: High-Performance Configuration

```env
# .env for high-performance deployment
ENVIRONMENT=production

# Optimized model
ISOLATION_FOREST_N_ESTIMATORS=100
ISOLATION_FOREST_CONTAMINATION=0.1

# Caching enabled
ENABLE_CACHING=true

# Longer refresh interval
DASHBOARD_REFRESH_INTERVAL=120

# API optimization
API_RELOAD=false
```

### Example 4: Custom Dataset Configuration

```env
# .env for custom dataset
DATASET_PATH=data/my_company_trades.csv
MODEL_PATH=models/my_company_model.pkl

# Adjust contamination based on your fraud rate
ISOLATION_FOREST_CONTAMINATION=0.08  # 8% fraud rate

# Custom thresholds based on your data
RISK_THRESHOLD_SAFE=-0.25
RISK_THRESHOLD_FRAUD=0.18
```

---

## Dataset Schema Requirements

Your custom dataset must include these columns:

### Required Columns

| Column | Type | Description |
|--------|------|-------------|
| `transaction_id` | string | Unique transaction identifier |
| `date` | datetime | Transaction date |
| `product` | string | Product name |
| `commodity_category` | string | Product category |
| `unit_price` | float | Transaction price |
| `market_price` | float | Market reference price |
| `quantity` | int | Quantity traded |
| `cargo_volume` | float | Cargo volume |
| `shipping_route` | string | Route identifier |
| `distance_km` | float | Shipping distance |
| `shipment_duration_days` | int | Duration in days |
| `company_risk_score` | float | Company risk (0-1) |
| `port_activity_index` | float | Port activity level |
| `price_deviation` | float | Price deviation ratio |
| `route_anomaly` | int | Route anomaly flag (0/1) |

### Optional Columns

- `company_name`: Company identifier
- `export_port`: Export port name
- `import_port`: Import port name
- `fraud_label`: Ground truth label (for evaluation)

---

## Troubleshooting

### Common Issues

#### Issue: Model training is slow
**Solution**: Reduce `ISOLATION_FOREST_N_ESTIMATORS` or use fewer features

#### Issue: Too many false positives
**Solution**: Increase `RISK_THRESHOLD_FRAUD` or decrease `ISOLATION_FOREST_CONTAMINATION`

#### Issue: Too few fraud detections
**Solution**: Decrease `RISK_THRESHOLD_FRAUD` or increase `ISOLATION_FOREST_CONTAMINATION`

#### Issue: Gemini API errors
**Solution**: Check `GEMINI_API_KEY` is valid and `GEMINI_TIMEOUT` is sufficient

#### Issue: Dashboard is slow
**Solution**: Increase `DASHBOARD_REFRESH_INTERVAL` and enable caching

---

## Configuration Validation

Use this checklist to validate your configuration:

- [ ] `.env` file exists and is properly formatted
- [ ] `GEMINI_API_KEY` is set and valid
- [ ] `DATASET_PATH` points to valid CSV file
- [ ] Port numbers are not in use by other services
- [ ] Risk thresholds are logically ordered (SAFE < FRAUD)
- [ ] Alert thresholds match your business requirements
- [ ] Log directory exists and is writable
- [ ] Model directory exists and is writable

---

## Support

For additional configuration help:
- Review the design document: `.kiro/specs/trinetra-ai-fraud-detection/design.md`
- Check the requirements: `.kiro/specs/trinetra-ai-fraud-detection/requirements.md`
- Examine example configurations in `.env.example`

---

**Last Updated**: 2024
**Version**: 1.0.0
