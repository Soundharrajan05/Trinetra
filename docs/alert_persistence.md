# Alert Persistence Implementation

## Overview

The alert persistence system provides in-memory storage for fraud detection alerts in the TRINETRA AI system. This implementation uses the `AlertStore` class to store and retrieve alerts without requiring a database, making it suitable for the prototype phase.

## Architecture

### Components

1. **AlertStore** (`backend/alerts.py`)
   - In-memory storage using dictionaries
   - Thread-safe operations with locking
   - Stores both individual alerts and alert summaries

2. **API Integration** (`backend/api.py`)
   - Alert store populated during system initialization
   - RESTful endpoints for alert retrieval
   - Statistics and filtering capabilities

### Data Flow

```
System Startup
    ↓
Load & Score Transactions
    ↓
For Each Transaction:
    - Check alert conditions
    - Create alert summary
    - Store in AlertStore
    ↓
API Endpoints Available
```

## API Endpoints

### 1. Get All Alerts
```
GET /alerts
```

Returns all alerts stored in the system, sorted by timestamp (newest first).

**Response:**
```json
{
  "status": "success",
  "data": {
    "alerts": [...],
    "count": 42
  },
  "message": "Retrieved 42 alerts"
}
```

### 2. Get Alerts by Transaction
```
GET /alerts/transaction/{transaction_id}
```

Returns all alerts for a specific transaction.

**Example:**
```
GET /alerts/transaction/TXN00123
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "transaction_id": "TXN00123",
    "alerts": [
      {
        "transaction_id": "TXN00123",
        "alert_type": "PRICE_ANOMALY",
        "severity": "HIGH",
        "timestamp": "2024-01-15T10:30:00",
        "message": "Price deviation of 70.0% exceeds threshold",
        "metadata": {
          "price_deviation": 0.7,
          "market_price": 100.0,
          "unit_price": 170.0
        }
      }
    ],
    "count": 1
  },
  "message": "Retrieved 1 alerts for transaction TXN00123"
}
```

### 3. Get Alerts by Priority
```
GET /alerts/priority/{priority}
```

Returns alert summaries filtered by priority level.

**Priority Levels:**
- `CRITICAL` - FRAUD category with multiple alerts
- `HIGH` - FRAUD category or multiple severe alerts
- `MEDIUM` - SUSPICIOUS category or single severe alert
- `LOW` - SUSPICIOUS category with minor alerts

**Example:**
```
GET /alerts/priority/CRITICAL
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "priority": "CRITICAL",
    "summaries": [...],
    "count": 15
  },
  "message": "Retrieved 15 alerts with CRITICAL priority"
}
```

### 4. Get Alert Statistics
```
GET /alerts/statistics
```

Returns comprehensive statistics about stored alerts.

**Response:**
```json
{
  "status": "success",
  "data": {
    "total_alerts": 127,
    "total_summaries": 89,
    "total_transactions": 89,
    "priority_counts": {
      "CRITICAL": 15,
      "HIGH": 28,
      "MEDIUM": 31,
      "LOW": 15
    },
    "alert_type_counts": {
      "PRICE_ANOMALY": 45,
      "ROUTE_ANOMALY": 32,
      "HIGH_RISK_COMPANY": 28,
      "PORT_CONGESTION": 22
    }
  },
  "message": "Alert statistics retrieved successfully"
}
```

### 5. Get All Alert Summaries
```
GET /alerts/summaries?min_priority={priority}
```

Returns all alert summaries, optionally filtered by minimum priority.

**Example:**
```
GET /alerts/summaries?min_priority=HIGH
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "summaries": [...],
    "count": 43,
    "min_priority": "HIGH"
  },
  "message": "Retrieved 43 alert summaries"
}
```

### 6. Enhanced Statistics Endpoint
```
GET /stats
```

The existing `/stats` endpoint now includes alert statistics in the response:

```json
{
  "status": "success",
  "data": {
    "total_transactions": 1000,
    "fraud_cases": 89,
    "suspicious_cases": 156,
    "safe_cases": 755,
    "fraud_rate": 8.9,
    "suspicious_rate": 15.6,
    "alert_statistics": {
      "total_alerts": 127,
      "total_summaries": 89,
      "priority_counts": {...},
      "alert_type_counts": {...}
    },
    ...
  }
}
```

## Alert Triggers

Alerts are automatically generated when transactions meet the following criteria:

| Alert Type | Condition | Severity |
|------------|-----------|----------|
| PRICE_ANOMALY | price_deviation > 0.5 | HIGH |
| ROUTE_ANOMALY | route_anomaly == 1 | MEDIUM |
| HIGH_RISK_COMPANY | company_risk_score > 0.8 | HIGH |
| PORT_CONGESTION | port_activity_index > 1.5 | MEDIUM |

## Priority Calculation

Alert priority is determined by:

1. **Risk Category**: FRAUD > SUSPICIOUS > SAFE
2. **Alert Count**: Number of triggered alerts
3. **Severity Score**: Sum of individual alert severities

