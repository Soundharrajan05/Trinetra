# TRINETRA AI - Investigation Scenarios for Demo

## Overview
This document provides realistic fraud investigation scenarios for demonstrating TRINETRA AI's capabilities during the hackathon presentation. Each scenario showcases different fraud detection features and the AI Investigation Assistant.

---

## Scenario 1: Price Manipulation - Aluminum Over-Invoicing

### Background
**Transaction ID:** TXN00027  
**Date:** April 27, 2024  
**Product:** Aluminum (HS Code: 760110)  
**Exporter:** AgriGrain (USA) → **Importer:** JiangsuCopper (China)  
**Route:** Houston → Shanghai (via Valparaiso)

### Fraud Indicators
- **Price Deviation:** +233.49% (Market: $2,400/ton, Trade: $8,003.86/ton)
- **Trade Value:** $18,552,947.48 for 2,318 tons
- **Company Risk Score:** 0.56 (Moderate)
- **Port Activity Index:** 1.32 (Elevated)

### Investigation Flow

#### Step 1: Initial Detection
**Investigator Action:** Review suspicious transactions table in dashboard  
**System Response:** Transaction TXN00027 flagged as FRAUD with high risk score

#### Step 2: AI Explanation Request
**Investigator Query:** "Why is transaction TXN00027 suspicious?"

**Expected AI Response:**
```
Transaction TXN00027 exhibits severe price manipulation. The aluminum is being 
traded at $8,003.86 per ton, which is 233% above the market price of $2,400. 
This extreme over-invoicing suggests potential money laundering or customs duty 
evasion. The exporter AgriGrain is primarily an agricultural company, making 
aluminum exports unusual. The elevated port activity index (1.32) and moderate 
company risk score (0.56) add to the suspicion.
```

#### Step 3: Deep Investigation
**Investigator Queries:**
1. "What is AgriGrain's typical export profile?"
2. "Has JiangsuCopper received similar over-priced shipments?"
3. "Show me other aluminum transactions from Houston to Shanghai"

**Expected Insights:**
- AgriGrain typically exports wheat and agricultural products, not metals
- Pattern of over-invoiced metal shipments to China detected
- Potential trade-based money laundering scheme

### Demo Talking Points
- Highlight the 233% price deviation visualization on the Price Deviation Chart
- Show how the AI explains complex fraud patterns in natural language
- Demonstrate the company risk network showing unusual trading relationships
- Emphasize real-time alert generation for extreme price anomalies

---

## Scenario 2: Under-Invoicing - Crude Oil Price Suppression

### Background
**Transaction ID:** TXN00006  
**Date:** March 4, 2024  
**Product:** Crude Oil (HS Code: 270900)  
**Exporter:** AusMetal (Australia) → **Importer:** NipponAlloys (Japan)  
**Route:** Perth → Yokohama (via Houston-Alexandria - anomalous route)

### Fraud Indicators
- **Price Deviation:** -73.12% (Market: $75/ton, Trade: $20.16/ton)
- **Trade Value:** Only $58,766.40 for 2,915 tons
- **Company Risk Score:** 0.07 (Very Low - suspicious for fraud case)
- **Port Activity Index:** 1.75 (High congestion)
- **Shipment Duration:** 34 days (unusually long)

### Investigation Flow

#### Step 1: Alert Trigger
**System Alert:** "CRITICAL: Severe under-invoicing detected - 73% below market price"

#### Step 2: Route Analysis
**Investigator Action:** Click on transaction in Route Intelligence Map  
**Observation:** Route goes Perth → Houston → Alexandria → Yokohama (highly inefficient)

**Investigator Query:** "Why would crude oil from Australia to Japan go through Houston and Alexandria?"

**Expected AI Response:**
```
This routing is highly suspicious. A direct Perth-Yokohama route would be 
approximately 7,800 km, but this shipment traveled 11,500 km through Houston 
and Alexandria. Combined with the 73% price under-invoicing ($20.16 vs $75 
market price), this suggests customs duty evasion. The cargo may have been 
partially offloaded or substituted during the unusual route. The 34-day 
shipment duration is excessive for this distance.
```

#### Step 3: Company Profile Investigation
**Investigator Query:** "What is unusual about AusMetal exporting crude oil?"

**Expected Insight:**
- AusMetal is primarily a metals company (name suggests metal focus)
- Crude oil exports are outside their typical commodity category
- Low company risk score (0.07) may indicate a shell company or front

### Demo Talking Points
- Show the Route Intelligence Map with the anomalous routing highlighted
- Demonstrate how multiple fraud indicators combine (price + route + duration)
- Explain how under-invoicing reduces customs duties and tax obligations
- Highlight the AI's ability to connect disparate fraud signals

---

## Scenario 3: Steel Under-Invoicing with Route Anomaly

### Background
**Transaction ID:** TXN00032  
**Date:** June 6, 2024  
**Product:** Steel (HS Code: 720712)  
**Exporter:** PetroGlobal (UAE) → **Importer:** BharatMetals (India)  
**Route:** Dubai → Chennai (via Valparaiso-Shanghai - highly anomalous)

### Fraud Indicators
- **Price Deviation:** -59.31% (Market: $520/ton, Trade: $211.58/ton)
- **Quantity:** 3,949 tons (large shipment)
- **Company Risk Score:** 0.59 (Moderate-High)
- **Trade Frequency:** 24 transactions in 30 days (very high)
- **Shipment Duration:** 31 days for 17,000 km route

### Investigation Flow

#### Step 1: Pattern Recognition
**Investigator Action:** Filter transactions by PetroGlobal and BharatMetals  
**Finding:** Multiple under-invoiced steel shipments in past 30 days

**Investigator Query:** "Show me all transactions between PetroGlobal and BharatMetals in the last month"

**Expected AI Response:**
```
PetroGlobal and BharatMetals have conducted 24 transactions in the past 30 days, 
which is unusually high frequency. Multiple shipments show significant under-
invoicing of steel products. This pattern suggests an organized scheme to evade 
customs duties through systematic price manipulation. The companies may have a 
collusive relationship to defraud customs authorities.
```

#### Step 2: Route Analysis
**Investigator Query:** "Why would steel from Dubai to Chennai go through Valparaiso and Shanghai?"

**Expected AI Response:**
```
The routing from Dubai to Chennai via Valparaiso (Chile) and Shanghai (China) 
is geographically illogical. A direct Dubai-Chennai route would be approximately 
3,000 km, but this shipment traveled 17,000 km. This extreme detour, combined 
with 59% under-invoicing, suggests the cargo may have been altered, substituted, 
or partially diverted during transit. The 31-day duration is excessive for what 
should be a 5-7 day direct voyage.
```

#### Step 3: Network Analysis
**Investigator Action:** View Company Risk Network graph  
**Observation:** PetroGlobal has connections to multiple high-risk importers

### Demo Talking Points
- Demonstrate pattern detection across multiple transactions
- Show the trade frequency indicator (24 transactions in 30 days)
- Highlight the Company Risk Network visualization showing suspicious relationships
- Explain how systematic fraud differs from one-off anomalies

---

## Scenario 4: Port Congestion Exploitation

### Background
**Transaction ID:** TXN00055  
**Date:** April 7, 2024  
**Product:** Crude Oil (HS Code: 270900)  
**Exporter:** PetroGlobal (UAE) → **Importer:** BharatMetals (India)  
**Route:** Dubai → Hamburg (incorrect destination for India-bound cargo)

### Fraud Indicators
- **Price Deviation:** -60.77% (Market: $75/ton, Trade: $29.42/ton)
- **Port Activity Index:** 1.19 (Elevated)
- **Company Risk Score:** 0.90 (Very High)
- **Port Calls:** 7 (multiple stops)
- **Cargo Volume:** 108,192 (large volume)

### Investigation Flow

#### Step 1: Destination Mismatch
**Investigator Observation:** Importer is BharatMetals (India) but import port is Hamburg (Germany)

**Investigator Query:** "Why is an Indian company importing crude oil through Hamburg?"

**Expected AI Response:**
```
This transaction shows a destination mismatch. BharatMetals is an Indian company, 
but the crude oil is being imported through Hamburg, Germany. Combined with 61% 
under-invoicing and a very high company risk score (0.90), this suggests potential 
cargo diversion or triangulation fraud. The oil may be re-exported to India to 
obscure its origin or avoid sanctions. The 7 port calls indicate multiple stops 
that could facilitate cargo manipulation.
```

#### Step 2: Port Congestion Analysis
**Investigator Query:** "How does port congestion relate to this fraud?"

**Expected AI Response:**
```
Elevated port activity (index 1.19) creates opportunities for fraud. During 
congestion, customs inspections may be rushed or less thorough. Fraudsters 
exploit these conditions to move suspicious cargo with reduced scrutiny. The 
multiple port calls (7 stops) during high activity periods suggest deliberate 
exploitation of overwhelmed port authorities.
```

#### Step 3: Company Risk Assessment
**Investigator Action:** Click on BharatMetals in Company Risk Network  
**Finding:** Company risk score of 0.90 indicates history of suspicious activity

### Demo Talking Points
- Show how port activity index correlates with fraud risk
- Demonstrate the alert system triggering on multiple criteria
- Explain real-world fraud tactics exploiting port congestion
- Highlight the importance of company risk scoring

---

## Scenario 5: Complex Multi-Factor Fraud Investigation

### Background
**Transaction ID:** TXN00062  
**Date:** March 3, 2024  
**Product:** Crude Oil (HS Code: 270900)  
**Exporter:** PetroGlobal (UAE) → **Importer:** BharatMetals (India)  
**Route:** Shanghai → Dubai → Turkey → Chennai (highly complex route)

### Fraud Indicators
- **Price Deviation:** -71.11% (Market: $75/ton, Trade: $21.67/ton)
- **Route Anomaly:** 1 (flagged as anomalous)
- **Company Risk Score:** 0.41 (Moderate)
- **Port Activity Index:** 1.54 (High)
- **Distance:** 9,100 km (circuitous route)
- **Shipment Duration:** 14 days

### Investigation Flow

#### Step 1: Comprehensive Analysis Request
**Investigator Query:** "Give me a complete fraud analysis for transaction TXN00062"

**Expected AI Response:**
```
Transaction TXN00062 exhibits multiple fraud indicators:

1. PRICE MANIPULATION: Crude oil priced at $21.67/ton, 71% below market ($75/ton)
2. ROUTE ANOMALY: Flagged route from Shanghai→Dubai→Turkey→Chennai is illogical 
   for UAE-to-India trade
3. PORT CONGESTION: High port activity index (1.54) suggests exploitation of 
   overwhelmed customs
4. COMPANY RISK: PetroGlobal and BharatMetals have moderate risk scores and 
   frequent suspicious transactions

This appears to be a sophisticated trade-based money laundering operation using 
under-invoicing, route obfuscation, and port congestion exploitation to move 
funds while evading customs duties.
```

#### Step 2: Comparative Analysis
**Investigator Query:** "Compare this to other crude oil transactions from UAE to India"

**Expected AI Response:**
```
Legitimate UAE-to-India crude oil transactions typically:
- Price within ±10% of market value ($67-$83/ton)
- Use direct Dubai-Chennai route (~3,000 km)
- Complete in 5-7 days
- Have route_anomaly = 0

Transaction TXN00062 deviates significantly on all parameters, confirming fraud.
```

#### Step 3: Recommendation
**Investigator Query:** "What action should be taken?"

**Expected AI Response:**
```
RECOMMENDED ACTIONS:
1. IMMEDIATE: Flag shipment for physical inspection at Chennai port
2. Investigate PetroGlobal and BharatMetals for systematic fraud
3. Review all transactions between these entities in past 90 days
4. Coordinate with customs authorities in Dubai, Turkey, and Chennai
5. Consider sanctions or enhanced monitoring for both companies
```

### Demo Talking Points
- Demonstrate the AI's ability to synthesize multiple fraud signals
- Show how the system provides actionable recommendations
- Highlight the investigation workflow from detection to action
- Emphasize the value of AI-powered explanations for complex cases

---

## Quick Demo Queries for AI Investigation Assistant

### General Queries
1. "What are the most common fraud patterns in the dataset?"
2. "Which companies have the highest risk scores?"
3. "Show me all transactions with price deviations above 50%"
4. "What percentage of transactions are flagged as fraud?"

### Product-Specific Queries
5. "Are aluminum transactions more likely to be fraudulent than steel?"
6. "What is the average price deviation for crude oil shipments?"
7. "Which commodity category has the most fraud cases?"

### Geographic Queries
8. "Which shipping routes have the most anomalies?"
9. "Are transactions from UAE more suspicious than other countries?"
10. "What is the fraud rate for shipments to China vs India?"

### Company Analysis Queries
11. "Tell me about PetroGlobal's transaction history"
12. "Which exporter-importer pairs have the most suspicious activity?"
13. "How many companies have risk scores above 0.8?"

### Temporal Queries
14. "Has fraud increased or decreased over the past 6 months?"
15. "Which month had the highest fraud rate?"
16. "Show me recent high-value fraudulent transactions"

---

## Demo Presentation Flow

### Opening (2 minutes)
1. **Introduction:** "TRINETRA AI detects trade fraud using machine learning and explainable AI"
2. **Dashboard Overview:** Show Global Trade Overview with KPIs
3. **Problem Statement:** "$2 trillion in trade-based money laundering annually"

### Live Investigation (5 minutes)
1. **Scenario 1 - Price Manipulation:**
   - Show TXN00027 in Suspicious Transactions Table
   - Click "Explain with AI" button
   - Demonstrate natural language explanation
   - Highlight 233% price deviation on chart

2. **Scenario 2 - Route Anomaly:**
   - Show TXN00006 on Route Intelligence Map
   - Demonstrate anomalous routing visualization
   - Ask AI: "Why is this route suspicious?"
   - Show combined fraud indicators

3. **Scenario 5 - Complex Investigation:**
   - Use AI Investigation Assistant for TXN00062
   - Show multi-factor fraud analysis
   - Demonstrate actionable recommendations

### Feature Highlights (2 minutes)
1. **Real-time Alerts:** Show alert banner for critical cases
2. **Company Risk Network:** Visualize suspicious relationships
3. **Price Deviation Chart:** Interactive fraud pattern visualization
4. **AI Assistant:** Answer audience questions live

### Closing (1 minute)
1. **Impact:** "Helps investigators process 1000s of transactions in minutes"
2. **Technology:** "Powered by IsolationForest ML + Gemini AI"
3. **Future:** "Scalable to millions of transactions, real-time streaming"

---

## Technical Demo Tips

### Before Demo
- [ ] Ensure Gemini API key is configured and has quota
- [ ] Pre-load the dashboard to avoid startup delay
- [ ] Test all AI queries to verify responses
- [ ] Have backup explanations ready if API fails
- [ ] Clear browser cache for clean demo

### During Demo
- [ ] Use dark theme for better visibility
- [ ] Zoom browser to 125% for audience viewing
- [ ] Keep AI queries concise and clear
- [ ] Explain fraud indicators in simple terms
- [ ] Show both detection AND explanation capabilities

### Fallback Plans
- [ ] If Gemini API fails: Use fallback explanations (already implemented)
- [ ] If dashboard is slow: Pre-load visualizations
- [ ] If questions stump AI: Pivot to pre-tested queries
- [ ] If data doesn't load: Have screenshots ready

---

## Fraud Pattern Summary

| Pattern | Indicator | Example Transaction | Detection Method |
|---------|-----------|---------------------|------------------|
| Over-Invoicing | Price deviation > +50% | TXN00027 (+233%) | Price anomaly score |
| Under-Invoicing | Price deviation < -50% | TXN00006 (-73%) | Price anomaly score |
| Route Anomaly | Illogical routing | TXN00062 (Shanghai→Dubai→Turkey→Chennai) | Route risk score |
| Port Exploitation | High port activity + fraud | TXN00055 (Port index 1.19) | Port congestion score |
| High-Risk Company | Company risk > 0.8 | TXN00055 (Risk 0.90) | Company network risk |
| Systematic Fraud | High trade frequency + anomalies | TXN00032 (24 trades/30d) | Pattern detection |

---

## Expected Questions from Audience

### Q1: "How accurate is the fraud detection?"
**Answer:** "Our IsolationForest model identifies anomalies with high precision. In this dataset, we detected 117 fraud cases out of 1,000 transactions (11.7% fraud rate). The AI explanations help investigators validate and prioritize cases."

### Q2: "Can this work with real-time data?"
**Answer:** "Yes! The current prototype processes batch data, but the architecture supports real-time streaming. We can integrate with customs databases and flag suspicious transactions as they occur."

### Q3: "What if fraudsters adapt to avoid detection?"
**Answer:** "The ML model can be retrained with new fraud patterns. The feature engineering approach captures fundamental fraud indicators (price, route, company risk) that are difficult to completely avoid."

### Q4: "How does this compare to existing solutions?"
**Answer:** "Traditional systems use rule-based detection (e.g., flag if price > X%). TRINETRA AI uses unsupervised learning to detect novel patterns and provides explainable AI insights, not just alerts."

### Q5: "What about false positives?"
**Answer:** "The AI explanations help investigators quickly assess whether a flagged transaction is truly fraudulent or a legitimate anomaly. This reduces investigation time even for false positives."

---

## Success Metrics for Demo

- [ ] Audience understands the fraud detection problem
- [ ] Live AI explanations work smoothly
- [ ] Visualizations clearly show fraud patterns
- [ ] Investigators can see how they'd use the tool
- [ ] Questions are answered confidently
- [ ] Demo completes within 10 minutes
- [ ] Judges understand the technical innovation
- [ ] Team demonstrates domain expertise

---

## Post-Demo Follow-Up

### For Judges
- Provide access to live demo instance
- Share GitHub repository with code
- Offer technical deep-dive session
- Discuss scalability and deployment

### For Potential Users
- Schedule pilot program discussion
- Provide API documentation
- Discuss integration requirements
- Share case studies and ROI analysis

---

*Document prepared for TRINETRA AI Hackathon Demo*  
*Last Updated: 2024*  
*For questions, contact the development team*
