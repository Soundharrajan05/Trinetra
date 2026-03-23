# 🛡️ TRINETRA AI - Demo Backup Plans for Hackathon

> **Emergency Response Guide for Demo Failures**  
> Quick reference for handling failures during hackathon demonstrations

**Version:** 1.0  
**Last Updated:** 2024  
**Purpose:** Ensure smooth demo execution with contingency plans for all failure scenarios

---

## 📋 Quick Reference Card

**Print this section and keep it handy during the demo!**

| Failure Scenario | Immediate Action | Backup Solution |
|------------------|------------------|-----------------|
| **System won't start** | Use pre-started backup instance | Show pre-recorded demo video |
| **Gemini API fails** | Switch to fallback explanations | Use pre-generated explanation screenshots |
| **Dashboard crashes** | Restart with `streamlit run frontend/dashboard.py` | Show static dashboard screenshots |
| **Network failure** | Enable offline mode | Use cached data and local explanations |
| **Data loading error** | Use backup dataset | Show pre-loaded data screenshots |
| **Slow performance** | Switch to demo mode (reduced dataset) | Navigate to pre-cached views |

---

## 🚨 Critical Failure Scenarios

### Scenario 1: Complete System Failure

**Symptoms:**
- Application won't start
- Both API and dashboard are down
- Fatal errors during startup


**Immediate Actions (30 seconds):**
1. Press Ctrl+C to stop current process
2. Run: `python main.py`
3. If fails again, proceed to backup plan

**Backup Plan A: Pre-Started Instance**
```bash
# Before demo, start a backup instance on different ports
export API_PORT=8001
export STREAMLIT_PORT=8502
python main.py &

# During demo, if main fails, switch to:
# http://localhost:8502
```

**Backup Plan B: Static Demo Materials**
- Location: `docs/demo_screenshots/`
- Contents:
  - Dashboard overview screenshot
  - Fraud transaction examples
  - AI explanation examples
  - Visualization screenshots
- **Action:** Walk through screenshots while explaining features

**Backup Plan C: Pre-Recorded Demo Video**
- Location: `docs/demo_video.mp4`
- Duration: 5 minutes
- **Action:** Play video and provide live commentary

**Recovery Time:** 
- Plan A: 10 seconds (switch browser tab)
- Plan B: 30 seconds (open screenshots)
- Plan C: 15 seconds (play video)

---

### Scenario 2: Gemini API Failure

**Symptoms:**
- "API key not valid" errors
- "Quota exceeded" messages
- Timeout errors from Gemini
- 429 or 403 HTTP errors

**Immediate Actions (10 seconds):**
1. System automatically switches to fallback explanations
2. Continue demo with rule-based analysis
3. Acknowledge: "Using our fallback analysis system"

**Backup Plan A: Pre-Generated Explanations**
```bash
# Before demo, generate explanations for key transactions
# Store in: docs/demo_explanations.json
```

Key transactions with pre-generated explanations:
- **TXN00006**: Extreme price deviation fraud
- **TXN00017**: High-risk company involvement
- **TXN00010**: Multiple alert triggers
- **TXN00452**: Route anomaly case

**Backup Plan B: Manual Explanation Script**

Use this script when explaining transactions:

```
"This transaction shows [FRAUD/SUSPICIOUS] indicators because:

1. Price Analysis: The trade price is [X]% [above/below] market value
2. Company Risk: Risk score of [X] indicates [high/medium] risk history
3. Route Analysis: [Normal/Abnormal] shipping route detected
4. Additional Factors: [Port congestion/Volume spike/Duration anomaly]

Our AI system flagged this for investigation based on these combined factors."
```

**Backup Plan C: Fallback Explanation Demo**
- **Action:** Demonstrate the fallback system as a feature
- **Script:** "Our system includes intelligent fallback analysis that works even without external AI APIs, ensuring continuous operation in any environment."

**Recovery Time:** Immediate (automatic fallback)

---

### Scenario 3: Dashboard Rendering Failure

**Symptoms:**
- Blank dashboard
- "Connection Error" messages
- Visualizations not loading
- White screen or error messages

**Immediate Actions (15 seconds):**
1. Refresh browser (F5 or Ctrl+R)
2. If fails, clear cache (Ctrl+Shift+R)
3. If still fails, restart dashboard

**Quick Restart:**
```bash
# Kill dashboard process
pkill -f streamlit

# Restart dashboard only
streamlit run frontend/dashboard.py --server.port 8501
```

