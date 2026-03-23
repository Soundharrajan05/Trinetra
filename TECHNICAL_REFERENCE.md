# 🔬 TRINETRA AI - Technical Reference

> **Quick technical reference for judges and evaluators**

## System Architecture

```
Streamlit Dashboard (8501) ←→ FastAPI Backend (8000) ←→ Gemini API
                                      ↓
                              ML Pipeline (IsolationForest)
                                      ↓
                              Data Layer (Pandas/CSV)
```

## Technology Stack

**Backend:** FastAPI, scikit-learn, Pandas  
**Frontend:** Streamlit, Plotly  
**AI:** Google Gemini API  
**Testing:** pytest, hypothesis

## ML Pipeline

**Algorithm:** IsolationForest (unsupervised anomaly detection)  
**Features:** 6 engineered fraud indicators  
**Classification:** SAFE (<-0.2), SUSPICIOUS (-0.2 to 0.2), FRAUD (>0.2)  
**Training Time:** <30 seconds for 1,000 transactions

## API Endpoints

- `GET /transactions` - All transactions with risk scores
- `GET /suspicious` - Suspicious transactions only
- `GET /fraud` - Fraud transactions only
- `POST /explain/{id}` - AI explanation for transaction
- `POST /query` - Natural language queries
- `GET /stats` - Dashboard statistics

## Performance Metrics

- Dashboard Load: <3 seconds
- API Response: <1 second
- ML Training: <30 seconds
- Transaction Processing: <5 seconds

## Security Features

- API key management via environment variables
- Input validation with Pydantic
- CORS configuration
- Error handling with generic messages

## Testing Coverage

- Unit tests for all modules
- Integration tests for data pipeline
- Property-based tests (5 correctness properties)
- Overall coverage: >80%

## Deployment

**Single Command:** `python main.py`  
**Requirements:** Python 3.8+, 4GB RAM, Internet connection  
**Startup Time:** ~30 seconds

## Scalability Path

**Current:** 1,000 transactions, CSV storage  
**Production:** PostgreSQL + Redis + Load balancing → 1M+ transactions

## Innovation Highlights

1. Hybrid AI (ML detection + AI explanation)
2. Production-ready (single command deployment)
3. Explainable AI (regulatory compliance)
4. User-friendly (no technical expertise needed)

---

**For complete details, see:**
- `README.md` - Full documentation
- `API_DOCUMENTATION.md` - API reference
- `HACKATHON_PRESENTATION.md` - Presentation guide
