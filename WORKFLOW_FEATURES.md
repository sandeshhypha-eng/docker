# Workflow Feature Comparison

## 🎯 What's New

### **Before vs After**

| Feature | Before | After |
|---------|--------|-------|
| **Trigger Type** | Push & PR only | Push, PR, & Manual (workflow_dispatch) |
| **File Selection** | Fixed to all files | Choose app.py or app_fixed.py |
| **Results Display** | Only in SonarQube | In GitHub Actions + SonarQube |
| **Manual Testing** | ❌ Not possible | ✅ Yes, click "Run workflow" |
| **Configuration** | Static | Dynamic with inputs |

---

## 🚀 How to Trigger Workflow

### **Method 1: Automatic (Push)**
```
1. Edit any file
2. git push origin main
3. ✅ Workflow runs automatically
```

### **Method 2: Automatic (Pull Request)**
```
1. Create Pull Request to main
2. ✅ Workflow runs automatically
```

### **Method 3: Manual Dispatch (NEW!) 🆕**
```
1. Go to GitHub → Actions tab
2. Select "SonarCloud Scan" workflow
3. Click "Run workflow" button
4. Select target file (app.py or app_fixed.py)
5. Click "Run workflow"
6. ✅ Workflow runs with your selection
```

---

## 📊 GitHub Actions Interface

### **Manual Trigger Screen**

```
┌─────────────────────────────────────────┐
│ Run workflow                            │
├─────────────────────────────────────────┤
│ Branch: main                            │
│                                         │
│ Select which file to analyze *          │
│ ○ app.py (default)                      │
│ ○ app_fixed.py                          │
│                                         │
│ [Run workflow]                          │
└─────────────────────────────────────────┘
```

### **Workflow Logs Output**

```
✅ Display Target File Information
   Target File: app.py
   Project Key: sandeshhypha-eng_docker
   Organization: sandeshhypha-eng

✅ Select File for Analysis
   Selected file: app.py
   ✅ File exists

✅ Run SonarCloud Scan
   Analyzing: app.py
   Status: ✅ Scan Completed

✅ Fetch SonarQube Analysis Results
   ==========================================
   SonarQube Analysis Results
   ==========================================
   Scanning: app.py
   Status: ✅ Scan Completed
   ==========================================
   
   📊 Quality Gates:
   - Security Rating: Check SonarQube Dashboard
   - Code Coverage: Check SonarQube Dashboard
   
   🔗 View Results:
   URL: https://sonarcloud.io/projects
   Project: sandeshhypha-eng_docker
   ==========================================
```

---

## 🔄 Complete Workflow Flow

```
┌─ On: push to main
├─ On: pull_request
└─ On: workflow_dispatch (MANUAL) ← NEW!
       └─ Input: target_file
           ├─ app.py (vulnerable)
           └─ app_fixed.py (secure)
           
           ↓
           
       Job: sonar
       ├─ Checkout code
       ├─ Setup Python 3.12
       ├─ Install dependencies
       ├─ Display Target File Info ← NEW!
       ├─ Select File for Analysis ← NEW!
       ├─ Setup Java 17
       ├─ Install SonarScanner
       ├─ Run SonarCloud Scan
       └─ Fetch & Display Results ← NEW!
       
           ↓
           
       Job: build (depends on sonar)
       ├─ Checkout code
       ├─ Setup Python
       ├─ Install dependencies
       └─ Run tests (if available)
       
           ↓
           
       Job: docker (depends on build)
       ├─ Checkout code
       ├─ Build Docker image
       ├─ Scan with Trivy
       ├─ Login to Docker Hub
       └─ Push image
```

---

## 📈 Results Comparison Example

### **Scan app.py (Vulnerable)**

