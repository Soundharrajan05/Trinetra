# TRINETRA AI - API Documentation

## Overview

The TRINETRA AI Trade Fraud Intelligence System provides a RESTful API built with FastAPI for accessing fraud detection data, AI-powered explanations, and dashboard statistics.

**Base URL**: `http://localhost:8000`

**API Version**: 1.0.0

---

## Table of Contents

1. [Authentication](#authentication)
2. [Response Format](#response-format)
3. [Endpoints](#endpoints)
   - [System Information](#1-system-information)
   - [Transaction Data](#2-transaction-data)
   - [Fraud Detection](#3-fraud-detection)
   - [AI Explanations](#4-ai-explanations)
   - [Statistics](#5-statistics)
   - [Session Management](#6-session-management)
   - [Alert Management](#7-alert-management)
4. [Error Handling](#error-handling)
5. [Rate Limits](#rate-limits)

---

## Authentication

Currently, the API does not require authentication. All endpoints are publicly accessible.

---

## Response Format

All API responses follow a consistent JSON structure:

```json
{
  "status": "success",
  "data": {},
  "message": "Descriptive message"
}
```

**Fields**:
- `status`: Either `"success"` or `"error"`
- `data`: Response payload (varies by endpoint)
- `message`: Human-readable message describing the result

---

## Endpoints

### 1. System Information

#### GET `/`

Get basic system information and API status.

**Request**:
```bash
curl http://localhost:8000/
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "name": "TRINETRA AI - Trade Fraud Intelligence API",
    "version": "1.0.0",
    "description": "AI-powered trade fraud detection and analysis"
  },
  "message": "TRINETRA AI API is running"
}
```

---

### 2. Transaction Data

#### GET `/transactions`

Retrieve all transactions with risk scores and pagination support.

**Query Parameters**:
- `limit` (optional): Number of transactions to return (1-1000, default: 100)
- `offset` (optional): Number of transactions to skip (default: 0)

**Request**:
```bash
# Get first 10 transactions
curl "http://localhost:8000/transactions?limit=10&offset=0"

# Get next 10 transactions
curl "http://localhost:8000/transactions?limit=10&offset=10"
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "transactions": [
      {
        "transaction_id": "TXN00001",
        "date": "2023-01-15",
        "product": "Electronics",
        "commodity_category": "Consumer Goods",
        "unit_price": 1250.50,
        "quantity": 100,
        "market_price": 1200.00,
        "price_deviation": 0.042,
        "shipping_route": "Shanghai-Rotterdam",
        "distance_km": 18500,
        "company_name": "Global Trade Corp",
        "company_risk_score": 0.35,
        "port_activity_index": 1.2,
        "route_anomaly": 0,
        "cargo_volume": 50.5,
        "shipment_duration_days": 45,
        "price_anomaly_score": 0.042,
        "route_risk_score": 0.0,
        "company_network_risk": 0.35,
        "port_congestion_score": 1.2,
        "shipment_duration_risk": 0.00243,
        "volume_spike_score": 0.505,
        "risk_score": -0.15,
        "risk_category": "SAFE"
      }
    ],
    "pagination": {
      "total": 1000,
      "limit": 10,
      "offset": 0,
      "returned": 10
    }
  },
  "message": "Retrieved 10 transactions"
}
```

---

#### GET `/suspicious`

Retrieve only transactions classified as SUSPICIOUS.

**Request**:
```bash
curl http://localhost:8000/suspicious
```

**Response**:
```json
{
  "status": "success",
  "data": [
    {
      "transaction_id": "TXN00452",
      "product": "Textiles",
      "unit_price": 850.00,
      "market_price": 600.00,
      "price_deviation": 0.417,
      "risk_score": 0.05,
      "risk_category": "SUSPICIOUS"
    }
  ],
  "message": "Retrieved 45 suspicious transactions"
}
```

---

#### GET `/fraud`

Retrieve only transactions classified as FRAUD.

**Request**:
```bash
curl http://localhost:8000/fraud
```

**Response**:
```json
{
  "status": "success",
  "data": [
    {
      "transaction_id": "TXN00789",
      "product": "Pharmaceuticals",
      "unit_price": 5000.00,
      "market_price": 2500.00,
      "price_deviation": 1.0,
      "route_anomaly": 1,
      "company_risk_score": 0.95,
      "risk_score": 0.85,
      "risk_category": "FRAUD"
    }
  ],
  "message": "Retrieved 23 fraud transactions"
}
```

---

### 3. Fraud Detection

Risk categories are determined by risk scores:
- **SAFE**: risk_score < -0.2
- **SUSPICIOUS**: -0.2 ≤ risk_score < 0.2
- **FRAUD**: risk_score ≥ 0.2

---

### 4. AI Explanations

#### POST `/explain/{transaction_id}`

Generate an AI-powered explanation for why a specific transaction is flagged as suspicious or fraudulent.

**Path Parameters**:
- `transaction_id`: The unique transaction identifier

**Request Body** (optional):
```json
{
  "force_ai": false
}
```

**Fields**:
- `force_ai` (optional): Set to `true` to force AI generation (uses Gemini API quota)

**Request**:
```bash
# Get explanation (uses cache if available)
curl -X POST http://localhost:8000/explain/TXN00452 \
  -H "Content-Type: application/json" \
  -d '{"force_ai": false}'

# Force AI generation
curl -X POST http://localhost:8000/explain/TXN00452 \
  -H "Content-Type: application/json" \
  -d '{"force_ai": true}'
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "transaction_id": "TXN00452",
    "explanation": "This transaction shows multiple fraud indicators: The trade price ($850) significantly exceeds the market price ($600), representing a 41.7% price deviation. This suggests potential invoice manipulation or value inflation. The company involved has a moderate risk score of 0.65, indicating previous suspicious activity. The shipping route shows normal patterns, but the combination of price anomaly and company risk warrants investigation.",
    "explanation_type": "ai_generated",
    "session_info": {
      "current_count": 1,
      "max_count": 3,
      "remaining": 2
    }
  },
  "message": "Generated ai_generated explanation for transaction TXN00452"
}
```

**Explanation Types**:
- `ai_generated`: Fresh explanation from Gemini API
- `cached`: Previously generated explanation
- `fallback`: Rule-based explanation (quota exceeded)
- `quota_exceeded`: Session limit reached

---

#### POST `/query`

Process natural language queries about fraud detection data.

**Request Body**:
```json
{
  "query": "What are the most common fraud patterns?"
}
```

**Request**:
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the most common fraud patterns?"}'
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "query": "What are the most common fraud patterns?",
    "answer": "Based on the analysis of 1000 transactions, the most common fraud patterns include: 1) Price manipulation where trade prices significantly deviate from market prices, 2) Route laundering involving unusual or circuitous shipping routes, 3) Volume misrepresentation with cargo volumes inconsistent with declared quantities, and 4) High-risk entity involvement where companies with elevated risk scores engage in suspicious transactions.",
    "context_summary": {
      "total_transactions": 1000,
      "fraud_rate": "2.3%",
      "suspicious_rate": "4.5%"
    }
  },
  "message": "Query processed successfully"
}
```

**Example Queries**:
- "Why is transaction TXN00452 suspicious?"
- "What are the high-risk companies?"
- "How many fraud cases were detected?"
- "What is the average risk score?"

---

### 5. Statistics

#### GET `/stats`

Retrieve comprehensive dashboard statistics and KPIs.

**Request**:
```bash
curl http://localhost:8000/stats
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "total_transactions": 1000,
    "fraud_cases": 23,
    "suspicious_cases": 45,
    "safe_cases": 932,
    "fraud_rate": 2.3,
    "suspicious_rate": 4.5,
    "total_trade_value": 12500000.50,
    "high_risk_countries": 5,
    "avg_risk_score": -0.125,
    "alert_statistics": {
      "total_alerts": 68,
      "by_priority": {
        "CRITICAL": 5,
        "HIGH": 18,
        "MEDIUM": 30,
        "LOW": 15
      },
      "by_type": {
        "PRICE_ANOMALY": 25,
        "ROUTE_ANOMALY": 15,
        "HIGH_RISK_COMPANY": 18,
        "PORT_CONGESTION": 10
      }
    },
    "session_info": {
      "explanations_used": 1,
      "explanations_remaining": 2,
      "max_per_session": 3
    }
  },
  "message": "Statistics retrieved successfully"
}
```

---

### 6. Session Management

#### GET `/session/info`

Get current session information including explanation quota usage.

**Request**:
```bash
curl http://localhost:8000/session/info
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "current_count": 1,
    "max_count": 3,
    "remaining": 2,
    "can_make_explanation": true
  },
  "message": "Session info retrieved successfully"
}
```

---

#### POST `/session/reset`

Reset the session explanation count and clear the explanation cache.

**Request**:
```bash
curl -X POST http://localhost:8000/session/reset
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "session_count": 0,
    "max_count": 3
  },
  "message": "Session reset successfully"
}
```

---

### 7. Alert Management

#### GET `/alerts`

Retrieve all alerts from the alert store.

**Request**:
```bash
curl http://localhost:8000/alerts
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "alerts": [
      {
        "alert_id": "ALT001",
        "transaction_id": "TXN00452",
        "alert_type": "PRICE_ANOMALY",
        "severity": "HIGH",
        "message": "Price deviation of 41.7% detected",
        "timestamp": "2024-01-15T10:30:00"
      }
    ],
    "count": 68
  },
  "message": "Retrieved 68 alerts"
}
```

---

#### GET `/alerts/transaction/{transaction_id}`

Get all alerts for a specific transaction.

**Path Parameters**:
- `transaction_id`: The unique transaction identifier

**Request**:
```bash
curl http://localhost:8000/alerts/transaction/TXN00452
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "transaction_id": "TXN00452",
    "alerts": [
      {
        "alert_id": "ALT001",
        "transaction_id": "TXN00452",
        "alert_type": "PRICE_ANOMALY",
        "severity": "HIGH",
        "message": "Price deviation of 41.7% detected"
      },
      {
        "alert_id": "ALT002",
        "transaction_id": "TXN00452",
        "alert_type": "HIGH_RISK_COMPANY",
        "severity": "MEDIUM",
        "message": "Company risk score of 0.65 exceeds threshold"
      }
    ],
    "count": 2
  },
  "message": "Retrieved 2 alerts for transaction TXN00452"
}
```

---

#### GET `/alerts/priority/{priority}`

Get alerts filtered by priority level.

**Path Parameters**:
- `priority`: Priority level (CRITICAL, HIGH, MEDIUM, LOW)

**Request**:
```bash
curl http://localhost:8000/alerts/priority/CRITICAL
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "priority": "CRITICAL",
    "summaries": [
      {
        "transaction_id": "TXN00789",
        "priority": "CRITICAL",
        "alert_count": 4,
        "risk_category": "FRAUD",
        "risk_score": 0.85
      }
    ],
    "count": 5
  },
  "message": "Retrieved 5 alerts with CRITICAL priority"
}
```

---

#### GET `/alerts/statistics`

Get comprehensive alert statistics.

**Request**:
```bash
curl http://localhost:8000/alerts/statistics
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "total_alerts": 68,
    "total_summaries": 45,
    "active_summaries": 40,
    "dismissed_summaries": 5,
    "by_priority": {
      "CRITICAL": 5,
      "HIGH": 18,
      "MEDIUM": 30,
      "LOW": 15
    },
    "by_type": {
      "PRICE_ANOMALY": 25,
      "ROUTE_ANOMALY": 15,
      "HIGH_RISK_COMPANY": 18,
      "PORT_CONGESTION": 10
    }
  },
  "message": "Alert statistics retrieved successfully"
}
```

---

#### GET `/alerts/summaries`

Get all alert summaries with optional priority filtering.

**Query Parameters**:
- `min_priority` (optional): Minimum priority level (CRITICAL, HIGH, MEDIUM, LOW)

**Request**:
```bash
# Get all summaries
curl http://localhost:8000/alerts/summaries

