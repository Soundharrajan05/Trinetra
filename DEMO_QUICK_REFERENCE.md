# TRINETRA AI - Demo Quick Reference Card

## 🚀 Pre-Demo Setup (5 min before)
```bash
cd trinetra-ai-fraud-detection
.\venv\Scripts\activate  # Windows
python main.py
# Wait for: ✅ FastAPI server started + ✅ Streamlit dashboard started
# Open: http://localhost:8501
```

---

## 📋 Demo Flow (10-12 minutes)

### 1. Introduction (2 min)
- Problem: Trade fraud costs billions
- Solution: AI-powered detection + explanations
- Tech: ML (IsolationForest) + Gemini AI
- **Show:** Dashboard overview

### 2. KPI Metrics (1.5 min)
- Total Transactions: ~1,000
- Active Alerts: [X]
- Fraud Rate: ~[X]%
- Trade Value: $[X]M
- High-Risk Routes: [X]

### 3. Alert System (2 min)
- **Show:** Alert priority (🔴 Critical, 🟠 High, 🟡 Medium)
- **Expand:** Alert details
- **Demo:** Dismiss functionality
- **Explain:** 4 alert triggers (Price, Route, Company, Port)

### 4. Transaction Investigation (3 min)
**Navigate:** Sidebar → "Fraud Transactions"

**Example 1: TXN00006 (Underpricing)**
- Crude Oil: $20.16 vs $75 market (-73%)
- Click "Get AI Explanation"
- Explain: Price manipulation, money laundering

**Example 2: TXN00027 (Overpricing)**
- Aluminum: $8,003 vs $2,400 market (+233%)
- Click "Get Fallback Explanation"
- Explain: Illegal money movement

**Example 3: TXN00020/00038/00048 (Route Anomaly)**
- Unusual route: Perth-Malaysia-Indonesia-Yokohama
- Route Anomaly = 1
- Explain: Route laundering

**Show:** Quota management (3 AI explanations/session)
**Demo:** Reset session button

### 5. Visualizations (2 min)
**Navigate:** Sidebar → "Visualizations"

**Route Intelligence Map:**
- Green triangles = Export ports
- Red triangles = Import ports
- Colored lines = Routes (green/yellow/red)
- Hover for details

**Company Risk Network:**
- Node size = Transaction volume
- Node color = Risk level
- Edge thickness = Relationship strength
- Hover for company stats

**Price Deviation Chart:**
- Diagonal line = Normal pricing
- Above = Overpricing
- Below = Underpricing
- Color = Risk category

### 6. AI Assistant (1.5 min)
**Navigate:** Sidebar → "AI Assistant"

**Query 1:** "What are the main fraud patterns?"
**Query 2:** "What should I investigate next?"

**Explain:** Fallback responses preserve AI quota

### 7. Technical Highlights (1 min)
- **ML:** IsolationForest, 6 features, auto-scoring
- **AI:** Gemini API, quota management, caching
- **Backend:** FastAPI, 8 endpoints, real-time
- **Frontend:** Streamlit, Plotly, dark theme
- **Deployment:** Single command (`python main.py`)

### 8. Closing (1 min)
**Key Features:**
1. Automated fraud detection
2. AI-powered explanations
3. Real-time alerts
4. Interactive visualizations
5. Investigation assistant
6. Production-ready

**Impact:**
- Faster detection
- Better accuracy
- Explainability
- Scalability
- Cost-effective

**Future:** Real-time streaming, advanced ML, multi-user, mobile app

---

## 🎯 Key Talking Points
1. "Single command deployment"
2. "AI-powered explanations"
3. "Smart quota management"
4. "Multi-factor risk assessment"
5. "Production-ready"
6. "Real-time analysis"
7. "Explainable AI"
8. "Scalable architecture"

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Dashboard won't load | Check terminal, refresh browser (Ctrl+F5) |
| AI explanations fail | Use fallback, show quota management |
| Visualizations broken | Show transaction table, explain features |
| Slow performance | Reduce limit (?limit=50), close tabs |

---

## 💡 Q&A Quick Answers

**Accuracy?** "Strong anomaly detection, multi-factor approach, continuous retraining"

**False positives?** "3 risk categories (SAFE/SUSPICIOUS/FRAUD), AI explanations help validate"

**API costs?** "3 explanations/session, caching, fallback responses"

**Scale?** "Batch processing, async APIs, add PostgreSQL for production"

**Security?** "Encrypted storage, RBAC, audit logging, environment-based keys"

**Build time?** "[X days/weeks] for hackathon, modular architecture"

**Differentiators?** "AI explanations, single command deployment, smart quota management"

---

## 📊 Demo Metrics

- Dashboard Load: < 3 sec ✅
- API Response: < 1 sec ✅
- ML Training: < 30 sec ✅
- Total Transactions: 1,000
- Fraud Cases: ~20-30 (2-3%)
- Suspicious: ~100-150 (10-15%)
- Alert Types: 4
- API Endpoints: 8
- Visualizations: 4

---

## ✅ Success Checklist

Before demo:
- [ ] System running (API + Dashboard)
- [ ] Browser open to localhost:8501
- [ ] Full screen mode
- [ ] Backup tab ready
- [ ] Know transaction IDs (TXN00006, TXN00027, TXN00020)

During demo:
- [ ] Speak clearly and confidently
- [ ] Make eye contact
- [ ] Point to screen elements
- [ ] Don't rush
- [ ] Show enthusiasm
- [ ] Handle errors gracefully

After demo:
- [ ] Thank audience
- [ ] Share GitHub/docs
- [ ] Answer questions
- [ ] Collect feedback

---

## 🎬 Opening Line
> "Good [morning/afternoon]! I'm excited to present **TRINETRA AI** - an AI-powered Trade Fraud Intelligence System that helps customs authorities and financial regulators detect and investigate suspicious international trade transactions in real-time."

## 🏁 Closing Line
> "TRINETRA AI represents the future of trade fraud detection - combining the power of machine learning with the explainability of AI to protect global commerce. Thank you!"

---

**Remember: You built something amazing - now show it off! 🚀**
