# Environment Configuration Guide

## Overview
TRINETRA AI uses environment variables for configuration management. This ensures sensitive information like API keys are not hardcoded in the source code.

## Quick Setup

### 1. Copy the Example File
```bash
cp .env.example .env
```

### 2. Configure Your API Key
Edit the `.env` file and replace `your_gemini_api_key_here` with your actual Gemini API key:

```bash
GEMINI_API_KEY=your_actual_api_key_here
```

### 3. Get Your Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key to your `.env` file

## Environment Variables Reference

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key for AI explanations | `AIzaSyC0jXIwaSAiPGuOFBXvN0ofK0rivEflShA` |

### Optional Variables

#### Application Configuration
| Variable | Description | Default |
|----------|-------------|---------|
| `API_HOST` | FastAPI backend host | `localhost` |
| `API_PORT` | FastAPI backend port | `8000` |
| `API_DEBUG` | Enable debug mode | `true` |
| `DASHBOARD_HOST` | Streamlit dashboard host | `localhost` |
| `DASHBOARD_PORT` | Streamlit dashboard port | `8501` |

#### Data Configuration
| Variable | Description | Default |
|----------|-------------|---------|
| `DATASET_PATH` | Path to the trade fraud dataset | `data/trinetra_trade_fraud_dataset_1000_rows_complex.csv` |
| `MODEL_PATH` | Path to save/load the ML model | `models/isolation_forest.pkl` |

#### ML Model Configuration
| Variable | Description | Default |
|----------|-------------|---------|
| `CONTAMINATION_RATE` | Expected fraud rate for IsolationForest | `0.1` |
| `N_ESTIMATORS` | Number of trees in IsolationForest | `100` |
| `RANDOM_STATE` | Random seed for reproducibility | `42` |
| `SAFE_THRESHOLD` | Risk score threshold for SAFE classification | `-0.2` |
| `FRAUD_THRESHOLD` | Risk score threshold for FRAUD classification | `0.2` |

#### Alert System Configuration
| Variable | Description | Default |
|----------|-------------|---------|
| `PRICE_DEVIATION_THRESHOLD` | Price deviation alert trigger | `0.5` |
| `COMPANY_RISK_THRESHOLD` | Company risk score alert trigger | `0.8` |
| `PORT_ACTIVITY_THRESHOLD` | Port activity index alert trigger | `1.5` |

#### API Configuration
| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_MODEL` | Gemini model to use | `gemini-pro` |
| `GEMINI_TIMEOUT` | API timeout in seconds | `10` |
| `GEMINI_MAX_RETRIES` | Maximum API retry attempts | `3` |

#### Logging Configuration
| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | `INFO` |
| `LOG_FILE` | Log file path | `trinetra.log` |

#### Security Configuration
| Variable | Description | Default |
|----------|-------------|---------|
| `CORS_ORIGINS` | Allowed CORS origins (comma-separated) | `*` |
| `CORS_METHODS` | Allowed CORS methods (comma-separated) | `*` |
| `CORS_HEADERS` | Allowed CORS headers (comma-separated) | `*` |

## Usage in Code

The system uses a centralized configuration class in `utils/config.py`:

```python
from utils.config import config

# Access configuration values
api_key = config.GEMINI_API_KEY
dataset_path = config.DATASET_PATH
fraud_threshold = config.FRAUD_THRESHOLD

# Validate required configuration
config.validate_required_config()
```

## Security Best Practices

1. **Never commit `.env` files** - They are already in `.gitignore`
2. **Use different `.env` files for different environments** (development, staging, production)
3. **Rotate API keys regularly**
4. **Use environment-specific values** for production deployments
5. **Validate configuration on startup** using `config.validate_required_config()`

## Troubleshooting

### Common Issues

1. **Missing API Key Error**
   ```
   ValueError: GEMINI_API_KEY is required but not set in environment variables
   ```
   **Solution**: Ensure your `.env` file exists and contains a valid `GEMINI_API_KEY`

2. **Dataset Not Found Error**
   ```
   FileNotFoundError: Dataset file not found: data/trinetra_trade_fraud_dataset_1000_rows_complex.csv
   ```
   **Solution**: Verify the dataset file exists at the specified path or update `DATASET_PATH`

3. **API Connection Issues**
   - Check your internet connection
   - Verify your API key is valid
   - Check if you've exceeded API rate limits

### Environment File Not Loading

If environment variables aren't being loaded:

1. Ensure `.env` file is in the project root directory
2. Check that `python-dotenv` is installed: `pip install python-dotenv`
3. Verify the `.env` f