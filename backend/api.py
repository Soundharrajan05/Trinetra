"""
FastAPI Backend for TRINETRA AI - Trade Fraud Intelligence System

This module provides REST API endpoints for the fraud detection system,
including transaction data access, AI explanations, and dashboard statistics.

Author: TRINETRA AI Team
Date: 2024
"""

import logging
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import time
from functools import lru_cache
from datetime import datetime, timedelta

# Import common error handlers
try:
    from utils.helpers import error_handlers, performance_tracker
except ImportError:
    # Fallback if utils.helpers is not available
    error_handlers = None
    performance_tracker = None

# Import our modules
from backend.data_loader import load_dataset, validate_schema
from backend.feature_engineering import engineer_features
from backend.fraud_detection import load_fraud_detector, score_transactions, classify_risk
from backend.ai_explainer import (
    explain_transaction, 
    answer_investigation_query,
    reset_session_count,
    get_session_count,
    clear_explanation_cache,
    can_make_explanation,
    MAX_EXPLANATIONS_PER_SESSION
)
from backend.alerts import (
    get_alert_store,
    create_alert_summary,
    AlertPriority
)
from backend.api_performance_optimizations import (
    get_response_cache,
    optimize_dataframe_filtering,
    optimize_dataframe_to_dict,
    get_performance_monitor,
    get_fast_query_response,
    log_performance_summary
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="TRINETRA AI - Trade Fraud Intelligence API",
    description="REST API for AI-powered trade fraud detection and analysis",
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

# Global data storage - prevent state loss
_transactions_df: Optional[pd.DataFrame] = None
_fraud_detector = None
GLOBAL_DATA: Optional[pd.DataFrame] = None

def initialize_data():
    """Initialize global data once at startup with performance monitoring."""
    global GLOBAL_DATA, _transactions_df
    
    if GLOBAL_DATA is not None:
        logger.info("Global data already initialized, skipping...")
        return
    
    total_start = time.time()
    logger.info("[STARTUP] Initializing global data...")
    
    try:
        # Step 1: Load dataset
        load_start = time.time()
        dataset_path = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
        GLOBAL_DATA = load_dataset(dataset_path)
        load_time = (time.time() - load_start) * 1000
        logger.info(f"[STARTUP] Dataset loading took {load_time:.2f}ms")
        
        if GLOBAL_DATA is None:
            logger.error("[STARTUP] Failed to load dataset")
            return
        
        # Step 2: Feature engineering
        feature_start = time.time()
        import sys
        from pathlib import Path
        backend_path = Path(__file__).parent
        sys.path.insert(0, str(backend_path))
        
        from feature_engineering import engineer_features
        GLOBAL_DATA = engineer_features(GLOBAL_DATA)
        feature_time = (time.time() - feature_start) * 1000
        logger.info(f"[STARTUP] Feature engineering took {feature_time:.2f}ms")
        
        # Step 3: Load ML model
        model_start = time.time()
        from fraud_detection import load_fraud_detector, score_transactions, classify_risk
        model = load_fraud_detector()
        model_time = (time.time() - model_start) * 1000
        logger.info(f"[STARTUP] ML model loading took {model_time:.2f}ms")
        
        # Step 4: Score transactions
        scoring_start = time.time()
        GLOBAL_DATA = score_transactions(GLOBAL_DATA, model)
        GLOBAL_DATA = classify_risk(GLOBAL_DATA)
        scoring_time = (time.time() - scoring_start) * 1000
        logger.info(f"[STARTUP] Transaction scoring took {scoring_time:.2f}ms")
        
        # Set global reference
        _transactions_df = GLOBAL_DATA
        
        total_time = (time.time() - total_start) * 1000
        logger.info(f"[STARTUP] ✅ Global data initialized with {len(GLOBAL_DATA)} transactions in {total_time:.2f}ms")
        
    except Exception as e:
        total_time = (time.time() - total_start) * 1000
        logger.error(f"[STARTUP] ❌ Failed to initialize global data after {total_time:.2f}ms: {str(e)}")
        GLOBAL_DATA = None
        _transactions_df = None

# Global data storage
_transactions_df: Optional[pd.DataFrame] = None
_fraud_detector = None

# Simple cache for expensive operations
_stats_cache = {"data": None, "timestamp": None}
_cache_ttl = 300  # Cache TTL in seconds

# Pydantic models for request/response validation
class ExplanationRequest(BaseModel):
    force_ai: bool = False  # Whether to force AI explanation (explicit user request)

class QueryRequest(BaseModel):
    query: str
    
class APIResponse(BaseModel):
    status: str
    data: Any = None
    message: str = ""

class SessionInfo(BaseModel):
    current_count: int
    max_count: int
    can_make_explanation: bool


def initialize_system():
    """Initialize the fraud detection system with data and model."""
    global _transactions_df, _fraud_detector
    
    try:
        logger.info("Initializing TRINETRA AI system...")
        
        # Clear caches on initialization
        cache = get_response_cache()
        cache.clear()
        logger.info("Response caches cleared")
        
        # Load and validate dataset
        logger.info("Loading dataset...")
        dataset_path = "data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
        _transactions_df = load_dataset(dataset_path)
        
        if _transactions_df is None or _transactions_df.empty:
            raise Exception("Failed to load dataset")
        
        validation_result = validate_schema(_transactions_df)
        if not validation_result:
            raise Exception("Dataset validation failed")
        
        # Engineer features
        logger.info("Engineering features...")
        _transactions_df = engineer_features(_transactions_df)
        
        # Load fraud detector
        logger.info("Loading fraud detection model...")
        _fraud_detector = load_fraud_detector()
        
        # Score transactions
        logger.info("Scoring transactions...")
        _transactions_df = score_transactions(_transactions_df, _fraud_detector)
        _transactions_df = classify_risk(_transactions_df)
        
        # Populate alert store (optimized - batch processing)
        logger.info("Populating alert store...")
        alert_store = get_alert_store()
        alert_count = 0
        
        # Process in batches for better performance
        batch_size = 100
        for i in range(0, len(_transactions_df), batch_size):
            batch = _transactions_df.iloc[i:i+batch_size]
            for _, transaction in batch.iterrows():
                transaction_dict = transaction.to_dict()
                summary = create_alert_summary(transaction_dict)
                if summary:
                    alert_store.store_summary(summary)
                    alert_store.store_alerts(summary.alerts)
                    alert_count += 1
        
        logger.info(f"Alert store populated with {alert_count} alert summaries")
        logger.info(f"System initialized successfully with {len(_transactions_df)} transactions")
        
    except Exception as e:
        logger.error(f"Failed to initialize system: {str(e)}")
        raise


@app.on_event("startup")
async def startup_event():
    """Initialize system on startup (only once)."""
    global _transactions_df, GLOBAL_DATA
    
    # Check if already initialized
    if _transactions_df is not None and GLOBAL_DATA is not None:
        logger.info("System already initialized, skipping startup")
        return
    
    try:
        logger.info("FastAPI startup event triggered - initializing system...")
        initialize_data()
        logger.info("FastAPI startup initialization completed successfully")
    except Exception as e:
        logger.error(f"FastAPI startup initialization failed: {str(e)}")
        raise


@app.get("/transactions/quick", response_model=APIResponse)
async def get_transactions_quick(limit: int = Query(10, ge=1, le=50)):
    """Get transactions quickly with minimal processing - fallback endpoint."""
    request_start = time.time()
    logger.info(f"[PERF] /transactions/quick request started - limit={limit}")
    
    try:
        # If global data is not ready, return mock data
        if GLOBAL_DATA is None:
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
        
        # Return first N transactions quickly
        quick_data = GLOBAL_DATA.head(limit).to_dict(orient="records")
        total_time = (time.time() - request_start) * 1000
        
        logger.info(f"[PERF] /transactions/quick completed in {total_time:.2f}ms")
        
        return APIResponse(
            status="success",
            data={
                "transactions": quick_data,
                "pagination": {
                    "total": len(GLOBAL_DATA) if GLOBAL_DATA is not None else 0,
                    "limit": limit,
                    "offset": 0,
                    "returned": len(quick_data)
                }
            },
            message=f"Quick response: {len(quick_data)} transactions in {total_time:.1f}ms"
        )
        
    except Exception as e:
        error_time = (time.time() - request_start) * 1000
        logger.error(f"[PERF] /transactions/quick failed after {error_time:.2f}ms: {str(e)}")
        
        return APIResponse(
            status="error",
            data={"transactions": [], "pagination": {"total": 0, "limit": limit, "offset": 0, "returned": 0}},
            message=f"Quick endpoint failed: {str(e)}"
        )

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/", response_model=APIResponse)
async def root():
    """Root endpoint with system information."""
    global _transactions_df
    
    # Fallback initialization if startup event didn't work
    if _transactions_df is None:
        logger.warning("System not initialized, attempting fallback initialization...")
        try:
            initialize_system()
            logger.info("Fallback initialization completed successfully")
        except Exception as e:
            logger.error(f"Fallback initialization failed: {str(e)}")
            return APIResponse(
                status="error",
                message=f"System initialization failed: {str(e)}"
            )
    
    return APIResponse(
        status="success",
        data={
            "name": "TRINETRA AI - Trade Fraud Intelligence API",
            "version": "1.0.0",
            "description": "AI-powered trade fraud detection and analysis",
            "transactions_loaded": len(_transactions_df) if _transactions_df is not None else 0,
            "system_status": "initialized" if _transactions_df is not None else "not_initialized"
        },
        message="TRINETRA AI API is running"
    )


@app.get("/transactions", response_model=APIResponse)
async def get_transactions(
    limit: int = Query(100, ge=1, le=1000, description="Number of transactions to return"),
    offset: int = Query(0, ge=0, description="Number of transactions to skip")
):
    """Get all transactions with risk scores and pagination (optimized with performance logging)."""
    request_start = time.time()
    global GLOBAL_DATA, _transactions_df
    
    # Log request start
    logger.info(f"[PERF] /transactions request started - limit={limit}, offset={offset}")
    
    try:
        # Ensure data is loaded with timeout protection
        data_load_start = time.time()
        if GLOBAL_DATA is None or _transactions_df is None:
            logger.warning("Global data not loaded, initializing...")
            initialize_data()
        
        if GLOBAL_DATA is None:
            logger.error("Failed to load global data")
            return APIResponse(
                status="error",
                message="Data not loaded - system initialization failed"
            )
        
        data_load_time = (time.time() - data_load_start) * 1000
        logger.info(f"[PERF] Data validation took {data_load_time:.2f}ms")
        
        # Fast pagination with performance logging
        pagination_start = time.time()
        total_count = len(GLOBAL_DATA)
        
        # Optimize for large offsets
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
        
        # Use iloc for fast slicing
        end_idx = min(offset + limit, total_count)
        transactions_subset = GLOBAL_DATA.iloc[offset:end_idx]
        
        pagination_time = (time.time() - pagination_start) * 1000
        logger.info(f"[PERF] Pagination took {pagination_time:.2f}ms")
        
        # Fast conversion to dict
        conversion_start = time.time()
        data = transactions_subset.to_dict(orient="records")
        conversion_time = (time.time() - conversion_start) * 1000
        logger.info(f"[PERF] Data conversion took {conversion_time:.2f}ms")
        
        # Calculate total request time
        total_time = (time.time() - request_start) * 1000
        logger.info(f"[PERF] /transactions completed in {total_time:.2f}ms - returned {len(data)} records")
        
        # Log performance metrics
        if performance_tracker:
            performance_tracker.log_api_response("/transactions", total_time/1000, 200)
        
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
            message=f"Retrieved {len(data)} transactions in {total_time:.1f}ms"
        )
        
    except Exception as e:
        error_time = (time.time() - request_start) * 1000
        logger.error(f"[PERF] /transactions failed after {error_time:.2f}ms: {str(e)}")
        
        if performance_tracker:
            performance_tracker.log_api_response("/transactions", error_time/1000, 500)
        
        # Always return valid JSON even on error
        return APIResponse(
            status="error",
            data={
                "transactions": [],
                "pagination": {
                    "total": 0,
                    "limit": limit,
                    "offset": offset,
                    "returned": 0
                }
            },
            message=f"Failed to retrieve transactions: {str(e)}"
        )