# Get summaries with HIGH priority or above
curl "http://localhost:8000/alerts/summaries?min_priority=HIGH"
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "summaries": [
      {
        "transaction_id": "TXN00452",
        "priority": "HIGH",
        "alert_count": 2,
        "risk_category": "SUSPICIOUS",
        "risk_score": 0.05,
        "dismissed": false
      }
    ],
    "count": 23,
    "min_priority": "HIGH"
  },
  "message": "Retrieved 23 alert summaries"
}
```

---

#### GET `/alerts/active`

Get all active (non-dismissed) alert summaries.

**Request**:
```bash
curl http://localhost:8000/alerts/active
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "summaries": [
      {
        "transaction_id": "TXN00452",
        "priority": "HIGH",
        "alert_count": 2,
        "dismissed": false
      }
    ],
    "count": 40
  },
  "message": "Retrieved 40 active alerts"
}
```

---

#### GET `/alerts/dismissed`

Get all dismissed alert summaries.

**Request**:
```bash
curl http://localhost:8000/alerts/dismissed
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "summaries": [
      {
        "transaction_id": "TXN00123",
        "priority": "LOW",
        "alert_count": 1,
        "dismissed": true,
        "dismissed_by": "analyst_john",
        "dismissed_at": "2024-01-15T14:30:00"
      }
    ],
    "count": 5
  },
  "message": "Retrieved 5 dismissed alerts"
}
```

---

#### POST `/alerts/dismiss/{transaction_id}`

Dismiss an alert summary for a specific transaction.

**Path Parameters**:
- `transaction_id`: The unique transaction identifier

**Query Parameters**:
- `dismissed_by` (optional): User who is dismissing the alert (default: "analyst")

**Request**:
```bash
curl -X POST "http://localhost:8000/alerts/dismiss/TXN00452?dismissed_by=analyst_john"
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "transaction_id": "TXN00452",
    "dismissed": true,
    "dismissed_by": "analyst_john"
  },
  "message": "Alert for transaction TXN00452 dismissed successfully"
}
```

---

#### POST `/alerts/undismiss/{transaction_id}`

Restore (undismiss) an alert summary for a specific transaction.

**Path Parameters**:
- `transaction_id`: The unique transaction identifier

**Request**:
```bash
curl -X POST http://localhost:8000/alerts/undismiss/TXN00452
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "transaction_id": "TXN00452",
    "dismissed": false
  },
  "message": "Alert for transaction TXN00452 restored successfully"
}
```

---

## Error Handling

### Error Response Format

All errors follow a consistent format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common HTTP Status Codes

- **200 OK**: Request succeeded
- **400 Bad Request**: Invalid request parameters
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server-side error

### Example Error Responses

**404 - Transaction Not Found**:
```bash
curl -X POST http://localhost:8000/explain/INVALID_ID
```

Response:
```json
{
  "detail": "Transaction INVALID_ID not found"
}
```

**400 - Invalid Priority Level**:
```bash
curl http://localhost:8000/alerts/priority/INVALID
```

Response:
```json
{
  "detail": "Invalid priority level: INVALID. Must be CRITICAL, HIGH, MEDIUM, or LOW"
}
```

**500 - System Not Initialized**:
```json
{
  "detail": "System not initialized"
}
```

---

## Rate Limits

### AI Explanation Quota

The system implements quota management for AI-powered explanations to prevent Gemini API errors:

- **Limit**: 3 AI explanations per session
- **Scope**: Per-session (resets on `/session/reset`)
- **Behavior**: 
  - Explanations are cached after first generation
  - `force_ai=true` required to generate new AI explanations
  - Fallback explanations provided when quota exceeded

**Check Quota**:
```bash
curl http://localhost:8000/session/info
```

**Reset Quota**:
```bash
curl -X POST http://localhost:8000/session/reset
```

---

## Complete Usage Example

Here's a complete workflow demonstrating common API usage:

```bash
# 1. Check API status
curl http://localhost:8000/

