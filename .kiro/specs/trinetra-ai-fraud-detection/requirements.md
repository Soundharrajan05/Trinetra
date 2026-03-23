# Requirements: TRINETRA AI - Trade Fraud Intelligence System

## Overview
TRINETRA AI is an AI-powered trade fraud detection platform designed to analyze international trade transactions, detect anomalies using machine learning, and provide explainable AI insights. The system simulates how financial regulators and customs authorities detect trade fraud using advanced analytics.

## Business Goals
- Provide real-time fraud detection for international trade transactions
- Enable investigators to understand fraud patterns through AI explanations
- Create a production-ready prototype suitable for hackathon demonstration
- Deliver actionable intelligence through an intuitive dashboard interface

## User Stories

### US-1: Data Ingestion and Processing
**As a** fraud analyst  
**I want** the system to automatically load and process trade transaction data  
**So that** I can analyze transactions without manual data preparation

**Acceptance Criteria:**
- System loads CSV dataset from data/trinetra_trade_fraud_dataset_1000_rows_complex.csv
- Date columns are parsed correctly
- Schema validation ensures data integrity
- Missing or invalid data is handled gracefully

### US-2: Fraud Detection with Machine Learning
**As a** fraud analyst  
**I want** the system to automatically detect suspicious transactions using ML  
**So that** I can focus investigation efforts on high-risk cases

**Acceptance Criteria:**
- IsolationForest model is trained on engineered features
- Transactions are classified as SAFE, SUSPICIOUS, or FRAUD
- Risk scores are calculated for each transaction
- Model is persisted and can be reloaded

### US-3: Feature Engineering
**As a** data scientist  
**I want** the system to generate fraud-relevant features from raw data  
**So that** the ML model can detect complex fraud patterns

**Acceptance Criteria:**
- price_anomaly_score calculated from price_deviation
- route_risk_score derived from route_anomaly
- company_network_risk based on company_risk_score
- port_congestion_score from port_activity_index
- shipment_duration_risk normalized by distance
- volume_spike_score from cargo_volume and quantity

### US-4: AI-Powered Fraud Explanations
**As a** fraud investigator  
**I want** AI-generated explanations for flagged transactions  
**So that** I can understand why a transaction is suspicious

**Acceptance Criteria:**
- Gemini API integration provides natural language explanations
- Explanations include product, pricing, route, and risk factors
- Explanations are generated on-demand for specific transactions
- API key is securely configured

### US-5: RESTful API Backend
**As a** frontend developer  
**I want** a well-structured API to access fraud detection data  
**So that** I can build interactive user interfaces

**Acceptance Criteria:**
- GET /transactions returns all transactions with risk scores
- GET /suspicious returns only suspicious transactions
- GET /fraud returns confirmed fraud cases
- POST /explain/{transaction_id} returns AI explanation
- POST /query supports natural language queries

### US-6: Interactive Dashboard
**As a** fraud analyst  
**I want** a visual dashboard to monitor trade fraud  
**So that** I can quickly identify and investigate suspicious activity

**Acceptance Criteria:**
- Global Trade Overview displays KPIs (total transactions, fraud rate, etc.)
- Suspicious Transactions Table shows flagged cases
- Fraud Alerts highlight critical cases
- Route Intelligence Map visualizes shipping routes
- Price Deviation Chart shows pricing anomalies
- Company Risk Network displays entity relationships
- Dark theme with modern card-based layout
- Interactive Plotly visualizations

### US-7: AI Investigation Assistant
**As a** fraud investigator  
**I want** to ask natural language questions about transactions  
**So that** I can quickly get insights without complex queries

**Acceptance Criteria:**
- Chat interface accepts natural language questions
- Questions are processed by Gemini API
- Responses are contextual and transaction-specific
- Example: "Why is transaction TXN00452 suspicious?"

### US-8: Automated Alert System
**As a** fraud analyst  
**I want** automatic alerts for high-risk transactions  
**So that** I can respond quickly to potential fraud

**Acceptance Criteria:**
- Alerts triggered when price_deviation > 0.5
- Alerts triggered when route_anomaly == 1
- Alerts triggered when company_risk_score > 0.8
- Alerts triggered when port_activity_index > 1.5
- Alerts displayed prominently in dashboard

### US-9: System Deployment
**As a** system administrator  
**I want** a simple deployment process  
**So that** the system can be demonstrated easily

**Acceptance Criteria:**
- Single command execution: python main.py
- All dependencies clearly documented
- System runs locally without external infrastructure
- Clear startup logs and error messages