@app.get("/suspicious", response_model=APIResponse)
async def get_suspicious_transactions():
    """Get transactions with risk_category = SUSPICIOUS (optimized with caching)."""
    start_time = time.time()
    
    if _transactions_df is None:
        raise HTTPException(status_code=500, detail="System not initialized")
    
    try:
        # Check cache first
        cache = get_response_cache()
        cached_result = cache.get("suspicious_transactions")
        
        if cached_result is not None:
            response_time = time.time() - start_time
            if performance_tracker:
                performance_tracker.log_api_response("/suspicious", response_time, 200)
            logger.info(f"/suspicious served from cache in {response_time:.3f}s")
            return cached_result
        
        # Cache miss - compute result
        suspicious_df = optimize_dataframe_filtering(_transactions_df, 'risk_category', 'SUSPICIOUS')
        transactions = optimize_dataframe_to_dict(suspicious_df)
        
        result = APIResponse(
            status="success",
            data=transactions,
            message=f"Retrieved {len(transactions)} suspicious transactions"
        )
        
        # Cache the result
        cache.set("suspicious_transactions", result, ttl=30)
        
        response_time = time.time() - start_time
        if performance_tracker:
            performance_tracker.log_api_response("/suspicious", response_time, 200)
        
        return result
        
    except Exception as e:
        response_time = time.time() - start_time
        if performance_tracker:
            performance_tracker.log_api_response("/suspicious", response_time, 500)
        logger.error(f"Error retrieving suspicious transactions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve suspicious transactions: {str(e)}")


