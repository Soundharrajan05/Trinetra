# TRINETRA AI - Deployment Checklist

## Pre-Deployment Checklist

### Environment Setup
- [ ] Python 3.8+ installed
- [ ] Python added to system PATH
- [ ] Terminal/Command Prompt has Python access
- [ ] Internet connection available

### Project Files
- [ ] All project files extracted/cloned
- [ ] Dataset file in `data/` directory
- [ ] `requirements.txt` present
- [ ] `.env.example` present

### API Configuration
- [ ] Gemini API key obtained from Google AI Studio
- [ ] API key ready to paste into `.env`

## Deployment Steps

### 1. Initial Setup
- [ ] Run setup script (`setup.bat` or `./setup.sh`)
- [ ] Virtual environment created successfully
- [ ] All dependencies installed without errors
- [ ] `.env` file created from template
- [ ] Directories created (`models/`, `logs/`, `data/`)

### 2. Configuration
- [ ] Edit `.env` file
- [ ] Add Gemini API key to `GEMINI_API_KEY`
- [ ] Verify dataset path in `.env` (if changed)
- [ ] Review and adjust other settings (optional)

### 3. Dataset Verification
- [ ] Dataset file exists at correct path
- [ ] File name matches: `trinetra_trade_fraud_dataset_1000_rows_complex.csv`
- [ ] File is readable and not corrupted
- [ ] File size is reasonable (~1000 rows)

### 4. First Run
- [ ] Run application script (`run.bat` or `./run.sh`)
- [ ] Virtual environment activates successfully
- [ ] Dataset loads without errors
- [ ] Features engineered successfully
- [ ] Model trains or loads successfully
- [ ] FastAPI server starts on port 8000
- [ ] Streamlit dashboard starts on port 8501
- [ ] No critical errors in console output

### 5. Verification
- [ ] Open browser to `http://localhost:8501`
- [ ] Dashboard loads successfully
- [ ] Data displays in dashboard
- [ ] Charts and visualizations render
- [ ] API accessible at `http://localhost:8000/docs`
- [ ] API endpoints respond correctly

### 6. Functionality Testing
- [ ] Dashboard shows transaction data
- [ ] Fraud detection scores visible
- [ ] Risk categories displayed (SAFE, SUSPICIOUS, FRAUD)
- [ ] Charts are interactive
- [ ] AI explanations work (or fallback active)
- [ ] Alerts display for high-risk transactions

## Post-Deployment Checklist

### System Health
- [ ] Check logs at `logs/trinetra_main.log`
- [ ] No critical errors in logs
- [ ] Both processes running (API + Dashboard)
- [ ] Memory usage acceptable
- [ ] CPU usage reasonable

### Performance
- [ ] Dashboard loads within 5 seconds
- [ ] API responses within 2 seconds
- [ ] Charts render smoothly
- [ ] No lag when interacting with UI

### Data Integrity
- [ ] Transaction count matches dataset
- [ ] Risk scores calculated for all transactions
- [ ] Risk categories assigned correctly
- [ ] No missing or null critical values

### AI Integration
- [ ] Gemini API responding (if configured)
- [ ] Explanations generating successfully
- [ ] Fallback system working (if API fails)
- [ ] No API rate limit errors

## Hackathon Demo Checklist

### Before Demo
- [ ] System fully started and warmed up
- [ ] Dashboard open in browser
- [ ] Sample transactions identified for demo
- [ ] High-risk cases ready to showcase
- [ ] AI explanations tested and working
- [ ] Backup plan if internet fails (fallback mode)

### Demo Preparation
- [ ] Browser zoom level appropriate for projection
- [ ] Dashboard in full-screen mode
- [ ] Logs hidden or minimized
- [ ] Sample queries prepared for AI assistant
- [ ] Key features list ready to demonstrate

