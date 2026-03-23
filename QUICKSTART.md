# TRINETRA AI - Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Setup (First Time Only)

**Windows:**
```batch
setup.bat
```

**Linux/Mac:**
```bash
chmod +x *.sh
./setup.sh
```

### Step 2: Configure API Key

Edit `.env` file and add your Gemini API key:
```env
GEMINI_API_KEY=your_api_key_here
```

Get your free API key: https://makersuite.google.com/app/apikey

### Step 3: Run

**Windows:**
```batch
run.bat
```

**Linux/Mac:**
```bash
./run.sh
```

## 🎯 Access the Dashboard

Open your browser to: **http://localhost:8501**

API Documentation: **http://localhost:8000/docs**

## 🛑 Stop the System

Press `Ctrl+C` in the terminal

## 📋 Prerequisites

- Python 3.8 or higher
- Gemini API key (free)
- Dataset in `data/` directory

## 🔧 Troubleshooting

**Python not found?**
- Install from https://www.python.org/downloads/

**Port already in use?**
- Edit `.env` and change `API_PORT` or `STREAMLIT_PORT`

**Permission denied (Linux/Mac)?**
```bash
chmod +x setup.sh run.sh cleanup.sh
```

## 📚 Full Documentation

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

## 🧹 Cleanup

To remove virtual environment and generated files:

**Windows:**
```batch
cleanup.bat
```

**Linux/Mac:**
```bash
./cleanup.sh
```

---

**Need Help?** Check the logs at `logs/trinetra_main.log`
