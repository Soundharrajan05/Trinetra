"""
Streamlit Dashboard for TRINETRA AI - Trade Fraud Intelligence System

This dashboard provides an interactive interface for fraud analysts to investigate
suspicious transactions with AI-powered explanations and quota management.

Author: TRINETRA AI Team
Date: 2024
"""

import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
from typing import Dict, List, Any
import time

# Configure Streamlit page
st.set_page_config(
    page_title="TRINETRA AI - Trade Fraud Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Custom CSS for dark theme and styling
st.markdown("""
<style>
    /* Main background - dark theme */
    .main {
        background-color: #0e1117;
    }
    
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    /* KPI Metric Cards - Dark theme with modern styling */
    .metric-card {
        background-color: #1e2130;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.4);
    }
    
    .metric-card h4 {
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-card h2 {
        font-size: 2rem;
        font-weight: 700;
        margin: 10px 0;
        color: #ffffff;
    }
    
    .metric-card p {
        font-size: 0.85rem;
        opacity: 0.8;
    }
    
    .alert-banner {
        background: #dc3545;
        color: white;
        padding: 0.75rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    
    .explanation-box {
        background: #1e2130;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2196f3;
        margin: 1rem 0;
        color: #e0e0e0;
    }
    
    .explanation-box h4 {
        color: #64b5f6;
        margin-bottom: 0.5rem;
    }
    
    .quota-info {
        background: #2a2d3a;
        color: #ffc107;
        padding: 0.75rem;
        border-radius: 5px;
        border-left: 4px solid #ffc107;
        margin-bottom: 1rem;
    }
    
    /* Responsive design for smaller screens */
    @media (max-width: 768px) {
        .metric-card h2 {
            font-size: 1.5rem;
        }
        
        .metric-card {
            padding: 15px;
        }
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=30)  # Cache for 30 seconds
def load_transactions_with_retry():
    """Load transactions with improved retry mechanism and timeout handling."""
    max_retries = 3
    base_timeout = 10  # Increased from 3 to 10 seconds
    
    for attempt in range(max_retries):
        try:
            # Progressive timeout: 10s, 15s, 20s
            timeout = base_timeout + (attempt * 5)
            
            st.info(f"Loading transactions... (attempt {attempt + 1}/{max_retries})")
            
            response = requests.get(
                f"{API_BASE_URL}/transactions?limit=100",
                timeout=timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success" and "data" in result:
                    transactions = result["data"]["transactions"] if "transactions" in result["data"] else result["data"]
                    st.success(f"✅ Loaded {len(transactions)} transactions successfully!")
                    return transactions
                else:
                    st.warning(f"⚠️ API returned unexpected format: {result.get('message', 'Unknown error')}")
                    
            elif response.status_code == 500:
                st.error(f"❌ Server error (500) - attempt {attempt + 1}/{max_retries}")
                
            else:
                st.error(f"❌ API error {response.status_code} - attempt {attempt + 1}/{max_retries}")
                
        except requests.exceptions.Timeout:
            st.warning(f"⏱️ Request timeout after {timeout}s (attempt {attempt + 1}/{max_retries})")
            
        except requests.exceptions.ConnectionError:
            st.error(f"🔌 Connection failed - API server may be down (attempt {attempt + 1}/{max_retries})")
            
        except requests.exceptions.RequestException as e:
            st.error(f"🌐 Network error: {str(e)} (attempt {attempt + 1}/{max_retries})")
            
        except Exception as e:
            st.error(f"💥 Unexpected error: {str(e)} (attempt {attempt + 1}/{max_retries})")
        
        # Wait before retry (exponential backoff)
        if attempt < max_retries - 1:
            wait_time = 2 ** attempt  # 1s, 2s, 4s
            st.info(f"⏳ Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
    
    # All retries failed - return empty list with clear error
    st.error("❌ Failed to load transactions after all retry attempts. Please check if the API server is running.")
    return []

def make_api_request_cached(endpoint: str) -> Dict:
    """Make cached GET API request with error handling."""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"status": "error", "message": "Connection failed"}
    except requests.exceptions.HTTPError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def make_api_request(endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
    """Make API request with error handling."""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        if method == "GET":
            # Use cached version for GET requests
            return make_api_request_cached(endpoint)
        elif method == "POST":
            response = requests.post(url, json=data or {}, timeout=10)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to TRINETRA AI API. Please ensure the backend is running.")
        return {"status": "error", "message": "Connection failed"}
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ API Error: {e.response.status_code} - {e.response.text}")
        return {"status": "error", "message": str(e)}
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        return {"status": "error", "message": str(e)}


def display_header():
    """Display the main header with branding and alert count."""
    # Get active alert count
    alerts_response = make_api_request("/alerts/active")
    alert_count = 0
    if alerts_response.get("status") == "success":
        summaries = alerts_response.get("data", {}).get("summaries", [])
        # Count only HIGH and CRITICAL priority alerts
        alert_count = len([s for s in summaries if s.get("priority") in ["HIGH", "CRITICAL"]])
    
    # Display header with alert badge
    if alert_count > 0:
        st.markdown(f"""
        <div class="main-header">
            <h1 style="color: white; margin: 0;">🛡️ TRINETRA AI 
                <span style="background: #dc3545; padding: 0.3rem 0.6rem; border-radius: 15px; 
                             font-size: 0.6em; margin-left: 1rem; vertical-align: middle;">
                    {alert_count} Active Alerts
                </span>
            </h1>
            <p style="color: #e3f2fd; margin: 0;">Trade Fraud Intelligence System</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="main-header">
            <h1 style="color: white; margin: 0;">🛡️ TRINETRA AI</h1>
            <p style="color: #e3f2fd; margin: 0;">Trade Fraud Intelligence System</p>
        </div>
        """, unsafe_allow_html=True)


def display_session_info():
    """Display session quota information."""
    session_response = make_api_request("/session/info")
    
    if session_response.get("status") == "success":
        session_data = session_response.get("data", {})
        current = session_data.get("current_count", 0)
        max_count = session_data.get("max_count", 3)
        remaining = session_data.get("remaining", 0)
        
        if remaining > 0:
            st.markdown(f"""
            <div class="quota-info">
                <strong>AI Explanations Available:</strong> {remaining}/{max_count} remaining this session
                <br><small>Click "Get AI Explanation" on any transaction to use Gemini AI analysis</small>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="alert-banner">
                <strong>AI Quota Exhausted:</strong> {current}/{max_count} explanations used this session
                <br><small>Fallback explanations are still available. Reset session to get more AI explanations.</small>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🔄 Reset Session", help="Reset AI explanation quota"):
                reset_response = make_api_request("/session/reset", method="POST")
                if reset_response.get("status") == "success":
                    st.success("✅ Session reset successfully! You now have 3 new AI explanations available.")
                    st.experimental_rerun()


def display_kpi_metrics(show_refresh_indicator: bool = False):
    """Display key performance indicators with custom styling."""
    # Show refresh indicator if data is being refreshed
    if show_refresh_indicator:
        st.markdown("""
        <div style="background: #2a5298; color: white; padding: 0.5rem; border-radius: 5px; margin-bottom: 1rem; text-align: center;">
            🔄 Refreshing data...
        </div>
        """, unsafe_allow_html=True)
    
    stats_response = make_api_request("/stats")
    
    if stats_response.get("status") == "success":
        stats = stats_response.get("data", {})
        
        # Get alert statistics
        alert_stats = stats.get("alert_statistics", {})
        active_alerts = alert_stats.get("active_count", 0)
        critical_alerts = alert_stats.get("priority_counts", {}).get("CRITICAL", 0)
        high_alerts = alert_stats.get("priority_counts", {}).get("HIGH", 0)
        
        # Create 5 columns for KPI cards (added alert count)
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            # Total Transactions counter
            st.markdown(f"""
            <div class="metric-card">
                <h4 style="color: #64b5f6; margin: 0;">📊 Total Transactions</h4>
                <h2 style="margin: 10px 0; color: #ffffff;">{stats.get('total_transactions', 0):,}</h2>
                <p style="color: #b0b0b0; margin: 0; font-size: 0.9em;">All trade records</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Active Alerts counter with color coding
            alert_color = "#dc3545" if active_alerts > 0 else "#28a745"
            alert_icon = "🚨" if active_alerts > 0 else "✅"
            st.markdown(f"""
            <div class="metric-card">
                <h4 style="color: {alert_color}; margin: 0;">{alert_icon} Active Alerts</h4>
                <h2 style="margin: 10px 0; color: #ffffff;">{active_alerts}</h2>
                <p style="color: #b0b0b0; margin: 0; font-size: 0.9em;">Critical: {critical_alerts} | High: {high_alerts}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            # Fraud Rate percentage
            fraud_rate = stats.get('fraud_rate', 0)
            fraud_cases = stats.get('fraud_cases', 0)
            st.markdown(f"""
            <div class="metric-card">
                <h4 style="color: #ef5350; margin: 0;">🚨 Fraud Rate</h4>
                <h2 style="margin: 10px 0; color: #ffffff;">{fraud_rate:.1f}%</h2>
                <p style="color: #b0b0b0; margin: 0; font-size: 0.9em;">{fraud_cases} fraud cases detected</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            # Total Trade Value
            trade_value = stats.get('total_trade_value', 0)
            st.markdown(f"""
            <div class="metric-card">
                <h4 style="color: #66bb6a; margin: 0;">💰 Total Trade Value</h4>
                <h2 style="margin: 10px 0; color: #ffffff;">${trade_value:,.0f}</h2>
                <p style="color: #b0b0b0; margin: 0; font-size: 0.9em;">Cumulative transaction value</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            # High-Risk Countries count
            high_risk_countries = stats.get('high_risk_countries', 0)
            avg_risk = stats.get('avg_risk_score', 0)
            st.markdown(f"""
            <div class="metric-card">
                <h4 style="color: #ffca28; margin: 0;">🌍 High-Risk Routes</h4>
                <h2 style="margin: 10px 0; color: #ffffff;">{high_risk_countries}</h2>
                <p style="color: #b0b0b0; margin: 0; font-size: 0.9em;">Avg Risk: {avg_risk:.3f}</p>
            </div>
            """, unsafe_allow_html=True)


def display_fraud_alerts():
    """Display fraud alert banners with priority-based color coding and dismissal functionality."""
    # Get alert summaries with minimum HIGH priority (only active alerts)
    alerts_response = make_api_request("/alerts/active")
    
    if alerts_response.get("status") != "success":
        return
    
    summaries_data = alerts_response.get("data", {})
    summaries = summaries_data.get("summaries", [])
    
    # Filter to only HIGH and CRITICAL priority
    high_priority_summaries = [s for s in summaries if s.get("priority") in ["HIGH", "CRITICAL"]]
    
    # Get alert counts by priority for indicators
    critical_count = len([s for s in summaries if s.get("priority") == "CRITICAL"])
    high_count = len([s for s in summaries if s.get("priority") == "HIGH"])
    medium_count = len([s for s in summaries if s.get("priority") == "MEDIUM"])
    total_active = len(summaries)
    
    # Display alert count summary bar
    if total_active > 0:
        st.markdown(f"""
        <div style="background: #2a2d3a; padding: 0.75rem; border-radius: 5px; margin-bottom: 1rem; 
                    border-left: 4px solid #ffc107;">
            <strong>📊 Alert Summary:</strong> {total_active} total active alerts | 
            <span style="color: #dc3545;">🔴 {critical_count} Critical</span> | 
            <span style="color: #ff9800;">🟠 {high_count} High</span> | 
            <span style="color: #ffc107;">🟡 {medium_count} Medium</span>
        </div>
        """, unsafe_allow_html=True)
    
    if not high_priority_summaries:
        if total_active > 0:
            st.markdown("""
            <div style="background: #28a745; color: white; padding: 0.75rem; border-radius: 5px; margin-bottom: 1rem;">
                <strong>✅ No High-Priority Alerts:</strong> All critical and high-priority alerts have been addressed.
                <br><small>There are medium/low priority alerts that can be reviewed when convenient.</small>
            </div>
            """, unsafe_allow_html=True)
        return
    
    # Group alerts by priority
    critical_alerts = [s for s in high_priority_summaries if s.get("priority") == "CRITICAL"]
    high_alerts = [s for s in high_priority_summaries if s.get("priority") == "HIGH"]
    
    # Display CRITICAL alerts (Red banner)
    if critical_alerts:
        # Get details about alert types
        alert_types_count = {}
        for summary in critical_alerts:
            for alert in summary.get("alerts", []):
                alert_type = alert.get("alert_type", "UNKNOWN")
                alert_types_count[alert_type] = alert_types_count.get(alert_type, 0) + 1
        
        alert_breakdown = ", ".join([f"{count} {atype.replace('_', ' ')}" 
                                     for atype, count in alert_types_count.items()])
        
        st.markdown(f"""
        <div class="alert-banner" style="background: #dc3545; border-left: 5px solid #a71d2a;">
            <strong>🚨 CRITICAL FRAUD ALERT:</strong> {len(critical_alerts)} high-risk transactions detected requiring immediate attention!
            <br><small style="opacity: 0.9;">Alert Types: {alert_breakdown}</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Display HIGH priority alerts (Yellow/Orange banner)
    if high_alerts:
        # Get details about alert types
        alert_types_count = {}
        for summary in high_alerts:
            for alert in summary.get("alerts", []):
                alert_type = alert.get("alert_type", "UNKNOWN")
                alert_types_count[alert_type] = alert_types_count.get(alert_type, 0) + 1
        
        alert_breakdown = ", ".join([f"{count} {atype.replace('_', ' ')}" 
                                     for atype, count in alert_types_count.items()])
        
        st.markdown(f"""
        <div class="alert-banner" style="background: #ff9800; border-left: 5px solid #f57c00;">
            <strong>⚠️ HIGH PRIORITY ALERT:</strong> {len(high_alerts)} suspicious transactions require investigation
            <br><small style="opacity: 0.9;">Alert Types: {alert_breakdown}</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Display expandable details section with dismiss functionality
    with st.expander(f"📋 View Alert Details ({len(high_priority_summaries)} total alerts)", expanded=False):
        for summary in high_priority_summaries[:10]:  # Show top 10 alerts
            transaction_id = summary.get("transaction_id", "UNKNOWN")
            priority = summary.get("priority", "UNKNOWN")
            risk_category = summary.get("risk_category", "UNKNOWN")
            alert_count = summary.get("alert_count", 0)
            priority_reason = summary.get("priority_reason", "No reason provided")
            
            # Color code by priority
            if priority == "CRITICAL":
                color = "#dc3545"
                icon = "🔴"
            elif priority == "HIGH":
                color = "#ff9800"
                icon = "🟠"
            elif priority == "MEDIUM":
                color = "#ffc107"
                icon = "🟡"
            else:
                color = "#2196f3"
                icon = "🔵"
            
            # Get alert types for this transaction
            alert_types = [alert.get("alert_type", "UNKNOWN") 
                          for alert in summary.get("alerts", [])]
            alert_types_str = ", ".join([at.replace("_", " ") for at in alert_types])
            
            # Create columns for alert info and dismiss button
            col1, col2 = st.columns([5, 1])
            
            with col1:
                st.markdown(f"""
                <div style="background: #1e2130; padding: 1rem; border-radius: 8px; 
                            border-left: 4px solid {color}; margin-bottom: 0.5rem;">
                    <strong>{icon} {transaction_id}</strong> - {priority} Priority
                    <br><small style="color: #b0b0b0;">
                        Risk Category: {risk_category} | Alerts: {alert_count} ({alert_types_str})
                        <br>Reason: {priority_reason}
                    </small>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Dismiss button
                if st.button("✓ Dismiss", key=f"dismiss_{transaction_id}", help="Mark this alert as reviewed"):
                    response = make_api_request(
                        f"/alerts/dismiss/{transaction_id}",
                        method="POST"
                    )
                    if response.get("status") == "success":
                        st.success(f"Alert {transaction_id} dismissed")
                        st.rerun()
                    else:
                        st.error(f"Failed to dismiss alert: {response.get('message', 'Unknown error')}")
        
        if len(high_priority_summaries) > 10:
            st.info(f"Showing top 10 of {len(high_priority_summaries)} alerts. Use the transaction table below to investigate all alerts.")
    
    # Add section to view dismissed alerts
    dismissed_response = make_api_request("/alerts/dismissed")
    if dismissed_response.get("status") == "success":
        dismissed_summaries = dismissed_response.get("data", {}).get("summaries", [])
        
        if dismissed_summaries:
            with st.expander(f"📁 View Dismissed Alerts ({len(dismissed_summaries)} dismissed)", expanded=False):
                st.info("These alerts have been reviewed and dismissed. You can restore them if needed.")
                
                for summary in dismissed_summaries[:10]:  # Show top 10 dismissed
                    transaction_id = summary.get("transaction_id", "UNKNOWN")
                    priority = summary.get("priority", "UNKNOWN")
                    risk_category = summary.get("risk_category", "UNKNOWN")
                    dismissed_at = summary.get("dismissed_at", "Unknown time")
                    dismissed_by = summary.get("dismissed_by", "Unknown user")
                    
                    # Color code by priority
                    if priority == "CRITICAL":
                        color = "#dc3545"
                        icon = "🔴"
                    elif priority == "HIGH":
                        color = "#ff9800"
                        icon = "🟠"
                    else:
                        color = "#2196f3"
                        icon = "🔵"
                    
                    # Create columns for alert info and restore button
                    col1, col2 = st.columns([5, 1])
                    
                    with col1:
                        st.markdown(f"""
                        <div style="background: #1e2130; padding: 1rem; border-radius: 8px; 
                                    border-left: 4px solid {color}; margin-bottom: 0.5rem; opacity: 0.7;">
                            <strong>{icon} {transaction_id}</strong> - {priority} Priority (Dismissed)
                            <br><small style="color: #b0b0b0;">
                                Risk Category: {risk_category}
                                <br>Dismissed by: {dismissed_by} at {dismissed_at[:19] if len(dismissed_at) > 19 else dismissed_at}
                            </small>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        # Restore button
                        if st.button("↺ Restore", key=f"restore_{transaction_id}", help="Restore this alert to active status"):
                            response = make_api_request(
                                f"/alerts/undismiss/{transaction_id}",
                                method="POST"
                            )
                            if response.get("status") == "success":
                                st.success(f"Alert {transaction_id} restored")
                                st.rerun()
                            else:
                                st.error(f"Failed to restore alert: {response.get('message', 'Unknown error')}")
                
                if len(dismissed_summaries) > 10:
                    st.info(f"Showing 10 of {len(dismissed_summaries)} dismissed alerts.")


def display_transaction_table(transaction_type: str = "all"):
    """Display interactive transaction table with explanation functionality."""
    st.subheader(f"📊 {transaction_type.title()} Transactions")
    
    # Get transactions based on type using retry mechanism
    if transaction_type == "suspicious":
        response = make_api_request("/suspicious")
    elif transaction_type == "fraud":
        response = make_api_request("/fraud")
    else:
        # Use the new retry mechanism for all transactions
        transactions = load_transactions_with_retry()
        if not transactions:
            st.error("Failed to load transactions")
            return
        response = {"status": "success", "data": transactions}
    
    if response.get("status") != "success":
        st.error("Failed to load transactions")
        return
    
    transactions = response.get("data", [])
    if isinstance(transactions, dict) and "transactions" in transactions:
        transactions = transactions["transactions"]
    
    # Add debugging output
    st.write("Loaded transactions:", len(transactions))
    if transactions:
        st.write("Sample transaction keys:", list(transactions[0].keys()) if transactions else "No transactions")
    
    if not transactions:
        st.info(f"No {transaction_type} transactions found.")
        return
    
    # Convert to DataFrame for display
    df = pd.DataFrame(transactions)
    
    # Select key columns for display
    display_columns = [
        'transaction_id', 'product', 'unit_price', 'market_price', 
        'price_deviation', 'risk_score', 'risk_category'
    ]
    
    # Filter columns that exist in the data
    available_columns = [col for col in display_columns if col in df.columns]
    display_df = df[available_columns]
    
    # Format numeric columns
    if 'price_deviation' in display_df.columns:
        display_df['price_deviation'] = display_df['price_deviation'].apply(lambda x: f"{x:.1%}" if pd.notnull(x) else "N/A")
    if 'risk_score' in display_df.columns:
        display_df['risk_score'] = display_df['risk_score'].apply(lambda x: f"{x:.3f}" if pd.notnull(x) else "N/A")
    
    # Display the table
    st.dataframe(display_df, use_container_width=True)
    
    # Transaction selection for explanation
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
            if st.button("📋 Get Fallback Explanation", help="Get rule-based explanation (no API quota used)"):
                explain_transaction(selected_transaction_id, force_ai=False)
        
        with col2:
            if st.button("🤖 Get AI Explanation", help="Get Gemini AI explanation (uses API quota)"):
                explain_transaction(selected_transaction_id, force_ai=True)


def explain_transaction(transaction_id: str, force_ai: bool = False):
    """Get and display transaction explanation."""
    with st.spinner("Generating explanation..."):
        explanation_response = make_api_request(
            f"/explain/{transaction_id}",
            method="POST",
            data={"force_ai": force_ai}
        )
    
    if explanation_response.get("status") == "success":
        data = explanation_response.get("data", {})
        explanation = data.get("explanation", "No explanation available")
        explanation_type = data.get("explanation_type", "unknown")
        session_info = data.get("session_info", {})
        
        # Display explanation with appropriate styling
        if explanation_type == "ai_generated":
            st.markdown(f"""
            <div class="explanation-box">
                <h4>🤖 AI-Powered Analysis</h4>
                <p>{explanation}</p>
                <small><strong>Source:</strong> Gemini AI | <strong>Remaining:</strong> {session_info.get('remaining', 0)} AI explanations</small>
            </div>
            """, unsafe_allow_html=True)
        elif explanation_type == "quota_exceeded":
            st.markdown(f"""
            <div class="alert-banner">
                <h4>⚠️ AI Quota Exceeded</h4>
                <p>{explanation}</p>
                <small>Reset session to get more AI explanations</small>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="explanation-box">
                <h4>📋 Rule-Based Analysis</h4>
                <p>{explanation}</p>
                <small><strong>Source:</strong> Automated rule analysis | <strong>Available:</strong> {session_info.get('remaining', 0)} AI explanations</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.error(f"Failed to generate explanation: {explanation_response.get('message', 'Unknown error')}")


def get_port_coordinates():
    """Get coordinates for major ports used in the dataset."""
    return {
        # Major Asian Ports
        'Shanghai': {'lat': 31.2304, 'lon': 121.4737},
        'Singapore': {'lat': 1.2966, 'lon': 103.7764},
        'Chennai': {'lat': 13.0827, 'lon': 80.2707},
        'Yokohama': {'lat': 35.4437, 'lon': 139.6380},
        'Hong Kong': {'lat': 22.3193, 'lon': 114.1694},
        'Busan': {'lat': 35.1796, 'lon': 129.0756},
        'Mumbai': {'lat': 19.0760, 'lon': 72.8777},
        'Kolkata': {'lat': 22.5726, 'lon': 88.3639},
        'Karachi': {'lat': 24.8607, 'lon': 67.0011},
        'Dubai': {'lat': 25.2048, 'lon': 55.2708},
        'Perth': {'lat': -31.9505, 'lon': 115.8605},
        
        # European Ports
        'Hamburg': {'lat': 53.5511, 'lon': 9.9937},
        'Rotterdam': {'lat': 51.9244, 'lon': 4.4777},
        'Antwerp': {'lat': 51.2194, 'lon': 4.4025},
        'Le Havre': {'lat': 49.4944, 'lon': 0.1079},
        'Barcelona': {'lat': 41.3851, 'lon': 2.1734},
        'Genoa': {'lat': 44.4056, 'lon': 8.9463},
        'Piraeus': {'lat': 37.9755, 'lon': 23.6348},
        
        # American Ports
        'Houston': {'lat': 29.7604, 'lon': -95.3698},
        'Los Angeles': {'lat': 34.0522, 'lon': -118.2437},
        'New York': {'lat': 40.7128, 'lon': -74.0060},
        'Miami': {'lat': 25.7617, 'lon': -80.1918},
        'Vancouver': {'lat': 49.2827, 'lon': -123.1207},
        'Santos': {'lat': -23.9608, 'lon': -46.3331},
        'Buenos Aires': {'lat': -34.6118, 'lon': -58.3960},
        'Valparaiso': {'lat': -33.0472, 'lon': -71.6127},
        
        # African Ports
        'Alexandria': {'lat': 31.2001, 'lon': 29.9187},
        'Cape Town': {'lat': -33.9249, 'lon': 18.4241},
        'Lagos': {'lat': 6.5244, 'lon': 3.3792},
        'Durban': {'lat': -29.8587, 'lon': 31.0218},
        'Casablanca': {'lat': 33.5731, 'lon': -7.5898},
        
        # Other Major Ports
        'Sydney': {'lat': -33.8688, 'lon': 151.2093},
        'Melbourne': {'lat': -37.8136, 'lon': 144.9631},
        'Fremantle': {'lat': -32.0569, 'lon': 115.7439}
    }

@st.cache_data(ttl=60)  # Cache for 60 seconds
def create_route_intelligence_map(df):
    """Create Route Intelligence Map using plotly.graph_objects.Scattergeo."""
    port_coords = get_port_coordinates()
    
    # Create the figure
    fig = go.Figure()
    
    # Color mapping for risk categories
    risk_colors = {
        'SAFE': '#28a745',
        'SUSPICIOUS': '#ffc107',
        'FRAUD': '#dc3545'
    }
    
    # Track export and import ports separately
    export_ports = set()
    import_ports = set()
    route_data = []
    
    # Process transactions to extract route information
    for _, row in df.iterrows():
        export_port = row.get('export_port', '')
        import_port = row.get('import_port', '')
        risk_category = row.get('risk_category', 'SAFE')
        
        # Add ports to respective sets
        if export_port in port_coords:
            export_ports.add(export_port)
        if import_port in port_coords:
            import_ports.add(import_port)
            
        # Store route data if both ports have coordinates
        if export_port in port_coords and import_port in port_coords:
            route_data.append({
                'export_port': export_port,
                'import_port': import_port,
                'risk_category': risk_category,
                'transaction_id': row.get('transaction_id', ''),
                'product': row.get('product', ''),
                'trade_value': row.get('trade_value', 0),
                'distance_km': row.get('distance_km', 0)
            })
    
    # Plot export ports (origin points)
    if export_ports:
        export_lons = [port_coords[port]['lon'] for port in export_ports]
        export_lats = [port_coords[port]['lat'] for port in export_ports]
        export_names = list(export_ports)
        
        fig.add_trace(go.Scattergeo(
            lon=export_lons,
            lat=export_lats,
            mode='markers',
            marker=dict(
                size=10,
                color='#28a745',  # Green for export ports
                symbol='triangle-up',
                line=dict(width=2, color='white')
            ),
            text=export_names,
            hovertemplate="<b>%{text}</b><br>Export Port<br><extra></extra>",
            showlegend=True,
            name="Export Ports"
        ))
    
    # Plot import ports (destination points)
    if import_ports:
        import_lons = [port_coords[port]['lon'] for port in import_ports]
        import_lats = [port_coords[port]['lat'] for port in import_ports]
        import_names = list(import_ports)
        
        fig.add_trace(go.Scattergeo(
            lon=import_lons,
            lat=import_lats,
            mode='markers',
            marker=dict(
                size=10,
                color='#dc3545',  # Red for import ports
                symbol='triangle-down',
                line=dict(width=2, color='white')
            ),
            text=import_names,
            hovertemplate="<b>%{text}</b><br>Import Port<br><extra></extra>",
            showlegend=True,
            name="Import Ports"
        ))
    
    # Group routes by risk category for better visualization
    for risk_cat in ['SAFE', 'SUSPICIOUS', 'FRAUD']:
        routes_in_category = [r for r in route_data if r['risk_category'] == risk_cat]
        
        if not routes_in_category:
            continue
            
        # Create route lines for this risk category
        lons = []
        lats = []
        hover_texts = []
        
        for route in routes_in_category:
            export_coords = port_coords[route['export_port']]
            import_coords = port_coords[route['import_port']]
            
            # Add route line (export -> import -> None for line break)
            lons.extend([export_coords['lon'], import_coords['lon'], None])
            lats.extend([export_coords['lat'], import_coords['lat'], None])
            
            # Hover text for the route
            hover_text = (
                f"<b>{route['transaction_id']}</b><br>"
                f"Route: {route['export_port']} → {route['import_port']}<br>"
                f"Product: {route['product']}<br>"
                f"Trade Value: ${route['trade_value']:,.2f}<br>"
                f"Distance: {route['distance_km']:,} km<br>"
                f"Risk: {route['risk_category']}"
            )
            hover_texts.extend([hover_text, hover_text, None])
        
        # Add route lines for this risk category
        fig.add_trace(go.Scattergeo(
            lon=lons,
            lat=lats,
            mode='lines',
            line=dict(
                width=2,
                color=risk_colors[risk_cat]
            ),
            hovertemplate='%{text}<extra></extra>',
            text=hover_texts,
            name=f"{risk_cat} Routes",
            showlegend=True
        ))
    
    # Update layout for the map
    fig.update_layout(
        title={
            'text': "🗺️ Route Intelligence Map",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': 'white'}
        },
        geo=dict(
            projection_type='natural earth',
            showland=True,
            landcolor='rgb(243, 243, 243)',
            coastlinecolor='rgb(204, 204, 204)',
            showocean=True,
            oceancolor='rgb(230, 245, 255)',
            showlakes=True,
            lakecolor='rgb(230, 245, 255)',
            showrivers=True,
            rivercolor='rgb(230, 245, 255)',
            bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        legend=dict(
            bgcolor='rgba(0,0,0,0.5)',
            bordercolor='white',
            borderwidth=1,
            font=dict(color='white')
        ),
        height=500
    )
    
    return fig

@st.cache_data(ttl=60)  # Cache for 60 seconds
def create_company_network_graph(df):
    """Create Company Risk Network visualization using plotly.graph_objects."""
    import networkx as nx
    import numpy as np
    
    # Create a directed graph for company relationships
    G = nx.DiGraph()
    
    # Track company statistics
    company_stats = {}
    edge_data = []
    
    # Process transactions to build network
    for _, row in df.iterrows():
        exporter = row.get('exporter_company', '')
        importer = row.get('importer_company', '')
        trade_value = row.get('trade_value', 0)
        risk_category = row.get('risk_category', 'SAFE')
        company_risk_score = row.get('company_risk_score', 0)
        
        if not exporter or not importer or exporter == importer:
            continue
            
        # Add nodes with attributes
        for company in [exporter, importer]:
            if company not in company_stats:
                company_stats[company] = {
                    'total_volume': 0,
                    'transaction_count': 0,
                    'risk_scores': [],
                    'risk_categories': []
                }
            
            company_stats[company]['total_volume'] += trade_value
            company_stats[company]['transaction_count'] += 1
            company_stats[company]['risk_scores'].append(company_risk_score)
            company_stats[company]['risk_categories'].append(risk_category)
        
        # Add edge data
        edge_key = (exporter, importer)
        edge_info = {
            'exporter': exporter,
            'importer': importer,
            'trade_value': trade_value,
            'risk_category': risk_category,
            'company_risk_score': company_risk_score
        }
        edge_data.append(edge_info)
        
        # Add edge to graph (sum trade values for multiple transactions)
        if G.has_edge(exporter, importer):
            G[exporter][importer]['weight'] += trade_value
            G[exporter][importer]['transaction_count'] += 1
            G[exporter][importer]['risk_categories'].append(risk_category)
        else:
            G.add_edge(exporter, importer, 
                      weight=trade_value, 
                      transaction_count=1,
                      risk_categories=[risk_category])
    
    if len(G.nodes()) == 0:
        # Return empty figure if no network data
        fig = go.Figure()
        fig.add_annotation(
            text="No company network data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=16, color='white')
        )
        fig.update_layout(
            title="🏢 Company Risk Network",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=500
        )
        return fig
    
    # Use spring layout for better visualization
    try:
        pos = nx.spring_layout(G, k=3, iterations=50, seed=42)
    except:
        # Fallback to circular layout if spring layout fails
        pos = nx.circular_layout(G)
    
    # Prepare node data
    node_x = []
    node_y = []
    node_text = []
    node_size = []
    node_color = []
    node_hover = []
    
    # Color mapping for risk levels
    risk_colors = {
        'SAFE': '#28a745',
        'SUSPICIOUS': '#ffc107',
        'FRAUD': '#dc3545'
    }
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        
        stats = company_stats[node]
        avg_risk = np.mean(stats['risk_scores']) if stats['risk_scores'] else 0
        
        # Determine node color based on average risk and dominant risk category
        risk_categories = stats['risk_categories']
        fraud_count = risk_categories.count('FRAUD')
        suspicious_count = risk_categories.count('SUSPICIOUS')
        safe_count = risk_categories.count('SAFE')
        
        if fraud_count > 0:
            color = risk_colors['FRAUD']
            risk_level = 'HIGH RISK'
        elif suspicious_count > safe_count:
            color = risk_colors['SUSPICIOUS']
            risk_level = 'MEDIUM RISK'
        else:
            color = risk_colors['SAFE']
            risk_level = 'LOW RISK'
        
        node_color.append(color)
        
        # Node size based on transaction volume (normalized)
        volume = stats['total_volume']
        size = max(20, min(60, 20 + (volume / 1000000) * 10))  # Scale based on millions
        node_size.append(size)
        
        # Node label (company name, truncated if too long)
        label = node[:15] + "..." if len(node) > 15 else node
        node_text.append(label)
        
        # Hover information
        hover_info = (
            f"<b>{node}</b><br>"
            f"Risk Level: {risk_level}<br>"
            f"Avg Risk Score: {avg_risk:.3f}<br>"
            f"Total Volume: ${volume:,.0f}<br>"
            f"Transactions: {stats['transaction_count']}<br>"
            f"Fraud: {fraud_count} | Suspicious: {suspicious_count} | Safe: {safe_count}"
        )
        node_hover.append(hover_info)
    
    # Prepare edge data
    edge_x = []
    edge_y = []
    edge_info = []
    edge_colors = []
    edge_widths = []
    
    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        
        # Add edge line coordinates
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        
        # Edge properties
        weight = edge[2]['weight']
        transaction_count = edge[2]['transaction_count']
        risk_categories = edge[2]['risk_categories']
        
        # Determine edge color based on risk
        fraud_count = risk_categories.count('FRAUD')
        suspicious_count = risk_categories.count('SUSPICIOUS')
        
        if fraud_count > 0:
            edge_color = risk_colors['FRAUD']
            risk_level = 'HIGH RISK'
        elif suspicious_count > 0:
            edge_color = risk_colors['SUSPICIOUS']
            risk_level = 'MEDIUM RISK'
        else:
            edge_color = risk_colors['SAFE']
            risk_level = 'LOW RISK'
        
        edge_colors.extend([edge_color, edge_color, edge_color])
        
        # Edge width based on transaction volume
        width = max(1, min(8, 1 + (weight / 1000000) * 3))
        edge_widths.extend([width, width, width])
        
        # Edge hover info (for middle point)
        edge_hover = (
            f"<b>{edge[0]} → {edge[1]}</b><br>"
            f"Risk Level: {risk_level}<br>"
            f"Total Volume: ${weight:,.0f}<br>"
            f"Transactions: {transaction_count}<br>"
            f"Fraud: {fraud_count} | Suspicious: {suspicious_count}"
        )
        edge_info.extend([edge_hover, edge_hover, None])
    
    # Create the figure
    fig = go.Figure()
    
    # Add edges
    if edge_x:
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            mode='lines',
            line=dict(width=2, color='rgba(128,128,128,0.5)'),
            hoverinfo='none',
            showlegend=False,
            name='Connections'
        ))
    
    # Add nodes
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        marker=dict(
            size=node_size,
            color=node_color,
            line=dict(width=2, color='white'),
            opacity=0.8
        ),
        text=node_text,
        textposition="middle center",
        textfont=dict(size=10, color='white'),
        hovertemplate='%{customdata}<extra></extra>',
        customdata=node_hover,
        showlegend=False,
        name='Companies'
    ))
    
    # Add legend manually
    legend_traces = []
    for risk_cat, color in risk_colors.items():
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=15, color=color),
            name=f'{risk_cat} Companies',
            showlegend=True
        ))
    
    # Update layout
    fig.update_layout(
        title={
            'text': "🏢 Company Risk Network",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': 'white'}
        },
        showlegend=True,
        legend=dict(
            bgcolor='rgba(0,0,0,0.5)',
            bordercolor='white',
            borderwidth=1,
            font=dict(color='white'),
            x=1.02,
            y=1
        ),
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        annotations=[
            dict(
                text="Node size = Transaction volume | Edge thickness = Trade relationship strength",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.005, y=-0.002,
                xanchor='left', yanchor='bottom',
                font=dict(size=12, color='rgba(255,255,255,0.7)')
            )
        ],
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=600
    )
    
    return fig


def display_visualizations():
    """Display fraud detection visualizations with lazy loading."""
    st.subheader("📈 Fraud Analysis Visualizations")
    
    # Add tabs for different visualizations to enable lazy loading
    tab1, tab2, tab3, tab4 = st.tabs([
        "🗺️ Route Map", 
        "🏢 Company Network", 
        "📊 Risk Distribution",
        "💰 Price Analysis"
    ])
    
    # Get transaction data for visualizations (cached)
    response = make_api_request("/transactions?limit=200")
    
    if response.get("status") != "success":
        st.error("Failed to load data for visualizations")
        return
    
    transactions = response.get("data", {}).get("transactions", [])
    if not transactions:
        st.info("No data available for visualizations")
        return
    
    df = pd.DataFrame(transactions)
    
    # Tab 1: Route Intelligence Map
    with tab1:
        st.subheader("🗺️ Route Intelligence Map")
        if 'export_port' in df.columns and 'import_port' in df.columns:
            try:
                with st.spinner("Loading route map..."):
                    route_map = create_route_intelligence_map(df)
                    st.plotly_chart(route_map, use_container_width=True)
            except Exception as e:
                st.error(f"Error creating route map: {str(e)}")
                st.info("Route visualization requires valid port data")
        else:
            st.info("Route data not available for visualization")
    
    # Tab 2: Company Risk Network
    with tab2:
        st.subheader("🏢 Company Risk Network")
        if 'exporter_company' in df.columns and 'importer_company' in df.columns:
            try:
                with st.spinner("Loading company network..."):
                    network_graph = create_company_network_graph(df)
                    st.plotly_chart(network_graph, use_container_width=True)
            except Exception as e:
                st.error(f"Error creating company network: {str(e)}")
                st.info("Company network visualization requires valid company data")
        else:
            st.info("Company data not available for network visualization")
    
    # Tab 3: Risk Distribution
    with tab3:
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
            fig_pie.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    
    # Tab 4: Price Deviation Chart
    with tab4:
        if 'market_price' in df.columns and 'unit_price' in df.columns:
            fig_price_deviation = px.scatter(
                df,
                x='market_price',
                y='unit_price',
                color='risk_category',
                title="Price Deviation Chart: Market Price vs Trade Price",
                labels={
                    'market_price': 'Market Price ($)',
                    'unit_price': 'Trade Price ($)',
                    'risk_category': 'Risk Category'
                },
                hover_data=['transaction_id', 'product', 'price_deviation'],
                color_discrete_map={
                    'SAFE': '#28a745',
                    'SUSPICIOUS': '#ffc107',
                    'FRAUD': '#dc3545'
                }
            )
            
            # Add diagonal line to show where market price equals trade price
            max_price = max(df['market_price'].max(), df['unit_price'].max())
            min_price = min(df['market_price'].min(), df['unit_price'].min())
            
            fig_price_deviation.add_shape(
                type="line",
                x0=min_price, y0=min_price,
                x1=max_price, y1=max_price,
                line=dict(color="rgba(255,255,255,0.5)", width=2, dash="dash"),
                name="Market Price = Trade Price"
            )
            
            # Add simple trend line using numpy polyfit
            try:
                import numpy as np
                # Calculate trend line
                x_vals = df['market_price'].values
                y_vals = df['unit_price'].values
                
                # Remove any NaN values
                mask = ~(np.isnan(x_vals) | np.isnan(y_vals))
                x_clean = x_vals[mask]
                y_clean = y_vals[mask]
                
                if len(x_clean) > 1:
                    # Calculate linear trend
                    z = np.polyfit(x_clean, y_clean, 1)
                    p = np.poly1d(z)
                    
                    # Create trend line points
                    x_trend = np.linspace(min_price, max_price, 100)
                    y_trend = p(x_trend)
                    
                    # Add trend line
                    fig_price_deviation.add_scatter(
                        x=x_trend,
                        y=y_trend,
                        mode='lines',
                        name='Trend Line',
                        line=dict(color='rgba(255,165,0,0.8)', width=2),
                        showlegend=True
                    )
            except Exception as e:
                # If trend line calculation fails, continue without it
                pass
            
            fig_price_deviation.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                showlegend=True
            )
            st.plotly_chart(fig_price_deviation, use_container_width=True)


def display_ai_assistant():
    """Display AI investigation assistant."""
    st.subheader("🤖 AI Investigation Assistant")
    
    st.info("💡 Ask questions about fraud patterns, statistics, or investigation guidance. This uses fallback responses to preserve AI quota for transaction explanations.")
    
    query = st.text_input(
        "Ask a question:",
        placeholder="e.g., What are the main fraud patterns? What should I investigate next?"
    )
    
    if st.button("🔍 Ask Question") and query:
        with st.spinner("Processing your question..."):
            query_response = make_api_request(
                "/query",
                method="POST",
                data={"query": query}
            )
        
        if query_response.get("status") == "success":
            data = query_response.get("data", {})
            answer = data.get("answer", "No answer available")
            context = data.get("context_summary", {})
            
            st.markdown(f"""
            <div class="explanation-box">
                <h4>💬 Investigation Assistant Response</h4>
                <p>{answer}</p>
                <hr>
                <small><strong>Context:</strong> {context.get('total_transactions', 0)} transactions | 
                Fraud Rate: {context.get('fraud_rate', '0%')} | 
                Suspicious Rate: {context.get('suspicious_rate', '0%')}</small>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error(f"Failed to process query: {query_response.get('message', 'Unknown error')}")


def main():
    """Main dashboard application."""
    # Display header
    display_header()
    
    # Initialize session state for auto-refresh
    if 'auto_refresh_enabled' not in st.session_state:
        st.session_state.auto_refresh_enabled = False
    if 'refresh_interval' not in st.session_state:
        st.session_state.refresh_interval = 30
    if 'last_refresh_time' not in st.session_state:
        st.session_state.last_refresh_time = time.time()
    
    # Display session information
    display_session_info()
    
    # Auto-refresh controls in sidebar
    st.sidebar.title("⚙️ Dashboard Settings")
    st.sidebar.markdown("### 🔄 Auto-Refresh Settings")
    
    # Toggle auto-refresh
    auto_refresh = st.sidebar.checkbox(
        "Enable Auto-Refresh",
        value=st.session_state.auto_refresh_enabled,
        help="Automatically refresh dashboard data at specified intervals"
    )
    st.session_state.auto_refresh_enabled = auto_refresh
    
    # Refresh interval selector
    if auto_refresh:
        refresh_interval = st.sidebar.selectbox(
            "Refresh Interval",
            options=[10, 30, 60, 120, 300],
            index=1,  # Default to 30 seconds
            format_func=lambda x: f"{x} seconds" if x < 60 else f"{x//60} minute{'s' if x > 60 else ''}",
            help="How often to refresh the data"
        )
        st.session_state.refresh_interval = refresh_interval
        
        # Show time until next refresh
        time_since_refresh = time.time() - st.session_state.last_refresh_time
        time_until_refresh = max(0, refresh_interval - time_since_refresh)
        
        st.sidebar.info(f"⏱️ Next refresh in: {int(time_until_refresh)} seconds")
        
        # Trigger refresh if interval has passed
        if time_since_refresh >= refresh_interval:
            st.session_state.last_refresh_time = time.time()
            st.rerun()
    
    # Manual refresh button
    if st.sidebar.button("🔄 Refresh Now", help="Manually refresh all dashboard data"):
        st.session_state.last_refresh_time = time.time()
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Display KPI metrics with refresh indicator
    st.subheader("📊 Key Performance Indicators")
    show_refresh = auto_refresh and (time.time() - st.session_state.last_refresh_time) < 2
    display_kpi_metrics(show_refresh_indicator=show_refresh)
    
    # Display fraud alerts
    display_fraud_alerts()
    
    # Sidebar for navigation
    st.sidebar.title("🔍 Investigation Tools")
    
    view_option = st.sidebar.selectbox(
        "Select View:",
        ["All Transactions", "Suspicious Transactions", "Fraud Transactions", "Visualizations", "AI Assistant"]
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
    elif view_option == "AI Assistant":
        display_ai_assistant()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**TRINETRA AI v1.0**")
    st.sidebar.markdown("Trade Fraud Intelligence System")


if __name__ == "__main__":
    main()