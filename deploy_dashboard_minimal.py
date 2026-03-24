#!/usr/bin/env python3
"""
Minimal deployment version of TRINETRA AI Dashboard for Render
No pandas dependency - uses pure Python data structures
"""

import streamlit as st
import requests
import time
import os

# Configure Streamlit page
st.set_page_config(
    page_title="TRINETRA AI - Trade Fraud Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    
    .metric-card {
        background-color: #1e2130;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    .explanation-box {
        background: #1e2130;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2196f3;
        margin: 1rem 0;
        color: #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

def make_api_request(endpoint: str, method: str = "GET", data: dict = None) -> dict:
    """Make API request with error handling."""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data or {}, timeout=10)
        
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to TRINETRA AI API. Please check if the API server is running.")
        return {"status": "error", "message": "Connection failed"}
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ API Error: {e.response.status_code}")
        return {"status": "error", "message": str(e)}
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        return {"status": "error", "message": str(e)}

def display_header():
    """Display the main header."""
    st.markdown("""
    <div class="main-header">
        <h1>🛡️ TRINETRA AI</h1>
        <p>Trade Fraud Intelligence System</p>
    </div>
    """, unsafe_allow_html=True)

def display_kpi_metrics():
    """Display key performance indicators."""
    stats_response = make_api_request("/stats")
    
    if stats_response.get("status") == "success":
        stats = stats_response.get("data", {})
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Transactions", f"{stats.get('total_transactions', 0):,}")
        
        with col2:
            fraud_rate = stats.get('fraud_rate', 0)
            st.metric("Fraud Rate", f"{fraud_rate:.1f}%")
        
        with col3:
            trade_value = stats.get('total_trade_value', 0)
            st.metric("Total Trade Value", f"${trade_value:,.0f}")
        
        with col4:
            avg_risk = stats.get('avg_risk_score', 0)
            st.metric("Avg Risk Score", f"{avg_risk:.3f}")

def display_transaction_table(transaction_type: str = "all"):
    """Display transaction table."""
    st.subheader(f"📊 {transaction_type.title()} Transactions")
    
    # Get transactions based on type
    if transaction_type == "suspicious":
        response = make_api_request("/suspicious")
    elif transaction_type == "fraud":
        response = make_api_request("/fraud")
    else:
        response = make_api_request("/transactions?limit=100")
    
    if response.get("status") != "success":
        st.error("Failed to load transactions")
        return
    
    transactions = response.get("data", [])
    if isinstance(transactions, dict) and "transactions" in transactions:
        transactions = transactions["transactions"]
    
    if not transactions:
        st.info(f"No {transaction_type} transactions found.")
        return
    
    # Display as simple table
    if transactions:
        # Create a simple table display
        table_data = []
        for t in transactions[:20]:  # Show first 20
            table_data.append({
                "ID": t.get("transaction_id", ""),
                "Product": t.get("product", ""),
                "Price": f"${t.get('unit_price', 0):.2f}",
                "Risk Score": f"{t.get('risk_score', 0):.3f}",
                "Category": t.get("risk_category", "")
            })
        
        st.table(table_data)
    
    # Transaction explanation
    st.subheader("🔍 Transaction Investigation")
    
    transaction_ids = [t["transaction_id"] for t in transactions[:50]]  # First 50 for dropdown
    selected_transaction_id = st.selectbox(
        "Select a transaction to investigate:",
        options=transaction_ids,
        help="Choose a transaction to get detailed fraud analysis"
    )
    
    if selected_transaction_id:
        if st.button("📋 Get Explanation"):
            explain_transaction(selected_transaction_id)

def explain_transaction(transaction_id: str):
    """Get and display transaction explanation."""
    with st.spinner("Generating explanation..."):
        explanation_response = make_api_request(
            f"/explain/{transaction_id}",
            method="POST",
            data={"force_ai": False}
        )
    
    if explanation_response.get("status") == "success":
        data = explanation_response.get("data", {})
        explanation = data.get("explanation", "No explanation available")
        
        st.markdown(f"""
        <div class="explanation-box">
            <h4>📋 Transaction Analysis</h4>
            <p>{explanation}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.error(f"Failed to generate explanation: {explanation_response.get('message', 'Unknown error')}")

def display_simple_chart():
    """Display simple risk distribution chart."""
    st.subheader("📈 Risk Distribution")
    
    response = make_api_request("/stats")
    
    if response.get("status") == "success":
        stats = response.get("data", {})
        
        # Simple bar chart data
        categories = ["Safe", "Suspicious", "Fraud"]
        values = [
            stats.get("safe_cases", 0),
            stats.get("suspicious_cases", 0),
            stats.get("fraud_cases", 0)
        ]
        
        # Create simple chart using Streamlit
        chart_data = {cat: val for cat, val in zip(categories, values)}
        st.bar_chart(chart_data)

def main():
    """Main dashboard application."""
    # Display header
    display_header()
    
    # Display KPI metrics
    st.subheader("📊 Key Performance Indicators")
    display_kpi_metrics()
    
    # Sidebar for navigation
    st.sidebar.title("🔍 Investigation Tools")
    
    view_option = st.sidebar.selectbox(
        "Select View:",
        ["All Transactions", "Suspicious Transactions", "Fraud Transactions", "Risk Chart"]
    )
    
    # Main content based on selection
    if view_option == "All Transactions":
        display_transaction_table("all")
    elif view_option == "Suspicious Transactions":
        display_transaction_table("suspicious")
    elif view_option == "Fraud Transactions":
        display_transaction_table("fraud")
    elif view_option == "Risk Chart":
        display_simple_chart()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**TRINETRA AI v1.0**")
    st.sidebar.markdown("Trade Fraud Intelligence System")

if __name__ == "__main__":
    main()