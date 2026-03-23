# TRINETRA AI - Known Limitations

**Version:** 1.0  
**Last Updated:** 2024  
**Document Type:** System Limitations and Constraints

---

## Overview

This document outlines the known limitations, constraints, and boundaries of the TRINETRA AI Trade Fraud Intelligence System. Understanding these limitations is essential for proper system deployment, demonstration, and future development planning.

---

## 1. Machine Learning Model Limitations

### 1.1 Unsupervised Learning Constraints

**Limitation:** The system uses IsolationForest, an unsupervised anomaly detection algorithm that does not learn from labeled fraud examples.

**Impact:**
- Cannot distinguish between different types of fraud patterns
- May flag legitimate unusual transactions as suspicious
- Accuracy depends on the assumption that fraud is rare (~10% contamination rate)
- No ability to improve from user feedback on false positives/negatives

**Workaround:** Manual review of flagged transactions by fraud analysts is required.

### 1.2 Model Accuracy

**Limitation:** The model is trained on a synthetic dataset of 1,000 transactions and has not been validated against real-world fraud cases.

**Impact:**
- Unknown true positive/false positive rates
- May not generalize to real trade fraud patterns
- Performance on production data is untested
- Risk classification thresholds (SAFE < -0.2, SUSPICIOUS -0.2 to 0.2, FRAUD > 0.2) are arbitrary

**Current Status:** System validation shows 100% of transactions classified as SUSPICIOUS, indicating threshold tuning is needed.

### 1.3 Feature Engineering Limitations

**Limitation:** Only 6 engineered features are used for fraud detection:
- price_anomaly_score
- route_risk_score
- company_network_risk
- port_congestion_score
- shipment_duration_risk
- volume_spike_score

**Impact:**
- May miss fraud patterns not captured by these features
- No temporal pattern analysis (time series)
- No network analysis of trading relationships
- Limited contextual understanding of trade regulations

### 1.4 Model Retraining

**Limitation:** The system does not support automatic model retraining or online learning.

**Impact:**
- Model becomes stale as fraud patterns evolve
- Cannot adapt to new fraud techniques
- Requires manual retraining and redeployment
- No feedback loop from analyst decisions

---

## 2. AI Explanation System Limitations

### 2.1 Gemini API Quota Constraints

**Limitation:** The system implements strict quota management with a maximum of 10 AI-powered explanations per session.

**Impact:**
- Limited AI explanations available during demonstrations
- Users must rely on fallback explanations after quota is reached
- Session must be manually reset to get more AI explanations
- No automatic quota replenishment

**Workaround:** Use the "Get Fallback Explanation" button for rule-based explanations, or reset the session via `/session/reset` endpoint.

### 2.2 API Timeout Constraints

**Limitation:** Gemini API calls have a 10-second timeout as per NFR-1 requirements.

**Impact:**
- Complex queries may timeout before completion
- Automatically falls back to rule-based explanations on timeout
- No retry mechanism for timed-out requests (to preserve quota)

### 2.3 Explanation Quality

**Limitation:** AI explanations are generated without domain-specific training on trade fraud regulations.

**Impact:**
- May not reference specific trade compliance regulations
- Cannot cite legal precedents or regulatory frameworks
- Explanations are general-purpose, not expert-level
- No guarantee of regulatory accuracy

### 2.4 Fallback Explanation Limitations

**Limitation:** Fallback explanations use simple rule-based logic when Gemini API is unavailable.

**Impact:**
- Less detailed and contextual than AI explanations
- Cannot answer complex investigation queries
- Limited to predefined fraud indicators
- No natural language understanding

---

## 3. Data and Scalability Limitations

### 3.1 Dataset Size

**Limitation:** System is designed for a static dataset of 1,000 transactions loaded from CSV.

**Impact:**
- Not suitable for large-scale production deployments
- No support for datasets larger than ~10,000 transactions without performance degradation
- Memory usage scales linearly with dataset size
- Dashboard performance degrades with large datasets

**Current Capacity:** Optimized for 1,000-5,000 transactions.

### 3.2 Real-Time Data Processing

**Limitation:** The system does not support real-time data streaming or incremental updates.

