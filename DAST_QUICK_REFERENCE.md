# OWASP DAST - Quick Reference Card

## 🎯 What DAST Does

**DAST = Dynamic Application Security Testing**
- Tests running application (unlike SAST which analyzes code)
- Simulates real attacker behavior
- Finds runtime vulnerabilities
- Generates security reports

---

## 🏗️ Your DAST Pipeline

```
┌────────────────────────────────────┐
│ Step 1: Start Flask App            │
│ python app.py (port 5000)          │
└────────────────────────────────────┘
                  ↓
┌────────────────────────────────────┐
│ Step 2: Health Check               │
│ curl http://localhost:5000/        │
│ (verify app is running)            │
└────────────────────────────────────┘
                  ↓
┌────────────────────────────────────┐
│ Step 3: Run ZAP Baseline Scan      │
│ docker run zaproxy/zaproxy:stable  │
│ zap-baseline.py (scan endpoints)   │
└────────────────────────────────────┘
                  ↓
┌────────────────────────────────────┐
│ Step 4: Generate Reports           │
│ HTML / JSON / XML format           │
│ (upload as artifacts)              │
└────────────────────────────────────┘
                  ↓
┌────────────────────────────────────┐
│ Step 5: Stop Flask App             │
│ kill $FLASK_PID (cleanup)          │
└────────────────────────────────────┘
```

---

## 🔍 What DAST Finds

| Type | Tool | Risk | Your App |
|------|------|------|----------|
| SQL Injection | ZAP Spider | 🔴 High | `/user` endpoint |
| Command Injection | ZAP Scanner | 🔴 High | `/run` endpoint |
| Code Injection | ZAP Fuzzer | 🔴 High | `/eval` endpoint |
| Path Traversal | ZAP Crawler | 🔴 High | `/upload` endpoint |
| Deserialization | ZAP Probes | 🔴 High | `/deserialize` endpoint |
| XSS | ZAP Spider | 🟠 Medium | All endpoints |
| Auth Bypass | ZAP Scripts | 🔴 High | `/login` endpoint |
| Weak TLS | ZAP Passive | 🟡 Low | HTTP config |

---

## 📋 Workflow File Location

```
.github/
└─ workflows/
   ├─ main.yml          (Original)
   └─ mainv2.yml        (New with DAST) ← Use this
```

---

## 🚀 How to Use

### **Option 1: Automatic Trigger**
```
1. Edit code
2. git push origin main
3. ✅ Workflow runs automatically
4. Check Actions tab for results
```

### **Option 2: Manual Trigger**
```
1. Go to GitHub → Actions
2. Select "Python CI/CD with SonarCloud, DAST, Docker"
3. Click "Run workflow"
4. ✅ Workflow starts immediately
```

---

## 📊 Expected Results

### **DAST Job Output:**
```
✅ Flask app started on port 5000
✅ Health check passed
✅ ZAP Docker image pulled
🔍 Scanning 7 endpoints...
✅ Scan completed

RESULTS:
  Total Alerts: 15
  🔴 High: 5
  🟠 Medium: 6
  🟡 Low: 3
  ℹ️  Info: 1

Reports Generated:
  - zap_baseline_report.html
  - zap_baseline_report.json
  - zap_baseline_report.xml
```

---

## 📥 Viewing Results

### **In GitHub:**
1. Go to: Actions → Workflow Run → dast job
2. Scroll to: "Upload ZAP Scan Reports"
3. Click: "zap-scan-reports" artifact
4. Download: All reports

### **In Browser:**
1. Extract: zap_baseline_report.html
2. Open: Open in any web browser
3. Review: Visual vulnerability report

### **Programmatically:**
```python
import json
with open('zap_baseline_report.json') as f:
    data = json.load(f)
    for alert in data['site'][0]['alerts']:
        print(f"{alert['name']}: {alert['riskdesc']}")
```

---

## 🔐 Key Configuration

### **ZAP Scan Settings (in mainv2.yml):**
```yaml
# Target
-t http://localhost:5000

# Reports
-r zap_baseline_report.html    # HTML
-J zap_baseline_report.json    # JSON
-x zap_baseline_report.xml     # XML

# Scan type
zap-baseline.py                # Fast, lightweight
# vs
zap-full-scan.py               # Comprehensive, slow
```

### **Flask Settings:**
```python
# Port: 5000 (configured in app.py)
# Host: 0.0.0.0 (accessible from Docker)
app.run(host='0.0.0.0', port=5000)
```

### **Health Check Settings:**
```yaml
# URL: http://localhost:5000/
# Retries: 10 times
# Interval: 2 seconds
# Timeout: 20 seconds total
```

---

## 🎯 Test Coverage