# 2. Get dashboard statistics
curl http://localhost:8000/stats

# 3. Retrieve suspicious transactions
curl http://localhost:8000/suspicious

# 4. Get details for a specific transaction
curl "http://localhost:8000/transactions?limit=1000" | jq '.data.transactions[] | select(.transaction_id == "TXN00452")'

# 5. Generate AI explanation
curl -X POST http://localhost:8000/explain/TXN00452 \
  -H "Content-Type: application/json" \
  -d '{"force_ai": true}'

# 6. Get alerts for the transaction
curl http://localhost:8000/alerts/transaction/TXN00452

# 7. Ask a natural language query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the most common fraud indicators?"}'

# 8. Get critical alerts
curl http://localhost:8000/alerts/priority/CRITICAL

# 9. Check session quota
curl http://localhost:8000/session/info

# 10. Reset session if needed
curl -X POST http://localhost:8000/session/reset
```

---

## Python Client Example

```python
import requests

BASE_URL = "http://localhost:8000"

# Get all transactions
response = requests.get(f"{BASE_URL}/transactions", params={"limit": 10})
transactions = response.json()["data"]["transactions"]

# Get explanation for a suspicious transaction
transaction_id = "TXN00452"
response = requests.post(
    f"{BASE_URL}/explain/{transaction_id}",
    json={"force_ai": True}
)
explanation = response.json()["data"]["explanation"]
print(f"Explanation: {explanation}")

