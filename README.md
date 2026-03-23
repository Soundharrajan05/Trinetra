# 🛡️ TRINETRA AI - Trade Fraud Intelligence System

> AI-powered trade fraud detection platform that analyzes international trade transactions, detects anomalies using machine learning, and provides explainable AI insights.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28.2-FF4B4B.svg)](https://streamlit.io/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3.2-F7931E.svg)](https://scikit-learn.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Technology Stack](#-technology-stack)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [API Documentation](#-api-documentation)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)
- [Demo Scenarios](#-demo-scenarios)
- [Architecture](#-architecture)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🔍 Overview

**TRINETRA AI** is an intelligent trade fraud detection system designed to help financial regulators, customs authorities, and compliance teams identify suspicious international trade transactions. The platform combines machine learning anomaly detection with AI-powered explanations to provide actionable fraud intelligence.

### Key Capabilities

- **Automated Fraud Detection**: Uses IsolationForest ML algorithm to identify anomalous trade patterns
- **AI-Powered Explanations**: Integrates Google Gemini API for natural language fraud analysis
- **Real-Time Monitoring**: Interactive dashboard with live alerts and KPI tracking
- **Investigation Tools**: Natural language query interface for fraud investigation
- **Visual Analytics**: Geographic route mapping, price deviation charts, and network analysis


## ✨ Features

### Core Features

- **🤖 Machine Learning Fraud Detection**
  - IsolationForest anomaly detection algorithm
  - 6 engineered fraud-detection features
  - Risk classification: SAFE, SUSPICIOUS, FRAUD
  - Automated model training and persistence

- **🧠 AI-Powered Explanations**
  - Google Gemini API integration
  - Natural language fraud explanations
  - Context-aware investigation assistant
  - Quota management and fallback system

- **📊 Interactive Dashboard**
  - Real-time KPI metrics (fraud rate, trade value, high-risk countries)
  - Suspicious transactions table with filtering and sorting
  - Priority-based fraud alerts
  - Dark theme with modern card-based layout

- **🗺️ Visual Analytics**
  - Route Intelligence Map: Geographic visualization of trade routes
  - Price Deviation Chart: Market price vs trade price analysis
  - Company Risk Network: Entity relationship visualization
  - Interactive Plotly charts with tooltips

- **🚨 Alert System**
  - Automated alerts for high-risk transactions
  - Multiple trigger criteria (price, route, company, port)
  - Alert prioritization and categorization
  - Visual alert indicators

- **🔍 Investigation Tools**
  - Natural language query interface
  - Transaction detail exploration
  - AI-powered fraud analysis
  - Conversation history tracking


## 🛠️ Technology Stack

### Backend
- **FastAPI** (0.104.1) - Modern, high-performance web framework
- **Uvicorn** (0.24.0) - ASGI server for FastAPI
- **scikit-learn** (1.3.2) - Machine learning library for IsolationForest
- **Pandas** (2.1.3) - Data manipulation and analysis
- **NumPy** (1.24.3) - Numerical computing

### Frontend
- **Streamlit** (1.28.2) - Interactive web dashboard framework
- **Plotly** (5.18.0) - Interactive visualization library
- **NetworkX** (3.2.1) - Network graph analysis

### AI Integration
- **Google Generative AI** (0.3.1) - Gemini API for AI explanations

### Development & Testing
- **pytest** (7.4.3) - Testing framework
- **hypothesis** (6.88.1) - Property-based testing
- **pytest-cov** (4.1.0) - Code coverage reporting
- **python-dotenv** (1.0.0) - Environment variable management


## 📋 Prerequisites

### System Requirements

- **Operating System**: Windows 10/11, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python**: Version 3.8 or higher
- **RAM**: Minimum 4GB (8GB recommended)
- **Disk Space**: At least 500MB free space
- **Internet Connection**: Required for Gemini API integration

### Required Software

1. **Python 3.8+**: Download from [python.org](https://www.python.org/downloads/)
2. **pip**: Python package installer (included with Python)
3. **Git** (optional): For cloning the repository

### Optional Requirements

- **Virtual Environment**: Recommended for dependency isolation
- **Google Gemini API Key**: For AI-powered explanations (system works with fallback if unavailable)


## 🚀 Installation

### Quick Start (Recommended)

```bash
# 1. Clone or download the repository
git clone <repository-url>
cd trinetra-ai-fraud-detection

# 2. Create and activate virtual environment
# On Windows:
python -m venv trinetra_env
trinetra_env\Scripts\activate

# On macOS/Linux:
python3 -m venv trinetra_env
source trinetra_env/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python main.py
```

### Detailed Installation Steps

#### Step 1: Set Up Virtual Environment

**Windows:**
```bash
# Create virtual environment
python -m venv trinetra_env

# Activate virtual environment
trinetra_env\Scripts\activate

# Verify activation (you should see (trinetra_env) in your prompt)
```

**macOS/Linux:**
```bash
# Create virtual environment
python3 -m venv trinetra_env

# Activate virtual environment
source trinetra_env/bin/activate

# Verify activation (you should see (trinetra_env) in your prompt)
```

#### Step 2: Install Dependencies

```bash
# Upgrade pip to latest version
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt

# Verify installation
pip list
```

#### Step 3: Verify Dataset

Ensure the dataset file exists:
```bash
# Check if dataset exists
ls data/trinetra_trade_fraud_dataset_1000_rows_complex.csv  # macOS/Linux
dir data\trinetra_trade_fraud_dataset_1000_rows_complex.csv  # Windows
```


## ⚙️ Configuration

### Environment Variables (Optional)

The system works with default configuration, but you can customize settings using environment variables.

#### Step 1: Create .env File

```bash
# Copy the example environment file
cp .env.example .env  # macOS/Linux
copy .env.example .env  # Windows
```

#### Step 2: Configure Gemini API Key (Optional)

Edit `.env` file and add your Gemini API key:

```bash
# Get your API key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_actual_api_key_here
```

**Note**: The system includes a pre-configured API key for demo purposes. You can also run without Gemini API - the system will use fallback explanations.

#### Configuration Options

```bash
# API Configuration
API_HOST=localhost
API_PORT=8000

# Dataset Path
DATASET_PATH=data/trinetra_trade_fraud_dataset_1000_rows_complex.csv

# Model Path
MODEL_PATH=models/isolation_forest.pkl

# ML Model Parameters
ISOLATION_FOREST_N_ESTIMATORS=100
ISOLATION_FOREST_CONTAMINATION=0.1

# Risk Thresholds
RISK_THRESHOLD_SAFE=-0.2
RISK_THRESHOLD_FRAUD=0.2

# Alert Thresholds
ALERT_PRICE_DEVIATION_THRESHOLD=0.5
ALERT_COMPANY_RISK_THRESHOLD=0.8
ALERT_PORT_ACTIVITY_THRESHOLD=1.5

# Logging
LOG_LEVEL=INFO
LOG_FILE=trinetra.log
```


## 🎯 Usage

### Starting the Application

#### Single Command Execution (Recommended)

```bash
python main.py
```

This command will:
1. Load and validate the trade transaction dataset
2. Engineer fraud-detection features
3. Train or load the ML model
4. Score all transactions for fraud risk
5. Start the FastAPI backend server (port 8000)
6. Launch the Streamlit dashboard (port 8501)

#### Accessing the Application

Once started, you'll see output like:
```
[INFO] Loading dataset from data/trinetra_trade_fraud_dataset_1000_rows_complex.csv
[INFO] Dataset loaded successfully: 1000 transactions
[INFO] Engineering features...
[INFO] Features engineered successfully
[INFO] Training ML model...
[INFO] Model trained and saved to models/isolation_forest.pkl
[INFO] Scoring transactions...
[INFO] Starting FastAPI backend on http://localhost:8000
[INFO] Starting Streamlit dashboard on http://localhost:8501
[INFO] System ready! Open http://localhost:8501 in your browser
```

**Access Points:**
- 🌐 **API Server**: http://localhost:8000
- 📊 **API Documentation**: http://localhost:8000/docs
- 📱 **Dashboard**: http://localhost:8501

### Using the Dashboard

#### 1. Global Trade Overview
- View total transactions, fraud rate, trade value, and high-risk countries
- Monitor real-time KPI metrics

#### 2. Fraud Alerts
- Review critical fraud alerts
- See alert criteria and severity levels
- Click alerts for detailed investigation

#### 3. Suspicious Transactions Table
- Browse all flagged transactions
- Sort by risk score, price deviation, or other columns
- Filter by risk category (SAFE, SUSPICIOUS, FRAUD)
- Click "Get AI Explanation" for detailed fraud analysis
- Use "Get Fallback Explanation" when quota is reached

#### 4. Route Intelligence Map
- Visualize trade routes on interactive map
- See export and import port locations
- Routes colored by risk level (green=safe, yellow=suspicious, red=fraud)

#### 5. Price Deviation Chart
- Compare market prices vs actual trade prices
- Identify pricing anomalies
- Interactive tooltips show transaction details

#### 6. Company Risk Network
- Explore trading relationships between companies
- Node size represents transaction volume
- Edge color indicates risk level

#### 7. AI Investigation Assistant
- Ask natural language questions about transactions
- Example: "Why is transaction TXN00452 suspicious?"
- Get AI-powered insights and explanations

### Stopping the Application

Press `Ctrl+C` in the terminal to gracefully shutdown all services.


## 📁 Project Structure

```
trinetra-ai-fraud-detection/
│
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variables template
├── .gitignore                       # Git ignore rules
│
├── backend/                         # Backend modules
│   ├── data_loader.py              # CSV loading and validation
│   ├── feature_engineering.py      # Feature generation (6 features)
│   ├── model.py                    # ML model training (IsolationForest)
│   ├── fraud_detection.py          # Fraud scoring and classification
│   ├── ai_explainer.py             # Gemini API integration
│   └── api.py                      # FastAPI REST endpoints
│
├── frontend/                        # Frontend modules
│   └── dashboard.py                # Streamlit dashboard UI
│
├── utils/                           # Utility modules
│   └── helpers.py                  # Helper functions and utilities
│
├── data/                            # Data directory
│   └── trinetra_trade_fraud_dataset_1000_rows_complex.csv
│
├── models/                          # ML models (auto-created)
│   └── isolation_forest.pkl        # Trained IsolationForest model
│
├── logs/                            # Application logs (auto-created)
│   ├── trinetra_main.log
│   ├── trinetra_data_loader.log
│   └── trinetra_model.log
│
├── tests/                           # Test suite
│   ├── test_data_integrity_property.py
│   ├── test_risk_score_consistency_property.py
│   ├── test_feature_engineering_property.py
│   ├── test_api_response_validity_property.py
│   └── test_alert_trigger_accuracy_property.py
│
└── .github/                         # GitHub configuration
    └── workflows/
        └── ci.yml                   # CI/CD pipeline
```

### Key Components

#### Backend Modules

- **data_loader.py**: Loads CSV dataset, validates schema, handles missing values
- **feature_engineering.py**: Generates 6 fraud-detection features from raw data
- **model.py**: Trains and persists IsolationForest ML model
- **fraud_detection.py**: Scores transactions and classifies risk levels
- **ai_explainer.py**: Integrates Gemini API for natural language explanations
- **api.py**: Provides RESTful API endpoints for frontend

#### Frontend Modules

- **dashboard.py**: Streamlit-based interactive dashboard with visualizations

#### Data Flow

```
CSV Dataset → Data Loader → Feature Engineering → ML Model → 
Fraud Detection → API Endpoints → Dashboard Visualization
                                ↓
                          Gemini API (Explanations)
```


## 🔌 API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 1. Get All Transactions
```http
GET /transactions
```

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "transaction_id": "TXN00001",
      "product": "Electronics",
      "unit_price": 1250.50,
      "market_price": 1200.00,
      "risk_score": 0.35,
      "risk_category": "FRAUD",
      ...
    }
  ]
}
```

#### 2. Get Suspicious Transactions
```http
GET /suspicious
```

Returns only transactions with `risk_category = "SUSPICIOUS"`

#### 3. Get Fraud Transactions
```http
GET /fraud
```

Returns only transactions with `risk_category = "FRAUD"`

#### 4. Get Transaction Explanation
```http
POST /explain/{transaction_id}
```

**Parameters:**
- `transaction_id` (path): Transaction ID to explain

**Response:**
```json
{
  "status": "success",
  "data": {
    "transaction_id": "TXN00452",
    "explanation": "This transaction shows suspicious patterns...",
    "risk_factors": ["price_anomaly", "route_anomaly"],
    "quota_info": {
      "remaining": 45,
      "total": 50
    }
  }
}
```

#### 5. Natural Language Query
```http
POST /query
```

**Request Body:**
```json
{
  "query": "Why is transaction TXN00452 suspicious?"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "answer": "Transaction TXN00452 is flagged as suspicious because...",
    "context": {...}
  }
}
```

#### 6. Get Statistics
```http
GET /stats
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "total_transactions": 1000,
    "fraud_rate": 12.5,
    "total_trade_value": 15000000.00,
    "high_risk_countries": 8,
    "alert_count": 23
  }
}
```

#### 7. Session Management
```http
GET /session/info
POST /session/reset
```

Manage Gemini API quota and session state.

### Interactive API Documentation

Visit http://localhost:8000/docs for interactive Swagger UI documentation.


## 🧪 Testing

### Running Tests

#### Run All Tests
```bash
# Run complete test suite
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=backend --cov=utils --cov-report=term-missing
```

#### Run Property-Based Tests
```bash
# Run all property tests
pytest backend/test_*_property.py -v