@app.get("/fraud", response_model=APIResponse)
async def get_fraud_transactions():
    """Get transactions with risk_category = FRAUD (optimized with caching)."""
    start_time = time.time()
    
    if _transactions_df is None:
        raise HTTPException(status_code=500, detail="System not initialized")
    
    try:
        # Check cache first
        cache = get_response_cache()
        cached_result = cache.get("fraud_transactions")
        
        if cached_result is not None:
            response_time = time.time() - start_time
            if performance_tracker:
                performance_tracker.log_api_response("/fraud", response_time, 200)
            logger.info(f"/fraud served from cache in {response_time:.3f}s")
            return cached_result
        
        # Cache miss - compute result
        fraud_df = optimize_dataframe_filtering(_transactions_df, 'risk_category', 'FRAUD')
        transactions = optimize_dataframe_to_dict(fraud_df)
        
        result = APIResponse(
            status="success",
            data=transactions,
            message=f"Retrieved {len(transactions)} fraud transactions"
        )
        
        # Cache the result
        cache.set("fraud_transactions", result, ttl=30)
        
        response_time = time.time() - start_time
        if performance_tracker:
            performance_tracker.log_api_response("/fraud", response_time, 200)
        
        return result
        
    except Exception as e:
        response_time = time.time() - start_time
        if performance_tracker:
            performance_tracker.log_api_response("/fraud", response_time, 500)
        logger.error(f"Error retrieving fraud transactions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve fraud transactions: {str(e)}")


