# Design: TRINETRA AI - Trade Fraud Intelligence System

## System Architecture

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                     TRINETRA AI System                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐      ┌───────────┐ │
│  │   Streamlit  │◄────►│   FastAPI    │◄────►│  Gemini   │ │
│  │   Dashboard  │      │   Backend    │      │    API    │ │
│  └──────────────┘      └──────────────┘      └───────────┘ │
│         │                      │                             │
│         │                      ▼                             │
│         │              ┌──────────────┐                      │
│         │              │  ML Pipeline │                      │
│         │              │ (scikit-learn)│                     │
│         │              └──────────────┘                      │
│         │                      │                             │
│         └──────────────────────┼─────────────────────────────┤
│                                ▼                             │
│                        ┌──────────────┐                      │
│                        │   CSV Data   │                      │
│                        │   Loader     │                      │
│                        └──────────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

### Component Overview

1. **Data Layer**: CSV file loading and validation
2. **Feature Engineering Layer**: Transform raw data into ML features
3. **ML Layer**: IsolationForest anomaly detection
4. **API Layer**: FastAPI REST endpoints
5. **AI Layer**: Gemini API integration for explanations
6. **Presentation Layer**: Streamlit dashboard

## Detailed Component Design

### 1. Data Loader Module (`backend/data_loader.py`)

**Purpose**: Load and validate trade transaction data

**Key Functions**:
```python
def load_dataset(file_path: str) -> pd.DataFrame
    """Load CSV dataset with date parsing and validation"""
    
def validate_schema(df: pd.DataFrame) -> bool
    """Ensure required columns exist"""
    
def get_dataset_stats(df: pd.DataFrame) -> dict
    """Return basic statistics about the dataset"""
```

**Implementation Details**:
- Use pandas.read_csv with date parsing
- Validate presence of required columns
- Handle missing values with forward fill or mean imputation
- Return clean DataFrame ready for feature engineering

**Error Handling**:
- FileNotFoundError if CSV missing
- ValueError if schema invalid
- Log warnings for missing data

### 2. Feature Engineering Module (`backend/feature_engineering.py`)

**Purpose**: Generate fraud detection features from raw transaction data

**Key Functions**:
```python
def engineer_features(df: pd.DataFrame) -> pd.DataFrame
    """Generate all fraud detection features"""
    
def calculate_price_anomaly_score(df: pd.DataFrame) -> pd.Series
    """price_anomaly_score = abs(price_deviation)"""
    
def calculate_route_risk_score(df: pd.DataFrame) -> pd.Series
    """route_risk_score = route_anomaly"""
    
def calculate_company_network_risk(df: pd.DataFrame) -> pd.Series
    """company_network_risk = company_risk_score"""
    
def calculate_port_congestion_score(df: pd.DataFrame) -> pd.Series
    """port_congestion_score = port_activity_index"""
    
def calculate_shipment_duration_risk(df: pd.DataFrame) -> pd.Series
    """shipment_duration_risk = shipment_duration_days / distance_km"""
    
def calculate_volume_spike_score(df: pd.DataFrame) -> pd.Series
    """volume_spike_score = cargo_volume / quantity"""
```

**Feature Definitions**:
- **price_anomaly_score**: Absolute deviation from market price
- **route_risk_score**: Binary indicator of abnormal route
- **company_network_risk**: Company's historical risk score
- **port_congestion_score**: Port activity level indicator
- **shipment_duration_risk**: Duration normalized by distance
- **volume_spike_score**: Cargo volume per unit quantity

**Data Flow**:
```
Raw DataFrame → Feature Calculation → Enriched DataFrame
```

### 3. ML Model Module (`backend/model.py`)

**Purpose**: Train and persist IsolationForest anomaly detection model

**Key Functions**:
```python
def train_model(df: pd.DataFrame) -> IsolationForest
    """Train IsolationForest on engineered features"""
    
def save_model(model: IsolationForest, path: str) -> None
    """Persist model to disk using joblib"""
    
def load_model(path: str) -> IsolationForest
    """Load trained model from disk"""
```

**Model Configuration**:
```python
IsolationForest(
    n_estimators=100,
    contamination=0.1,  # Expect ~10% fraud
    random_state=42,
    n_jobs=-1
)
```

**Training Features**:
- price_anomaly_score
- route_risk_score
- company_network_risk
- port_congestion_score
- shipment_duration_risk
- volume_spike_score

**Output**:
- Trained model saved to `models/isolation_forest.pkl`
- Model metrics logged (training time, feature importance)

### 4. Fraud Detection Engine (`backend/fraud_detection.py`)

**Purpose**: Score transactions and classify risk levels

**Key Functions**:
```python
def load_fraud_detector() -> IsolationForest
    """Load trained model"""
    
def score_transactions(df: pd.DataFrame, model: IsolationForest) -> pd.DataFrame
    """Add risk_score to dataframe"""
    
def classify_risk(df: pd.DataFrame) -> pd.DataFrame
    """Add risk_category based on thresholds"""
```

