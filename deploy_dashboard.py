#!/usr/bin/env python3
"""
Deployment version of TRINETRA AI Dashboard for Render
Simplified for cloud deployment
"""

import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import time
import os

# Configure Streamlit page
st.set_page_config(
    page_title="TRINETRA AI - Trade Fraud Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration - Use environment variable for deployment
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
    
    # Convert to DataFrame for display
    df = pd.DataFrame(transactions)
    
    # Select key columns for display
    display_columns = ['transaction_id', 'product', 'unit_price', 'risk_score', 'risk_category']
    available_columns = [col for col in display_columns if col in df.columns]
    display_df = df[available_columns]
    
    # Format numeric columns
    if 'risk_score' in display_df.columns:
        display_df['risk_score'] = display_df['risk_score'].apply(lambda x: f"{x:.3f}" if pd.notnull(x) else "N/A")
    
    # Display the table
    st.dataframe(display_df, use_container_width=True)
    
    # Transaction explanation
    st.subheader("🔍 Transaction Investigation")
    
    transaction_ids = df['transaction_id'].tolist()
    selected_transaction_id = st.selectbox(
        "Select a transaction to investigate:",
        options=transaction_ids,
        help="Choose a transaction to get detailed fraud analysis"
    )
    
    if selected_transaction_id:
        col1, col2 = st.columns([1, 1])
        
        with col1:
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

def display_visualizations():
    """Display fraud analysis visualizations."""
    st.subheader("📈 Fraud Analysis")
    
    response = make_api_request("/transactions?limit=200")
    
    if response.get("status") != "success":
        st.error("Failed to load data for visualizations")
        return
    
    transactions = response.get("data", {}).get("transactions", [])
    if not transactions:
        st.info("No data available for visualizations")
        return
    
    df = pd.DataFrame(transactions)
    
    # Risk Distribution Pie Chart
    if 'risk_category' in df.columns:
        risk_counts = df['risk_category'].value_counts()
        fig_pie = px.pie(
            values=risk_counts.values,
            names=risk_counts.index,
            title="Risk Category Distribution",
            color_discrete_map={
                'SAFE': '#28a745',
                'SUSPICIOUS': '#ffc107', 
                'FRAUD': '#dc3545'
            }
        )
        st.plotly_chart(fig_pie, use_container_width=True)

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
        ["All Transactions", "Suspicious Transactions", "Fraud Transactions", "Visualizations"]
    )
    
    # Main content based on selection
    if view_option == "All Transactions":
        display_transaction_table("all")
    elif view_option == "Suspicious Transactions":
        display_transaction_table("suspicious")
    elif view_option == "Fraud Transactions":
        display_transaction_table("fraud")
    elif view_option == "Visualizations":
        display_visualizations()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**TRINETRA AI v1.0**")
    st.sidebar.markdown("Trade Fraud Intelligence System")

if __name__ == "__main__":
    main()