# Run specific property test
pytest backend/test_data_integrity_property.py -v
pytest backend/test_risk_score_consistency_property.py -v
pytest backend/test_feature_engineering_property.py -v
pytest backend/test_api_response_validity_property.py -v
pytest backend/test_alert_trigger_accuracy_property.py -v
```

#### Run Unit Tests
```bash
# Run unit tests for specific module
pytest backend/test_data_loader.py -v
pytest backend/test_model.py -v
pytest backend/test_fraud_detection.py -v
```

### Test Coverage

The project includes comprehensive testing:

- **Unit Tests**: Test individual functions and modules
- **Integration Tests**: Test component interactions
- **Property-Based Tests**: Validate correctness properties using Hypothesis

**Coverage Goals:**
- Overall code coverage: >80%
- Critical modules (fraud_detection, model): >90%

### Continuous Integration

The project uses GitHub Actions for automated testing:
- Runs on every push and pull request
- Tests against Python 3.9, 3.10, and 3.11
- Generates coverage reports
- Validates all property-based tests

See `.github/workflows/ci.yml` for CI configuration.


## 🔧 Troubleshooting

### Common Issues and Solutions

#### Issue: Port Already in Use

**Error:**
```
OSError: [Errno 48] Address already in use
```

**Solution:**
```bash
# Find and kill process using port 8000 or 8501
# On Windows:
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# On macOS/Linux:
lsof -ti:8000 | xargs kill -9
lsof -ti:8501 | xargs kill -9
```

Or modify ports in `main.py`:
```python
API_PORT = 8001  # Change from 8000
STREAMLIT_PORT = 8502  # Change from 8501
```

#### Issue: Dataset Not Found

**Error:**
```
FileNotFoundError: data/trinetra_trade_fraud_dataset_1000_rows_complex.csv not found
```

**Solution:**
- Verify the dataset file exists in the `data/` directory
- Check file name spelling and path
- Ensure you're running from the project root directory

#### Issue: Module Import Errors

**Error:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```bash
# Ensure virtual environment is activated
# Then reinstall dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep fastapi
```

#### Issue: Gemini API Errors

**Error:**
```
google.api_core.exceptions.PermissionDenied: API key not valid
```

**Solution:**
- The system works with fallback explanations if Gemini API fails
- To use Gemini API, get a valid API key from https://makersuite.google.com/app/apikey
- Add key to `.env` file: `GEMINI_API_KEY=your_key_here`
- Or use the pre-configured demo key

#### Issue: Model Training Fails

**Error:**
```
ValueError: Input contains NaN, infinity or a value too large
```

**Solution:**
- Check dataset for missing or invalid values
- Verify feature engineering handles edge cases
- Review logs in `logs/trinetra_model.log`

#### Issue: Dashboard Not Loading

**Problem:** Browser shows "This site can't be reached"

**Solution:**
1. Check if Streamlit started successfully in terminal output
2. Verify port 8501 is not blocked by firewall
3. Try accessing http://127.0.0.1:8501 instead of localhost
4. Clear browser cache and reload

#### Issue: Slow Performance

**Problem:** Dashboard takes too long to load

**Solution:**
- Reduce dataset size for testing
- Enable caching in Streamlit (already configured)
- Close other resource-intensive applications
- Increase system RAM allocation

#### Issue: Virtual Environment Not Activating

**Windows:**
```bash
# If activation fails, try:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
trinetra_env\Scripts\activate
```

**macOS/Linux:**
```bash
# Ensure script has execute permissions
chmod +x trinetra_env/bin/activate
source trinetra_env/bin/activate
```

### Getting Help

If you encounter issues not covered here:

1. Check application logs in `logs/` directory
2. Review error messages carefully
3. Ensure all prerequisites are met
4. Verify Python version: `python --version` (should be 3.8+)
5. Check GitHub Issues for similar problems
6. Create a new issue with error details and logs


## 🎬 Demo Scenarios

### Scenario 1: High-Risk Transaction Investigation

**Objective:** Investigate a transaction flagged as FRAUD

**Steps:**
1. Start the application: `python main.py`
2. Open dashboard at http://localhost:8501
3. Navigate to "Fraud Alerts" section
4. Click on a red alert (FRAUD category)
5. Review transaction details in the table
6. Click "Get AI Explanation" button
7. Read the AI-generated fraud analysis
8. Check Route Intelligence Map for geographic anomalies
9. Review Price Deviation Chart for pricing issues

**Expected Outcome:** Clear understanding of why the transaction is fraudulent with specific risk factors identified.

---

### Scenario 2: Price Anomaly Detection

**Objective:** Identify transactions with significant price deviations

**Steps:**
1. Open the dashboard
2. Scroll to "Price Deviation Chart"
3. Look for red dots (high-risk transactions)
4. Hover over dots to see transaction details
5. Identify transactions where trade price significantly differs from market price
6. Click on suspicious transactions in the table
7. Get AI explanation for pricing anomalies

**Expected Outcome:** Identification of overpriced or underpriced transactions that may indicate fraud.

---

### Scenario 3: Route Intelligence Analysis

**Objective:** Detect unusual shipping routes

**Steps:**
1. Navigate to "Route Intelligence Map"
2. Observe trade routes between export and import ports
3. Identify routes colored in red (high risk)
4. Look for unusual route patterns (e.g., long detours, high-risk regions)
5. Cross-reference with transaction table
6. Filter transactions by route_anomaly = 1
7. Investigate flagged routes

**Expected Outcome:** Discovery of suspicious shipping routes that deviate from normal patterns.

---

### Scenario 4: Company Risk Network Analysis

**Objective:** Identify high-risk trading entities

**Steps:**
1. Scroll to "Company Risk Network" visualization
2. Observe node sizes (larger = more transactions)
3. Identify nodes with red edges (high-risk connections)
4. Filter transactions by company name
5. Review company_risk_score values
6. Investigate companies with scores > 0.8
7. Get AI explanation for company-related risks

**Expected Outcome:** Identification of companies with suspicious trading patterns.

---

### Scenario 5: Natural Language Investigation

**Objective:** Use AI assistant for fraud investigation

**Steps:**
1. Navigate to "AI Investigation Assistant" section
2. Enter query: "Show me transactions with price deviation greater than 50%"
3. Review AI response
4. Ask follow-up: "Why is transaction TXN00452 suspicious?"
5. Get detailed explanation
6. Ask: "What are the common fraud patterns in this dataset?"
7. Analyze AI insights

**Expected Outcome:** Interactive investigation using natural language queries with AI-powered responses.

---

### Scenario 6: Alert Management

**Objective:** Monitor and respond to fraud alerts

**Steps:**
1. Check "Fraud Alerts" section at dashboard top
2. Review alert count and severity
3. Click on each alert type:
   - PRICE_ANOMALY alerts
   - ROUTE_ANOMALY alerts
   - HIGH_RISK_COMPANY alerts
   - PORT_CONGESTION alerts
4. Investigate transactions triggering multiple alerts
5. Prioritize high-severity cases
6. Document findings

**Expected Outcome:** Systematic review of all fraud alerts with prioritized investigation list.

---

### Scenario 7: KPI Monitoring

**Objective:** Track overall fraud detection metrics

**Steps:**
1. Review "Global Trade Overview" KPIs:
   - Total Transactions
   - Fraud Rate %
   - Total Trade Value
   - High-Risk Countries
2. Monitor fraud rate trends
3. Identify countries with highest fraud rates
4. Compare trade values across risk categories
5. Export statistics for reporting

**Expected Outcome:** Comprehensive understanding of fraud landscape with key metrics.

---

### Hackathon Presentation Tips

**Opening (2 minutes):**
- Introduce TRINETRA AI and its purpose
- Highlight the problem: $1.6 trillion in trade fraud annually
- Show the dashboard overview

**Demo (5 minutes):**
- Run Scenario 1 (High-Risk Transaction Investigation)
- Show AI explanation feature
- Demonstrate Route Intelligence Map
- Use AI Investigation Assistant

**Technical Highlights (2 minutes):**
- Explain IsolationForest ML algorithm
- Show Gemini API integration
- Highlight real-time processing

**Q&A (1 minute):**
- Be prepared to discuss scalability
- Explain feature engineering approach
- Discuss potential real-world applications


## 🏗️ Architecture

### System Architecture

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
│         │              │(IsolationForest)                    │
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

### Component Layers

#### 1. Data Layer
- **CSV Data Loader**: Loads and validates trade transaction data
- **Schema Validation**: Ensures data integrity
- **Missing Value Handling**: Imputes or removes invalid data

#### 2. Feature Engineering Layer
- **Price Anomaly Score**: `abs(price_deviation)`
- **Route Risk Score**: `route_anomaly`
- **Company Network Risk**: `company_risk_score`
- **Port Congestion Score**: `port_activity_index`
- **Shipment Duration Risk**: `shipment_duration_days / distance_km`
- **Volume Spike Score**: `cargo_volume / quantity`

#### 3. Machine Learning Layer
- **Algorithm**: IsolationForest (unsupervised anomaly detection)
- **Parameters**: 100 estimators, 10% contamination rate
- **Training**: Automated on first run, then loads from disk
- **Persistence**: Model saved to `models/isolation_forest.pkl`

#### 4. Fraud Detection Layer
- **Scoring**: Generates anomaly scores for all transactions
- **Classification**: SAFE (< -0.2), SUSPICIOUS (-0.2 to 0.2), FRAUD (> 0.2)
- **Alert Generation**: Triggers alerts based on multiple criteria

#### 5. API Layer (FastAPI)
- **REST Endpoints**: 7 endpoints for data access
- **CORS Support**: Enables frontend integration
- **Error Handling**: Graceful error responses
- **Session Management**: Quota tracking for Gemini API

#### 6. AI Explanation Layer
- **Gemini Integration**: Google Generative AI API
- **Natural Language Processing**: Converts fraud data to explanations
- **Quota Management**: Tracks API usage (50 calls per session)
- **Fallback System**: Rule-based explanations when quota exceeded

#### 7. Presentation Layer (Streamlit)
- **Interactive Dashboard**: Real-time data visualization
- **Plotly Charts**: Interactive geographic and statistical charts
- **Dark Theme**: Modern, professional UI
- **Responsive Design**: Adapts to different screen sizes

### Data Flow

```
1. CSV File
   ↓