**Impact:**
- Cannot process live transaction feeds
- Requires full system restart to load new data
- No support for continuous monitoring
- Data must be batch-loaded from CSV files

**Out of Scope:** Real-time data streaming (as per requirements).

### 3.3 Data Persistence

**Limitation:** All data is stored in-memory using pandas DataFrames. No database backend.

**Impact:**
- Data is lost when system restarts
- No transaction history or audit trail
- Cannot handle concurrent users modifying data
- Limited to single-instance deployment

**Out of Scope:** Database persistence (as per requirements).

### 3.4 Data Quality Dependencies

**Limitation:** System assumes clean, well-formatted CSV data with all required columns.

**Impact:**
- Minimal data validation and cleaning
- May fail on malformed or incomplete data
- No support for data quality monitoring
- Assumes data integrity at source

---

## 4. API and Integration Limitations

### 4.1 Single-User Architecture

**Limitation:** The system is designed for single-user local deployment without authentication.

**Impact:**
- No user authentication or authorization
- Cannot support multiple concurrent analysts
- No user-specific session management
- All users share the same explanation quota

**Out of Scope:** Multi-user authentication (as per requirements).

### 4.2 API Rate Limiting

**Limitation:** No rate limiting or throttling on API endpoints.

**Impact:**
- Vulnerable to abuse or accidental overload
- No protection against denial-of-service
- All requests processed immediately
- May impact performance under heavy load

### 4.3 CORS Configuration

**Limitation:** CORS is configured to allow all origins (`allow_origins=["*"]`).

**Impact:**
- Not suitable for production deployment
- Potential security vulnerability
- Should be restricted to specific domains in production

**Note:** Acceptable for local development and hackathon demonstration.

### 4.4 Error Handling

**Limitation:** Generic error messages returned to clients without detailed diagnostics.

**Impact:**
- Difficult to debug integration issues
- Limited error context for developers
- No structured error codes
- Logs required for troubleshooting

---

## 5. Dashboard and Visualization Limitations

### 5.1 Performance Constraints

**Limitation:** Dashboard load time target is <3 seconds, but may degrade with large datasets or slow networks.

**Impact:**
- Visualizations may be slow to render with >1,000 transactions
- Interactive charts may lag on older hardware
- Network latency affects API response times
- No progressive loading or lazy rendering

### 5.2 Browser Compatibility

**Limitation:** Dashboard is optimized for modern browsers (Chrome, Firefox, Edge, Safari).

**Impact:**
- May not work on older browsers (IE11, older mobile browsers)
- JavaScript must be enabled
- Requires modern CSS support
- No graceful degradation for unsupported browsers

### 5.3 Mobile Responsiveness

**Limitation:** Dashboard is designed for desktop/laptop screens (1280x720 minimum).

**Impact:**
- Limited mobile device support
- Visualizations may not render properly on small screens
- Touch interactions not optimized
- No mobile-specific UI

**Out of Scope:** Mobile application (as per requirements).

### 5.4 Visualization Limitations

**Limitation:** Route Intelligence Map requires valid geographic coordinates for ports.

**Impact:**
- Missing or invalid coordinates result in blank maps
- Limited to 5 export and 5 import ports in demo dataset
- No support for complex multi-leg routes
- Static map projection (cannot change map style)

---

## 6. Deployment and Infrastructure Limitations

### 6.1 Local Deployment Only

**Limitation:** System is designed for local development and demonstration, not production deployment.

**Impact:**
- No cloud deployment scripts or configurations
- No containerization (Docker) support
- No load balancing or high availability
- Single point of failure

**Out of Scope:** Production deployment infrastructure (as per requirements).

### 6.2 Dependency Management

**Limitation:** System requires specific Python package versions and may conflict with other projects.

**Impact:**
- Virtual environment is mandatory
- Version conflicts possible with system Python packages
- No automated dependency resolution
- Manual troubleshooting required for installation issues

### 6.3 Operating System Support

**Limitation:** Tested primarily on Windows 10/11, macOS 10.14+, and Ubuntu 18.04+.

**Impact:**
- May not work on other Linux distributions without modification
- Path separators and scripts may need adjustment
- Some features may behave differently across OS
- Limited testing on non-standard configurations

