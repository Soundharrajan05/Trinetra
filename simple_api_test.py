#!/usr/bin/env python3
"""
Simple API test server to verify basic functionality
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Simple TRINETRA Test API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Simple API is working"}

@app.get("/test")
def test_endpoint():
    return {"status": "success", "data": {"test": "working"}, "message": "Test endpoint working"}

if __name__ == "__main__":
    print("Starting simple test API on port 8001...")
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")