**Backup Plan A: Alternative Browser**
- Have Chrome, Firefox, and Edge ready
- Switch to different browser if rendering issues
- **Recovery Time:** 5 seconds

**Backup Plan B: API Direct Access**
- Use FastAPI docs interface: `http://localhost:8000/docs`
- Demonstrate API functionality directly
- Show JSON responses
- **Script:** "Let me show you the underlying API that powers our dashboard"

**Backup Plan C: Static Dashboard Screenshots**
Location: `docs/demo_screenshots/dashboard/`
- `01_overview.png` - KPI metrics
- `02_alerts.png` - Fraud alerts
- `03_transactions.png` - Transaction table
- `04_route_map.png` - Route intelligence
- `05_network.png` - Company network
- `06_charts.png` - Price deviation charts

**Recovery Time:** 
- Restart: 20 seconds
- Alternative browser: 5 seconds
- Screenshots: 10 seconds

---

### Scenario 4: Network/Internet Failure

**Symptoms:**
- Cannot reach external APIs
- Gemini API unreachable
- Slow or no connectivity

**Immediate Actions (5 seconds):**
1. System automatically uses offline mode
2. All features work except live AI explanations
3. Continue demo normally

**Backup Plan A: Offline Mode (Pre-Configured)**
```python
# Already configured in backend/ai_explainer.py
# Automatically falls back to local explanations
# No action needed - system handles it
```

**Backup Plan B: Cached Data Demo**
- All transaction data is local
- ML model is local
- Visualizations work offline
- Only AI explanations affected

**What Still Works:**
- ✅ Dashboard loading
- ✅ Transaction browsing
- ✅ Fraud detection
- ✅ Risk scoring
- ✅ Visualizations
- ✅ Fallback explanations
- ❌ Live Gemini AI explanations

**Demo Script Adjustment:**
"Our system is designed for deployment in secure, air-gapped environments. All core fraud detection runs locally, with optional cloud AI enhancement when available."

**Recovery Time:** Immediate (automatic)

---

### Scenario 5: Data Loading Failure

**Symptoms:**
- "Dataset not found" errors
- "Failed to load dataset" messages
- Empty dashboard
- No transactions displayed

**Immediate Actions (20 seconds):**
1. Check if dataset file exists
2. Verify file path
3. Use backup dataset

**Quick Fix:**
```bash
# Verify dataset
ls -la data/trinetra_trade_fraud_dataset_1000_rows_complex.csv

# If missing, use backup
cp data/backup/trinetra_trade_fraud_dataset_1000_rows_complex.csv data/

# Restart system
python main.py
```

**Backup Plan A: Backup Dataset**
- Location: `data/backup/`
- Identical copy of main dataset
- **Recovery Time:** 30 seconds (copy + restart)

**Backup Plan B: Reduced Dataset**
- Location: `data/demo_dataset_100_rows.csv`
- Smaller dataset for quick loading
- Contains key demo transactions
- **Recovery Time:** 20 seconds

**Backup Plan C: Synthetic Data Generation**
```python
# Emergency data generation script
python scripts/generate_demo_data.py --rows 100 --output data/emergency_dataset.csv
```
**Recovery Time:** 45 seconds

---

### Scenario 6: Model Loading Failure

**Symptoms:**
- "Model not found" errors
- "Failed to load model" messages
- Scoring errors
- All transactions show same risk

**Immediate Actions (30 seconds):**
1. Delete corrupted model
2. System will retrain automatically
3. Or use backup model

**Quick Fix:**
```bash
# Option 1: Use backup model
cp models/backup/isolation_forest.pkl models/

# Option 2: Retrain (takes ~15 seconds)
rm models/isolation_forest.pkl
python main.py  # Will auto-retrain
```

**Backup Plan A: Pre-Trained Backup Model**
- Location: `models/backup/isolation_forest.pkl`
- Trained on full dataset
- Ready to use
- **Recovery Time:** 10 seconds

**Backup Plan B: Quick Retrain**
- System automatically retrains if model missing
- Takes 15-20 seconds
- **Action:** Continue talking while model trains

**Demo Script During Retrain:**
"Let me show you how quickly our system can train a new fraud detection model from scratch. This IsolationForest model is analyzing 1,000 transactions and learning fraud patterns in real-time..."

**Recovery Time:** 
- Backup model: 10 seconds
- Retrain: 20 seconds

---


## ⚡ Performance Issues

### Scenario 7: Slow Dashboard Loading

**Symptoms:**
- Dashboard takes >10 seconds to load
- Visualizations rendering slowly
- Laggy interactions
- Browser becomes unresponsive