### 6.4 Resource Requirements

**Limitation:** Minimum 4GB RAM, 8GB recommended. No support for resource-constrained environments.

**Impact:**
- Cannot run on low-memory systems
- May compete with other applications for resources
- No memory optimization for embedded systems
- Requires modern multi-core CPU for acceptable performance

---

## 7. Security Limitations

### 7.1 API Key Management

**Limitation:** Gemini API key is hardcoded in source code for demo purposes.

**Impact:**
- API key visible in source code
- No key rotation mechanism
- Shared key across all users
- Potential for quota exhaustion or abuse

**Note:** For production, API keys must be stored in environment variables or secure vaults.

### 7.2 Input Validation

**Limitation:** Minimal input validation on API endpoints and user inputs.

**Impact:**
- Vulnerable to injection attacks if exposed to internet
- No sanitization of natural language queries
- Limited protection against malformed requests
- Assumes trusted input sources

**Mitigation:** System is designed for local use only, not internet-facing.

### 7.3 Data Privacy

**Limitation:** No encryption of data at rest or in transit (local deployment).

**Impact:**
- Sensitive transaction data stored in plain text
- No audit logging of data access
- Cannot comply with data protection regulations (GDPR, etc.)
- Not suitable for processing real sensitive data

**Out of Scope:** Production security features (as per requirements).

### 7.4 Logging and Monitoring

**Limitation:** Basic file-based logging with no centralized monitoring or alerting.

**Impact:**
- No real-time system health monitoring
- Manual log file review required
- No automated error alerting
- Limited observability in production scenarios

---

## 8. Functional Limitations

### 8.1 Alert Management

**Limitation:** Alerts are generated at startup and stored in-memory. No real-time alert generation.

**Impact:**
- New transactions do not trigger alerts until system restart
- Alert dismissal state is lost on restart
- No alert history or audit trail
- Cannot configure custom alert rules

### 8.2 Investigation Tools

**Limitation:** Natural language query interface has limited understanding and context.

**Impact:**
- Cannot answer complex multi-step queries
- No support for aggregations or statistical analysis
- Limited to predefined query patterns
- Falls back to generic responses for unknown queries

### 8.3 Reporting and Export

**Limitation:** No built-in reporting or data export functionality.

**Impact:**
- Cannot generate PDF or Excel reports
- No scheduled report generation
- Manual copy-paste required for data extraction
- No integration with BI tools

**Out of Scope:** Advanced reporting features (as per requirements).

### 8.4 Transaction Management

**Limitation:** Transactions are read-only. No support for updating, annotating, or managing transaction lifecycle.

**Impact:**
- Cannot mark transactions as reviewed or resolved
- No case management workflow
- Cannot add analyst notes or comments
- No transaction status tracking

---

## 9. Testing and Quality Assurance Limitations

### 9.1 Test Coverage

**Limitation:** Property-based tests cover core correctness properties, but integration testing is limited.

**Impact:**
- End-to-end workflows not fully tested
- Dashboard component integration partially tested
- Limited stress testing or load testing
- No automated UI testing

**Current Coverage:** >80% code coverage for backend modules, limited frontend testing.

### 9.2 Performance Testing

**Limitation:** Performance testing conducted on small dataset (1,000 transactions) only.

**Impact:**
- Unknown performance characteristics at scale
- No benchmarks for large datasets (>10,000 transactions)
- Memory usage patterns not profiled
- No performance regression testing

### 9.3 Error Recovery

**Limitation:** Limited testing of error scenarios and recovery procedures.

**Impact:**
- Unknown behavior under resource exhaustion
- Partial testing of network failures
- Limited validation of corrupt data handling
- No chaos engineering or fault injection testing

---

## 10. Documentation Limitations

### 10.1 API Documentation

**Limitation:** API documentation available via Swagger UI, but lacks detailed examples and use cases.

**Impact:**
- Developers may need to experiment to understand API behavior
- No comprehensive integration guide
- Limited error code documentation
- No API versioning strategy

### 10.2 User Documentation

**Limitation:** User guide covers basic usage but lacks advanced workflows and troubleshooting.

