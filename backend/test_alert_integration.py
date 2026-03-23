"""
Integration tests for alert persistence in the API.

This module tests the integration between the AlertStore and the API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from backend.api import app, initialize_system
from backend.alerts import get_alert_store, reset_alert_store


@pytest.fixture(scope="module")
def client():
    """Create a test client for the FastAPI app."""
    # Initialize the system before running tests
    initialize_system()
    return TestClient(app)


def test_alert_store_populated_on_startup(client):
    """Test that the alert store is populated during system initialization."""
    alert_store = get_alert_store()
    
    # Check that alerts were stored
    alert_count = alert_store.get_alert_count()
    summary_count = alert_store.get_summary_count()
    
    assert alert_count > 0, "Alert store should contain alerts after initialization"
    assert summary_count > 0, "Alert store should contain summaries after initialization"
    
    print(f"Alert store contains {alert_count} alerts and {summary_count} summaries")


def test_get_all_alerts_endpoint(client):
    """Test the GET /alerts endpoint."""
    response = client.get("/alerts")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert "data" in data
    assert "alerts" in data["data"]
    assert "count" in data["data"]
    assert data["data"]["count"] > 0
    
    print(f"GET /alerts returned {data['data']['count']} alerts")


def test_get_alerts_by_transaction_endpoint(client):
    """Test the GET /alerts/transaction/{transaction_id} endpoint."""
    # First, get all summaries to find a transaction with alerts
    alert_store = get_alert_store()
    summaries = alert_store.get_all_summaries()
    
    if summaries:
        transaction_id = summaries[0].transaction_id
        
        response = client.get(f"/alerts/transaction/{transaction_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert data["data"]["transaction_id"] == transaction_id
        assert data["data"]["count"] > 0
        
        print(f"Transaction {transaction_id} has {data['data']['count']} alerts")


def test_get_alerts_by_priority_endpoint(client):
    """Test the GET /alerts/priority/{priority} endpoint."""
    priorities = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    
    for priority in priorities:
        response = client.get(f"/alerts/priority/{priority}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert data["data"]["priority"] == priority
        assert "summaries" in data["data"]
        assert "count" in data["data"]
        
        print(f"Priority {priority}: {data['data']['count']} alerts")


def test_get_alert_statistics_endpoint(client):
    """Test the GET /alerts/statistics endpoint."""
    response = client.get("/alerts/statistics")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert "data" in data
    
    stats = data["data"]
    assert "total_alerts" in stats
    assert "total_summaries" in stats
    assert "priority_counts" in stats
    assert "alert_type_counts" in stats
    
    print(f"Alert statistics: {stats}")


def test_get_all_summaries_endpoint(client):
    """Test the GET /alerts/summaries endpoint."""
    response = client.get("/alerts/summaries")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert "summaries" in data["data"]
    assert "count" in data["data"]
    assert data["data"]["count"] > 0
    
    print(f"GET /alerts/summaries returned {data['data']['count']} summaries")


def test_get_summaries_with_min_priority(client):
    """Test the GET /alerts/summaries endpoint with min_priority filter."""
    response = client.get("/alerts/summaries?min_priority=HIGH")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert data["data"]["min_priority"] == "HIGH"
    
    # Verify all returned summaries have priority >= HIGH
    for summary in data["data"]["summaries"]:
        priority_value = summary["priority_value"]
        assert priority_value >= 3, f"Expected priority >= HIGH (3), got {priority_value}"
    
    print(f"GET /alerts/summaries?min_priority=HIGH returned {data['data']['count']} summaries")


def test_stats_includes_alert_statistics(client):
    """Test that the /stats endpoint includes alert statistics."""
    response = client.get("/stats")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert "alert_statistics" in data["data"]
    
    alert_stats = data["data"]["alert_statistics"]
    assert "total_alerts" in alert_stats
    assert "total_summaries" in alert_stats
    assert "priority_counts" in alert_stats
    
    print(f"Stats endpoint includes alert statistics: {alert_stats}")


def test_invalid_priority_returns_400(client):
    """Test that invalid priority values return 400 error."""
    response = client.get("/alerts/priority/INVALID")
    
    assert response.status_code == 400
    data = response.json()
    
    assert "Invalid priority level" in data["detail"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
