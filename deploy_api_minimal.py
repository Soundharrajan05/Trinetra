#!/usr/bin/env python3
"""
Minimal deployment version of TRINETRA AI API for Render
No pandas dependency - uses pure Python data structures
"""

import os
import logging
import json
import random
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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
GLOBAL_DATA: List[Dict] = []
_initialization_complete = False

class APIResponse(BaseModel):
    status: str
    data: Any = None
    message: str = ""

def generate_sample_data():
    """Generate sample fraud detection data without pandas."""
    random.seed(42)
    
    # Sample data
    products = ['Electronics', 'Textiles', 'Machinery', 'Chemicals', 'Food']
    companies = [f'Company_{i}' for i in range(50)]
    importers = [f'Importer_{i}' for i in range(30)]
    
    transactions = []
    
    for i in range(1, 1001):  # 1000 transactions
        unit_price = random.uniform(10, 1000)
        market_price = random.uniform(10, 1000)
        quantity = random.randint(1, 100)
        
        # Calculate features
        price_deviation = abs(unit_price - market_price) / market_price
        company_risk_score = random.uniform(0, 1)
        port_activity_index = random.uniform(0.5, 2.0)
        route_anomaly = random.choice([0, 1])
        
        # Simple risk scoring
        risk_factors = [
            price_deviation > 0.3,
            company_risk_score > 0.7,
            port_activity_index > 1.5,
            route_anomaly == 1
        ]
        
        risk_score = sum(risk_factors) / len(risk_factors)
        
        # Classify risk
        if risk_score > 0.6:
            risk_category = 'FRAUD'
        elif risk_score > 0.3:
            risk_category = 'SUSPICIOUS'
        else:
            risk_category = 'SAFE'
        
        transaction = {
            'transaction_id': f'TXN{i:05d}',
            'product': random.choice(products),
            'unit_price': round(unit_price, 2),
            'market_price': round(market_price, 2),
            'quantity': quantity,
            'price_deviation': round(price_deviation, 4),
            'company_risk_score': round(company_risk_score, 3),
            'port_activity_index': round(port_activity_index, 3),
            'route_anomaly': route_anomaly,
            'risk_score': round(risk_score, 3),
            'risk_category': risk_category,
            'trade_value': round(unit_price * quantity, 2),
            'exporter_company': random.choice(companies),
            'importer_company': random.choice(importers)
        }
        
        transactions.append(transaction)
    
    return transactions

def initialize_data():
    """Initialize sample data for deployment."""
    global GLOBAL_DATA, _initialization_complete
    
    try:
        logger.info("Initializing sample data for deployment...")
        GLOBAL_DATA = generate_sample_data()
        _initialization_complete = True
        
        # Log statistics
        fraud_count = len([t for t in GLOBAL_DATA if t['risk_category'] == 'FRAUD'])
        suspicious_count = len([t for t in GLOBAL_DATA if t['risk_category'] == 'SUSPICIOUS'])
        safe_count = len([t for t in GLOBAL_DATA if t['risk_category'] == 'SAFE'])
        
        logger.info(f"Generated {len(GLOBAL_DATA)} transactions")
        logger.info(f"Risk distribution: FRAUD={fraud_count}, SUSPICIOUS={suspicious_count}, SAFE={safe_count}")
        
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
            "transactions_loaded": len(GLOBAL_DATA),
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
    if not _initialization_complete:
        return APIResponse(status="loading", message="System is still initializing")
    
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
        transactions_subset = GLOBAL_DATA[offset:end_idx]
        
        return APIResponse(
            status="success",
            data={
                "transactions": transactions_subset,
                "pagination": {"total": total_count, "limit": limit, "offset": offset, "returned": len(transactions_subset)}
            },
            message=f"Retrieved {len(transactions_subset)} transactions"
        )
        
    except Exception as e:
        return APIResponse(status="error", message=f"Failed to retrieve transactions: {str(e)}")

@app.get("/suspicious", response_model=APIResponse)
async def get_suspicious_transactions():
    """Get suspicious transactions."""
    if not _initialization_complete:
        return APIResponse(status="loading", message="System initializing")
    
    try:
        suspicious_transactions = [t for t in GLOBAL_DATA if t['risk_category'] == 'SUSPICIOUS']
        
        return APIResponse(
            status="success",
            data=suspicious_transactions,
            message=f"Retrieved {len(suspicious_transactions)} suspicious transactions"
        )
    except Exception as e:
        return APIResponse(status="error", message=f"Failed to retrieve suspicious transactions: {str(e)}")

@app.get("/fraud", response_model=APIResponse)
async def get_fraud_transactions():
    """Get fraud transactions."""
    if not _initialization_complete:
        return APIResponse(status="loading", message="System initializing")
    
    try:
        fraud_transactions = [t for t in GLOBAL_DATA if t['risk_category'] == 'FRAUD']
        
        return APIResponse(
            status="success",
            data=fraud_transactions,
            message=f"Retrieved {len(fraud_transactions)} fraud transactions"
        )
    except Exception as e:
        return APIResponse(status="error", message=f"Failed to retrieve fraud transactions: {str(e)}")

@app.get("/stats", response_model=APIResponse)
async def get_statistics():
    """Get dashboard statistics."""
    if not _initialization_complete:
        return APIResponse(status="loading", message="System initializing")
    
    try:
        total_transactions = len(GLOBAL_DATA)
        fraud_cases = len([t for t in GLOBAL_DATA if t['risk_category'] == 'FRAUD'])
        suspicious_cases = len([t for t in GLOBAL_DATA if t['risk_category'] == 'SUSPICIOUS'])
        safe_cases = len([t for t in GLOBAL_DATA if t['risk_category'] == 'SAFE'])
        
        fraud_rate = (fraud_cases / total_transactions * 100) if total_transactions > 0 else 0
        suspicious_rate = (suspicious_cases / total_transactions * 100) if total_transactions > 0 else 0
        
        # Calculate averages
        total_trade_value = sum(t['trade_value'] for t in GLOBAL_DATA)
        avg_risk_score = sum(t['risk_score'] for t in GLOBAL_DATA) / len(GLOBAL_DATA) if GLOBAL_DATA else 0
        
        stats = {
            "total_transactions": total_transactions,
            "fraud_cases": fraud_cases,
            "suspicious_cases": suspicious_cases,
            "safe_cases": safe_cases,
            "fraud_rate": round(fraud_rate, 2),
            "suspicious_rate": round(suspicious_rate, 2),
            "avg_risk_score": round(avg_risk_score, 3),
            "total_trade_value": round(total_trade_value, 2),
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
    if not _initialization_complete:
        return APIResponse(status="loading", message="System initializing")
    
    try:
        # Find transaction
        transaction = None
        for t in GLOBAL_DATA:
            if t['transaction_id'] == transaction_id:
                transaction = t
                break
        
        if not transaction:
            return APIResponse(status="error", message=f"Transaction {transaction_id} not found")
        
        risk_category = transaction['risk_category']
        risk_score = transaction['risk_score']
        price_deviation = transaction['price_deviation']
        
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
    if not _initialization_complete:
        return APIResponse(status="loading", message="System initializing")
    
    query = request.get("query", "")
    
    try:
        total_transactions = len(GLOBAL_DATA)
        fraud_cases = len([t for t in GLOBAL_DATA if t['risk_category'] == 'FRAUD'])
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