# Get statistics
response = requests.get(f"{BASE_URL}/stats")
stats = response.json()["data"]
print(f"Fraud Rate: {stats['fraud_rate']}%")

# Natural language query
response = requests.post(
    f"{BASE_URL}/query",
    json={"query": "How many high-risk transactions are there?"}
)
answer = response.json()["data"]["answer"]
print(f"Answer: {answer}")
```

---

## JavaScript/Fetch Example

```javascript
const BASE_URL = "http://localhost:8000";

// Get suspicious transactions
async function getSuspiciousTransactions() {
  const response = await fetch(`${BASE_URL}/suspicious`);
  const data = await response.json();
  return data.data;
}

// Get explanation
async function getExplanation(transactionId, forceAI = false) {
  const response = await fetch(`${BASE_URL}/explain/${transactionId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ force_ai: forceAI })
  });
  const data = await response.json();
  return data.data.explanation;
}

// Get statistics
async function getStats() {
  const response = await fetch(`${BASE_URL}/stats`);
  const data = await response.json();
  return data.data;
}

// Usage
(async () => {
  const suspicious = await getSuspiciousTransactions();
  console.log(`Found ${suspicious.length} suspicious transactions`);
  
  const explanation = await getExplanation("TXN00452", true);
  console.log(`Explanation: ${explanation}`);
  
  const stats = await getStats();
  console.log(`Fraud Rate: ${stats.fraud_rate}%`);
})();
```

---

## Support

For issues or questions about the API:
- Check the error message in the response
- Verify the request format matches the examples
- Ensure the system is properly initialized
- Check session quota for AI explanations

---

**Last Updated**: 2024
**API Version**: 1.0.0