**Impact:**
- Users may struggle with complex scenarios
- Limited guidance on interpreting results
- No decision-making framework for fraud analysts
- Assumes technical proficiency

### 10.3 Code Documentation

**Limitation:** Code comments and docstrings present but not comprehensive.

**Impact:**
- Some functions lack detailed parameter descriptions
- Limited architectural documentation
- No design decision rationale documented
- Onboarding new developers may be challenging

---

## 11. Known Issues and Bugs

### 11.1 Risk Classification Imbalance

**Issue:** System validation shows 100% of transactions classified as SUSPICIOUS (0% FRAUD, 0% SAFE).

**Impact:**
- Risk thresholds need tuning
- Reduced utility of risk categories
- All transactions appear equally risky

**Status:** Known issue, requires threshold adjustment based on real data.

### 11.2 Geographic Data Limitations

**Issue:** Demo dataset has limited geographic diversity (5 export ports, 5 import ports).

**Impact:**
- Route Intelligence Map shows limited coverage
- Cannot demonstrate global trade patterns
- Reduced visual impact in demonstrations

**Status:** Limitation of demo dataset, not a system bug.

### 11.3 Explanation Cache Persistence

**Issue:** Explanation cache is cleared on system restart.

**Impact:**
- Previously generated explanations must be regenerated
- Quota count resets on restart
- No persistent explanation history

**Status:** By design for demo system, would require database for persistence.

---

## 12. Comparison with Production Requirements

### Features NOT Implemented (Out of Scope)

The following features are explicitly out of scope as per requirements:

1. **Real-time data streaming** - System uses batch CSV loading
2. **Multi-user authentication** - Single-user local deployment
3. **Database persistence** - In-memory data storage only
4. **Production deployment infrastructure** - Local development setup
5. **Mobile application** - Desktop web interface only
6. **Advanced model tuning and optimization** - Basic IsolationForest configuration
7. **Integration with external trade databases** - Standalone system

### Performance Targets

| Metric | Target | Current Status | Notes |
|--------|--------|----------------|-------|
| Dashboard load time | <3 seconds | ✅ Achieved | With 1,000 transactions |
| API response time | <1 second | ✅ Achieved | Most endpoints |
| ML model training | <30 seconds | ✅ Achieved | ~2 seconds for 1,000 rows |
| Gemini API timeout | 10 seconds | ✅ Implemented | With fallback |

---

## 13. Recommendations for Future Development

### High Priority

1. **Tune risk classification thresholds** to achieve balanced distribution across SAFE/SUSPICIOUS/FRAUD categories
2. **Implement database backend** (PostgreSQL) for data persistence and scalability
3. **Add user authentication** for multi-user support
4. **Expand test coverage** for dashboard components and end-to-end workflows

### Medium Priority

5. **Implement real-time data streaming** for continuous monitoring
6. **Add transaction annotation and case management** features
7. **Develop reporting and export** functionality (PDF, Excel)
8. **Optimize performance** for datasets >10,000 transactions

### Low Priority

9. **Mobile-responsive dashboard** design
10. **Advanced ML models** (XGBoost, Neural Networks) for improved accuracy
11. **Integration with external APIs** (customs databases, sanctions lists)
12. **Automated model retraining** pipeline

---

## 14. Conclusion

TRINETRA AI is a **functional prototype** suitable for hackathon demonstration and proof-of-concept purposes. It successfully demonstrates:

✅ AI-powered fraud detection using machine learning  
✅ Natural language explanations via Gemini API  
✅ Interactive dashboard with visualizations  
✅ RESTful API for data access  
✅ Automated alert generation  

However, it has **significant limitations** that prevent production deployment without substantial additional development:

⚠️ No database persistence or scalability  
⚠️ Single-user local deployment only  
⚠️ Limited ML model accuracy and validation  
⚠️ Quota-constrained AI explanations  
⚠️ No real-time data processing  

**For Hackathon Demonstration:** The system is ready and meets all specified requirements.

**For Production Use:** Significant additional development is required to address scalability, security, multi-user support, and data persistence limitations.

---

**Document Prepared By:** TRINETRA AI Development Team  
**Review Status:** Final  
**Next Review Date:** Upon production deployment planning