**Risk Classification Logic**:
```python
def get_risk_category(score: float) -> str:
    if score < -0.2:
        return "SAFE"
    elif score < 0.2:
        return "SUSPICIOUS"
    else:
        return "FRAUD"
```

**Thresholds**:
- SAFE: score < -0.2
- SUSPICIOUS: -0.2 ≤ score < 0.2
- FRAUD: score ≥ 0.2

**Output Schema**:
```
Original columns + risk_score + risk_category
```

### 5. AI Explainer Module (`backend/ai_explainer.py`)

**Purpose**: Generate natural language fraud explanations using Gemini

**Key Functions**:
```python
def initialize_gemini(api_key: str) -> genai.GenerativeModel
    """Initialize Gemini API client"""
    
def explain_transaction(transaction: dict) -> str
    """Generate fraud explanation for a transaction"""
    
def answer_investigation_query(query: str, context: dict) -> str
    """Answer natural language investigation questions"""
```

**Gemini Configuration**:
```python
API_KEY = "AIzaSyC0jXIwaSAiPGuOFBXvN0ofK0rivEflShA"
MODEL = "gemini-pro"
```

**Explanation Prompt Template**:
```
Analyze the following trade transaction and explain why it may be fraudulent.

Transaction ID: {transaction_id}
Product: {product}
Commodity Category: {commodity_category}
Market Price: ${market_price}
Trade Price: ${unit_price}
Price Deviation: {price_deviation}%
Shipping Route: {shipping_route}
Distance: {distance_km} km
Company Risk Score: {company_risk_score}
Port Activity Index: {port_activity_index}
Route Anomaly: {route_anomaly}

Explain possible fraud indicators in 3-4 sentences.
```

**Error Handling**:
- Retry logic for API failures
- Fallback to rule-based explanations
- Timeout after 10 seconds

### 6. FastAPI Backend (`backend/api.py`)

**Purpose**: Provide RESTful API for frontend

**Endpoints**:

```python
@app.get("/transactions")
async def get_all_transactions() -> List[dict]:
    """Return all transactions with risk scores"""
    
@app.get("/suspicious")
async def get_suspicious_transactions() -> List[dict]:
    """Return transactions with risk_category = SUSPICIOUS"""
    
@app.get("/fraud")
async def get_fraud_transactions() -> List[dict]:
    """Return transactions with risk_category = FRAUD"""
    
@app.post("/explain/{transaction_id}")
async def explain_transaction(transaction_id: str) -> dict:
    """Return Gemini explanation for specific transaction"""
    
@app.post("/query")
async def natural_language_query(query: str) -> dict:
    """Process natural language queries"""
    
@app.get("/stats")
async def get_statistics() -> dict:
    """Return dashboard statistics"""
```

**Response Format**:
```json
{
    "status": "success",
    "data": [...],
    "message": "Optional message"
}
```

**CORS Configuration**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)
```

### 7. Streamlit Dashboard (`frontend/dashboard.py`)

**Purpose**: Interactive web interface for fraud analysis

**Layout Structure**:
```
┌─────────────────────────────────────────────────────┐
│              TRINETRA AI - Header                    │
├─────────────────────────────────────────────────────┤
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐           │
│  │ KPI  │  │ KPI  │  │ KPI  │  │ KPI  │           │
│  │  1   │  │  2   │  │  3   │  │  4   │           │
│  └──────┘  └──────┘  └──────┘  └──────┘           │
├─────────────────────────────────────────────────────┤
│  ┌─────────────────────┐  ┌──────────────────────┐ │
│  │  Fraud Alerts       │  │  Price Deviation     │ │
│  │  (Critical Cases)   │  │  Chart               │ │
│  └─────────────────────┘  └──────────────────────┘ │
├─────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────┐  │
│  │  Suspicious Transactions Table               │  │
│  │  (Filterable, Sortable)                      │  │
│  └──────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────┤
│  ┌─────────────────────┐  ┌──────────────────────┐ │
│  │  Route Intelligence │  │  Company Risk        │ │
│  │  Map                │  │  Network             │ │
│  └─────────────────────┘  └──────────────────────┘ │
├─────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────┐  │
│  │  AI Investigation Assistant                  │  │
│  │  [Chat Interface]                            │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

**Key Sections**:

1. **Global Trade Overview**
   - Total Transactions
   - Fraud Rate %
   - Total Trade Value
   - High-Risk Countries

2. **Fraud Alerts**
   - Real-time alerts for critical cases
   - Alert criteria indicators
   - Quick action buttons

3. **Suspicious Transactions Table**
   - Columns: ID, Product, Price Deviation, Risk Score, Category
   - Sortable and filterable
   - Click to view details

4. **Route Intelligence Map**
   - Plotly scatter_geo visualization
   - Export/Import port locations
   - Route lines colored by risk

