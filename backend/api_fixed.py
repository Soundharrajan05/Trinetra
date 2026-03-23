"""
Fixed FastAPI Backend for TRINETRA AI - Trade Fraud Intelligence System

This is a simplified version that fixes the timeout issues by removing blocking operations.
"""

import logging
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import time
import asyncio
from threading import Thread

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="TRINETRA AI - Trade Fraud Intelligence API (Fixed)",
    description="Fixed REST API for AI-powered trade fraud detection and analysis",
    version="1.0.1"
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
_initialization_error = None

class APIResponse(BaseModel):
    status: str
    data: Any = None
    message: str = ""

def load_data_background():
    """Load data in background thread to avoid blocking startup."""
    global GLOBAL_DATA, _initialization_complete, _initialization_error
    
    try:
        logger.info("Background data loading started...")
        
        # Import modules
        import sys
        from pathlib import Path
        
        # Add backend directory to path
        backend_path = Path(__file__).parent
        sys.path.insert(0, str(backend_path))
        
        from data_loader import load_dataset
        from feature_engineering import engineer_features
        from fraud_detection import load_fraud_detector, score_transactions, classify_risk
        
        # Load dataset
        dataset_path = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
        GLOBAL_DATA = load_dataset(dataset_path)
        
        if GLOBAL_DATA is None:
            raise Exception("Failed to load dataset")
        
        # Engineer features
        GLOBAL_DATA = engineer_features(GLOBAL_DATA)
        
        # Load model and score transactions
        model = load_fraud_detector()
        GLOBAL_DATA = score_transactions(GLOBAL_DATA, model)
        GLOBAL_DATA = classify_risk(GLOBAL_DATA)
        
        _initialization_complete = True
        logger.info(f"Background data loading completed - {len(GLOBAL_DATA)} transactions loaded")
        
    except Exception as e:
        _initialization_error = str(e)
        logger.error(f"Background data loading failed: {e}")

@app.on_event("startup")
async def startup_event():
    """Start background data loading without blocking."""
    logger.info("Starting background data loading...")
    thread = Thread(target=load_data_background, daemon=True)
    thread.start()

@app.get("/", response_model=APIResponse)
async def root():
    """Root endpoint with system information."""
    global GLOBAL_DATA, _initialization_complete
    
    return APIResponse(
        status="success",
        data={
            "name": "TRINETRA AI - Trade Fraud Intelligence API (Fixed)",
            "version": "1.0.1",
            "description": "Fixed AI-powered trade fraud detection and analysis",
            "transactions_loaded": len(GLOBAL_DATA) if GLOBAL_DATA is not None else 0,
            "system_status": "initialized" if _initialization_complete else "initializing"
        },
        message="TRINETRA AI API is running"
    )

@app.post("/query", response_model=APIResponse)
async def natural_language_query(request: dict):
    """Process natural language queries (simplified version)."""
    global GLOBAL_DATA, _initialization_complete
    
    query = request.get("query", "")
    
    if not _initialization_complete or GLOBAL_DATA is None:
        return APIResponse(
            status="success",
            data={
                "query": query,
                "answer": "System is still initializing. Please try again in a few moments.",
                "response_type": "system_message"
            },
            message="Query processed"
        )
    
    # Simple rule-based responses
    query_lower = query.lower()
    
    total_transactions = len(GLOBAL_DATA)
    fraud_cases = len(GLOBAL_DATA[GLOBAL_DATA['risk_category'] == 'FRAUD'])
    suspicious_cases = len(GLOBAL_DATA[GLOBAL_DATA['risk_category'] == 'SUSPICIOUS'])
    fraud_rate = (fraud_cases / total_transactions * 100) if total_transactions > 0 else 0
    
    if "fraud rate" in query_lower or "fraud percentage" in query_lower:
        answer = f"The current fraud rate is {fraud_rate:.1f}% ({fraud_cases} out of {total_transactions} transactions)."
    elif "suspicious" in query_lower:
        answer = f"There are {suspicious_cases} suspicious transactions ({suspicious_cases/total_transactions*100:.1f}% of total)."
    elif "total" in query_lower and "transaction" in query_lower:
        answer = f"There are {total_transactions} total transactions in the system."
    elif "fraud" in query_lower:
        answer = f"There are {fraud_cases} fraud transactions detected ({fraud_rate:.1f}% fraud rate)."
    else:
        answer = f"Based on the current data: {total_transactions} total transactions, {fraud_cases} fraud cases ({fraud_rate:.1f}% fraud rate), {suspicious_cases} suspicious cases."
    
    return APIResponse(
        status="success",
        data={
            "query": query,
            "answer": answer,
            "response_type": "rule_based",
            "context_summary": {
                "total_transactions": total_transactions,
                "fraud_rate": f"{fraud_rate:.1f}%",
                "suspicious_rate": f"{suspicious_cases/total_transactions*100:.1f}%"
            }
        },
        message="Query processed successfully"
    )