@app.post("/explain/{transaction_id}", response_model=APIResponse)
async def explain_transaction_endpoint(
    transaction_id: str, 
    request: ExplanationRequest = ExplanationRequest()
):
    """
    Generate AI explanation for a specific transaction.
    
    This endpoint implements quota management to prevent Gemini API errors:
    - Only calls Gemini API when force_ai=True (explicit user request)
    - Limits to 3 AI explanations per session
    - Uses caching to avoid repeated API calls
    - Provides fallback explanations when quota is exceeded
    """
    if _transactions_df is None:
        raise HTTPException(status_code=500, detail="System not initialized")
    
    try:
        # Find the transaction
        transaction_row = _transactions_df[_transactions_df['transaction_id'] == transaction_id]
        
        if transaction_row.empty:
            raise HTTPException(status_code=404, detail=f"Transaction {transaction_id} not found")
        
        transaction = transaction_row.iloc[0].to_dict()
        
        # Generate explanation with quota management
        explanation = explain_transaction(transaction, force_api=request.force_ai)
        
        # Determine explanation type
        explanation_type = "cached"
        if request.force_ai and can_make_explanation():
            explanation_type = "ai_generated"
        elif not can_make_explanation():
            explanation_type = "quota_exceeded"
        else:
            explanation_type = "fallback"
        
        return APIResponse(
            status="success",
            data={
                "transaction_id": transaction_id,
                "explanation": explanation,
                "explanation_type": explanation_type,
                "session_info": {
                    "current_count": get_session_count(),
                    "max_count": MAX_EXPLANATIONS_PER_SESSION,
                    "remaining": MAX_EXPLANATIONS_PER_SESSION - get_session_count()
                }
            },
            message=f"Generated {explanation_type} explanation for transaction {transaction_id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error explaining transaction {transaction_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to explain transaction: {str(e)}")