**Priority Rules:**
- **CRITICAL**: FRAUD with 2+ alerts OR 3+ alerts with severity ≥6
- **HIGH**: FRAUD with 1 alert OR SUSPICIOUS with 3+ alerts OR severity ≥6
- **MEDIUM**: SUSPICIOUS with 1-2 alerts OR severity 3-5
- **LOW**: Other alert conditions

## Data Structures

### Alert Object
```python
{
  "transaction_id": "TXN00123",
  "alert_type": "PRICE_ANOMALY",
  "severity": "HIGH",
  "timestamp": "2024-01-15T10:30:00",
  "transaction_data": {...},
  "message": "Price deviation of 70.0% exceeds threshold",
  "metadata": {
    "price_deviation": 0.7,
    "market_price": 100.0,
    "unit_price": 170.0
  }
}
```

### Alert Summary Object
```python
{
  "transaction_id": "TXN00123",
  "alerts": [...],
  "priority": "CRITICAL",
  "priority_value": 4,
  "risk_category": "FRAUD",
  "alert_count": 3,
  "severity_score": 8,
  "priority_reason": "FRAUD category with 3 alerts",
  "timestamp": "2024-01-15T10:30:00"
}
```

## Usage Examples

### Python Client Example

```python
import requests

# Get all critical alerts
response = requests.get("http://localhost:8000/alerts/priority/CRITICAL")
critical_alerts = response.json()["data"]["summaries"]

# Get alerts for a specific transaction
response = requests.get("http://localhost:8000/alerts/transaction/TXN00123")
transaction_alerts = response.json()["data"]["alerts"]

# Get alert statistics
response = requests.get("http://localhost:8000/alerts/statistics")
stats = response.json()["data"]
print(f"Total alerts: {stats['total_alerts']}")
```

### Dashboard Integration Example

```python
import streamlit as st
import requests

# Display critical alerts
response = requests.get("http://localhost:8000/alerts/summaries?min_priority=HIGH")
high_priority_alerts = response.json()["data"]["summaries"]

st.subheader("🚨 High Priority Alerts")
for alert in high_priority_alerts:
    st.error(f"{alert['transaction_id']}: {alert['priority_reason']}")
```

## Thread Safety

The `AlertStore` uses Python's `threading.Lock` to ensure thread-safe operations:

```python
with self._lock:
    # All read/write operations are protected
    self._alerts[transaction_id] = alerts
```

This allows concurrent access from multiple API requests without data corruption.

## Performance Considerations

### Memory Usage
- In-memory storage suitable for prototype with ~1000 transactions
- Each alert summary: ~1-2 KB
- Total memory for 1000 transactions: ~1-2 MB

### Retrieval Performance
- O(1) lookup by transaction ID
- O(n) filtering by priority (where n = number of summaries)
- All operations complete in <1ms for prototype scale

### Scalability Notes
For production deployment with larger datasets:
- Consider Redis for distributed caching
- Implement database persistence (PostgreSQL)
- Add pagination for large result sets
- Implement time-based cleanup for old alerts

## Testing

### Unit Tests
Located in `backend/test_alert_store.py`:
- Test alert storage and retrieval
- Test filtering by priority
- Test statistics calculation
- Test thread safety

### Integration Tests
Located in `backend/test_alert_integration.py`:
- Test API endpoint responses
- Test alert store population on startup
- Test end-to-end alert flow

### Running Tests
```bash
# Run unit tests
python -m pytest backend/test_alert_store.py -v

# Run integration tests
python -m pytest backend/test_alert_integration.py -v

# Run all tests
python -m pytest backend/ -v
```

## Future Enhancements

1. **Database Persistence**
   - PostgreSQL for permanent storage
   - Alert history and audit trail
   - Time-series analysis

2. **Real-time Notifications**
   - WebSocket support for live alerts
   - Email/SMS notifications
   - Slack/Teams integration

3. **Alert Management**
   - Alert acknowledgment
   - Alert resolution workflow
   - Alert comments and notes

4. **Advanced Filtering**
   - Date range filtering
   - Multi-criteria filtering
   - Custom alert rules

5. **Analytics**
   - Alert trends over time
   - False positive tracking
   - Alert effectiveness metrics

## Troubleshooting

### No Alerts Generated
- Check that transactions meet alert thresholds
- Verify feature engineering completed successfully
- Check logs for errors during alert creation

### Missing Alerts in API Response
- Verify system initialization completed
- Check alert store population logs
- Ensure transaction IDs match exactly

### Performance Issues
- Monitor memory usage with large datasets
- Consider implementing pagination
- Add caching for frequently accessed alerts

## References

- Design Document: `.kiro/specs/trinetra-ai-fraud-detection/design.md` (Section 8)
- Requirements: `.kiro/specs/trinetra-ai-fraud-detection/requirements.md` (US-8)
- Alert Module: `backend/alerts.py`
- API Module: `backend/api.py`
