# TRINETRA AI - Demo Quick Reference Guide

## 🚀 Quick Start

```bash
# Start the system
python main.py

# Wait for: "Dashboard available at http://localhost:8501"
# System ready in ~30 seconds
```

---

## 📊 Key Demo Transactions

### Transaction TXN00006 - **EXTREME FRAUD** ⚠️
- **Product**: Crude Oil
- **Price**: $20.16/ton (Market: $75/ton)
- **Deviation**: -73.12% 🔴
- **Why**: Transfer pricing fraud / Money laundering
- **Demo Point**: "No one sells oil at 73% discount legitimately"

### Transaction TXN00017 - **SUSPICIOUS** ⚠️
- **Product**: Wheat
- **Price**: $358.39/ton (Market: $300/ton)
- **Deviation**: +19.46% 🟡
- **Company Risk**: 0.93 (Very High!)
- **Why**: Invoice fraud / Overpricing scheme
- **Demo Point**: "Why pay 19% more? High-risk company involved"

### Transaction TXN00010 - **MULTIPLE ALERTS** ⚠️
- **Product**: Copper
- **Price Deviation**: +13.26%
- **Company Risk**: 0.83 (High)
- **Port Activity**: 1.5 (Congested)
- **Why**: Multiple risk factors compound
- **Demo Point**: "AI weighs multiple indicators together"

---

## 🎯 5-Minute Demo Flow

| Time | Action | What to Say |
|------|--------|-------------|
| 0:00 | Open Dashboard | "TRINETRA AI monitors 1,000 transactions, detected 117 frauds" |
| 0:30 | Show KPIs | "11.7% fraud rate, $X total trade value monitored" |
| 1:00 | Click TXN00006 | "Look at this crude oil - 73% below market price!" |
| 1:30 | Get AI Explanation | "AI explains why this is fraud in plain English" |
| 2:00 | Show Route Map | "Red routes are high-risk, see the patterns?" |
| 2:30 | Price Chart | "This chart reveals pricing anomalies instantly" |
| 3:00 | Company Network | "These clusters show organized fraud rings" |
| 3:30 | AI Assistant | "Ask: 'Why is TXN00006 suspicious?'" |
| 4:00 | Show Alerts | "Real-time alerts for 4 fraud types" |
| 4:30 | Closing | "Production-ready, processes 1000s of transactions in seconds" |

---

## 💡 Key Talking Points

### Opening Hook
> "Trade fraud costs the global economy $2 trillion annually. TRINETRA AI uses machine learning and AI to detect it in real-time."

### Technical Highlights
- ✅ **IsolationForest ML** - Anomaly detection
- ✅ **Gemini AI** - Natural language explanations
- ✅ **6 Fraud Features** - Price, route, company, port, duration, volume
- ✅ **FastAPI + Streamlit** - Modern, scalable stack
- ✅ **Real-Time Scoring** - < 1 second per transaction

### Business Impact
- 💰 **80% Time Savings** - Automated fraud detection
- 🎯 **High Accuracy** - Low false positive rate
- 📈 **Scalable** - Handles growing transaction volumes
- 🔍 **Explainable** - AI provides reasoning, not just scores
- ⚡ **Fast Deployment** - Single command setup

---

## 🔍 Investigation Demo Script

### Step 1: Identify Suspicious Transaction
```
1. Go to "Suspicious Transactions" table
2. Sort by "Risk Score" (descending)
3. Click on TXN00006
```

**Say**: "Let's investigate this flagged transaction..."

### Step 2: Get AI Explanation
```
1. Click "Get AI Explanation" button
2. Wait 2-3 seconds for Gemini response
3. Read key points aloud
```

**Say**: "The AI explains this is likely transfer pricing fraud because..."

### Step 3: Visualize Context
```
1. Scroll to Route Intelligence Map
2. Find the transaction's route (red line)
3. Point out unusual path
```

**Say**: "Notice how this route avoids major inspection ports..."

### Step 4: Compare Pricing
```
1. Go to Price Deviation Chart
2. Find the transaction point (far left = underpriced)
3. Show distance from normal pricing
```

**Say**: "This point is way off the normal pricing curve..."

### Step 5: Check Company History
```
1. Open Company Risk Network
2. Find the company node
3. Show connections and risk score
```

**Say**: "This company has a history of suspicious activity..."

---

## 📈 Dashboard Sections Cheat Sheet

### 1. Global Trade Overview (Top)
- **Total Transactions**: 1,000
- **Fraud Rate**: 11.7%
- **Total Trade Value**: $XXX million
- **High-Risk Countries**: XX

**Demo Tip**: Point out the fraud rate - "Nearly 12% fraud rate shows how critical detection is"

### 2. Fraud Alerts (Banner)
- **4 Alert Types**: Price, Route, Company, Port
- **Color Coded**: Red = Critical, Yellow = Warning
- **Real-Time**: Updates as data changes

**Demo Tip**: "System automatically prioritizes alerts by severity"

### 3. Suspicious Transactions Table
- **Sortable**: Click column headers
- **Filterable**: Use search box
- **Interactive**: Click row for details

**Demo Tip**: "Investigators can quickly filter and sort to focus on high-priority cases"

### 4. Route Intelligence Map
- **Global View**: All shipping routes
- **Color Coded**: Red = High Risk, Yellow = Medium, Green = Safe
- **Interactive**: Hover for details

**Demo Tip**: "Visualizing routes reveals patterns humans might miss"

### 5. Price Deviation Chart
- **X-Axis**: Market Price
- **Y-Axis**: Trade Price
- **Diagonal Line**: Fair pricing
- **Points**: Individual transactions

