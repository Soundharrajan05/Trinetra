# TRINETRA AI - Deployment Resources Index

## Quick Navigation

### 🚀 Getting Started
- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 3 steps
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Comprehensive deployment guide
- **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - Pre/post deployment checklist

### 📜 Scripts Documentation
- **[DEPLOYMENT_SCRIPTS_README.md](DEPLOYMENT_SCRIPTS_README.md)** - Detailed scripts documentation

### 🔧 Setup Scripts
| Platform | Script | Description |
|----------|--------|-------------|
| Windows CMD | `setup.bat` | Batch setup script |
| Windows PowerShell | `setup.ps1` | PowerShell setup script |
| Linux/Mac | `setup.sh` | Bash setup script |

### ▶️ Run Scripts
| Platform | Script | Description |
|----------|--------|-------------|
| Windows CMD | `run.bat` | Batch run script |
| Windows PowerShell | `run.ps1` | PowerShell run script |
| Linux/Mac | `run.sh` | Bash run script |

### 🧹 Cleanup Scripts
| Platform | Script | Description |
|----------|--------|-------------|
| Windows | `cleanup.bat` | Remove generated files |
| Linux/Mac | `cleanup.sh` | Remove generated files |

### ✅ Validation
| Script | Description |
|--------|-------------|
| `validate_deployment.py` | Cross-platform deployment validator |

## Quick Commands

### First Time Setup

**Windows (Command Prompt):**
```batch
setup.bat
# Edit .env file
python validate_deployment.py
run.bat
```

**Windows (PowerShell):**
```powershell
.\setup.ps1
# Edit .env file
python validate_deployment.py
.\run.ps1
```

**Linux/Mac:**
```bash
chmod +x *.sh
./setup.sh
# Edit .env file
python validate_deployment.py
./run.sh
```

### Regular Use

**Windows:**
```batch
run.bat
```

**Linux/Mac:**
```bash
./run.sh
```

### Cleanup

**Windows:**
```batch
cleanup.bat
```

**Linux/Mac:**
```bash
./cleanup.sh
```

## Documentation Structure

```
Deployment Documentation
│
├── QUICKSTART.md                    # 3-step quick start
├── DEPLOYMENT.md                    # Comprehensive guide
├── DEPLOYMENT_CHECKLIST.md          # Checklists
├── DEPLOYMENT_SCRIPTS_README.md     # Scripts documentation
├── DEPLOYMENT_INDEX.md              # This file
│
├── Setup Scripts
│   ├── setup.bat                    # Windows batch
│   ├── setup.ps1                    # Windows PowerShell
│   └── setup.sh                     # Linux/Mac bash
│
├── Run Scripts
│   ├── run.bat                      # Windows batch
│   ├── run.ps1                      # Windows PowerShell
│   └── run.sh                       # Linux/Mac bash
│
├── Cleanup Scripts
│   ├── cleanup.bat                  # Windows
│   └── cleanup.sh                   # Linux/Mac
│
└── Validation
    └── validate_deployment.py       # Cross-platform validator
```

## Common Tasks

### Task: First Time Setup
1. Read: [QUICKSTART.md](QUICKSTART.md)
2. Run: `setup.bat` or `./setup.sh`
3. Edit: `.env` file
4. Validate: `python validate_deployment.py`
5. Run: `run.bat` or `./run.sh`

### Task: Daily Use
1. Run: `run.bat` or `./run.sh`
2. Access: http://localhost:8501

### Task: Troubleshooting
1. Check: `logs/trinetra_main.log`
2. Validate: `python validate_deployment.py`
3. Read: [DEPLOYMENT.md](DEPLOYMENT.md) troubleshooting section

### Task: Clean Reinstall
1. Run: `cleanup.bat` or `./cleanup.sh`
2. Run: `setup.bat` or `./setup.sh`
3. Configure: Edit `.env`
4. Run: `run.bat` or `./run.sh`

### Task: Hackathon Demo Prep
1. Follow: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
2. Validate: `python validate_deployment.py`
3. Test: Run and verify all features
4. Prepare: Sample queries and transactions

## Prerequisites

- **Python**: 3.8 or higher
- **Gemini API Key**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
- **Dataset**: `trinetra_trade_fraud_dataset_1000_rows_complex.csv` in `data/` directory

## System Access Points

After successful deployment:

- **Dashboard**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **API Health**: http://localhost:8000/

## Support Resources

### Documentation
- [README.md](README.md) - Main project documentation
- [USER_GUIDE.md](USER_GUIDE.md) - User guide
- [TROUBLESHOOTING_GUIDE.md](TROUBLESHOOTING_GUIDE.md) - Troubleshooting
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - API reference

### Logs
- `logs/trinetra_main.log` - Main application log
- Console output - Real-time status

### Configuration
- `.env` - Environment configuration
- `.env.example` - Configuration template
- `requirements.txt` - Python dependencies

## Platform-Specific Notes

### Windows
- Use Command Prompt or PowerShell
- PowerShell may require execution policy change
- Batch scripts work in CMD

### Linux
- Make scripts executable: `chmod +x *.sh`
- Use `python3` if `python` not available
- May need `python3-venv` package

### Mac
- Similar to Linux
- Use Terminal
- May need Xcode Command Line Tools

## Version Information

- **Scripts Version**: 1.0
- **Python Required**: 3.8+
- **Last Updated**: 2024

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ TRINETRA AI - Quick Reference                           │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ SETUP (First Time):                                     │
│   Windows:  setup.bat                                   │
│   Linux:    ./setup.sh                                  │
│                                                          │
│ CONFIGURE:                                              │
│   Edit .env and add GEMINI_API_KEY                      │
│                                                          │
│ VALIDATE:                                               │
│   python validate_deployment.py                         │
│                                                          │
│ RUN:                                                    │
│   Windows:  run.bat                                     │
│   Linux:    ./run.sh                                    │
│                                                          │
│ ACCESS:                                                 │
│   Dashboard: http://localhost:8501                      │
│   API Docs:  http://localhost:8000/docs                 │
│                                                          │
│ STOP:                                                   │
│   Press Ctrl+C                                          │
│                                                          │
│ CLEANUP:                                                │
│   Windows:  cleanup.bat                                 │
│   Linux:    ./cleanup.sh                                │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

**Need Help?** Start with [QUICKSTART.md](QUICKSTART.md) or [DEPLOYMENT.md](DEPLOYMENT.md)
