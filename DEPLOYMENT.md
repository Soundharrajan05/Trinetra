# TRINETRA AI - Deployment Guide

## Quick Start

### Windows (Batch)
```batch
# Setup (first time only)
setup.bat

# Run the application
run.bat
```

### Windows (PowerShell)
```powershell
# Setup (first time only)
.\setup.ps1

# Run the application
.\run.ps1
```

### Linux/Mac
```bash
# Setup (first time only)
chmod +x setup.sh run.sh cleanup.sh
./setup.sh

# Run the application
./run.sh
```

## Detailed Setup Instructions

### Prerequisites

1. **Python 3.8 or higher**
   - Windows: Download from [python.org](https://www.python.org/downloads/)
   - Linux: `sudo apt install python3 python3-venv python3-pip`
   - Mac: `brew install python3`

2. **Gemini API Key**
   - Get your free API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

3. **Dataset**
   - Ensure `trinetra_trade_fraud_dataset_1000_rows_complex.csv` is in the `data/` directory

### Step-by-Step Setup

#### 1. Clone or Extract the Project
```bash
cd trinetra-ai
```

#### 2. Run Setup Script

**Windows (Batch):**
```batch
setup.bat
```

**Windows (PowerShell):**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\setup.ps1
```

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

The setup script will:
- ✅ Check Python installation and version
- ✅ Create virtual environment (`trinetra_env`)
- ✅ Install all dependencies from `requirements.txt`
- ✅ Create `.env` file from template
- ✅ Create necessary directories (`models/`, `logs/`, `data/`)
- ✅ Verify installation

#### 3. Configure Environment Variables

Edit the `.env` file and add your Gemini API key:

```env
GEMINI_API_KEY=your_actual_api_key_here
```

You can also customize other settings:
- API host and port
- Model parameters
- Alert thresholds
- Dashboard settings

#### 4. Verify Dataset

Ensure the dataset file exists:
```
data/trinetra_trade_fraud_dataset_1000_rows_complex.csv
```

If missing, place your dataset in the `data/` directory.

### Running the Application

#### Windows (Batch)
```batch
run.bat
```

#### Windows (PowerShell)
```powershell
.\run.ps1
```

#### Linux/Mac
```bash
./run.sh
```

The run script will:
- ✅ Activate the virtual environment
- ✅ Check for `.env` file
- ✅ Check for dataset
- ✅ Start the TRINETRA AI system

### Accessing the Application

Once started, the system will display:

```
╔══════════════════════════════════════════════════════════════╗
║  ✅ TRINETRA AI System Successfully Started!                ║
║                                                              ║
║  🌐 API Server:    http://localhost:8000                    ║
║  📱 Dashboard:     http://localhost:8501                    ║
║                                                              ║
║  Press Ctrl+C to stop the system                            ║
╚══════════════════════════════════════════════════════════════╝
```

**Access Points:**
- **Dashboard**: Open browser to `http://localhost:8501`
- **API Documentation**: `http://localhost:8000/docs`
- **API Health Check**: `http://localhost:8000/`

### Stopping the Application

Press `Ctrl+C` in the terminal to gracefully shutdown both the API server and dashboard.

## Maintenance Scripts

### Cleanup

Remove virtual environment, models, logs, and cache files:

**Windows:**
```batch
cleanup.bat
```

**Linux/Mac:**
```bash
./cleanup.sh
```

This will remove:
- Virtual environment
- Generated model files (`.pkl`)
- Log files
- Python cache (`__pycache__`, `.pyc`)
- Test artifacts

**Note:** `.env` and data files are preserved.

### Reinstallation

If you need to reinstall:

```bash
# Clean everything
./cleanup.sh  # or cleanup.bat

# Setup again
./setup.sh    # or setup.bat

# Run
./run.sh      # or run.bat
```

## Troubleshooting

### Python Not Found

**Windows:**
- Ensure Python is installed and added to PATH
- Restart terminal after installation
- Try `py` instead of `python`

**Linux/Mac:**
- Install Python 3: `sudo apt install python3`
- Use `python3` instead of `python`

### Permission Denied (Linux/Mac)

Make scripts executable:
```bash
chmod +x setup.sh run.sh cleanup.sh
```

### PowerShell Execution Policy Error

Run PowerShell as Administrator:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Port Already in Use

If ports 8000 or 8501 are in use, edit `.env`:

```env
API_PORT=8001
STREAMLIT_PORT=8502
```

### Gemini API Errors

- Verify API key in `.env`
- Check internet connection
- System will use fallback explanations if API fails

### Dataset Not Found

Ensure dataset is at:
```
data/trinetra_trade_fraud_dataset_1000_rows_complex.csv
```

### Dependencies Installation Failed

Try manual installation:
```bash
# Activate environment
source trinetra_env/bin/activate  # Linux/Mac
# or
trinetra_env\Scripts\activate.bat  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Virtual Environment Activation Failed

**Windows PowerShell:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Linux/Mac:**
Ensure script has execute permissions:
```bash
chmod +x run.sh
```

## Manual Setup (Alternative)

If automated scripts don't work, follow these manual steps:

### 1. Create Virtual Environment
```bash
python -m venv trinetra_env
```

### 2. Activate Virtual Environment

**Windows (CMD):**
```batch
trinetra_env\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
trinetra_env\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
source trinetra_env/bin/activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Setup Environment
```bash
cp .env.example .env
# Edit .env and add your Gemini API key
```

### 5. Create Directories
```bash
mkdir -p models logs data
```

### 6. Run Application
```bash
python main.py
```

## Production Deployment

For production deployment beyond local development:

### Docker Deployment (Future)

```dockerfile
# Dockerfile example
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

### Cloud Deployment Options

1. **Streamlit Cloud** (Dashboard only)
   - Deploy dashboard to Streamlit Cloud
   - Point to separate API server

2. **Heroku/Railway** (Full stack)
   - Deploy both API and dashboard
   - Use environment variables for configuration

3. **AWS/GCP/Azure** (Enterprise)
   - Use container services (ECS, Cloud Run, AKS)
   - Add load balancing and auto-scaling
   - Use managed databases

### Environment Variables for Production

```env
ENVIRONMENT=production
DEBUG=false
API_HOST=0.0.0.0
ENABLE_CACHING=true
LOG_LEVEL=WARNING
```

## System Requirements

### Minimum Requirements
- **CPU**: 2 cores
- **RAM**: 4 GB
- **Disk**: 2 GB free space
- **OS**: Windows 10+, Ubuntu 20.04+, macOS 10.15+
- **Python**: 3.8+
- **Internet**: Required for Gemini API

### Recommended Requirements
- **CPU**: 4+ cores
- **RAM**: 8+ GB
- **Disk**: 5+ GB free space
- **Python**: 3.10+

## File Structure

```
trinetra-ai/
├── setup.bat              # Windows setup script
├── setup.ps1              # PowerShell setup script
├── setup.sh               # Linux/Mac setup script
├── run.bat                # Windows run script
├── run.ps1                # PowerShell run script
├── run.sh                 # Linux/Mac run script
├── cleanup.bat            # Windows cleanup script
├── cleanup.sh             # Linux/Mac cleanup script
├── main.py                # Application entry point
├── requirements.txt       # Python dependencies
├── .env.example           # Environment template
├── .env                   # Your configuration (created by setup)
├── backend/               # Backend modules
│   ├── api.py
│   ├── data_loader.py
│   ├── feature_engineering.py
│   ├── fraud_detection.py
│   ├── model.py
│   └── ai_explainer.py
├── frontend/              # Frontend dashboard
│   └── dashboard.py
├── data/                  # Dataset directory
│   └── trinetra_trade_fraud_dataset_1000_rows_complex.csv
├── models/                # Trained models (generated)
│   └── isolation_forest.pkl
├── logs/                  # Application logs (generated)
│   └── trinetra_main.log
└── trinetra_env/          # Virtual environment (generated)
```

## Support

For issues or questions:
1. Check this deployment guide
2. Review logs in `logs/trinetra_main.log`
3. Verify environment configuration in `.env`
4. Ensure all prerequisites are met

## License

TRINETRA AI - Trade Fraud Intelligence System
Developed for hackathon demonstration purposes.
