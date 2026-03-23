# Demo Screenshots Directory

This directory contains backup screenshots for demo presentations.

## Purpose

These screenshots serve as backup materials when:
- The live system encounters technical issues
- Network connectivity is unavailable
- Performance is degraded
- You need to show specific features quickly

## Directory Structure

```
demo_screenshots/
├── dashboard/
│   ├── 01_overview.png          # KPI metrics and statistics
│   ├── 02_alerts.png            # Fraud alert banners
│   ├── 03_transactions.png      # Transaction table view
│   ├── 04_explanations.png      # AI explanation examples
│   ├── 05_route_map.png         # Route intelligence map
│   ├── 06_network.png           # Company risk network
│   ├── 07_price_chart.png       # Price deviation chart
│   └── 08_ai_assistant.png      # AI investigation assistant
├── api/
│   ├── 01_swagger_ui.png        # FastAPI documentation interface
│   ├── 02_transactions_json.png # Transaction API response
│   └── 03_stats_json.png        # Statistics API response
└── README.md                     # This file
```

## How to Capture Screenshots

### Before Your Demo

1. **Start the system**:
   ```bash
   python main.py
   ```

2. **Wait for services to be ready** (look for ✅ messages)

3. **Open the dashboard**: `http://localhost:8501`

4. **Capture each section**:
   - Use full-screen mode for clean screenshots
   - Ensure zoom is at 100%
   - Capture at high resolution (1920x1080 or higher)
   - Save as PNG for best quality

### Dashboard Screenshots

**01_overview.png** - KPI Metrics
- Navigate to main dashboard
- Ensure all 5 KPI cards are visible
- Capture: Total Transactions, Active Alerts, Fraud Rate, Trade Value, High-Risk Routes

**02_alerts.png** - Fraud Alerts
- Scroll to alert section
- Expand alert details if available
- Capture: Alert banners with priority indicators

**03_transactions.png** - Transaction Table
- Select "All Transactions" or "Suspicious Transactions"
- Show table with multiple rows
- Capture: Transaction ID, Product, Price Deviation, Risk Score, Category

**04_explanations.png** - AI Explanations
- Select transaction TXN00006
- Click "Get AI Explanation"
- Wait for explanation to load
- Capture: Full explanation text with transaction details

**05_route_map.png** - Route Intelligence Map
- Navigate to "Visualizations" section
- Wait for route map to fully render
- Capture: World map with shipping routes and ports

**06_network.png** - Company Risk Network
- Scroll to company network visualization
- Wait for network graph to render
- Capture: Network graph with company nodes and connections

**07_price_chart.png** - Price Deviation Chart
- Locate price deviation scatter plot
- Ensure legend is visible
- Capture: Chart showing market price vs trade price

**08_ai_assistant.png** - AI Investigation Assistant
- Navigate to AI Assistant section
- Ask a sample question (e.g., "What are the main fraud patterns?")
- Wait for response
- Capture: Question and answer

### API Screenshots

**01_swagger_ui.png** - API Documentation
- Open: `http://localhost:8000/docs`
- Expand a few endpoints
- Capture: Swagger UI interface

**02_transactions_json.png** - Transaction Response
- In Swagger UI, try GET /transactions
- Click "Execute"
- Capture: JSON response

**03_stats_json.png** - Statistics Response
- In Swagger UI, try GET /stats
- Click "Execute"
- Capture: JSON response with statistics

## Screenshot Guidelines

### Quality Standards

- **Resolution**: Minimum 1920x1080 (Full HD)
- **Format**: PNG (lossless compression)
- **File Size**: Keep under 5MB per image
- **Clarity**: Ensure text is readable
- **Completeness**: Capture entire relevant section

### What to Include

✅ **DO Include:**
- Full interface elements
- Clear, readable text
- Relevant data and visualizations
- UI controls and buttons
- Legend and labels

❌ **DON'T Include:**
- Personal information
- Sensitive data (if using real data)
- Browser bookmarks or tabs
- Desktop background
- System notifications

### Naming Convention

Use the provided naming scheme:
- `01_`, `02_`, etc. for ordering
- Descriptive names: `overview`, `alerts`, `transactions`
- `.png` extension

## Using Screenshots During Demo

### When to Use

1. **System Failure**: Complete system crash or won't start
2. **Performance Issues**: Dashboard too slow to navigate
3. **Network Problems**: Cannot reach external services
4. **Visualization Errors**: Charts/maps not rendering
5. **Time Constraints**: Need to show features quickly

### How to Present

1. **Open screenshots folder** before demo starts
2. **Use slideshow mode** or image viewer
3. **Navigate in order** (01, 02, 03, etc.)
4. **Explain as you show**: Describe what users would see in live system
5. **Be transparent**: Acknowledge you're showing screenshots due to technical issues

### Presentation Tips

- **Practice**: Know which screenshot shows what
- **Prepare transitions**: Smooth movement between images
- **Add context**: Explain what actions would trigger each view
- **Stay confident**: Screenshots are a valid backup plan
- **Offer follow-up**: Promise live demo later

## Updating Screenshots

### When to Update

- After major UI changes
- Before important demos
- When adding new features
- If data changes significantly
- Quarterly maintenance

### Update Process

1. Pull latest code
2. Start fresh system
3. Recapture all screenshots
4. Verify quality
5. Replace old screenshots
6. Test in presentation mode

## Backup Checklist

Before your demo, verify:

- [ ] All 8 dashboard screenshots exist
- [ ] All 3 API screenshots exist
- [ ] Screenshots are recent (< 1 month old)
- [ ] Images are high quality and readable
- [ ] File sizes are reasonable (< 5MB each)
- [ ] Screenshots match current UI
- [ ] You know how to access them quickly
- [ ] You've practiced presenting with them

## Alternative: Screen Recording

Consider also creating a screen recording:

```bash
# Record a 5-minute demo walkthrough
# Save as: docs/demo_video.mp4
# Tools: OBS Studio, QuickTime, Windows Game Bar
```

Benefits:
- Shows actual interactions
- Includes transitions and animations
- More engaging than static images
- Can include narration

## Troubleshooting

**Q: Screenshots look blurry**
- A: Increase resolution, use 100% zoom, save as PNG

**Q: File sizes too large**
- A: Use PNG compression tools (TinyPNG, pngquant)

**Q: Can't capture full page**
- A: Use browser extensions (Full Page Screen Capture)

**Q: Colors look different**
- A: Ensure dark theme is enabled, check monitor calibration

## Resources

- **Screenshot Tools**:
  - Windows: Snipping Tool, Snip & Sketch
  - macOS: Cmd+Shift+4
  - Linux: GNOME Screenshot, Flameshot
  - Browser: Full Page Screen Capture extension

- **Image Editing**:
  - GIMP (free)
  - Photoshop
  - Preview (macOS)
  - Paint.NET (Windows)

- **Compression**:
  - TinyPNG (online)
  - ImageOptim (macOS)
  - pngquant (command-line)

## Support

For questions about demo materials:
- See: `docs/DEMO_BACKUP_PLANS.md`
- See: `docs/DEMO_QUICK_REFERENCE_CARD.md`
- See: `TROUBLESHOOTING_GUIDE.md`

---

**Last Updated**: 2024  
**Maintained By**: TRINETRA AI Team
