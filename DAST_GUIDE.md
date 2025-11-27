# OWASP DAST Setup Guide

## 📋 Overview

**DAST (Dynamic Application Security Testing)** scans your running application for security vulnerabilities. Unlike SAST (Static Code Analysis), DAST interacts with the application while it's running.

### **What is OWASP ZAP?**

OWASP ZAP (Zed Attack Proxy) is a free, open-source security tool that:
- Finds security vulnerabilities in web applications
- Performs automated security scanning
- Generates detailed security reports
- Tests for OWASP Top 10 vulnerabilities

---

## 🏗️ Updated Workflow Architecture

```
┌─────────────────────────────────────────────────┐
│ GitHub Actions Workflow                         │
├─────────────────────────────────────────────────┤
│                                                 │
│ 1. sonar (SAST - Static Analysis)               │
│    └─ SonarCloud scans source code             │
│                                                 │
│ 2. dast (DAST - Dynamic Analysis) ← NEW!       │
│    ├─ Start Flask app (port 5000)              │
│    ├─ Health check (verify app running)        │
│    ├─ Run ZAP baseline scan                    │
│    ├─ Generate reports (HTML, JSON, XML)       │
│    └─ Stop Flask app                           │
│                                                 │
│ 3. build (Build & Test)                        │
│    └─ Run pytest                               │
│                                                 │
│ 4. docker (Container Security)                 │
│    ├─ Build Docker image                       │
│    └─ Scan with Trivy                          │
│                                                 │
│ 5. push (Deploy)                               │
│    └─ Push to Docker Hub                       │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 🔍 DAST Job Breakdown

### **Step 1: Start Flask Application**
```yaml
- name: Start Flask Application
  run: |
    python app.py > /tmp/flask.log 2>&1 &
    FLASK_PID=$!
    sleep 3
```

**What happens:**
- Starts Flask app in background
- Redirects output to `/tmp/flask.log`
- Saves process ID for later cleanup
- Waits 3 seconds for app startup

### **Step 2: Health Check**
```yaml
- name: Health Check
  run: |
    curl -s http://localhost:5000/
    # Retries up to 10 times with 2-second intervals
```

**What happens:**
- Verifies Flask app is responding on port 5000
- Retries 10 times (20 seconds total)
- Exits with error if app doesn't start
- Displays Flask logs if startup fails

### **Step 3: Run OWASP ZAP**
```yaml
- name: Run OWASP DAST
  run: |
    docker run --network host \
      ghcr.io/zaproxy/zaproxy:stable \
      zap-baseline.py \
      -t http://localhost:5000 \
      -r zap_baseline_report.html
```

**What happens:**
- Pulls latest ZAP Docker image
- Runs baseline scan against Flask app
- Tests all endpoints for vulnerabilities
- Generates 3 reports (HTML, JSON, XML)

### **Step 4: Parse Results**
```yaml
- name: Parse ZAP Results
  run: python3 << 'EOF'
  # Extracts and displays vulnerability summary
```

**What happens:**
- Reads JSON report
- Counts vulnerabilities by risk level
- Displays summary in GitHub Actions logs
- Shows detected issues

### **Step 5: Upload Artifacts**
```yaml
- name: Upload ZAP Scan Reports
  uses: actions/upload-artifact@v3
```

**What happens:**
- Saves reports as GitHub artifacts
- Reports available for download
- Can be viewed after workflow completes

### **Step 6: Stop Flask Application**
```yaml
- name: Stop Flask Application
  run: kill $FLASK_PID
```

**What happens:**
- Terminates Flask process
- Cleans up resources
- Runs even if previous steps failed

---

## 🎯 What DAST Scans For

### **OWASP Top 10 Vulnerabilities**

| Vulnerability | Detected By | Your App |
|---------------|------------|----------|
| **SQL Injection** | Testing database endpoints | ✅ GET /user |
| **Command Injection** | Testing command execution | ✅ GET /run |
| **Code Injection** | Testing eval/exec usage | ✅ POST /eval |
| **Path Traversal** | Testing file upload | ✅ POST /upload |
| **Insecure Deserialization** | Testing deserialization | ✅ POST /deserialize |
| **Authentication Bypass** | Testing login endpoints | ✅ POST /login |
| **Cross-Site Scripting (XSS)** | Testing input reflection | ✅ All endpoints |
| **Broken Access Control** | Testing authorization | ✅ Protected routes |
| **Security Misconfiguration** | Testing headers/settings | ✅ Flask config |
| **Sensitive Data Exposure** | Testing encryption/TLS | ✅ Data transmission |

---

## 📊 Expected DAST Report

### **GitHub Actions Output:**

```
==========================================
Starting OWASP ZAP Dynamic Security Scan
==========================================
Target: http://localhost:5000
Scan Type: Baseline (Fast)