**Immediate Actions (10 seconds):**
1. Close unnecessary browser tabs
2. Disable auto-refresh if enabled
3. Use pagination/filtering

**Backup Plan A: Demo Mode (Reduced Dataset)**
```python
# Before demo, set in main.py:
DEMO_MODE = True
SAMPLE_SIZE = 500  # Instead of 1000

# Restart with:
python main.py
```
**Recovery Time:** 30 seconds (restart with smaller dataset)

**Backup Plan B: Pre-Cached Views**
- Navigate to already-loaded sections
- Avoid triggering new data loads
- Use expanders sparingly
- **Recovery Time:** Immediate

**Backup Plan C: Simplified Demo Flow**
Skip heavy visualizations:
1. Show KPI metrics (fast)
2. Show transaction table (fast)
3. Show one fraud example (fast)
4. Skip network graph (slow)
5. Skip route map (slow)

**Demo Script:**
"For time efficiency, I'll focus on the core fraud detection features. The full visualization suite is available in the documentation."

**Recovery Time:** Immediate (adjust demo flow)

---

### Scenario 8: API Response Timeout

**Symptoms:**
- "Request timeout" errors
- Dashboard shows loading spinner indefinitely
- 504 Gateway Timeout errors

**Immediate Actions (5 seconds):**
1. Refresh the page
2. Try a different endpoint
3. Check API health

**Quick Check:**
```bash
# Test API health
curl http://localhost:8000/

# Test specific endpoint
curl http://localhost:8000/stats
```

**Backup Plan A: Restart API Only**
```bash
# Kill API process
pkill -f uvicorn

# Restart API
python -m uvicorn backend.api:app --host 0.0.0.0 --port 8000 &

# Wait 5 seconds
sleep 5

# Refresh dashboard
```
**Recovery Time:** 15 seconds

**Backup Plan B: Use Cached Data**
- Dashboard caches recent data
- Use cached views for demo
- Avoid triggering new API calls
- **Recovery Time:** Immediate

**Backup Plan C: Direct API Demo**
- Switch to FastAPI docs: `http://localhost:8000/docs`
- Demonstrate API directly
- Show JSON responses
- **Recovery Time:** 5 seconds

---

## 🔧 Pre-Demo Preparation Checklist

### 24 Hours Before Demo

```bash
# 1. Full system test
python main.py
# Verify both services start successfully

# 2. Create backup model
cp models/isolation_forest.pkl models/backup/

# 3. Create backup dataset
cp data/trinetra_trade_fraud_dataset_1000_rows_complex.csv data/backup/

# 4. Test all demo scenarios
# - Load dashboard
# - View all sections
# - Test AI explanations
# - Test visualizations

# 5. Generate demo materials
python scripts/generate_demo_screenshots.py
python scripts/generate_demo_explanations.py

# 6. Test on presentation laptop
# - Install all dependencies
# - Run full system
# - Test with projector connected

# 7. Prepare offline mode
# - Download all dependencies
# - Cache all data
# - Test without internet

# 8. Create backup instance
# Start on alternate ports
export API_PORT=8001
export STREAMLIT_PORT=8502
python main.py &
```

### 1 Hour Before Demo

```bash
# 1. System health check
python main.py
# Verify startup completes in <30 seconds

# 2. Clear caches
rm -rf ~/.streamlit/cache
rm -rf .hypothesis/

# 3. Close unnecessary applications
# - Close other browsers
# - Close heavy applications
# - Disable system updates

# 4. Test network connectivity
ping google.com
curl https://generativelanguage.googleapis.com

# 5. Verify demo transactions
# - TXN00006 (extreme fraud)
# - TXN00017 (high-risk company)
# - TXN00010 (multiple alerts)

# 6. Prepare backup materials
# - Open screenshots folder
# - Have demo video ready
# - Print quick reference card

# 7. Test Gemini API
python -c "from backend.ai_explainer import test_gemini_connection; test_gemini_connection()"

# 8. Start backup instance
# Keep running in background
```

### 5 Minutes Before Demo

```bash
# 1. Final system restart
pkill -f python
python main.py

# 2. Open all necessary tabs
# - Dashboard: http://localhost:8501
# - API Docs: http://localhost:8000/docs
# - Backup dashboard: http://localhost:8502

# 3. Verify services
curl http://localhost:8000/stats
curl http://localhost:8501/

# 4. Have backup materials ready
# - Screenshots folder open
# - Demo video ready to play
# - Quick reference card visible

# 5. Test one transaction explanation
# Click "Get AI Explanation" on TXN00006

# 6. Disable screen saver
# Prevent screen from sleeping during demo

# 7. Set browser zoom to 100%
# Ensure optimal visibility

# 8. Close notification popups
# Disable system notifications
```