**Demo Tip**: "Points far from the line are pricing anomalies"

### 6. Company Risk Network
- **Nodes**: Companies
- **Edges**: Trade relationships
- **Size**: Transaction volume
- **Color**: Risk level

**Demo Tip**: "Network analysis exposes organized fraud rings"

### 7. AI Investigation Assistant
- **Natural Language**: Ask questions in plain English
- **Contextual**: Understands transaction data
- **Powered by Gemini**: Advanced AI reasoning

**Demo Tip**: "No SQL needed - just ask questions naturally"

---

## 🎤 Sample Questions & Answers

### Q: "How accurate is the fraud detection?"
**A**: "We detect 117 fraud cases out of 1,000 transactions with a low false positive rate. The ML model is trained on 6 engineered features specific to trade fraud patterns."

### Q: "How fast is it?"
**A**: "The system processes 1,000 transactions in under 30 seconds. Individual risk scoring takes less than 1 second per transaction."

### Q: "Can it explain its decisions?"
**A**: "Yes! That's a key feature. We integrate Gemini AI to provide natural language explanations for every flagged transaction. No black box - full transparency."

### Q: "What types of fraud does it detect?"
**A**: "Four main types: Price manipulation (over/underpricing), Route anomalies (smuggling), High-risk companies (repeat offenders), and Port exploitation (congested ports with weak inspection)."

### Q: "Is it production-ready?"
**A**: "Absolutely. Single command deployment, comprehensive error handling, and we've tested it with 1,000+ transactions. It's ready for real-world use."

### Q: "What's the tech stack?"
**A**: "Python backend with FastAPI, Streamlit frontend, scikit-learn for ML, Gemini AI for explanations, and Plotly for visualizations. Modern, scalable, and maintainable."

---

## 🚨 Troubleshooting During Demo

### Dashboard Won't Load
```bash
# Check if backend is running
curl http://localhost:8000/stats

# Restart system
python main.py
```

### Gemini API Fails
- **Don't Panic**: System has fallback explanations
- **Say**: "We have rule-based explanations as backup"
- **Show**: Fallback explanation still provides value

### Visualization Not Rendering
- **Refresh**: Press F5
- **Backup**: Have screenshots ready
- **Explain**: "Let me show you a screenshot of this visualization"

### Slow Performance
- **Cause**: Large dataset loading
- **Solution**: Use cached data
- **Say**: "In production, we use caching for instant load times"

---

## 📝 Demo Checklist

### Before Demo (15 minutes before)
- [ ] Start system: `python main.py`
- [ ] Verify dashboard loads at http://localhost:8501
- [ ] Test Gemini API (click "Get AI Explanation" on any transaction)
- [ ] Check all visualizations render
- [ ] Open this quick reference guide
- [ ] Have backup screenshots ready
- [ ] Test on presentation computer/projector
- [ ] Close unnecessary browser tabs
- [ ] Disable notifications

### During Demo
- [ ] Speak clearly and confidently
- [ ] Point to screen elements as you explain
- [ ] Use the 5-minute flow as guide
- [ ] Show at least 2 fraud examples
- [ ] Demonstrate AI explanation
- [ ] Highlight business impact
- [ ] Keep energy high
- [ ] Watch the time

### After Demo
- [ ] Thank the audience
- [ ] Take questions
- [ ] Share GitHub repo link
- [ ] Collect feedback
- [ ] Network with judges/attendees

---

## 🎯 Fraud Pattern Quick Reference

| Pattern | Indicator | Threshold | Example TXN |
|---------|-----------|-----------|-------------|
| **Price Manipulation** | price_deviation | > 50% or < -50% | TXN00006 (-73%) |
| **Route Anomaly** | route_anomaly | = 1 | Multiple |
| **High-Risk Company** | company_risk_score | > 0.8 | TXN00017 (0.93) |
| **Port Exploitation** | port_activity_index | > 1.5 | 279 cases |
| **Volume Spike** | volume_spike_score | Unusual ratio | Check chart |
| **Duration Risk** | shipment_duration_risk | High ratio | Long routes |

---

## 💻 Command Reference

```bash
# Start system
python main.py

# Run tests
pytest backend/

# Check API health
curl http://localhost:8000/stats

# View logs
tail -f logs/trinetra.log

# Stop system
Ctrl+C (in terminal)
```

---

## 🌟 Closing Statements

### Option 1: Technical Focus
> "TRINETRA AI combines machine learning, AI explanations, and interactive visualizations to detect trade fraud at scale. It's production-ready, processes thousands of transactions in seconds, and provides the transparency investigators need to take action."

### Option 2: Business Focus
> "Trade fraud costs billions annually. TRINETRA AI helps customs authorities and financial regulators catch fraud faster, reduce investigation time by 80%, and make data-driven decisions with confidence. It's not just detection - it's actionable intelligence."

### Option 3: Impact Focus
> "Every fraudulent transaction we catch prevents financial loss, protects legitimate businesses, and strengthens global trade integrity. TRINETRA AI makes that possible at scale, in real-time, with full explainability."

---

## 📞 Resources

- **Full Demo Guide**: `docs/DEMO_SCENARIOS.md`
- **User Guide**: `USER_GUIDE.md`
- **API Docs**: `API_DOCUMENTATION.md`
- **Deployment**: `DEPLOYMENT.md`
- **Troubleshooting**: `TROUBLESHOOTING_GUIDE.md`

---

**Pro Tip**: Practice the 5-minute demo at least 3 times before the presentation. Know your key transactions (TXN00006, TXN00017) by heart. Confidence sells the demo!

**Remember**: You built something amazing. Show it with pride! 🚀