## Functional Requirements

### FR-1: Data Management
- Load CSV dataset with 1000+ trade transactions
- Parse and validate 30+ data columns
- Handle missing values and data quality issues
- Support data refresh and updates

### FR-2: Machine Learning Pipeline
- Train IsolationForest anomaly detection model
- Engineer 6 fraud-detection features
- Calculate risk scores for all transactions
- Classify transactions into 3 risk categories
- Persist trained model to disk

### FR-3: AI Integration
- Integrate Gemini API for explanations
- Generate fraud explanations on-demand
- Support investigation queries
- Handle API rate limits and errors

### FR-4: API Services
- Implement 5 RESTful endpoints
- Return JSON responses
- Handle errors gracefully
- Support CORS for frontend integration

### FR-5: User Interface
- Streamlit-based dashboard
- 6 visualization sections
- Dark theme styling
- Responsive layout
- Interactive charts with Plotly

### FR-6: Alert Management
- Real-time alert generation
- Multiple alert criteria
- Alert prioritization
- Visual alert indicators

## Non-Functional Requirements

### NFR-1: Performance
- Dashboard loads within 3 seconds
- API responses within 1 second
- ML model training completes within 30 seconds
- Gemini API calls timeout after 10 seconds

### NFR-2: Usability
- Intuitive navigation
- Clear visual hierarchy
- Accessible color schemes
- Responsive design

### NFR-3: Reliability
- Graceful error handling
- Fallback for API failures
- Data validation at all layers
- Logging for debugging

### NFR-4: Maintainability
- Modular code structure
- Clear separation of concerns
- Comprehensive comments
- Consistent naming conventions

### NFR-5: Security
- API key stored securely
- Input validation on all endpoints
- No sensitive data in logs
- HTTPS for production deployment

## Technical Constraints

### TC-1: Technology Stack
- Backend: Python 3.8+ with FastAPI
- ML: scikit-learn
- AI: Gemini API
- Frontend: Streamlit
- Visualization: Plotly

### TC-2: Data Source
- Dataset: data/trinetra_trade_fraud_dataset_1000_rows_complex.csv
- Format: CSV with headers
- Size: 1000 rows, 30+ columns

### TC-3: External Dependencies
- Gemini API key: AIzaSyC0jXIwaSAiPGuOFBXvN0ofK0rivEflShA
- Internet connection required for AI features
- Python package dependencies managed via requirements.txt

## Project Structure
```
project_root/
├── backend/
│   ├── data_loader.py          # CSV loading and validation
│   ├── feature_engineering.py  # Feature generation
│   ├── model.py                # ML model training
│   ├── fraud_detection.py      # Fraud scoring engine
│   ├── ai_explainer.py         # Gemini integration
│   └── api.py                  # FastAPI endpoints
├── frontend/
│   └── dashboard.py            # Streamlit UI
├── models/
│   └── isolation_forest.pkl    # Trained model
├── utils/
│   └── helpers.py              # Utility functions
└── main.py                     # Application entry point
```

## Success Criteria
1. System successfully loads and processes the dataset
2. ML model achieves reasonable fraud detection accuracy
3. Gemini API provides meaningful explanations
4. Dashboard displays all required visualizations
5. System runs with single command: python main.py
6. Demo-ready for hackathon presentation

## Out of Scope
- Real-time data streaming
- Multi-user authentication
- Database persistence
- Production deployment infrastructure
- Mobile application
- Advanced model tuning and optimization
- Integration with external trade databases

## Correctness Properties

### CP-1: Data Integrity
**Property:** All loaded transactions must have valid transaction_id, date, and fraud_label  
**Test Strategy:** Property-based test generating random row indices and validating required fields are non-null

### CP-2: Risk Score Consistency
**Property:** Risk scores must be monotonically related to risk categories (SAFE < SUSPICIOUS < FRAUD)  
**Test Strategy:** Property-based test verifying score thresholds align with category assignments

### CP-3: Feature Engineering Correctness
**Property:** Engineered features must be mathematically correct and within expected ranges  
**Test Strategy:** Property-based test with known input values verifying feature calculations

### CP-4: API Response Validity
**Property:** All API endpoints must return valid JSON with expected schema  
**Test Strategy:** Property-based test calling each endpoint and validating response structure

### CP-5: Alert Trigger Accuracy
**Property:** Alerts must be triggered if and only if threshold conditions are met  
**Test Strategy:** Property-based test with transactions at boundary conditions verifying alert logic