2. Data Loader (validation, cleaning)
   ↓
3. Feature Engineering (6 features)
   ↓
4. ML Model Training/Loading
   ↓
5. Fraud Detection (scoring + classification)
   ↓
6. FastAPI Backend (REST endpoints)
   ↓
7. Streamlit Dashboard (visualization)
   ↓
8. Gemini API (AI explanations)
```

### Technology Decisions

**Why IsolationForest?**
- Unsupervised learning (no labeled fraud data needed)
- Effective for anomaly detection
- Fast training and inference
- Handles high-dimensional data well

**Why FastAPI?**
- Modern, high-performance framework
- Automatic API documentation
- Async support for better performance
- Type validation with Pydantic

**Why Streamlit?**
- Rapid dashboard development
- Python-native (no JavaScript needed)
- Built-in caching and state management
- Easy deployment

**Why Gemini API?**
- Advanced natural language generation
- Context-aware responses
- Free tier available for demos
- Easy integration


## 📊 Performance Metrics

### System Performance

- **Dashboard Load Time**: < 3 seconds
- **API Response Time**: < 1 second
- **ML Model Training**: < 30 seconds (1000 transactions)
- **Transaction Scoring**: < 5 seconds (1000 transactions)
- **Gemini API Call**: < 10 seconds (with timeout)

### Scalability

**Current Capacity:**
- Dataset: 1000 transactions (demo)
- Concurrent Users: 1-5 (local deployment)
- API Throughput: ~100 requests/second

**Production Considerations:**
- Use database (PostgreSQL) instead of CSV
- Implement caching (Redis)
- Deploy with Gunicorn/Nginx
- Use load balancer for multiple instances
- Implement batch processing for large datasets

## 🔒 Security Considerations

### Current Implementation

- **API Key Management**: Environment variables for Gemini API key
- **Input Validation**: Pydantic models validate all API inputs
- **Error Handling**: Generic error messages (no internal details exposed)
- **CORS**: Configured for local development (restrict in production)

### Production Recommendations

- Use HTTPS for all communications
- Implement authentication and authorization
- Rate limiting on API endpoints
- Encrypt sensitive data at rest
- Regular security audits
- Implement logging and monitoring
- Use secrets management service (AWS Secrets Manager, Azure Key Vault)

## 🚀 Future Enhancements

### Planned Features

1. **Real-Time Data Streaming**
   - Kafka integration for live transaction feeds
   - WebSocket support for real-time dashboard updates

2. **Advanced ML Models**
   - XGBoost for improved accuracy
   - Neural networks for pattern recognition
   - Ensemble methods combining multiple models

3. **Multi-User Support**
   - User authentication and authorization
   - Role-based access control
   - User activity tracking

4. **Database Integration**
   - PostgreSQL for transaction storage
   - Redis for caching
   - Time-series database for metrics

5. **Enhanced Visualizations**
   - 3D network graphs
   - Time-series fraud trends
   - Predictive analytics dashboard

6. **Automated Reporting**
   - PDF report generation
   - Email alerts for critical cases
   - Scheduled reports

7. **Mobile Application**
   - iOS and Android apps
   - Push notifications for alerts
   - Mobile-optimized dashboard

8. **Integration Capabilities**
   - Customs database integration
   - Banking system APIs
   - Regulatory reporting systems

## 📚 Additional Resources

### Documentation

- **API Documentation**: http://localhost:8000/docs (when running)
- **Streamlit Docs**: https://docs.streamlit.io/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **scikit-learn Docs**: https://scikit-learn.org/stable/

### Related Projects

- **IsolationForest**: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html
- **Google Gemini API**: https://ai.google.dev/docs
- **Plotly**: https://plotly.com/python/

### Research Papers

- Liu, F. T., Ting, K. M., & Zhou, Z. H. (2008). "Isolation Forest"
- Trade fraud detection methodologies
- Anomaly detection in financial transactions


## 🤝 Contributing

### How to Contribute

We welcome contributions to TRINETRA AI! Here's how you can help:

1. **Report Bugs**
   - Use GitHub Issues to report bugs
   - Include error messages and logs
   - Describe steps to reproduce

2. **Suggest Features**
   - Open a feature request issue
   - Describe the use case
   - Explain expected behavior

3. **Submit Pull Requests**
   - Fork the repository
   - Create a feature branch
   - Make your changes
   - Add tests for new features
   - Submit PR with clear description

### Development Setup

```bash
# Clone the repository
git clone <repository-url>
cd trinetra-ai-fraud-detection

