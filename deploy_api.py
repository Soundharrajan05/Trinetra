#!/usr/bin/env python3
"""
Deployment version of the TRINETRA AI API for Render
Simplified for cloud deployment without local file dependencies
"""

import os
import logging
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import time
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="TRINETRA AI - Trade Fraud Intelligence API",
    description="AI-powered trade fraud detection and analysis",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global data storage
GLOBAL_DATA: Optional[pd.DataFrame] = None
_initialization_complete = False

class APIResponse(BaseModel):
    status: str
    data: Any = None
    message: str = ""

def generate_sample_data():
    """Generate sample fraud detection data for deployment demo."""
    np.random.seed(42)
    
    # Generate 1000 sample transactions
    n_transactions = 1000
    
    data = {
        'transaction_id': [f'TXN{i:05d}' for i in range(1, n_transactions + 1)],
        'product': np.random.choice(['Electronics', 'Textiles', 'Machinery', 'Chemicals', 'Food'], n_transactions),
        'unit_price': np.random.uniform(10, 1000, n_transactions),
        'market_price': np.random.uniform(10, 1000, n_transactions),
        'quantity': np.random.randint(1, 100, n_transactions),
        'company_risk_score': np.random.uniform(0, 1, n_transactions),
        'port_activity_index': np.random.uniform(0.5, 2.0, n_transactions),
        'route_anomaly': np.random.choice([0, 1], n_transactions, p=[0.9, 0.1]),
        'exporter_company': [f'Company_{i%50}' for i in range(n_transactions)],
        'importer_company': [f'Importer_{i%30}' for i in range(n_transactions)],
    }
    
    df = pd.DataFrame(data)
    
    # Calculate derived features
    df['price_deviation'] = abs(df['unit_price'] - df['market_price']) / df['market_price']
    df['trade_value'] = df['unit_price'] * df['quantity']
    
    # Generate risk scores using IsolationForest
    features = ['price_deviation', 'company_risk_score', 'port_activity_index', 'route_anomaly']
    model = IsolationForest(contamination=0.1, random_state=42)
    
    # Fit and predict
    risk_scores = model.decision_function(df[features])
    df['risk_score'] = risk_scores
    
    # Classify risk categories
    def classify_risk(score):
        if score > 0.2:
            return 'FRAUD'
        elif score > -0.2:
            return 'SUSPICIOUS'
        else:
            return 'SAFE'
    
    df['risk_category'] = df['risk_score'].apply(classify_risk)
    
    logger.info(f"Generated {len(df)} sample transactions")
    logger.info(f"Risk distribution: {df['risk_category'].value_counts().to_dict()}")
    
    return df

def initialize_data():
    """Initialize sample data for deployment."""
    global GLOBAL_DATA, _initialization_complete
    
    try:
        logger.info("Initializing sample data for deployment...")
        GLOBAL_DATA = generate_sample_data()
        _initialization_complete = True
        logger.info("Sample data initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize data: {str(e)}")
        _initialization_complete = False

@app.on_event("startup")
async def startup_event():
    """Initialize system on startup."""
    initialize_data()

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "TRINETRA AI API is running"}

@app.get("/", response_model=APIResponse)
async def root():
    """Root endpoint with system information."""
    return APIResponse(
        status="success",
        data={
            "name": "TRINETRA AI - Trade Fraud Intelligence API",
            "version": "1.0.0",
            "description": "AI-powered trade fraud detection and analysis",
            "transactions_loaded": len(GLOBAL_DATA) if GLOBAL_DATA is not None else 0,
            "system_status": "initialized" if _initialization_complete else "initializing"
        },
        message="TRINETRA AI API is running"
    )