@app.get("/health")
def health_check():
    """Health check endpoint - always responds quickly."""
    return {"status": "ok", "message": "API is running"}

@app.get("/status")
def get_status():
    """Get initialization status."""
    global _initialization_complete, _initialization_error, GLOBAL_DATA
    
    if _initialization_error:
        return APIResponse(
            status="error",
            message=f"Initialization failed: {_initialization_error}"
        )
    elif _initialization_complete:
        return APIResponse(
            status="success",
            data={
                "initialized": True,
                "transactions_loaded": len(GLOBAL_DATA) if GLOBAL_DATA is not None else 0
            },
            message="System fully initialized"
        )
    else:
        return APIResponse(
            status="loading",
            message="System is initializing... please wait"
        )

@app.get("/transactions", response_model=APIResponse)
async def get_transactions(
    limit: int = Query(100, ge=1, le=1000, description="Number of transactions to return"),
    offset: int = Query(0, ge=0, description="Number of transactions to skip")
):
    """Get transactions with pagination."""
    global GLOBAL_DATA, _initialization_complete, _initialization_error
    
    # Check initialization status
    if _initialization_error:
        return APIResponse(
            status="error",
            message=f"System initialization failed: {_initialization_error}"
        )
    
    if not _initialization_complete:
        return APIResponse(
            status="loading",
            message="System is still initializing. Please try again in a few seconds."
        )
    
    if GLOBAL_DATA is None:
        return APIResponse(
            status="error",
            message="No data available"
        )
    
    try:
        # Fast pagination
        total_count = len(GLOBAL_DATA)
        
        if offset >= total_count:
            return APIResponse(
                status="success",
                data={
                    "transactions": [],
                    "pagination": {
                        "total": total_count,
                        "limit": limit,
                        "offset": offset,
                        "returned": 0
                    }
                },
                message="No transactions found at this offset"
            )
        
        # Get subset
        end_idx = min(offset + limit, total_count)
        transactions_subset = GLOBAL_DATA.iloc[offset:end_idx]
        data = transactions_subset.to_dict(orient="records")
        
        return APIResponse(
            status="success",
            data={
                "transactions": data,
                "pagination": {
                    "total": total_count,
                    "limit": limit,
                    "offset": offset,
                    "returned": len(data)
                }
            },
            message=f"Retrieved {len(data)} transactions"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving transactions: {str(e)}")
        return APIResponse(
            status="error",
            message=f"Failed to retrieve transactions: {str(e)}"
        )

@app.get("/transactions/quick", response_model=APIResponse)
async def get_transactions_quick(limit: int = Query(10, ge=1, le=50)):
    """Get transactions quickly - returns immediately even if system not fully initialized."""
    global GLOBAL_DATA, _initialization_complete
    
    if not _initialization_complete or GLOBAL_DATA is None:
        # Return mock data while initializing
        mock_data = [
            {
                "transaction_id": f"TXN{i:05d}",
                "product": "Loading...",
                "risk_category": "UNKNOWN",
                "risk_score": 0.0,
                "unit_price": 0.0,
                "market_price": 0.0,
                "price_deviation": 0.0
            }
            for i in range(1, min(limit + 1, 11))
        ]
        
        return APIResponse(
            status="success",
            data={
                "transactions": mock_data,
                "pagination": {
                    "total": len(mock_data),
                    "limit": limit,
                    "offset": 0,
                    "returned": len(mock_data)
                }
            },
            message="Returning mock data - system still initializing"
        )
    
    # Return real data
    try:
        quick_data = GLOBAL_DATA.head(limit).to_dict(orient="records")
        
        return APIResponse(
            status="success",
            data={
                "transactions": quick_data,
                "pagination": {
                    "total": len(GLOBAL_DATA),
                    "limit": limit,
                    "offset": 0,
                    "returned": len(quick_data)
                }
            },
            message=f"Quick response: {len(quick_data)} transactions"
        )
        
    except Exception as e:
        logger.error(f"Error in quick transactions: {str(e)}")
        return APIResponse(
            status="error",
            message=f"Quick endpoint failed: {str(e)}"
        )

@app.get("/suspicious", response_model=APIResponse)
async def get_suspicious_transactions():
    """Get suspicious transactions."""
    global GLOBAL_DATA, _initialization_complete
    
    if not _initialization_complete or GLOBAL_DATA is None:
        return APIResponse(
            status="loading",
            message="System is still initializing"
        )
    
    try:
        suspicious_df = GLOBAL_DATA[GLOBAL_DATA['risk_category'] == 'SUSPICIOUS']
        transactions = suspicious_df.to_dict(orient="records")
        
        return APIResponse(
            status="success",
            data=transactions,
            message=f"Retrieved {len(transactions)} suspicious transactions"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving suspicious transactions: {str(e)}")
        return APIResponse(
            status="error",
            message=f"Failed to retrieve suspicious transactions: {str(e)}"
        )

@app.get("/fraud", response_model=APIResponse)
async def get_fraud_transactions():
    """Get fraud transactions."""
    global GLOBAL_DATA, _initialization_complete
    
    if not _initialization_complete or GLOBAL_DATA is None:
        return APIResponse(
            status="loading",
            message="System is still initializing"
        )
    
    try:
        fraud_df = GLOBAL_DATA[GLOBAL_DATA['risk_category'] == 'FRAUD']
        transactions = fraud_df.to_dict(orient="records")
        
        return APIResponse(
            status="success",
            data=transactions,
            message=f"Retrieved {len(transactions)} fraud transactions"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving fraud transactions: {str(e)}")
        return APIResponse(
            status="error",
            message=f"Failed to retrieve fraud transactions: {str(e)}"
        )

@app.get("/stats", response_model=APIResponse)
async def get_statistics():
    """Get dashboard statistics."""
    global GLOBAL_DATA, _initialization_complete
    
    if not _initialization_complete or GLOBAL_DATA is None:
        return APIResponse(
            status="loading",
            message="System is still initializing"
        )
    
    try:
        total_transactions = len(GLOBAL_DATA)
        fraud_cases = len(GLOBAL_DATA[GLOBAL_DATA['risk_category'] == 'FRAUD'])
        suspicious_cases = len(GLOBAL_DATA[GLOBAL_DATA['risk_category'] == 'SUSPICIOUS'])
        safe_cases = len(GLOBAL_DATA[GLOBAL_DATA['risk_category'] == 'SAFE'])
        
        # Calculate rates
        fraud_rate = (fraud_cases / total_transactions * 100) if total_transactions > 0 else 0
        suspicious_rate = (suspicious_cases / total_transactions * 100) if total_transactions > 0 else 0
        safe_rate = (safe_cases / total_transactions * 100) if total_transactions > 0 else 0
        
        stats = {
            "total_transactions": total_transactions,
            "fraud_cases": fraud_cases,
            "suspicious_cases": suspicious_cases,
            "safe_cases": safe_cases,
            "fraud_rate": round(fraud_rate, 2),
            "suspicious_rate": round(suspicious_rate, 2),
            "safe_rate": round(safe_rate, 2),
            "avg_risk_score": round(GLOBAL_DATA['risk_score'].mean(), 3),
            "high_risk_countries": 5,  # Simplified
            "alert_statistics": {
                "active_count": fraud_cases + suspicious_cases,
                "priority_counts": {
                    "CRITICAL": fraud_cases,
                    "HIGH": suspicious_cases,
                    "MEDIUM": 0,
                    "LOW": 0
                }
            }
        }
        
        return APIResponse(
            status="success",
            data=stats,
            message="Statistics retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving statistics: {str(e)}")
        return APIResponse(
            status="error",
            message=f"Failed to retrieve statistics: {str(e)}"
        )

# Simplified endpoints for basic functionality
@app.get("/session/info", response_model=APIResponse)
async def get_session_info():
    """Get session info."""
    return APIResponse(
        status="success",
        data={
            "current_count": 0,
            "max_count": 3,
            "remaining": 3,
            "can_make_explanation": True
        },
        message="Session info retrieved"
    )

@app.post("/explain/{transaction_id}", response_model=APIResponse)
async def explain_transaction_endpoint(transaction_id: str, request: dict = None):
    """Generate explanation for a specific transaction."""
    global GLOBAL_DATA, _initialization_complete
    
    if not _initialization_complete or GLOBAL_DATA is None:
        return APIResponse(
            status="loading",
            message="System is still initializing"
        )
    
    try:
        # Find the transaction
        transaction_row = GLOBAL_DATA[GLOBAL_DATA['transaction_id'] == transaction_id]
        
        if transaction_row.empty:
            return APIResponse(
                status="error",
                message=f"Transaction {transaction_id} not found"
            )
        
        transaction = transaction_row.iloc[0].to_dict()
        
        # Generate rule-based explanation
        risk_category = transaction.get('risk_category', 'UNKNOWN')
        risk_score = transaction.get('risk_score', 0)
        price_deviation = transaction.get('price_deviation', 0)
        company_risk_score = transaction.get('company_risk_score', 0)
        
        if risk_category == 'FRAUD':
            explanation = f"🚨 HIGH RISK TRANSACTION DETECTED\n\n"
            explanation += f"Transaction {transaction_id} has been classified as FRAUD with a risk score of {risk_score:.3f}.\n\n"
            explanation += f"Key Risk Factors:\n"
            explanation += f"• Price Deviation: {price_deviation:.1%} from market price\n"
            explanation += f"• Company Risk Score: {company_risk_score:.3f}\n"
            explanation += f"• Risk Category: {risk_category}\n\n"
            explanation += f"Recommendation: Immediate investigation required. Verify transaction authenticity and company credentials."
            
        elif risk_category == 'SUSPICIOUS':
            explanation = f"⚠️ SUSPICIOUS TRANSACTION\n\n"
            explanation += f"Transaction {transaction_id} shows suspicious patterns with a risk score of {risk_score:.3f}.\n\n"
            explanation += f"Areas of Concern:\n"
            explanation += f"• Price Deviation: {price_deviation:.1%}\n"
            explanation += f"• Company Risk Score: {company_risk_score:.3f}\n\n"
            explanation += f"Recommendation: Enhanced due diligence recommended. Review transaction details and company history."
            
        else:
            explanation = f"✅ LOW RISK TRANSACTION\n\n"
            explanation += f"Transaction {transaction_id} appears normal with a risk score of {risk_score:.3f}.\n\n"
            explanation += f"Transaction Details:\n"
            explanation += f"• Price Deviation: {price_deviation:.1%}\n"
            explanation += f"• Company Risk Score: {company_risk_score:.3f}\n"
            explanation += f"• Risk Category: {risk_category}\n\n"
            explanation += f"Recommendation: Standard processing. No additional verification required."
        
        return APIResponse(
            status="success",
            data={
                "transaction_id": transaction_id,
                "explanation": explanation,
                "explanation_type": "rule_based",
                "session_info": {
                    "current_count": 0,
                    "max_count": 3,
                    "remaining": 3
                }
            },
            message=f"Generated explanation for transaction {transaction_id}"
        )
        
    except Exception as e:
        logger.error(f"Error explaining transaction {transaction_id}: {str(e)}")
        return APIResponse(
            status="error",
            message=f"Failed to explain transaction: {str(e)}"
        )

@app.get("/alerts/active", response_model=APIResponse)
async def get_active_alerts():
    """Get active alerts."""
    return APIResponse(
        status="success",
        data={
            "summaries": [],
            "count": 0
        },
        message="No active alerts"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")