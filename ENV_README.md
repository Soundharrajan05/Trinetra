# Environment Configuration

## Setup
1. Copy `.env.example` to `.env`
2. Replace `your_gemini_api_key_here` with your actual Gemini API key
3. Get API key from: https://makersuite.google.com/app/apikey

## Required Variables
- `GEMINI_API_KEY`: Google Gemini API key for AI explanations

## Usage
```python
from utils.config import config
api_key = config.GEMINI_API_KEY
```

## Security
- Never commit `.env` files to version control
- `.env` is already in `.gitignore`
- Use different keys for different environments