---

## 📱 Emergency Contact Information

### During Demo Issues

**Technical Support (if available):**
- Name: [Team Member Name]
- Phone: [Phone Number]
- Role: Can restart systems remotely

**Backup Presenter:**
- Name: [Team Member Name]
- Role: Can take over if primary presenter has issues

### Post-Demo Recovery

**If demo fails completely:**
1. Acknowledge the issue professionally
2. Offer to show backup materials
3. Schedule follow-up demo
4. Provide documentation links

**Professional Response Script:**
"I apologize for the technical difficulty. Let me show you our comprehensive documentation and pre-recorded demo that showcases all features. I'd be happy to schedule a follow-up session where you can see the live system in action."

---

## 🎯 Demo Recovery Decision Tree

```
System Issue Detected
    ↓
Is it critical? (System won't work at all)
    ├─ YES → Use Backup Instance (Plan A)
    │         ↓
    │      Still failing?
    │         ├─ YES → Show Screenshots (Plan B)
    │         └─ NO → Continue demo
    │
    └─ NO → Is it Gemini API?
              ├─ YES → Use fallback explanations (automatic)
              │         ↓
              │      Continue demo normally
              │
              └─ NO → Is it performance?
                        ├─ YES → Simplify demo flow
                        │         ↓
                        │      Skip heavy visualizations
                        │
                        └─ NO → Is it visualization?
                                  ├─ YES → Use screenshots
                                  └─ NO → Restart component
```

---

## 📊 Backup Materials Inventory

### Required Files (Prepare Before Demo)

**1. Screenshots** (`docs/demo_screenshots/`)
```
dashboard/
├── 01_overview.png          # KPI metrics
├── 02_alerts.png            # Fraud alerts
├── 03_transactions.png      # Transaction table
├── 04_explanations.png      # AI explanations
├── 05_route_map.png         # Route intelligence
├── 06_network.png           # Company network
├── 07_price_chart.png       # Price deviation
└── 08_ai_assistant.png      # AI assistant

api/
├── 01_swagger_ui.png        # API documentation
├── 02_transactions_json.png # JSON response
└── 03_stats_json.png        # Statistics response
```

**2. Pre-Generated Explanations** (`docs/demo_explanations.json`)
```json
{
  "TXN00006": {
    "transaction_id": "TXN00006",
    "risk_category": "FRAUD",
    "explanation": "This crude oil transaction shows extreme price manipulation...",
    "key_indicators": ["Price deviation: -73%", "Below market value", "Transfer pricing fraud"]
  },
  "TXN00017": {
    "transaction_id": "TXN00017",
    "risk_category": "SUSPICIOUS",
    "explanation": "This wheat shipment involves a high-risk company...",
    "key_indicators": ["Company risk: 0.93", "Price inflation: +19%", "Invoice fraud"]
  }
}
```

**3. Demo Video** (`docs/demo_video.mp4`)
- Duration: 5 minutes
- Content: Full system walkthrough
- Quality: 1080p
- Format: MP4 (universally compatible)

**4. Backup Datasets**
```
data/
├── trinetra_trade_fraud_dataset_1000_rows_complex.csv  # Main
├── backup/
│   └── trinetra_trade_fraud_dataset_1000_rows_complex.csv  # Backup copy
├── demo_dataset_100_rows.csv                           # Quick load
└── emergency_dataset.csv                               # Generated on-demand
```

**5. Backup Models**
```
models/
├── isolation_forest.pkl        # Main model
└── backup/
    └── isolation_forest.pkl    # Backup copy
```

**6. Quick Reference Materials**
```
docs/
├── DEMO_BACKUP_PLANS.md        # This document
├── DEMO_QUICK_REFERENCE.md     # Quick demo guide
├── DEMO_SCENARIOS.md           # Demo scenarios
└── quick_reference_card.pdf    # Printable card
```

---

## 🎬 Demo Script Adaptations

### If Using Fallback Explanations

**Original Script:**
"Let me get an AI-powered explanation for this transaction using Google's Gemini API..."

**Adapted Script:**
"Our system provides intelligent fraud analysis using both AI and rule-based methods. Let me show you the analysis for this transaction..."

### If Using Screenshots

**Original Script:**
"Let me navigate to the dashboard and show you the live fraud detection..."

**Adapted Script:**
"Let me walk you through our fraud detection dashboard. Here you can see the real-time interface that analysts use..."