@app.post("/query", response_model=APIResponse)
async def natural_language_query(request: QueryRequest):
    """
    Process natural language queries about the fraud detection data.
    
    Optimized to use fast fallback responses instead of Gemini API
    to ensure sub-second response times.
    """
    start_time = time.time()
    
    if _transactions_df is None:
        raise HTTPException(status_code=500, detail="System not initialized")
    
    try:
        # Prepare context data
        total_transactions = len(_transactions_df)
        fraud_cases = len(_transactions_df[_transactions_df['risk_category'] == 'FRAUD'])
        suspicious_cases = len(_transactions_df[_transactions_df['risk_category'] == 'SUSPICIOUS'])
        avg_risk_score = _transactions_df['risk_score'].mean()
        
        # Calculate rates
        fraud_rate = f"{(fraud_cases/total_transactions*100):.1f}" if total_transactions > 0 else "0.0"
        suspicious_rate = f"{(suspicious_cases/total_transactions*100):.1f}" if total_transactions > 0 else "0.0"
        
        context = {
            'total_transactions': total_transactions,
            'fraud_cases': fraud_cases,
            'suspicious_cases': suspicious_cases,
            'avg_risk_score': f"{avg_risk_score:.3f}",
            'fraud_rate': fraud_rate,
            'suspicious_rate': suspicious_rate
        }
        
        # Use fast query response (no Gemini API call)
        answer = get_fast_query_response(request.query, context)
        
        response_time = time.time() - start_time
        if performance_tracker:
            performance_tracker.log_api_response("/query", response_time, 200)
        
        logger.info(f"/query processed in {response_time:.3f}s (fast fallback)")
        
        return APIResponse(
            status="success",
            data={
                "query": request.query,
                "answer": answer,
                "response_type": "fast_fallback",
                "context_summary": {
                    "total_transactions": total_transactions,
                    "fraud_rate": f"{fraud_rate}%",
                    "suspicious_rate": f"{suspicious_rate}%"
                }
            },
            message="Query processed successfully"
        )
        
    except Exception as e:
        response_time = time.time() - start_time
        if performance_tracker:
            performance_tracker.log_api_response("/query", response_time, 500)
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process query: {str(e)}")