# Create virtual environment
python -m venv trinetra_env
source trinetra_env/bin/activate  # or trinetra_env\Scripts\activate on Windows

# Install dependencies including dev tools
pip install -r requirements.txt

# Run tests
pytest

# Run with coverage
pytest --cov=backend --cov=utils
```

### Code Style

- Follow PEP 8 guidelines
- Use type hints where possible
- Write docstrings for functions and classes
- Keep functions focused and small
- Add comments for complex logic

### Testing Requirements

- Write unit tests for new functions
- Maintain >80% code coverage
- Add property-based tests for critical logic
- Ensure all tests pass before submitting PR

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### MIT License Summary

- ✅ Commercial use
- ✅ Modification
- ✅ Distribution
- ✅ Private use
- ❌ Liability
- ❌ Warranty

## 👥 Authors and Acknowledgments

### Development Team

- **TRINETRA AI Team** - Initial development and design

### Acknowledgments

- Google Gemini API for AI-powered explanations
- scikit-learn community for machine learning tools
- Streamlit team for the amazing dashboard framework
- FastAPI developers for the modern web framework
- Open-source community for various libraries and tools

### Special Thanks

- Trade fraud detection research community
- Financial regulators and customs authorities for domain insights
- Beta testers and early adopters

## 📞 Contact and Support

### Getting Help

- **Documentation**: Read this README and inline code comments
- **Issues**: Report bugs on GitHub Issues
- **Discussions**: Join GitHub Discussions for questions
- **Email**: [Your contact email]

### Project Links

- **Repository**: [GitHub URL]
- **Documentation**: [Docs URL]
- **Demo**: [Demo URL]
- **Website**: [Project Website]

---

## 🎯 Quick Reference

### Essential Commands

```bash
# Start application
python main.py

# Run tests
pytest

# Install dependencies
pip install -r requirements.txt

# Activate virtual environment
source trinetra_env/bin/activate  # macOS/Linux
trinetra_env\Scripts\activate     # Windows
```

### Important URLs

- Dashboard: http://localhost:8501
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Key Files

- `main.py` - Application entry point
- `backend/api.py` - REST API endpoints
- `frontend/dashboard.py` - Dashboard UI
- `requirements.txt` - Dependencies
- `.env` - Configuration (create from .env.example)

---

<div align="center">

**TRINETRA AI v1.0** - Trade Fraud Intelligence System

*Powered by Machine Learning and Artificial Intelligence*

Made with ❤️ for financial regulators and compliance teams

[⬆ Back to Top](#️-trinetra-ai---trade-fraud-intelligence-system)

</div>