@app.get("/transactions", response_model=APIResponse)
async def get_transactions(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Get transactions with pagination."""
    if not _initialization_complete or GLOBAL_DATA is None:
        return APIResponse(
            status="loading",
            message="System is still initializing"
        )
    
    try:
        total_count = len(GLOBAL_DATA)
        
        if offset >= total_count:
            return APIResponse(
                status="success",
                data={
                    "transactions": [],
                    "pagination": {"total": total_count, "limit": limit, "offset": offset, "returned": 0}
                },
                message="No transactions found at this offset"
            )
        
        end_idx = min(offset + limit, total_count)
        transactions_subset = GLOBAL_DATA.iloc[offset:end_idx]
        data = transactions_subset.to_dict(orient="records")
        
        return APIResponse(
            status="success",
            data={
                "transactions": data,
                "pagination": {"total": total_count, "limit": limit, "offset": offset, "returned": len(data)}
            },
            message=f"Retrieved {len(data)} transactions"
        )
        
    except Exception as e:
        return APIResponse(
            status="error",
            message=f"Failed to retrieve transactions: {str(e)}"
        )

@app.get("/suspicious", response_model=APIResponse)
async def get_suspicious_transactions():
    """Get suspicious transactions."""
    if not _initialization_complete or GLOBAL_DATA is None:
        return APIResponse(status="loading", message="System initializing")
    
    try:
        suspicious_df = GLOBAL_DATA[GLOBAL_DATA['risk_category'] == 'SUSPICIOUS']
        transactions = suspicious_df.to_dict(orient="records")
        
        return APIResponse(
            status="success",
            data=transactions,
            message=f"Retrieved {len(transactions)} suspicious transactions"
        )
    except Exception as e:
        return APIResponse(status="error", message=f"Failed to retrieve suspicious transactions: {str(e)}")

@app.get("/fraud", response_model=APIResponse)
async def get_fraud_transactions():
    """Get fraud transactions."""
    if not _initialization_complete or GLOBAL_DATA is None:
        return APIResponse(status="loading", message="System initializing")
    
    try:
        fraud_df = GLOBAL_DATA[GLOBAL_DATA['risk_category'] == 'FRAUD']
        transactions = fraud_df.to_dict(orient="records")
        
        return APIResponse(
            status="success",
            data=transactions,
            message=f"Retrieved {len(transactions)} fraud transactions"
        )
    except Exception as e:
        return APIResponse(status="error", message=f"Failed to retrieve fraud transactions: {str(e)}")

@app.get("/stats", response_model=APIResponse)
async def get_statistics():
    """Get dashboard statistics."""
    if not _initialization_complete or GLOBAL_DATA is None:
        return APIResponse(status="loading", message="System initializing")
    
    try:
        total_transactions = len(GLOBAL_DATA)
        fraud_cases = len(GLOBAL_DATA[GLOBAL_DATA['risk_category'] == 'FRAUD'])
        suspicious_cases = len(GLOBAL_DATA[GLOBAL_DATA['risk_category'] == 'SUSPICIOUS'])
        safe_cases = len(GLOBAL_DATA[GLOBAL_DATA['risk_category'] == 'SAFE'])
        
        fraud_rate = (fraud_cases / total_transactions * 100) if total_transactions > 0 else 0
        suspicious_rate = (suspicious_cases / total_transactions * 100) if total_transactions > 0 else 0
        
        stats = {
            "total_transactions": total_transactions,
            "fraud_cases": fraud_cases,
            "suspicious_cases": suspicious_cases,
            "safe_cases": safe_cases,
            "fraud_rate": round(fraud_rate, 2),
            "suspicious_rate": round(suspicious_rate, 2),
            "avg_risk_score": round(GLOBAL_DATA['risk_score'].mean(), 3),
            "total_trade_value": round(GLOBAL_DATA['trade_value'].sum(), 2),
            "high_risk_countries": 5,
            "alert_statistics": {
                "active_count": fraud_cases + suspicious_cases,
                "priority_counts": {"CRITICAL": fraud_cases, "HIGH": suspicious_cases, "MEDIUM": 0, "LOW": 0}
            }
        }
        
        return APIResponse(status="success", data=stats, message="Statistics retrieved successfully")
        
    except Exception as e:
        return APIResponse(status="error", message=f"Failed to retrieve statistics: {str(e)}")

@app.post("/explain/{transaction_id}", response_model=APIResponse)
async def explain_transaction_endpoint(transaction_id: str, request: dict = None):
    """Generate explanation for a transaction."""
    if not _initialization_complete or GLOBAL_DATA is None:
        return APIResponse(status="loading", message="System initializing")
    
    try:
        transaction_row = GLOBAL_DATA[GLOBAL_DATA['transaction_id'] == transaction_id]
        
        if transaction_row.empty:
            return APIResponse(status="error", message=f"Transaction {transaction_id} not found")
        
        transaction = transaction_row.iloc[0].to_dict()
        risk_category = transaction.get('risk_category', 'UNKNOWN')
        risk_score = transaction.get('risk_score', 0)
        price_deviation = transaction.get('price_deviation', 0)
        
        if risk_category == 'FRAUD':
            explanation = f"🚨 HIGH RISK: Transaction {transaction_id} classified as FRAUD (risk score: {risk_score:.3f}). Price deviation: {price_deviation:.1%}. Immediate investigation required."
        elif risk_category == 'SUSPICIOUS':
            explanation = f"⚠️ SUSPICIOUS: Transaction {transaction_id} shows suspicious patterns (risk score: {risk_score:.3f}). Price deviation: {price_deviation:.1%}. Enhanced due diligence recommended."
        else:
            explanation = f"✅ LOW RISK: Transaction {transaction_id} appears normal (risk score: {risk_score:.3f}). Standard processing recommended."
        
        return APIResponse(
            status="success",
            data={
                "transaction_id": transaction_id,
                "explanation": explanation,
                "explanation_type": "rule_based",
                "session_info": {"current_count": 0, "max_count": 3, "remaining": 3}
            },
            message=f"Generated explanation for transaction {transaction_id}"
        )
        
    except Exception as e:
        return APIResponse(status="error", message=f"Failed to explain transaction: {str(e)}")

@app.post("/query", response_model=APIResponse)
async def natural_language_query(request: dict):
    """Process natural language queries."""
    if not _initialization_complete or GLOBAL_DATA is None:
        return APIResponse(status="loading", message="System initializing")
    
    query = request.get("query", "")
    
    try:
        total_transactions = len(GLOBAL_DATA)
        fraud_cases = len(GLOBAL_DATA[GLOBAL_DATA['risk_category'] == 'FRAUD'])
        fraud_rate = (fraud_cases / total_transactions * 100) if total_transactions > 0 else 0
        
        if "fraud rate" in query.lower():
            answer = f"The current fraud rate is {fraud_rate:.1f}% ({fraud_cases} out of {total_transactions} transactions)."
        elif "total" in query.lower():
            answer = f"There are {total_transactions} total transactions in the system."
        else:
            answer = f"System overview: {total_transactions} transactions, {fraud_rate:.1f}% fraud rate."
        
        return APIResponse(
            status="success",
            data={"query": query, "answer": answer, "response_type": "rule_based"},
            message="Query processed successfully"
        )
        
    except Exception as e:
        return APIResponse(status="error", message=f"Failed to process query: {str(e)}")

@app.get("/session/info", response_model=APIResponse)
async def get_session_info():
    """Get session information."""
    return APIResponse(
        status="success",
        data={"current_count": 0, "max_count": 3, "remaining": 3, "can_make_explanation": True},
        message="Session info retrieved"
    )

@app.get("/alerts/active", response_model=APIResponse)
async def get_active_alerts():
    """Get active alerts."""
    return APIResponse(
        status="success",
        data={"summaries": [], "count": 0},
        message="No active alerts"
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")