```
GitHub Actions Log Output:
========================================
SonarQube Scan Configuration
========================================
Target File: app.py
Project Key: sandeshhypha-eng_docker
Organization: sandeshhypha-eng
========================================

Selected file: app.py
Status: ✅ Scan Completed

📊 Quality Gates:
- Security Rating: E (from SonarQube)
- New Issues: 5
- Security Hotspots: 10

🔗 View Results:
https://sonarcloud.io/dashboard?id=sandeshhypha-eng_docker
```

### **Scan app_fixed.py (Secure)**

```
GitHub Actions Log Output:
========================================
SonarQube Scan Configuration
========================================
Target File: app_fixed.py
Project Key: sandeshhypha-eng_docker
Organization: sandeshhypha-eng
========================================

Selected file: app_fixed.py
Status: ✅ Scan Completed

📊 Quality Gates:
- Security Rating: A (from SonarQube)
- New Issues: 0
- Security Hotspots: 0 (Fixed!)

🔗 View Results:
https://sonarcloud.io/dashboard?id=sandeshhypha-eng_docker
```

---

## 🎓 Step-by-Step: Running Manual Scan

### **Step 1: Navigate to Workflow**
```
GitHub Repository
  └─ Actions tab
     └─ SonarCloud Scan (left sidebar)
```

### **Step 2: Trigger Workflow**
```
Click: "Run workflow" dropdown button
```

### **Step 3: Select File**
```
Choose one:
- app.py (original with vulnerabilities)
- app_fixed.py (secure version)
```

### **Step 4: Start Scan**
```
Click: "Run workflow" button
```

### **Step 5: View Progress**
```
Workflow runs (takes 2-3 minutes)
Check these steps:
- Display Target File Information
- Select File for Analysis
- Run SonarCloud Scan
- Fetch SonarQube Analysis Results
```

### **Step 6: View Detailed Results**
```
Click: "Fetch SonarQube Analysis Results" step
Scroll to see output with:
- File being scanned
- Quality gate status
- Link to SonarQube dashboard
```

### **Step 7: Compare on SonarQube**
```
Visit: https://sonarcloud.io/projects
Project: sandeshhypha-eng_docker
Compare:
- Issues tab (5 vs 0)
- Security Hotspots (10 vs 0)
- Code Quality (E vs A)
```

---

## 💻 Workflow YAML Structure

```yaml
name: SonarCloud Scan

on:
  push:
    branches: [main]
  pull_request:
  workflow_dispatch:           # ← Manual trigger
    inputs:                    # ← User inputs
      target_file:            # ← Input name
        description: 'Select which file to analyze'
        required: true
        default: 'app.py'
        type: choice
        options:              # ← Dropdown options
          - app.py
          - app_fixed.py

jobs:
  sonar:
    steps:
      # Display configuration
      # Select file
      # Run scan
      # Display results (GITHUB ACTIONS OUTPUT) ← NEW!
```

---

## 🔐 Security Notes

✅ **Environment Variables:**
- `SONAR_TOKEN` - Use GitHub Secrets
- `DOCKER_USERNAME` - Use GitHub Secrets
- `DOCKER_PASSWORD` - Use GitHub Secrets

✅ **File Selection:**
- Only allows predefined files (app.py, app_fixed.py)
- Validates file exists before scanning
- Prevents arbitrary file selection

✅ **Results Display:**
- GitHub Actions logs (public)
- SonarQube dashboard (with access control)
- No sensitive data exposed

---

## 📞 Support & Troubleshooting

### **Q: Can I add more file options?**
A: Yes! Edit `workflow_dispatch.inputs.target_file.options` in main.yml

### **Q: Why doesn't it show real-time issue count?**
A: GitHub Actions can't directly query SonarQube API without additional setup. Use the dashboard link for detailed metrics.

### **Q: Can I run specific tests?**
A: Yes! Add to the build job:
```yaml
- name: Run Specific Tests
  run: pytest tests/test_security.py -v
```

### **Q: How do I compare app.py vs app_fixed.py?**
A: 
1. Run workflow with app.py, note the issues
2. Run workflow with app_fixed.py, note the improvement
3. Visit SonarQube dashboard to see metrics