### Key Features to Demonstrate
- [ ] Global trade overview KPIs
- [ ] Fraud detection in action
- [ ] Risk scoring and classification
- [ ] Interactive visualizations
- [ ] Route intelligence map
- [ ] Price deviation analysis
- [ ] AI-powered explanations
- [ ] Alert system
- [ ] Natural language queries

### Backup Plans
- [ ] Screenshots of working system
- [ ] Pre-recorded demo video (optional)
- [ ] Fallback explanations if API fails
- [ ] Local dataset backup
- [ ] Alternative port numbers if conflicts

## Troubleshooting Checklist

### If Setup Fails
- [ ] Check Python version: `python --version`
- [ ] Check pip installation: `pip --version`
- [ ] Try manual virtual environment creation
- [ ] Check internet connection for downloads
- [ ] Review error messages in console

### If Run Fails
- [ ] Verify virtual environment exists
- [ ] Check `.env` file exists and configured
- [ ] Verify dataset file present
- [ ] Check ports 8000 and 8501 available
- [ ] Review logs for specific errors

### If Dashboard Won't Load
- [ ] Check Streamlit process running
- [ ] Verify port 8501 not blocked by firewall
- [ ] Try different browser
- [ ] Clear browser cache
- [ ] Check console for JavaScript errors

### If API Fails
- [ ] Check FastAPI process running
- [ ] Verify port 8000 accessible
- [ ] Test with curl or Postman
- [ ] Check API logs
- [ ] Verify dataset loaded correctly

### If AI Explanations Fail
- [ ] Verify Gemini API key in `.env`
- [ ] Check internet connection
- [ ] Verify API key is valid
- [ ] Check for rate limiting
- [ ] Confirm fallback system activates

## Cleanup Checklist

### After Demo/Testing
- [ ] Stop application (Ctrl+C)
- [ ] Verify both processes stopped
- [ ] Review logs for any issues
- [ ] Backup any important logs
- [ ] Note any bugs or improvements

### Full Cleanup (Optional)
- [ ] Run cleanup script (`cleanup.bat` or `./cleanup.sh`)
- [ ] Verify virtual environment removed
- [ ] Verify model files removed
- [ ] Verify log files removed
- [ ] Verify cache files removed
- [ ] `.env` and data preserved

## Maintenance Checklist

### Regular Maintenance
- [ ] Update dependencies periodically
- [ ] Review and rotate logs
- [ ] Clean up old model files
- [ ] Update dataset if needed
- [ ] Test with latest Python version

### Before Each Use
- [ ] Verify dataset is current
- [ ] Check API key still valid
- [ ] Update dependencies if needed
- [ ] Clear old logs if disk space low
- [ ] Test system startup

## Security Checklist

### API Key Security
- [ ] API key in `.env` file only
- [ ] `.env` in `.gitignore`
- [ ] Never commit API key to version control
- [ ] Use environment variables in production
- [ ] Rotate API key periodically

### Data Security
- [ ] Dataset contains no real PII
- [ ] Logs don't expose sensitive data
- [ ] API endpoints don't leak information
- [ ] Error messages are generic

## Documentation Checklist

### User Documentation
- [ ] README.md complete
- [ ] DEPLOYMENT.md detailed
- [ ] QUICKSTART.md concise
- [ ] API documentation accessible
- [ ] Code comments present

### Technical Documentation
- [ ] Architecture documented
- [ ] Dependencies listed
- [ ] Configuration options explained
- [ ] Troubleshooting guide complete
- [ ] Known issues documented

## Success Criteria

### System is Ready When:
- ✅ All setup steps completed without errors
- ✅ Dashboard accessible and functional
- ✅ API responding to requests
- ✅ Data loaded and processed correctly
- ✅ Fraud detection working
- ✅ Visualizations rendering
- ✅ AI explanations generating (or fallback active)
- ✅ No critical errors in logs
- ✅ Performance is acceptable
- ✅ Ready for demonstration

---

**Last Updated:** Check this list before each deployment or demo!
