# 🎯 TRINETRA AI - Demo Quick Reference Card

> **Print this card and keep it visible during your demo!**

---

## 🚨 EMERGENCY CONTACTS

| Issue | Immediate Action | Recovery Time |
|-------|------------------|---------------|
| **System Crash** | Switch to backup: `http://localhost:8502` | 10 sec |
| **Gemini API Fails** | Automatic fallback (no action needed) | 0 sec |
| **Dashboard Slow** | Skip heavy visualizations | 0 sec |
| **Network Down** | Continue (system works offline) | 0 sec |

---

## ⚡ QUICK RESTART COMMANDS

```bash
# Restart everything
pkill -f python && python main.py

# Restart API only  
pkill -f uvicorn && python -m uvicorn backend.api:app --port 8000 &

# Restart dashboard only
pkill -f streamlit && streamlit run frontend/dashboard.py &
```

---

## 🎬 DEMO FLOW (5 MINUTES)

1. **Overview** (30s) - Show KPIs: 1000 transactions, 11.7% fraud rate
2. **Fraud Case** (2m) - Investigate TXN00006: -73% price deviation
3. **AI Explanation** (1m) - Get Gemini explanation or fallback
4. **Visualizations** (1m) - Show route map and company network
5. **Q&A** (30s) - Use AI assistant for questions

---

## 🔑 KEY DEMO TRANSACTIONS

| ID | Type | Key Feature |
|----|------|-------------|
| **TXN00006** | FRAUD | -73% price deviation (crude oil) |
| **TXN00017** | SUSPICIOUS | High-risk company (0.93 score) |
| **TXN00010** | SUSPICIOUS | Multiple alerts (port congestion) |

---

## 💬 TALKING POINTS

- ✅ **11.7% fraud rate** detected across 1,000 transactions
- ✅ **AI-powered** explanations using Google Gemini
- ✅ **Real-time detection** with IsolationForest ML
- ✅ **Multi-factor scoring**: price, route, company, port
- ✅ **Interactive visualizations** for pattern analysis
- ✅ **RESTful API** for system integration

---

## 🛡️ BACKUP MATERIALS LOCATIONS

- **Screenshots**: `docs/demo_screenshots/`
- **Explanations**: `docs/demo_explanations.json`
- **Video**: `docs/demo_video.mp4`
- **Backup Instance**: `http://localhost:8502`

---

## 🔧 PRE-DEMO CHECKLIST

- [ ] Start main system: `python main.py`
- [ ] Start backup instance on port 8502
- [ ] Test Gemini API (get one explanation)
- [ ] Open backup materials folder
- [ ] Close unnecessary applications
- [ ] Disable system notifications
- [ ] Test with projector connected

---

## 📞 IF EVERYTHING FAILS

1. **Stay calm** - Technical issues happen
2. **Use screenshots** - Walk through static images
3. **Show API docs** - `http://localhost:8000/docs`
4. **Play video** - `docs/demo_video.mp4`
5. **Offer follow-up** - Schedule live demo later

---

## 🎓 PROFESSIONAL RESPONSES

**If Gemini fails:**
> "Our system includes intelligent fallback analysis that works even without external AI APIs, ensuring continuous operation in any environment."

**If system is slow:**
> "For time efficiency, I'll focus on the core fraud detection features. The full visualization suite is available in the documentation."

**If complete failure:**
> "I apologize for the technical difficulty. Let me show you our comprehensive documentation and pre-recorded demo. I'd be happy to schedule a follow-up session."

---

## ✅ SUCCESS METRICS

- ✅ Audience understands system capabilities
- ✅ Key features demonstrated (even via backups)
- ✅ Professional image maintained
- ✅ Follow-up opportunities created
- ✅ Technical issues don't dominate

---

**Remember: The best backup plan is the one you've practiced!**

**Good luck! 🚀**