[SCAN IN PROGRESS]

==========================================
OWASP ZAP Scan Results Summary
==========================================
Total Alerts Found: 15

📊 Vulnerabilities by Risk Level:
  🔴 High: 5
  🟠 Medium: 6
  🟡 Low: 3
  ℹ️  Informational: 1

Detected Issues:
  - SQL Injection
    Risk: High
    URL: http://localhost:5000/user

  - Command Injection
    Risk: High
    URL: http://localhost:5000/run

  - Code Injection
    Risk: High
    URL: http://localhost:5000/eval

  - Path Traversal
    Risk: High
    URL: http://localhost:5000/upload

  - Insecure Deserialization
    Risk: High
    URL: http://localhost:5000/deserialize

...

==========================================
✅ DAST scan completed. Check artifacts for detailed reports.
==========================================
```

### **Generated Reports:**

1. **zap_baseline_report.html** - Visual report (view in browser)
2. **zap_baseline_report.json** - Machine-readable data
3. **zap_baseline_report.xml** - XML format for integration

---

## 🚀 Running DAST Locally

### **Option 1: Using Docker**

```bash
# 1. Start your Flask app
python app.py &

# 2. Wait for app to start
sleep 3

# 3. Run ZAP baseline scan
docker run --rm --network host \
  -v $(pwd):/zap/wrk \
  ghcr.io/zaproxy/zaproxy:stable \
  zap-baseline.py \
  -t http://localhost:5000 \
  -r zap_baseline_report.html

# 4. View report
open zap_baseline_report.html
```

### **Option 2: Using ZAP GUI (Desktop)**

```bash
# 1. Download ZAP from: https://www.zaproxy.org/download/
# 2. Install and launch ZAP
# 3. Set target: http://localhost:5000
# 4. Click "Attack" → "Spider"
# 5. Click "Attack" → "Active Scan"
```

### **Option 3: Using OWASP ZAP Docker Interactive**

```bash
# Start ZAP with API enabled
docker run --rm --network host \
  ghcr.io/zaproxy/zaproxy:stable \
  zap.sh -cmd \
  -quickurl http://localhost:5000 \
  -quickout /zap/wrk/report.html
```

---

## 🔐 Scan Types

### **1. Baseline Scan (Default - Used in Workflow)**
```yaml
zap-baseline.py -t http://localhost:5000
```
- **Speed:** Fast (2-5 minutes)
- **Coverage:** Good (common vulnerabilities)
- **Best for:** CI/CD pipelines
- **Risk Level:** Low (passive + light active scanning)

### **2. Full Scan**
```yaml
zap-full-scan.py -t http://localhost:5000
```
- **Speed:** Slow (15-30 minutes)
- **Coverage:** Comprehensive (all endpoints)
- **Best for:** Detailed security audits
- **Risk Level:** Medium (aggressive scanning)

### **3. API Scan**
```yaml
zap-api-scan.py -t http://localhost:5000/openapi.json
```
- **Speed:** Medium (5-10 minutes)
- **Coverage:** API-focused
- **Best for:** REST/GraphQL APIs
- **Risk Level:** Low

---

## 📝 Workflow Configuration

### **Current Configuration in mainv2.yml**

```yaml
dast:
  runs-on: ubuntu-latest
  needs: sonar
  steps:
    # 1. Checkout code
    # 2. Setup Python
    # 3. Install dependencies
    # 4. Start Flask app (background)
    # 5. Health check (verify app running)
    # 6. Pull ZAP image
    # 7. Run ZAP baseline scan
    # 8. Upload reports as artifacts
    # 9. Parse and display results
    # 10. Stop Flask app (cleanup)
```

### **Key Configuration Options:**

```yaml
# Target URL
-t http://localhost:5000

# Report formats
-r zap_baseline_report.html    # HTML report
-J zap_baseline_report.json    # JSON report
-x zap_baseline_report.xml     # XML report

