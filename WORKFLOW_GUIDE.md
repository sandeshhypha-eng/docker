# GitHub Actions Workflow - SonarQube Scan Guide

## 🆕 New Features Added

### 1. **Manual Workflow Dispatch** 🎯
You can now manually trigger the workflow from GitHub with file selection:

```
On: Manual Trigger (workflow_dispatch)
```

### 2. **File Selection Input** 📁
Choose which file to analyze:
- `app.py` - Original file with vulnerabilities
- `app_fixed.py` - Secure version with all fixes

### 3. **GitHub Actions Results Display** 📊
Results are displayed directly in GitHub Actions logs

---

## 🚀 How to Use

### **Step 1: Manual Trigger (Dispatch)**

1. Go to your GitHub repository
2. Click **Actions** tab
3. Select **SonarCloud Scan** workflow
4. Click **Run workflow**
5. Select your target file:
   - ✅ `app.py` (to scan vulnerable version)
   - ✅ `app_fixed.py` (to scan fixed version)
6. Click **Run workflow**

### **Step 2: View Results in GitHub Actions**

1. The workflow runs automatically
2. Check the logs under **Fetch SonarQube Analysis Results** step
3. You'll see:
   ```
   ==========================================
   SonarQube Analysis Results
   ==========================================
   Scanning: app.py (or app_fixed.py)
   Status: ✅ Scan Completed
   ==========================================
   
   📊 Quality Gates:
   - Security Rating: Check SonarQube Dashboard
   - Code Coverage: Check SonarQube Dashboard
   - Security Hotspots: Check SonarQube Dashboard
   
   🔗 View Results:
   URL: https://sonarcloud.io/projects
   Project: sandeshhypha-eng_docker
   ```

### **Step 3: View Detailed Results in SonarQube Cloud**

1. Visit: https://sonarcloud.io/projects
2. Click: **sandeshhypha-eng_docker**
3. View issues:
   - **Issues tab** - All vulnerabilities
   - **Security Hotspots** - Security concerns
   - **Code Coverage** - Test coverage

---

## 📋 Workflow Configuration

### **Trigger Events:**
```yaml
on:
  push:           # Automatic on push to main
    branches:
      - main
  pull_request:   # Automatic on pull requests
  workflow_dispatch:  # Manual trigger with inputs
    inputs:
      target_file:
        description: 'Select which file to analyze'
        required: true
        default: 'app.py'
        type: choice
        options:
          - app.py
          - app_fixed.py
```

### **Jobs:**
1. **sonar** - Runs SonarQube scan (required)
2. **build** - Builds application (depends on sonar)
3. **docker** - Builds and pushes Docker image (depends on build)

---

## 🔍 Expected Results Comparison

### **app.py (Vulnerable Version)**
```
✅ Issues Found: 5 Blockers
- SQL Injection
- Command Injection  
- Code Injection (eval)
- Path Traversal
- Insecure Deserialization

Security Rating: E (Worst)
Coverage: 0%
```

### **app_fixed.py (Secure Version)**
```
✅ Issues Found: 0 Blockers (Fixed)
- Parameterized SQL queries
- Command whitelist + shell=False
- ast.literal_eval() instead of eval()
- secure_filename() + validation
- JSON deserialization instead of pickle

Security Rating: A (Best)
Coverage: Still 0% (needs unit tests)
```

---

## 🔐 Security Best Practices

### **Environment Secrets**
The workflow now supports secure token handling:

```yaml
env:
  SONAR_TOKEN: ${{ secrets.SONAR_TOKEN || 'fallback' }}
```

**To set it properly in GitHub:**
1. Go to: Settings → Secrets and variables → Actions
2. Add: `SONAR_TOKEN` with your SonarCloud token
3. Add: `DOCKER_USERNAME` and `DOCKER_PASSWORD`

---

## 📊 Sample GitHub Actions Output

```
===========================================
SonarQube Scan Configuration
===========================================
Target File: app.py
Project Key: sandeshhypha-eng_docker
Organization: sandeshhypha-eng
===========================================

Selected file: app.py
✅ File exists

===========================================
SonarQube Analysis Results
===========================================
Scanning: app.py
Status: ✅ Scan Completed
===========================================

📊 Quality Gates:
- Security Rating: Check SonarQube Dashboard
- Code Coverage: Check SonarQube Dashboard
- Security Hotspots: Check SonarQube Dashboard

🔗 View Results:
URL: https://sonarcloud.io/projects
Project: sandeshhypha-eng_docker

📋 To see detailed issues:
1. Go to: https://sonarcloud.io/projects
2. Click: sandeshhypha-eng_docker
3. Click: Issues tab
===========================================
```

---

## 💡 Tips & Tricks

### **Compare Versions**
1. Run scan with `app.py` → See vulnerabilities
2. Run scan with `app_fixed.py` → See improvements
3. Compare results in SonarQube dashboard

### **Automate Testing**
Add to your build job:
```yaml
- name: Run Tests
  run: pytest tests/ --cov=app
```

### **Add Code Coverage**
```yaml
- name: SonarQube Coverage Report
  run: |
    sonar-scanner \
      -Dsonar.coverage.exclusions=tests/**
```

---

## 🆘 Troubleshooting

### **File Not Found Error**
```
Error: app_fixed.py not found!
```
**Solution:** Ensure the file exists in the repository root

### **SONAR_TOKEN Invalid**
```
Failed to authenticate with SonarCloud
```
**Solution:** 
1. Add token to GitHub Secrets
2. Update workflow to use: `${{ secrets.SONAR_TOKEN }}`

### **No Results Displayed**
```
Quality Gates: Check SonarQube Dashboard
```
**Solution:**
1. Wait 2-3 minutes for SonarCloud to process
2. Refresh: https://sonarcloud.io/projects
3. Check project is linked to repository

---

## 📝 Next Steps

1. ✅ Push changes to `main` branch
2. ✅ Go to Actions tab
3. ✅ Manually trigger workflow with file selection
4. ✅ View results in GitHub Actions logs
5. ✅ Compare results on SonarCloud dashboard
6. ✅ Review security improvements