@app.get("/stats", response_model=APIResponse)
async def get_statistics():
    """Get dashboard statistics and KPIs with caching."""
    global _stats_cache
    
    if _transactions_df is None:
        raise HTTPException(status_code=500, detail="System not initialized")
    
    try:
        # Check if cache is valid
        if (_stats_cache["data"] is not None and 
            _stats_cache["timestamp"] is not None and
            (time.time() - _stats_cache["timestamp"]) < _cache_ttl):
            logger.info("Returning cached statistics")
            return APIResponse(
                status="success",
                data=_stats_cache["data"],
                message="Statistics retrieved successfully (cached)"
            )
        
        # Calculate fresh statistics
        total_transactions = len(_transactions_df)
        fraud_cases = len(_transactions_df[_transactions_df['risk_category'] == 'FRAUD'])
        suspicious_cases = len(_transactions_df[_transactions_df['risk_category'] == 'SUSPICIOUS'])
        safe_cases = len(_transactions_df[_transactions_df['risk_category'] == 'SAFE'])
        
        # Calculate rates
        fraud_rate = (fraud_cases / total_transactions * 100) if total_transactions > 0 else 0
        suspicious_rate = (suspicious_cases / total_transactions * 100) if total_transactions > 0 else 0
        safe_rate = (safe_cases / total_transactions * 100) if total_transactions > 0 else 0
        
        # Calculate total trade value (if available)
        total_trade_value = 0
        if 'unit_price' in _transactions_df.columns and 'quantity' in _transactions_df.columns:
            if 'trade_value' not in _transactions_df.columns:
                _transactions_df['trade_value'] = _transactions_df['unit_price'] * _transactions_df['quantity']
            total_trade_value = _transactions_df['trade_value'].sum()
        
        # High-risk countries (simplified - using port or route data)
        high_risk_countries = []
        if 'shipping_route' in _transactions_df.columns:
            # Extract unique routes and count as "countries"
            routes = _transactions_df['shipping_route'].value_counts().head(5)
            high_risk_countries = routes.index.tolist()
        
        # Get alert statistics (use full statistics from alert store)
        try:
            alert_store = get_alert_store()
            alert_stats = alert_store.get_statistics()
        except Exception as e:
            logger.warning(f"Failed to get alert statistics: {e}")
            alert_stats = {
                'total_summaries': 0,
                'active_count': 0,
                'dismissed_count': 0,
                'priority_counts': {
                    'CRITICAL': 0,
                    'HIGH': 0,
                    'MEDIUM': 0,
                    'LOW': 0
                }
            }
        
        stats = {
            "total_transactions": total_transactions,
            "fraud_cases": fraud_cases,
            "suspicious_cases": suspicious_cases,
            "safe_cases": safe_cases,
            "fraud_rate": round(fraud_rate, 2),
            "suspicious_rate": round(suspicious_rate, 2),
            "safe_rate": round(safe_rate, 2),
            "total_trade_value": round(total_trade_value, 2),
            "high_risk_countries": len(high_risk_countries),
            "avg_risk_score": round(_transactions_df['risk_score'].mean(), 3),
            "alert_statistics": alert_stats,
            "session_info": {
                "explanations_used": get_session_count(),
                "explanations_remaining": MAX_EXPLANATIONS_PER_SESSION - get_session_count(),
                "max_per_session": MAX_EXPLANATIONS_PER_SESSION
            }
        }
        
        # Update cache
        _stats_cache["data"] = stats
        _stats_cache["timestamp"] = time.time()
        
        return APIResponse(
            status="success",
            data=stats,
            message="Statistics retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve statistics: {str(e)}")


@app.post("/session/reset", response_model=APIResponse)
async def reset_session():
    """Reset the session explanation count and clear cache."""
    try:
        reset_session_count()
        clear_explanation_cache()
        
        return APIResponse(
            status="success",
            data={
                "session_count": get_session_count(),
                "max_count": MAX_EXPLANATIONS_PER_SESSION
            },
            message="Session reset successfully"
        )
        
    except Exception as e:
        logger.error(f"Error resetting session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to reset session: {str(e)}")