# Scan options
--self-contained               # Include all resources
--ajax-spider                  # Test AJAX endpoints
--auto-off-on                  # Auto start/stop proxy
```

---

## 🔗 Report Artifacts

### **Where to Find Reports**

1. **GitHub Actions Tab:**
   - Go to: Actions → Workflow Run
   - Click: "dast" job
   - Scroll to: "Upload ZAP Scan Reports" step
   - Click: "zap-scan-reports" artifact
   - Download all reports

2. **Report Files:**
   - `zap_baseline_report.html` - Open in browser
   - `zap_baseline_report.json` - Parse programmatically
   - `zap_baseline_report.xml` - Import to tools

---

## 🛡️ Security Best Practices

### **1. Port Selection**
```yaml
# Use non-standard port
app.run(host='0.0.0.0', port=5000)

# Avoid ports like 80, 443 (might need sudo)
```

### **2. Flask Configuration**
```python
# For DAST testing, disable CSRF in dev
app.config['WTF_CSRF_ENABLED'] = False

# Set debug mode appropriately
if os.getenv('FLASK_ENV') == 'testing':
    app.config['DEBUG'] = False
```

### **3. Timeout Configuration**
```yaml
# Give sufficient timeout for scan
timeout: 300  # 5 minutes

# Add sleep before scan
sleep 5  # Wait for app stability
```

### **4. Report Security**
```yaml
# Artifacts contain sensitive info
# Only download in secure environments
# Don't commit reports to Git
```

---

## ⚠️ Common Issues & Solutions

### **Issue 1: "Connection refused" Error**
```
Error: Failed to connect to http://localhost:5000
```

**Solution:**
```bash
# Increase health check timeout
sleep 5  # Changed from 3 to 5

# Check Flask logs
cat /tmp/flask.log

# Verify port isn't in use
lsof -i :5000
```

### **Issue 2: ZAP Scan Hangs**
```
Scan taking too long, timeout reached
```

**Solution:**
```yaml
# Add timeout to DAST job
timeout-minutes: 10

# Switch to lighter baseline scan (already in workflow)
zap-baseline.py  # Instead of zap-full-scan.py
```

### **Issue 3: False Positives**
```
Report shows many low-risk issues
```

**Solution:**
```bash
# Configure ZAP to ignore certain alerts
# Create zap config file

# Or filter results
grep -i "High" zap_baseline_report.json
```

### **Issue 4: Network Issues in Docker**
```
ZAP can't reach localhost from Docker
```

**Solution:**
```yaml
# Use --network host flag (already in workflow)
--network host

# Or use host.docker.internal on Mac
-t http://host.docker.internal:5000
```

---

## 📈 Integrating Results

### **Option 1: GitHub Security Tab**
```yaml
# Upload SARIF format for GitHub security tab
- name: Upload to GitHub Security Tab
  uses: github/codeql-action/upload-sarif@v2
  with:
    sarif_file: zap_baseline_report.sarif
```

### **Option 2: SonarQube Integration**
```yaml
# Import ZAP results to SonarQube
sonar-scanner \
  -Dsonar.zaproxy.reportPath=zap_baseline_report.json
```

### **Option 3: Slack Notification**
```yaml
- name: Send Slack Notification
  run: |
    curl -X POST ${{ secrets.SLACK_WEBHOOK }} \
      -d '{
        "text": "DAST Scan Complete",
        "attachments": [{
          "color": "danger",
          "text": "High severity issues found"
        }]
      }'
```

---

## 🎓 DAST vs SAST Comparison

| Aspect | SAST (SonarCloud) | DAST (ZAP) |
|--------|------------------|-----------|
| **When** | During development | Runtime |
| **What** | Source code | Running application |
| **Coverage** | All code paths | Reachable endpoints |
| **False Positives** | Lower | Higher |
| **Speed** | Fast | Slow |
| **Setup** | Simple | Complex |
| **Best for** | Code quality | Real-world attacks |

---

## 📚 Additional Resources

- **OWASP ZAP:** https://www.zaproxy.org/
- **ZAP Baseline:** https://www.zaproxy.org/docs/docker/baseline-scan/
- **OWASP Top 10:** https://owasp.org/www-project-top-ten/
- **ZAP API Docs:** https://www.zaproxy.org/docs/api/

---

## ✅ Checklist

- ✅ DAST job added to workflow
- ✅ Flask app starts before scan
- ✅ Health check verifies app running
- ✅ ZAP baseline scan configured
- ✅ Reports generated (HTML, JSON, XML)
- ✅ Results parsed and displayed
- ✅ Artifacts uploaded
- ✅ Flask app stops after scan

**Your DAST pipeline is ready! Push to GitHub and trigger the workflow.** 🚀