### If Using API Docs

**Original Script:**
"The dashboard provides an intuitive interface for investigators..."

**Adapted Script:**
"Let me show you the powerful API that drives our system. This RESTful API provides programmatic access to all fraud detection capabilities..."

### If System is Slow

**Original Script:**
"Let me show you all the visualizations including the route map and company network..."

**Adapted Script:**
"Let me focus on the core fraud detection features. The system includes additional visualizations for route analysis and company networks, which you can explore in detail later..."

---

## 🔍 Troubleshooting Quick Commands

### System Status Check
```bash
# Check if services are running
ps aux | grep python
ps aux | grep uvicorn
ps aux | grep streamlit

# Check ports
netstat -an | grep 8000
netstat -an | grep 8501

# Check logs
tail -n 20 logs/trinetra_main.log
```

### Quick Restart Commands
```bash
# Restart everything
pkill -f python && python main.py

# Restart API only
pkill -f uvicorn && python -m uvicorn backend.api:app --host 0.0.0.0 --port 8000 &

# Restart dashboard only
pkill -f streamlit && streamlit run frontend/dashboard.py --server.port 8501 &
```

### Emergency Recovery
```bash
# Nuclear option - complete reset
pkill -f python
rm models/isolation_forest.pkl
python main.py
```

---

## 📞 Support Resources

### Documentation Links (Share with Audience)
- **GitHub Repository**: [Your repo URL]
- **API Documentation**: `http://localhost:8000/docs`
- **User Guide**: `docs/USER_GUIDE.md`
- **Troubleshooting**: `TROUBLESHOOTING_GUIDE.md`

### Demo Materials (Share After Demo)
- **Demo Video**: [Upload to YouTube/Vimeo]
- **Screenshots**: [Upload to Google Drive/Dropbox]
- **Presentation Slides**: [Upload to SlideShare]

---

## ✅ Post-Demo Checklist

### Immediate (Within 5 minutes)
- [ ] Thank the audience
- [ ] Collect feedback
- [ ] Share documentation links
- [ ] Answer questions
- [ ] Exchange contact information

### Follow-Up (Within 24 hours)
- [ ] Send demo recording (if recorded)
- [ ] Share GitHub repository
- [ ] Send additional documentation
- [ ] Schedule follow-up meetings
- [ ] Document any issues encountered

### System Cleanup
- [ ] Stop all running processes
- [ ] Review logs for errors
- [ ] Document what worked/didn't work
- [ ] Update backup plans based on experience
- [ ] Prepare for next demo

---

## 🎓 Lessons Learned Template

After each demo, document:

**What Worked Well:**
- [List successful aspects]

**What Failed:**
- [List failures and causes]

**Recovery Actions Taken:**
- [List backup plans used]

**Improvements for Next Time:**
- [List improvements needed]

**Audience Feedback:**
- [List feedback received]

---

## 📝 Final Notes

### Key Principles for Demo Recovery

1. **Stay Calm**: Technical issues happen. Handle them professionally.

2. **Have Backups**: Always prepare multiple backup plans.

3. **Practice Recovery**: Test failure scenarios before the demo.

4. **Communicate Clearly**: Explain issues honestly and professionally.

5. **Keep Moving**: Don't spend too much time troubleshooting during demo.

6. **Know When to Switch**: If something isn't working, move to backup plan quickly.

7. **End Strong**: Even if there are issues, finish with confidence.

### Success Metrics

A successful demo recovery means:
- ✅ Audience still understands the system capabilities
- ✅ Key features are demonstrated (even if via backup materials)
- ✅ Professional image is maintained
- ✅ Follow-up opportunities are created
- ✅ Technical issues don't dominate the presentation

---

## 🚀 Remember

**"The best backup plan is the one you've practiced."**

Test all backup scenarios before the actual demo. Know your recovery procedures by heart. Have all backup materials ready and accessible.

**Good luck with your demo! 🎉**

---

**Document Version:** 1.0  
**Last Updated:** 2024  
**Maintained By:** TRINETRA AI Team

For additional support, see:
- [TROUBLESHOOTING_GUIDE.md](../TROUBLESHOOTING_GUIDE.md) - Comprehensive troubleshooting
- [DEMO_SCENARIOS.md](DEMO_SCENARIOS.md) - Demo scenarios and scripts
- [DEMO_QUICK_REFERENCE.md](DEMO_QUICK_REFERENCE.md) - Quick demo guide
- [USER_GUIDE.md](USER_GUIDE.md) - Complete user guide

