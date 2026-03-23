# TRINETRA AI Dashboard - User Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Dashboard Overview](#dashboard-overview)
4. [Key Performance Indicators (KPIs)](#key-performance-indicators-kpis)
5. [Fraud Alerts System](#fraud-alerts-system)
6. [Transaction Investigation](#transaction-investigation)
7. [Visualizations](#visualizations)
8. [AI Investigation Assistant](#ai-investigation-assistant)
9. [Understanding Risk Scores](#understanding-risk-scores)
10. [Tips for Effective Fraud Investigation](#tips-for-effective-fraud-investigation)
11. [Troubleshooting](#troubleshooting)

---

## Introduction

TRINETRA AI is an AI-powered trade fraud detection platform designed to help fraud analysts and investigators identify suspicious international trade transactions. The system uses machine learning (IsolationForest) to detect anomalies and provides AI-powered explanations through Google's Gemini API.

**Key Features:**
- Real-time fraud detection with ML-based risk scoring
- Interactive dashboard with multiple visualization tools
- AI-powered transaction explanations
- Alert management system with priority levels
- Comprehensive trade route and company network analysis

---

## Getting Started

### Accessing the Dashboard

1. Ensure the TRINETRA AI system is running by executing:
   ```bash
   python main.py
   ```

2. The dashboard will automatically open in your default web browser at:
   ```
   http://localhost:8501
   ```

3. The backend API runs on:
   ```
   http://localhost:8000
   ```

### First-Time Setup

When you first access the dashboard:
- The system automatically loads and processes the trade transaction dataset
- ML model scores all transactions for fraud risk
- Alert system identifies high-priority cases
- All data is ready for investigation within seconds

---

## Dashboard Overview

### Main Layout

The dashboard is organized into several key sections:

```
┌─────────────────────────────────────────────────────┐
│              TRINETRA AI Header                      │
│              (with Active Alert Count)               │
├─────────────────────────────────────────────────────┤
│  Session Info (AI Explanation Quota)                │
├─────────────────────────────────────────────────────┤
│  Key Performance Indicators (5 KPI Cards)           │
├─────────────────────────────────────────────────────┤
│  Fraud Alerts (Priority-based Banners)              │
├─────────────────────────────────────────────────────┤
│  Main Content Area (Selectable Views)               │
│  - All Transactions                                  │
│  - Suspicious Transactions                           │
│  - Fraud Transactions                                │
│  - Visualizations                                    │
│  - AI Assistant                                      │
└─────────────────────────────────────────────────────┘
```

### Sidebar Navigation

The left sidebar provides:
- **Investigation Tools**: Select different views
- **Dashboard Settings**: Configure auto-refresh
- **Manual Refresh**: Update data on demand

---

## Key Performance Indicators (KPIs)

The dashboard displays 5 critical metrics at the top:

### 1. Total Transactions 📊
- **What it shows**: Total number of trade transactions in the system
- **Use case**: Understand the overall volume of trade activity being monitored

### 2. Active Alerts 🚨
- **What it shows**: Number of active (non-dismissed) alerts requiring attention
- **Color coding**:
  - Red: Active alerts present
  - Green: No active alerts
- **Details**: Shows breakdown of Critical and High priority alerts
- **Use case**: Quickly identify how many cases need immediate investigation

### 3. Fraud Rate 🚨
- **What it shows**: Percentage of transactions classified as FRAUD
- **Details**: Shows absolute number of fraud cases detected
- **Use case**: Monitor overall fraud prevalence in trade activity

### 4. Total Trade Value 💰
- **What it shows**: Cumulative value of all transactions (in USD)
- **Use case**: Understand the financial scale of monitored trade activity

### 5. High-Risk Routes 🌍
- **What it shows**: Number of high-risk shipping routes identified
- **Details**: Shows average risk score across all transactions
- **Use case**: Identify geographic patterns in fraud activity

---

## Fraud Alerts System

### Understanding Alert Priorities

TRINETRA AI uses a 4-level priority system:

| Priority | Icon | Color | Meaning |
|----------|------|-------|---------|
| **CRITICAL** | 🔴 | Red | Immediate action required - multiple high-risk indicators |
| **HIGH** | 🟠 | Orange | Requires investigation soon - significant risk factors |
| **MEDIUM** | 🟡 | Yellow | Review when convenient - moderate risk indicators |
| **LOW** | 🔵 | Blue | Low priority - minor anomalies detected |

### Alert Triggers

Alerts are automatically generated when transactions meet these criteria:

1. **Price Anomaly**: `price_deviation > 0.5` (50% deviation from market price)
2. **Route Anomaly**: `route_anomaly == 1` (unusual shipping route detected)
3. **High-Risk Company**: `company_risk_score > 0.8` (company has high historical risk)
4. **Port Congestion**: `port_activity_index > 1.5` (unusual port activity levels)

### Alert Management

#### Viewing Active Alerts

1. Active alerts are displayed prominently at the top of the dashboard
2. Click **"View Alert Details"** to expand and see individual alerts
3. Each alert shows:
   - Transaction ID
   - Priority level and icon
   - Risk category (SAFE/SUSPICIOUS/FRAUD)
   - Number and types of alerts triggered
   - Priority reason (why it's classified at this level)

#### Dismissing Alerts

When you've investigated an alert:

1. Click the **"✓ Dismiss"** button next to the alert
2. The alert moves to the "Dismissed Alerts" section
3. Dismissed alerts are hidden from the active view but can be restored

#### Restoring Dismissed Alerts

If you need to revisit a dismissed alert:

1. Expand the **"View Dismissed Alerts"** section
2. Find the alert you want to restore
3. Click the **"↺ Restore"** button
4. The alert returns to the active alerts list

---

## Transaction Investigation

### Viewing Transactions

Select from three transaction views in the sidebar:

1. **All Transactions**: Complete dataset (limited to 50 for performance)
2. **Suspicious Transactions**: Only transactions with `risk_category = SUSPICIOUS`
3. **Fraud Transactions**: Only transactions with `risk_category = FRAUD`

### Transaction Table Columns

The table displays key information:

- **transaction_id**: Unique identifier for the transaction
- **product**: Product being traded
- **unit_price**: Actual trade price
- **market_price**: Expected market price
- **price_deviation**: Percentage deviation from market price
- **risk_score**: ML-generated anomaly score
- **risk_category**: Classification (SAFE/SUSPICIOUS/FRAUD)

### Getting Transaction Explanations

TRINETRA AI provides two types of explanations:

#### 1. Fallback Explanation (Rule-Based) 📋

- **How to use**: Select a transaction and click **"Get Fallback Explanation"**
- **What it provides**: Rule-based analysis using predefined fraud indicators
- **Quota**: Unlimited - does not use AI API quota
- **Best for**: Quick initial assessment of transactions

**Example Fallback Explanation:**
```
This transaction shows suspicious characteristics:
- Price deviation of 45% above market price suggests potential 
  price manipulation
- Route anomaly detected indicating unusual shipping path
- Company risk score of 0.85 indicates high-risk entity involvement
```

#### 2. AI Explanation (Gemini-Powered) 🤖

- **How to use**: Select a transaction and click **"Get AI Explanation"**
- **What it provides**: Natural language analysis from Google Gemini AI
- **Quota**: Limited to 3 per session (to prevent API errors)
- **Best for**: Complex cases requiring detailed analysis

**Example AI Explanation:**
```
This transaction exhibits multiple fraud indicators that warrant 
investigation. The 45% price deviation significantly exceeds normal 
market fluctuations for this commodity category. Combined with the 
unusual shipping route and the exporter's elevated risk profile 
(score: 0.85), this suggests potential trade-based money laundering. 
The port activity index of 1.8 also indicates abnormal congestion 
patterns. Recommend immediate verification of documentation and 
beneficial ownership.
```

### AI Quota Management

The dashboard displays your AI explanation quota:

- **Available**: Shows remaining AI explanations (e.g., "2/3 remaining")
- **Exhausted**: Red banner when quota is used up
- **Reset**: Click **"🔄 Reset Session"** to get 3 new AI explanations

**Best Practice**: Use fallback explanations for initial screening, reserve AI explanations for complex or high-priority cases.

---

## Visualizations

Access comprehensive visualizations by selecting **"Visualizations"** in the sidebar.

### 1. Route Intelligence Map 🗺️

**Purpose**: Visualize global trade routes and identify geographic fraud patterns

**Features**:
- **Export Ports**: Green triangles (▲) show origin points
- **Import Ports**: Red triangles (▼) show destination points
- **Route Lines**: Colored by risk category
  - Green: SAFE routes
  - Yellow: SUSPICIOUS routes
  - Red: FRAUD routes
- **Interactive**: Hover over routes to see:
  - Transaction ID
  - Route details (origin → destination)
  - Product information
  - Trade value
  - Distance in kilometers
  - Risk category

**How to Use**:
1. Identify clusters of high-risk routes (red lines)
2. Look for unusual route patterns (e.g., indirect paths)
3. Investigate ports with high concentrations of fraud activity
4. Compare expected vs. actual shipping routes

### 2. Company Risk Network 🏢

**Purpose**: Analyze relationships between trading companies and identify high-risk entities

**Features**:
- **Nodes (Companies)**: 
  - Size indicates transaction volume (larger = more activity)
  - Color indicates risk level:
    - Red: High risk (fraud detected)
    - Yellow: Medium risk (suspicious activity)
    - Green: Low risk (safe transactions)
- **Edges (Connections)**:
  - Lines show trading relationships
  - Thickness indicates relationship strength (trade volume)
  - Color indicates risk level of the relationship
- **Interactive**: Hover over nodes to see:
  - Company name
  - Risk level and average risk score
  - Total transaction volume
  - Number of transactions
  - Breakdown of fraud/suspicious/safe transactions

**How to Use**:
1. Identify high-risk companies (large red nodes)
2. Trace connections to find networks of suspicious entities
3. Look for companies with many high-risk relationships
4. Investigate companies with sudden volume spikes

### 3. Risk Category Distribution (Pie Chart)

**Purpose**: Understand the overall distribution of risk classifications

**Features**:
- Visual breakdown of SAFE, SUSPICIOUS, and FRAUD transactions
- Percentage and count for each category
- Color-coded for quick interpretation

**How to Use**:
- Monitor changes in fraud rate over time
- Identify if fraud is increasing or decreasing
- Assess overall system health

### 4. Price Deviation Chart

**Purpose**: Identify pricing anomalies and manipulation patterns

**Features**:
- **X-axis**: Market Price (expected price)
- **Y-axis**: Trade Price (actual price)
- **Diagonal Line**: Shows where market price = trade price
- **Trend Line**: Orange line showing overall pricing trend
- **Color Coding**: Points colored by risk category
- **Interactive**: Hover to see:
  - Transaction ID
  - Product name
  - Exact prices
  - Price deviation percentage

**How to Use**:
1. Points **above** the diagonal line = overpriced (potential money laundering)
2. Points **below** the diagonal line = underpriced (potential tax evasion)
3. Points **far from** the diagonal = high price deviation (investigate first)
4. Clusters of red points = systematic pricing fraud

---

## AI Investigation Assistant

### Purpose

The AI Investigation Assistant helps you:
- Understand fraud patterns in the dataset
- Get guidance on investigation priorities
- Ask questions about statistics and trends
- Receive recommendations for next steps

### How to Use

1. Select **"AI Assistant"** from the sidebar
2. Type your question in the text input field
3. Click **"🔍 Ask Question"**
4. Review the response and context summary

### Example Questions

**Pattern Analysis**:
- "What are the main fraud patterns in the dataset?"
- "Which companies have the highest risk scores?"
- "What routes show the most suspicious activity?"

**Investigation Guidance**:
- "What should I investigate next?"
- "Which transactions require immediate attention?"
- "How do I identify trade-based money laundering?"

**Statistics**:
- "What is the current fraud rate?"
- "How many high-risk alerts are active?"
- "What percentage of transactions are suspicious?"

### Understanding Responses

The assistant provides:
- **Answer**: Natural language response to your question
- **Context Summary**: Key statistics including:
  - Total transactions
  - Fraud rate
  - Suspicious rate

**Note**: The AI Assistant uses fallback responses to preserve API quota for transaction explanations. For detailed AI analysis, use the transaction explanation feature.

---

## Understanding Risk Scores

### Risk Score Calculation

TRINETRA AI uses an **IsolationForest** machine learning model to calculate risk scores based on 6 engineered features:

1. **price_anomaly_score**: Absolute deviation from market price
2. **route_risk_score**: Binary indicator of abnormal shipping route
3. **company_network_risk**: Company's historical risk profile
4. **port_congestion_score**: Port activity level indicator
5. **shipment_duration_risk**: Duration normalized by distance
6. **volume_spike_score**: Cargo volume per unit quantity

### Risk Score Interpretation

| Risk Score | Risk Category | Meaning | Action Required |
|------------|---------------|---------|-----------------|
| **< -0.2** | SAFE | Normal transaction, low fraud probability | Routine monitoring |
| **-0.2 to 0.2** | SUSPICIOUS | Moderate anomalies detected | Investigation recommended |
| **> 0.2** | FRAUD | High fraud probability | Immediate investigation required |

### Risk Categories

#### SAFE ✅
- Transaction follows normal patterns
- All indicators within expected ranges
- Low priority for investigation
- **Action**: Routine monitoring, no immediate action needed

#### SUSPICIOUS ⚠️
- One or more moderate anomalies detected
- Deviates from normal patterns but not extreme
- Medium priority for investigation
- **Action**: Review transaction details, check documentation, investigate if time permits

#### FRAUD 🚨
- Multiple severe anomalies detected
- Significant deviation from normal patterns
- High priority for immediate investigation
- **Action**: Immediate investigation, verify documentation, check beneficial ownership, consider escalation

---

## Tips for Effective Fraud Investigation

### 1. Start with High-Priority Alerts

**Workflow**:
1. Check the **Active Alerts** count in the header
2. Review **CRITICAL** alerts first (red banners)
3. Then investigate **HIGH** priority alerts (orange banners)
4. Use the alert details to understand why each transaction was flagged

### 2. Use the Right Explanation Type

**Decision Tree**:
```
Is this a complex case with multiple risk factors?
├─ YES → Use AI Explanation (if quota available)
└─ NO → Use Fallback Explanation

Is this a high-value transaction?
├─ YES → Use AI Explanation
└─ NO → Use Fallback Explanation

Do you need detailed reasoning?
├─ YES → Use AI Explanation
└─ NO → Use Fallback Explanation
```

### 3. Leverage Visualizations

**Route Intelligence Map**:
- Look for routes that deviate from direct paths
- Identify ports with high concentrations of fraud
- Compare similar products to find route anomalies

**Company Risk Network**:
- Trace connections between high-risk entities
- Identify companies that frequently trade with fraudulent entities
- Look for isolated clusters of suspicious activity

**Price Deviation Chart**:
- Focus on points far from the diagonal line
- Investigate clusters of overpriced transactions (above line)
- Check for systematic underpricing (below line)

### 4. Investigate Systematically

**Step-by-Step Process**:

1. **Initial Screening**:
   - Review KPIs to understand overall fraud landscape
   - Check active alerts for immediate priorities
   - Scan suspicious transactions table

2. **Detailed Investigation**:
   - Select high-priority transaction
   - Get fallback explanation for quick assessment
   - Review all risk indicators (price, route, company, port)
   - Check visualizations for context (route map, company network)

3. **Deep Analysis** (for complex cases):
   - Use AI explanation for detailed reasoning
   - Cross-reference with company network to find related entities
   - Check route map for geographic patterns
   - Review price deviation chart for pricing anomalies

4. **Documentation**:
   - Note key findings
   - Dismiss alerts after investigation
   - Flag cases for escalation if needed

### 5. Monitor Patterns Over Time

**Use Auto-Refresh**:
1. Enable auto-refresh in the sidebar
2. Set appropriate interval (30-60 seconds recommended)
3. Watch for:
   - Sudden spikes in fraud rate
   - New high-risk routes appearing
   - Changes in company risk profiles
   - Emerging fraud patterns

### 6. Prioritize by Impact

**High-Impact Indicators**:
- **High trade value** + suspicious indicators = priority investigation
- **Multiple alerts** on single transaction = likely fraud
- **CRITICAL priority** alerts = immediate action required
- **Known high-risk companies** = escalate quickly

### 7. Use Context Clues

**Red Flags to Watch For**:
- Price deviation > 50% (extreme over/underpricing)
- Route anomaly + high company risk score (coordinated fraud)
- Port congestion + volume spike (smuggling indicators)
- Multiple transactions between same high-risk entities (network fraud)

---

## Troubleshooting

### Dashboard Not Loading

**Problem**: Dashboard shows "Cannot connect to TRINETRA AI API"

**Solution**:
1. Ensure the backend API is running:
   ```bash
   python main.py
   ```
2. Check that port 8000 is not blocked by firewall
3. Verify the API is accessible at `http://localhost:8000`

### AI Explanations Not Working

**Problem**: "AI Quota Exhausted" message appears

**Solution**:
1. Click **"🔄 Reset Session"** button to get 3 new AI explanations
2. Use fallback explanations for routine investigations
3. Reserve AI explanations for complex cases

**Problem**: AI explanation returns generic response

**Solution**:
- This is expected behavior when quota is exhausted
- The system automatically falls back to rule-based explanations
- Reset session to restore AI functionality

### Visualizations Not Displaying

**Problem**: "No data available for visualization" message

**Solution**:
1. Ensure transactions are loaded (check KPI metrics)
2. Verify the dataset contains required columns (export_port, import_port, etc.)
3. Try refreshing the dashboard manually

**Problem**: Route map shows no routes

**Solution**:
- The dataset may not contain valid port coordinates
- Check that export_port and import_port columns have recognized port names
- Refer to the port coordinates dictionary in the code

### Slow Performance

**Problem**: Dashboard is slow or unresponsive

**Solution**:
1. Reduce auto-refresh frequency (increase interval)
2. Limit transaction table to fewer rows (default is 50)
3. Close unused browser tabs
4. Restart the application:
   ```bash
   # Stop the application (Ctrl+C)
   # Restart
   python main.py
   ```

### Data Not Refreshing

**Problem**: KPIs or alerts not updating

**Solution**:
1. Click **"🔄 Refresh Now"** in the sidebar
2. Enable auto-refresh if disabled
3. Check that the backend API is responding (visit `http://localhost:8000`)

---

## Best Practices Summary

### For Fraud Analysts

✅ **DO**:
- Start each session by reviewing active alerts
- Use fallback explanations for initial screening
- Reserve AI explanations for complex cases
- Dismiss alerts after investigation to keep workspace clean
- Enable auto-refresh during active monitoring
- Use visualizations to identify patterns
- Document findings for each investigation

❌ **DON'T**:
- Waste AI quota on simple cases
- Ignore CRITICAL priority alerts
- Dismiss alerts without investigation
- Rely solely on risk scores (review context)
- Forget to reset session when quota is exhausted

### For Investigators

✅ **DO**:
- Use the company network graph to trace fraud networks
- Cross-reference route map with price deviations
- Investigate clusters of high-risk activity
- Look for systematic patterns (not just individual transactions)
- Use AI assistant for investigation guidance
- Monitor trends over time with auto-refresh

❌ **DON'T**:
- Focus only on individual transactions (miss the bigger picture)
- Ignore geographic patterns in route map
- Overlook company relationships in network graph
- Skip visualization analysis

---

## Quick Reference Card

### Navigation Shortcuts

| Action | Location | Shortcut |
|--------|----------|----------|
| View all transactions | Sidebar → "All Transactions" | - |
| View suspicious only | Sidebar → "Suspicious Transactions" | - |
| View fraud only | Sidebar → "Fraud Transactions" | - |
| Access visualizations | Sidebar → "Visualizations" | - |
| Use AI assistant | Sidebar → "AI Assistant" | - |
| Refresh data | Sidebar → "🔄 Refresh Now" | - |
| Reset AI quota | Session Info → "🔄 Reset Session" | - |

### Risk Score Quick Reference

| Score | Category | Priority | Action |
|-------|----------|----------|--------|
| < -0.2 | SAFE | Low | Monitor |
| -0.2 to 0.2 | SUSPICIOUS | Medium | Investigate |
| > 0.2 | FRAUD | High | Immediate action |

### Alert Priority Quick Reference

| Priority | Icon | Action Timeline |
|----------|------|-----------------|
| CRITICAL | 🔴 | Immediate (within 1 hour) |
| HIGH | 🟠 | Same day |
| MEDIUM | 🟡 | Within 2-3 days |
| LOW | 🔵 | When convenient |

---

## Support and Additional Resources

### Documentation Files

- **README.md**: System setup and installation instructions
- **API_DOCUMENTATION.md**: Complete API endpoint reference
- **requirements.md**: System requirements and acceptance criteria
- **design.md**: Technical architecture and design decisions

### Getting Help

For technical issues or questions:
1. Check this user guide first
2. Review the troubleshooting section
3. Consult the API documentation for backend issues
4. Check system logs in `trinetra.log`

### System Information

- **Version**: 1.0.0
- **Backend**: FastAPI (Python)
- **Frontend**: Streamlit
- **ML Model**: IsolationForest (scikit-learn)
- **AI Engine**: Google Gemini API

---

**End of User Guide**

*Last Updated: 2024*
*TRINETRA AI - Trade Fraud Intelligence System*