| Endpoint | Method | DAST Tests |
|----------|--------|-----------|
| `/` | GET | XSS, CSRF, headers |
| `/` | POST | Input validation, XSS |
| `/user` | GET | SQL injection, param tampering |
| `/login` | POST | Auth bypass, brute force |
| `/run` | GET | Command injection, OS execution |
| `/eval` | POST | Code injection, eval abuse |
| `/upload` | POST | Path traversal, file upload |
| `/deserialize` | POST | Insecure deserialization, RCE |

---

## 📈 Comparing Scans

### **app.py (Vulnerable):**
```
Expected Findings:
- 5 High severity issues
- 6 Medium severity issues  
- 3 Low severity issues
Total: 14+ vulnerabilities
```

### **app_fixed.py (Secure):**
```
Expected Findings:
- 0 High severity issues (FIXED!)
- 1-2 Medium issues (config-related)
- 2-3 Low severity issues (info)
Total: 3-5 issues (reduced by 70%+)
```

---

## ⏱️ Timing

| Stage | Duration | Notes |
|-------|----------|-------|
| Setup | 1 min | Python, Java, Docker |
| Flask Start | 10 sec | App initialization |
| Health Check | 5 sec | Verify connectivity |
| ZAP Scan | 2-3 min | Baseline scan |
| Report Gen | 30 sec | Parse results |
| **Total** | **~5 min** | End to end |

---

## 🆘 Troubleshooting

### **Flask app fails to start:**
```
❌ Error: Connection refused
✅ Fix: Check app.py syntax, increase sleep time
```

### **ZAP can't connect to app:**
```
❌ Error: http://localhost:5000 unreachable
✅ Fix: Use --network host in docker run
```

### **Reports not generated:**
```
❌ Error: No zap_baseline_report.html
✅ Fix: Check ZAP finished (check logs)
```

### **Too many findings:**
```
❌ Too many false positives
✅ Fix: Switch to app_fixed.py to see improvements
```

---

## 📚 Report Interpretation

### **Risk Levels:**
- 🔴 **High** - Exploit possible, serious impact → FIX FIRST
- 🟠 **Medium** - Exploit difficult, moderate impact → FIX SECOND
- 🟡 **Low** - Exploit unlikely, minor impact → FIX LATER
- ℹ️ **Info** - Not a vulnerability, informational → REVIEW

### **Confidence Levels:**
- 🟢 **High** - Vulnerability confirmed
- 🟡 **Medium** - Likely vulnerable
- 🔵 **Low** - Possible vulnerability

### **Action Required:**
- High Risk + High Confidence → Critical, fix immediately
- High Risk + Low Confidence → Investigate
- Medium Risk → Plan fix
- Low Risk + Info → Monitor

---

## ✅ Pre-Flight Checklist

- ✅ mainv2.yml workflow file exists
- ✅ app.py or app_fixed.py in repository
- ✅ requirements.txt has dependencies
- ✅ Flask runs on port 5000
- ✅ No hardcoded secrets in code
- ✅ GitHub Actions enabled
- ✅ Workflow file is valid YAML

---

## 🔗 Quick Links

| Resource | Link |
|----------|------|
| OWASP ZAP | https://www.zaproxy.org/ |
| Baseline Scan | https://www.zaproxy.org/docs/docker/baseline-scan/ |
| Full Scan | https://www.zaproxy.org/docs/docker/full-scan/ |
| OWASP Top 10 | https://owasp.org/www-project-top-ten/ |
| ZAP Reports | https://www.zaproxy.org/docs/alerts/ |

---

## 💡 Pro Tips

1. **Compare Scans:** Run both app.py and app_fixed.py to see improvements
2. **Export Results:** Download JSON to parse programmatically
3. **Schedule Scans:** Use cron in GitHub Actions for periodic testing
4. **Integrate:** Link results to SonarQube or security dashboards
5. **Automate Fixes:** Create issues for each finding

---

## 🎓 Learning Resources

**Understanding DAST:**
- DAST scans runtime behavior, not code
- Tests all endpoints for vulnerabilities
- Simulates real attacker scenarios
- Takes longer than SAST but catches runtime issues

**ZAP Basics:**
- ZAP = Zed Attack Proxy
- Free, open-source security tool
- Docker version runs in CI/CD
- Generates HTML/JSON/XML reports

**Integration:**
- Works with GitHub Actions
- Reports as downloadable artifacts
- Can integrate with other tools
- Supports automated scanning

---

## 🚀 Next Steps

1. **Verify mainv2.yml** is in `.github/workflows/`
2. **Push to GitHub** (or trigger manually)
3. **Wait for DAST job** (2-3 minutes)
4. **Download reports** from artifacts
5. **Analyze findings** in HTML report
6. **Fix vulnerabilities** based on recommendations
7. **Re-run scan** to verify improvements

**You're ready to scan!** 🎉
