#!/usr/bin/env python3
"""
Ultra minimal HTML dashboard for TRINETRA AI
No Streamlit dependency - pure HTML/CSS/JavaScript
"""

import os
import json
import requests
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# API Configuration
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

app = FastAPI(title="TRINETRA AI Dashboard")

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TRINETRA AI - Trade Fraud Intelligence</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .metric-card {
            background: rgba(255, 255, 255, 0.15);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #4CAF50;
        }
        
        .metric-label {
            font-size: 0.9em;
            opacity: 0.8;
            margin-top: 5px;
        }
        
        .controls {
            margin-bottom: 20px;
            text-align: center;
        }
        
        .btn {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            margin: 5px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        
        .btn:hover {
            background: #45a049;
        }
        
        .btn.active {
            background: #2196F3;
        }
        
        .transactions {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }
        
        .transaction-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        
        .transaction-table th,
        .transaction-table td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .transaction-table th {
            background: rgba(255, 255, 255, 0.2);
            font-weight: bold;
        }
        
        .risk-fraud {
            color: #f44336;
            font-weight: bold;
        }
        
        .risk-suspicious {
            color: #ff9800;
            font-weight: bold;
        }
        
        .risk-safe {
            color: #4caf50;
            font-weight: bold;
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            font-size: 1.2em;
        }
        
        .error {
            background: #f44336;
            color: white;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ TRINETRA AI</h1>
            <p>Trade Fraud Intelligence System</p>
        </div>
        
        <div class="metrics" id="metrics">
            <div class="metric-card">
                <div class="metric-value" id="total-transactions">-</div>
                <div class="metric-label">Total Transactions</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="fraud-rate">-</div>
                <div class="metric-label">Fraud Rate</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="trade-value">-</div>
                <div class="metric-label">Total Trade Value</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="avg-risk">-</div>
                <div class="metric-label">Avg Risk Score</div>
            </div>
        </div>
        
        <div class="controls">
            <button class="btn active" onclick="loadTransactions('all')">All Transactions</button>
            <button class="btn" onclick="loadTransactions('suspicious')">Suspicious</button>
            <button class="btn" onclick="loadTransactions('fraud')">Fraud Cases</button>
        </div>
        
        <div class="transactions">
            <h2 id="table-title">All Transactions</h2>
            <div id="loading" class="loading">Loading...</div>
            <div id="error" class="error" style="display: none;"></div>
            <table class="transaction-table" id="transaction-table" style="display: none;">
                <thead>
                    <tr>
                        <th>Transaction ID</th>
                        <th>Product</th>
                        <th>Unit Price</th>
                        <th>Risk Score</th>
                        <th>Category</th>
                        <th>Trade Value</th>
                    </tr>
                </thead>
                <tbody id="transaction-body">
                </tbody>
            </table>
        </div>
    </div>

    <script>
        const API_BASE = '{api_base_url}';
        
        async function fetchData(endpoint) {
            try {
                const response = await fetch(`${API_BASE}${endpoint}`);
                const data = await response.json();
                return data;
            } catch (error) {
                console.error('API Error:', error);
                return { status: 'error', message: error.message };
            }
        }
        
        async function loadMetrics() {
            const stats = await fetchData('/stats');
            if (stats.status === 'success') {
                const data = stats.data;
                document.getElementById('total-transactions').textContent = data.total_transactions.toLocaleString();
                document.getElementById('fraud-rate').textContent = data.fraud_rate + '%';
                document.getElementById('trade-value').textContent = '$' + data.total_trade_value.toLocaleString();
                document.getElementById('avg-risk').textContent = data.avg_risk_score.toFixed(3);
            }
        }
        
        async function loadTransactions(type) {
            // Update button states
            document.querySelectorAll('.btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            // Show loading
            document.getElementById('loading').style.display = 'block';
            document.getElementById('error').style.display = 'none';
            document.getElementById('transaction-table').style.display = 'none';
            
            // Update title
            const titles = {
                'all': 'All Transactions',
                'suspicious': 'Suspicious Transactions', 
                'fraud': 'Fraud Cases'
            };
            document.getElementById('table-title').textContent = titles[type];
            
            // Fetch data
            let endpoint = '/transactions?limit=50';
            if (type === 'suspicious') endpoint = '/suspicious';
            if (type === 'fraud') endpoint = '/fraud';
            
            const response = await fetchData(endpoint);
            
            document.getElementById('loading').style.display = 'none';
            
            if (response.status === 'success') {
                let transactions = response.data;
                if (transactions.transactions) {
                    transactions = transactions.transactions;
                }
                
                displayTransactions(transactions);
            } else {
                document.getElementById('error').textContent = 'Failed to load transactions: ' + response.message;
                document.getElementById('error').style.display = 'block';
            }
        }
        
        function displayTransactions(transactions) {
            const tbody = document.getElementById('transaction-body');
            tbody.innerHTML = '';
            
            transactions.forEach(t => {
                const row = document.createElement('tr');
                const riskClass = `risk-${t.risk_category.toLowerCase()}`;
                
                row.innerHTML = `
                    <td>${t.transaction_id}</td>
                    <td>${t.product}</td>
                    <td>$${t.unit_price.toFixed(2)}</td>
                    <td>${t.risk_score.toFixed(3)}</td>
                    <td class="${riskClass}">${t.risk_category}</td>
                    <td>$${t.trade_value.toLocaleString()}</td>
                `;
                tbody.appendChild(row);
            });
            
            document.getElementById('transaction-table').style.display = 'table';
        }
        
        // Initialize dashboard
        async function init() {
            await loadMetrics();
            await loadTransactions('all');
        }
        
        // Start the dashboard
        init();
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Serve the HTML dashboard."""
    return HTML_TEMPLATE.format(api_base_url=API_BASE_URL)

@app.get("/health")
def health_check():
    """Health check for dashboard."""
    return {"status": "ok", "message": "TRINETRA AI Dashboard is running"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")