5. **Price Deviation Chart**
   - Scatter plot: Market Price vs Trade Price
   - Color-coded by risk category
   - Interactive tooltips

6. **Company Risk Network**
   - Network graph of trading relationships
   - Node size = transaction volume
   - Edge color = risk level

7. **AI Investigation Assistant**
   - Text input for questions
   - Gemini-powered responses
   - Transaction context awareness

**Styling**:
```python
st.set_page_config(
    page_title="TRINETRA AI",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark theme CSS
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2130; padding: 20px; border-radius: 10px; }
    .stAlert { background-color: #ff4b4b; }
</style>
""", unsafe_allow_html=True)
```

### 8. Alert System

**Alert Triggers**:
```python
def check_alerts(transaction: dict) -> List[str]:
    alerts = []
    
    if transaction['price_deviation'] > 0.5:
        alerts.append("PRICE_ANOMALY")
    
    if transaction['route_anomaly'] == 1:
        alerts.append("ROUTE_ANOMALY")
    
    if transaction['company_risk_score'] > 0.8:
        alerts.append("HIGH_RISK_COMPANY")
    
    if transaction['port_activity_index'] > 1.5:
        alerts.append("PORT_CONGESTION")
    
    return alerts
```

**Alert Display**:
- Red banner for FRAUD category
- Yellow banner for SUSPICIOUS category
- Alert count in dashboard header
- Detailed alert panel with explanations

### 9. Main Application Entry Point (`main.py`)

**Purpose**: Orchestrate system startup

```python
def main():
    # 1. Load dataset
    df = load_dataset("data/trinetra_trade_fraud_dataset_1000_rows_complex.csv")
    
    # 2. Engineer features
    df = engineer_features(df)
    
    # 3. Train or load model
    if not os.path.exists("models/isolation_forest.pkl"):
        model = train_model(df)
        save_model(model, "models/isolation_forest.pkl")
    else:
        model = load_model("models/isolation_forest.pkl")
    
    # 4. Score transactions
    df = score_transactions(df, model)
    df = classify_risk(df)
    
    # 5. Start FastAPI backend (background thread)
    start_api_server(df)
    
    # 6. Launch Streamlit dashboard
    launch_dashboard()
```

## Data Flow

```
CSV File
   ↓
Data Loader (validation)
   ↓
Feature Engineering (6 features)
   ↓
ML Model Training/Loading
   ↓
Fraud Detection (scoring + classification)
   ↓
FastAPI Backend (REST endpoints)
   ↓
Streamlit Dashboard (visualization)
   ↓
Gemini API (explanations)
```

## Technology Stack Details

### Backend Dependencies
```
fastapi==0.104.1
uvicorn==0.24.0
pandas==2.1.3
scikit-learn==1.3.2
joblib==1.3.2
google-generativeai==0.3.1
pydantic==2.5.0
```

### Frontend Dependencies
```
streamlit==1.28.2
plotly==5.18.0
requests==2.31.0
```

## Security Considerations

1. **API Key Management**
   - Store Gemini API key in environment variable
   - Never commit keys to version control
   - Use .env file for local development

2. **Input Validation**
   - Validate all API inputs
   - Sanitize user queries before sending to Gemini
   - Limit query length to prevent abuse

3. **Error Handling**
   - Never expose internal errors to users
   - Log errors securely
   - Provide generic error messages

## Performance Optimization

1. **Data Loading**
   - Cache loaded dataset in memory
   - Use pandas chunking for large files

2. **Model Inference**
   - Batch predictions when possible
   - Cache model in memory

3. **API Responses**
   - Implement response caching
   - Use async endpoints

4. **Dashboard**
   - Lazy load visualizations
   - Paginate large tables
   - Use Streamlit caching decorators

## Deployment Strategy

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

### Production Considerations
- Use gunicorn for FastAPI
- Deploy Streamlit on Streamlit Cloud
- Use environment variables for configuration
- Implement proper logging
- Add health check endpoints

## Testing Strategy

### Unit Tests
- Test each module independently
- Mock external dependencies (Gemini API)
- Test edge cases and error conditions

### Integration Tests
- Test API endpoints
- Test data flow through pipeline
- Test dashboard rendering

### Property-Based Tests
- Validate correctness properties from requirements
- Use hypothesis library for property testing
- Test data integrity, risk score consistency, feature calculations

## Monitoring and Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trinetra.log'),
        logging.StreamHandler()
    ]
)
```

**Key Metrics to Log**:
- Dataset load time
- Model training time
- API response times
- Gemini API call success/failure
- Alert trigger counts

## Future Enhancements

1. Real-time data streaming
2. Advanced ML models (XGBoost, Neural Networks)
3. Multi-user authentication
4. Database persistence (PostgreSQL)
5. Advanced network analysis
6. Automated report generation
7. Mobile application
8. Integration with customs databases