@app.get("/alerts", response_model=APIResponse)
async def get_all_alerts():
    """Get all alerts from the alert store."""
    try:
        alert_store = get_alert_store()
        all_alerts = alert_store.get_all_alerts()
        
        # Convert alerts to dictionaries
        alerts_data = [alert.to_dict() for alert in all_alerts]
        
        return APIResponse(
            status="success",
            data={
                "alerts": alerts_data,
                "count": len(alerts_data)
            },
            message=f"Retrieved {len(alerts_data)} alerts"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving alerts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve alerts: {str(e)}")


@app.get("/alerts/transaction/{transaction_id}", response_model=APIResponse)
async def get_alerts_by_transaction(transaction_id: str):
    """Get all alerts for a specific transaction."""
    try:
        alert_store = get_alert_store()
        alerts = alert_store.get_alerts_by_transaction(transaction_id)
        
        if not alerts:
            return APIResponse(
                status="success",
                data={
                    "transaction_id": transaction_id,
                    "alerts": [],
                    "count": 0
                },
                message=f"No alerts found for transaction {transaction_id}"
            )
        
        # Convert alerts to dictionaries
        alerts_data = [alert.to_dict() for alert in alerts]
        
        return APIResponse(
            status="success",
            data={
                "transaction_id": transaction_id,
                "alerts": alerts_data,
                "count": len(alerts_data)
            },
            message=f"Retrieved {len(alerts_data)} alerts for transaction {transaction_id}"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving alerts for transaction {transaction_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve alerts: {str(e)}")


@app.get("/alerts/priority/{priority}", response_model=APIResponse)
async def get_alerts_by_priority(priority: str):
    """Get alerts by priority level (CRITICAL, HIGH, MEDIUM, LOW)."""
    try:
        # Validate priority level
        priority_upper = priority.upper()
        if priority_upper not in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid priority level: {priority}. Must be CRITICAL, HIGH, MEDIUM, or LOW"
            )
        
        alert_store = get_alert_store()
        priority_enum = AlertPriority[priority_upper]
        summaries = alert_store.get_alerts_by_priority(priority_enum)
        
        # Convert summaries to dictionaries
        summaries_data = [summary.to_dict() for summary in summaries]
        
        return APIResponse(
            status="success",
            data={
                "priority": priority_upper,
                "summaries": summaries_data,
                "count": len(summaries_data)
            },
            message=f"Retrieved {len(summaries_data)} alerts with {priority_upper} priority"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving alerts by priority {priority}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve alerts: {str(e)}")


@app.get("/alerts/statistics", response_model=APIResponse)
async def get_alert_statistics():
    """Get alert statistics including counts by priority and type."""
    try:
        alert_store = get_alert_store()
        stats = alert_store.get_statistics()
        
        return APIResponse(
            status="success",
            data=stats,
            message="Alert statistics retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving alert statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve alert statistics: {str(e)}")


@app.get("/alerts/summaries", response_model=APIResponse)
async def get_all_alert_summaries(
    min_priority: Optional[str] = Query(None, description="Minimum priority level (CRITICAL, HIGH, MEDIUM, LOW)")
):
    """Get all alert summaries, optionally filtered by minimum priority."""
    try:
        alert_store = get_alert_store()
        
        if min_priority:
            # Validate and filter by minimum priority
            priority_upper = min_priority.upper()
            if priority_upper not in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid priority level: {min_priority}. Must be CRITICAL, HIGH, MEDIUM, or LOW"
                )
            
            priority_enum = AlertPriority[priority_upper]
            summaries = alert_store.get_alerts_by_min_priority(priority_enum)
        else:
            summaries = alert_store.get_all_summaries()
        
        # Convert summaries to dictionaries
        summaries_data = [summary.to_dict() for summary in summaries]
        
        return APIResponse(
            status="success",
            data={
                "summaries": summaries_data,
                "count": len(summaries_data),
                "min_priority": min_priority.upper() if min_priority else None
            },
            message=f"Retrieved {len(summaries_data)} alert summaries"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving alert summaries: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve alert summaries: {str(e)}")


@app.get("/session/info", response_model=APIResponse)
async def get_session_info():
    """Get current session information."""
    try:
        return APIResponse(
            status="success",
            data={
                "current_count": get_session_count(),
                "max_count": MAX_EXPLANATIONS_PER_SESSION,
                "remaining": MAX_EXPLANATIONS_PER_SESSION - get_session_count(),
                "can_make_explanation": can_make_explanation()
            },
            message="Session info retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving session info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve session info: {str(e)}")


@app.post("/alerts/dismiss/{transaction_id}", response_model=APIResponse)
async def dismiss_alert(
    transaction_id: str,
    dismissed_by: str = Query("analyst", description="User who is dismissing the alert")
):
    """Dismiss an alert summary for a specific transaction."""
    try:
        alert_store = get_alert_store()
        success = alert_store.dismiss_alert_summary(transaction_id, dismissed_by)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"No alert found for transaction {transaction_id}"
            )
        
        return APIResponse(
            status="success",
            data={
                "transaction_id": transaction_id,
                "dismissed": True,
                "dismissed_by": dismissed_by
            },
            message=f"Alert for transaction {transaction_id} dismissed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error dismissing alert for transaction {transaction_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to dismiss alert: {str(e)}")


@app.post("/alerts/undismiss/{transaction_id}", response_model=APIResponse)
async def undismiss_alert(transaction_id: str):
    """Undismiss (restore) an alert summary for a specific transaction."""
    try:
        alert_store = get_alert_store()
        success = alert_store.undismiss_alert_summary(transaction_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"No alert found for transaction {transaction_id}"
            )
        
        return APIResponse(
            status="success",
            data={
                "transaction_id": transaction_id,
                "dismissed": False
            },
            message=f"Alert for transaction {transaction_id} restored successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error undismissing alert for transaction {transaction_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to undismiss alert: {str(e)}")


@app.get("/alerts/active", response_model=APIResponse)
async def get_active_alerts():
    """Get all active (non-dismissed) alert summaries."""
    try:
        alert_store = get_alert_store()
        summaries = alert_store.get_active_summaries()
        
        summaries_data = [summary.to_dict() for summary in summaries]
        
        return APIResponse(
            status="success",
            data={
                "summaries": summaries_data,
                "count": len(summaries_data)
            },
            message=f"Retrieved {len(summaries_data)} active alerts"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving active alerts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve active alerts: {str(e)}")


@app.get("/alerts/dismissed", response_model=APIResponse)
async def get_dismissed_alerts():
    """Get all dismissed alert summaries."""
    try:
        alert_store = get_alert_store()
        summaries = alert_store.get_dismissed_summaries()
        
        summaries_data = [summary.to_dict() for summary in summaries]
        
        return APIResponse(
            status="success",
            data={
                "summaries": summaries_data,
                "count": len(summaries_data)
            },
            message=f"Retrieved {len(summaries_data)} dismissed alerts"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving dismissed alerts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve dismissed alerts: {str(e)}")


@app.get("/performance/stats", response_model=APIResponse)
async def get_performance_stats():
    """Get API performance statistics."""
    try:
        monitor = get_performance_monitor()
        cache = get_response_cache()
        
        perf_stats = monitor.get_stats()
        cache_stats = cache.get_stats()
        
        return APIResponse(
            status="success",
            data={
                "performance": perf_stats,
                "cache": cache_stats
            },
            message="Performance statistics retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving performance stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve performance stats: {str(e)}")


@app.post("/performance/reset", response_model=APIResponse)
async def reset_performance_stats():
    """Reset performance monitoring statistics."""
    try:
        monitor = get_performance_monitor()
        monitor.reset()
        
        return APIResponse(
            status="success",
            data={},
            message="Performance statistics reset successfully"
        )
        
    except Exception as e:
        logger.error(f"Error resetting performance stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to reset performance stats: {str(e)}")


@app.post("/cache/clear", response_model=APIResponse)
async def clear_response_cache():
    """Clear all response caches."""
    try:
        cache = get_response_cache()
        cache.clear()
        
        return APIResponse(
            status="success",
            data={},
            message="Response cache cleared successfully"
        )
        
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    # Initialize system
    initialize_system()
    
    # Run the API server
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )