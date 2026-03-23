# TRINETRA AI - Demo Transaction Examples

## 📋 Curated Transaction Examples for Live Demo

This document provides specific transaction IDs with their details and expected AI explanations for practice and demo preparation.

---

## 🔴 FRAUD CASES - High Impact Examples

### Example 1: Extreme Underpricing (Price Manipulation)

**Transaction ID:** `TXN00006`

**Key Details:**
- **Product:** Crude Oil
- **Commodity Category:** Energy
- **Quantity:** 2,915 tons
- **Market Price:** $75.00/ton
- **Trade Price:** $20.16/ton
- **Price Deviation:** -73.12% (MASSIVE underpricing!)
- **Trade Value:** $58,766.40
- **Exporter:** PetroGlobal (UAE, Dubai)
- **Importer:** NipponAlloys (Japan, Yokohama)
- **Shipping Route:** Houston-Alexandria
- **Distance:** 11,500 km
- **Company Risk Score:** 0.07
- **Route Anomaly:** 0
- **Fraud Label:** 2 (Confirmed Fraud)

**Why This is Fraud:**
- Crude oil priced 73% below market value is extremely suspicious
- Such extreme underpricing suggests invoice manipulation
- Likely used for money laundering or tax evasion
- Could be hiding true transaction value to avoid duties/taxes
- The low company risk score makes this even more suspicious (legitimate company doing fraud)

**Expected AI Explanation:**
> "This transaction shows severe price manipulation with crude oil priced at $20.16 per ton, which is 73% below the market price of $75. Such extreme underpricing is a classic indicator of trade-based money laundering or customs fraud. The exporter may be attempting to move money illegally or help the importer evade import duties. Despite the relatively low company risk score, the massive price deviation is a clear red flag requiring immediate investigation."

**Demo Talking Points:**
- "This is textbook price manipulation"
- "73% below market - that's not a discount, that's fraud"
- "Could cost governments millions in lost tax revenue"

---

### Example 2: Extreme Overpricing (Money Movement)

**Transaction ID:** `TXN00027`

**Key Details:**
- **Product:** Aluminum
- **Commodity Category:** Metal
- **Quantity:** 2,318 tons
- **Market Price:** $2,400.00/ton
- **Trade Price:** $8,003.86/ton
- **Price Deviation:** +233.49% (EXTREME overpricing!)
- **Trade Value:** $18,552,947.48
- **Exporter:** AgriGrain (USA, Houston)
- **Importer:** JiangsuCopper (China, Shanghai)
- **Shipping Route:** Valparaiso-Shanghai
- **Distance:** 17,000 km
- **Company Risk Score:** 0.56
- **Route Anomaly:** 0
- **Fraud Label:** 2 (Confirmed Fraud)

**Why This is Fraud:**
- Aluminum priced 233% above market value is absurd
- Classic method for moving money illegally across borders
- Importer overpays to transfer funds to exporter
- Could be used for capital flight, bribery, or corruption
- The moderate company risk score adds to suspicion

**Expected AI Explanation:**
> "This transaction exhibits extreme overpricing with aluminum traded at $8,003.86 per ton, which is 233% above the market price of $2,400. This is a strong indicator of trade-based money laundering, where the importer deliberately overpays to transfer funds to the exporter. Such transactions are often used for capital flight, corruption, or circumventing currency controls. The significant price deviation combined with the moderate company risk score warrants immediate investigation and potential reporting to financial authorities."

**Demo Talking Points:**
- "The opposite of underpricing - paying 3x market value"
- "This is how money moves illegally across borders"
- "Nearly $19 million transaction - high stakes fraud"

---

### Example 3: Severe Underpricing (Steel Fraud)

**Transaction ID:** `TXN00032`

**Key Details:**
- **Product:** Steel
- **Commodity Category:** Metal
- **Quantity:** 3,949 tons
- **Market Price:** $520.00/ton
- **Trade Price:** $211.58/ton
- **Price Deviation:** -59.31% (Severe underpricing)
- **Trade Value:** $835,529.42
- **Exporter:** PetroGlobal (UAE, Dubai)
- **Importer:** BharatMetals (India, Chennai)
- **Shipping Route:** Valparaiso-Shanghai
- **Distance:** 17,000 km
- **Company Risk Score:** 0.59
- **Route Anomaly:** 0
- **Fraud Label:** 2 (Confirmed Fraud)

**Why This is Fraud:**
- Steel priced 59% below market value
- Large quantity (3,949 tons) amplifies the fraud impact
- Moderate company risk score suggests pattern of suspicious activity
- Could be customs duty evasion or transfer pricing manipulation

**Expected AI Explanation:**
> "This steel transaction shows significant underpricing at $211.58 per ton, 59% below the market price of $520. With a quantity of 3,949 tons, this represents substantial potential customs duty evasion. The moderate company risk score of 0.59 suggests this may be part of a pattern of suspicious trading activity. Investigators should examine the trading history between these companies and verify the actual quality and specifications of the steel being traded."

**Demo Talking Points:**
- "Nearly 4,000 tons of steel at 60% discount"
- "This could cost the importing country significant tax revenue"
- "Company risk score suggests this isn't their first rodeo"

---

## 🟡 SUSPICIOUS CASES - Investigation Required

### Example 4: Route Anomaly (Unusual Shipping Path)

**Transaction ID:** `TXN00020`

**Key Details:**
- **Product:** Steel
- **Commodity Category:** Metal
- **Quantity:** 2,563 tons
- **Market Price:** $520.00/ton
- **Trade Price:** $542.39/ton
- **Price Deviation:** +4.31% (Slight overpricing)
- **Trade Value:** $1,390,145.57
- **Exporter:** AusMetal (Australia, Perth)
- **Importer:** DeltaFoods (Egypt, Alexandria)
- **Shipping Route:** Perth-Malaysia-Indonesia-Yokohama (UNUSUAL!)
- **Distance:** 12,000 km
- **Company Risk Score:** 0.73
- **Route Anomaly:** 1 (Flagged!)
- **Fraud Label:** 0 (Not confirmed, but suspicious)

**Why This is Suspicious:**
- Route doesn't make sense: Perth to Alexandria via Malaysia, Indonesia, and Yokohama
- Yokohama (Japan) is completely off the direct path
- Could be route laundering to avoid sanctions or tariffs
- Slight price overpricing adds to suspicion
- High company risk score (0.73) is concerning

**Expected Fallback Explanation:**
> "This transaction is flagged for route anomaly. The shipping route from Perth to Alexandria via Malaysia, Indonesia, and Yokohama is highly unusual and inefficient. Direct routes exist that would be significantly shorter and cheaper. This circuitous routing could indicate an attempt to obscure the true origin or destination of goods, possibly to evade sanctions, tariffs, or trade restrictions. Combined with the slight price overpricing and high company risk score, this transaction requires detailed investigation."

**Demo Talking Points:**
- "Why would steel from Australia to Egypt go through Japan?"
- "This is route laundering - hiding the true path"
- "Could be avoiding sanctions or specific trade restrictions"

---

### Example 5: Route Anomaly with Price Deviation

**Transaction ID:** `TXN00038`

**Key Details:**
- **Product:** Wheat
- **Commodity Category:** Agriculture
- **Quantity:** 1,572 tons
- **Market Price:** $300.00/ton
- **Trade Price:** $337.68/ton
- **Price Deviation:** +12.56% (Moderate overpricing)
- **Trade Value:** $530,832.96
- **Exporter:** AgriGrain (USA, Houston)
- **Importer:** NipponAlloys (Japan, Yokohama)
- **Shipping Route:** Perth-Malaysia-Indonesia-Yokohama (UNUSUAL!)
- **Distance:** 12,000 km
- **Company Risk Score:** 0.40
- **Route Anomaly:** 1 (Flagged!)
- **Fraud Label:** 0 (Suspicious)

**Why This is Suspicious:**
- Wheat from Houston to Yokohama shouldn't go via Perth, Malaysia, Indonesia
- 12.56% price overpricing on top of unusual route
- Could be combining multiple fraud techniques
- Moderate company risk score

**Expected Fallback Explanation:**
> "This wheat transaction exhibits both route anomaly and price overpricing. The shipping route from Houston to Yokohama via Perth, Malaysia, and Indonesia is geographically illogical and suggests potential route laundering. Additionally, the 12.56% price premium over market value raises concerns about invoice manipulation. This combination of red flags indicates possible trade-based money laundering or sanctions evasion. Investigators should verify the actual shipping path and examine the business relationship between AgriGrain and NipponAlloys."

**Demo Talking Points:**
- "Two red flags: unusual route AND overpricing"
- "When you see multiple indicators, investigate deeper"
- "This is how sophisticated fraud operations work"

---

### Example 6: Route Anomaly (Crude Oil)

**Transaction ID:** `TXN00048`

**Key Details:**
- **Product:** Crude Oil
- **Commodity Category:** Energy
- **Quantity:** 2,665 tons
- **Market Price:** $75.00/ton
- **Trade Price:** $80.38/ton
- **Price Deviation:** +7.17% (Slight overpricing)
- **Trade Value:** $214,212.70
- **Exporter:** PetroGlobal (UAE, Dubai)
- **Importer:** DeltaFoods (Egypt, Alexandria)
- **Shipping Route:** Perth-Malaysia-Indonesia-Yokohama (UNUSUAL!)
- **Distance:** 12,000 km
- **Company Risk Score:** 0.19
- **Route Anomaly:** 1 (Flagged!)
- **Fraud Label:** 0 (Suspicious)

**Why This is Suspicious:**
- Crude oil from Dubai to Alexandria via Perth and Japan makes no sense
- Should be a direct route through Suez Canal
- Slight price overpricing adds to concerns
- Low company risk score makes the route anomaly even more suspicious

**Expected Fallback Explanation:**
> "This crude oil transaction is flagged for a highly suspicious shipping route. Oil from Dubai to Alexandria should follow a direct path through the Suez Canal, not via Perth, Malaysia, Indonesia, and Yokohama. This circuitous route adds thousands of kilometers and significant costs, suggesting possible sanctions evasion or origin obfuscation. The 7.17% price premium may be covering the additional routing costs or could indicate invoice manipulation. Despite the low company risk score, this transaction requires immediate investigation to verify the actual shipping path and business justification."

**Demo Talking Points:**
- "Oil from UAE to Egypt via Australia and Japan? No way."
- "This is textbook route laundering"
- "Even legitimate companies can be used for fraud"

---

## 🟢 SAFE CASES - For Comparison

### Example 7: Normal Transaction (Baseline)

**Transaction ID:** `TXN00001`

**Key Details:**
- **Product:** Wheat
- **Commodity Category:** Agriculture
- **Quantity:** 2,330 tons
- **Market Price:** $300.00/ton
- **Trade Price:** $280.54/ton
- **Price Deviation:** -6.49% (Minor discount, acceptable)
- **Trade Value:** $653,658.20
- **Exporter:** AndesMining (Chile, Valparaiso)
- **Importer:** DeltaFoods (Egypt, Alexandria)
- **Shipping Route:** Shanghai-Singapore-Chennai
- **Distance:** 5,600 km
- **Company Risk Score:** 0.32
- **Route Anomaly:** 0
- **Fraud Label:** 0 (Safe)

**Why This is Safe:**
- Price deviation is minor (-6.49%) - within normal negotiation range
- Route is logical and efficient
- Low company risk score (0.32)
- No route anomaly
- All indicators are normal

**Expected Fallback Explanation:**
> "This wheat transaction appears legitimate with a minor 6.49% discount from market price, which is within normal trading ranges. The shipping route is logical and efficient, the company risk score is low, and there are no route anomalies. This represents a standard international trade transaction with no red flags."

**Demo Talking Points:**
- "This is what normal trade looks like"
- "Small price variations are expected in negotiations"
- "No red flags - this is the baseline we compare against"

---

## 📊 Demo Strategy: Transaction Selection

### For Maximum Impact, Show in This Order:

1. **Start with TXN00006** (Extreme underpricing)
   - Most dramatic example (-73%)
   - Clear fraud indicator
   - Use AI explanation to show capability

2. **Follow with TXN00027** (Extreme overpricing)
   - Shows opposite fraud technique
   - Demonstrates system catches both directions
   - Use fallback explanation to show quota management

3. **Show TXN00020 or TXN00048** (Route anomaly)
   - Different fraud type (route-based)
   - Shows multi-factor detection
   - Demonstrates geographic intelligence

4. **Optional: Show TXN00001** (Safe transaction)
   - Provides contrast
   - Shows system doesn't flag everything
   - Demonstrates accuracy

---

## 🎯 Key Phrases for Each Example

### TXN00006 (Underpricing):
- "73% below market - that's not a discount, that's fraud"
- "Classic invoice manipulation"
- "Could be money laundering or tax evasion"

### TXN00027 (Overpricing):
- "Paying 3x market value - nobody does that legitimately"
- "This is how money moves illegally across borders"
- "Nearly $19 million in suspicious transactions"

### TXN00032 (Steel Underpricing):
- "4,000 tons at 60% discount - massive duty evasion"
- "Company risk score suggests a pattern"
- "This could cost governments millions"

### TXN00020/00038/00048 (Route Anomaly):
- "Why would goods go thousands of kilometers out of the way?"
- "This is route laundering - hiding the true path"
- "Could be avoiding sanctions or trade restrictions"

### TXN00001 (Safe):
- "This is what normal trade looks like"
- "Small variations are expected"
- "No red flags - this is our baseline"

---

## 💡 Pro Tips for Demo

1. **Memorize these transaction IDs:**
   - TXN00006 (underpricing)
   - TXN00027 (overpricing)
   - TXN00020 (route anomaly)

2. **Know the key numbers:**
   - -73% (TXN00006)
   - +233% (TXN00027)
   - Route anomaly = 1

3. **Practice the flow:**
   - Select transaction
   - Highlight key details
   - Click explanation button
   - Read/paraphrase AI response
   - Add your own insight

4. **Use the quota strategically:**
   - First transaction: AI explanation (show capability)
   - Second transaction: Fallback explanation (show quota management)
   - Third transaction: Your choice based on remaining quota

5. **Have backup transactions ready:**
   - If one doesn't load, move to another
   - All fraud cases tell a similar story
   - Don't get stuck on one example

---

## 🔍 Investigation Questions to Demonstrate

When showing transactions, ask these rhetorical questions:

1. **"Why would someone sell crude oil at 73% below market?"**
   - Answer: They wouldn't - unless they're hiding something

2. **"Who pays 3x market value for aluminum?"**
   - Answer: Someone moving money illegally

3. **"Does this shipping route make geographic sense?"**
   - Answer: No - it's route laundering

4. **"What patterns do we see across these fraud cases?"**
   - Answer: Price manipulation, route anomalies, high-risk companies

5. **"How does AI help investigators?"**
   - Answer: Explains the 'why', not just the 'what'

---

## 📈 Expected Audience Reactions

**When showing TXN00006 (-73%):**
- Gasps or surprised looks
- "That's obviously fraud"
- Questions about how common this is

**When showing TXN00027 (+233%):**
- Understanding nods
- "Ah, the opposite technique"
- Questions about money laundering

**When showing route anomalies:**
- Confusion about geography
- "Why would they do that?"
- Interest in sanctions evasion

**When showing AI explanations:**
- Impressed by natural language
- Questions about AI accuracy
- Interest in quota management

---

## ✅ Pre-Demo Checklist

Before your demo, verify these transactions are in the system:

- [ ] TXN00006 exists and shows -73% deviation
- [ ] TXN00027 exists and shows +233% deviation
- [ ] TXN00020 exists and shows route anomaly = 1
- [ ] TXN00001 exists as safe baseline
- [ ] AI explanations work (test with one transaction)
- [ ] Fallback explanations work
- [ ] Quota system displays correctly
- [ ] Session reset button works

---

**Remember: These are real examples from the dataset. Practice with them before the demo!**
