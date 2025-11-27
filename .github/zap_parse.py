import json
import sys

REPORT_PATH = 'zap-reports/zap_baseline_report.json'

try:
    with open(REPORT_PATH, 'r') as f:
        data = json.load(f)

    alerts = []
    if isinstance(data, dict) and 'site' in data and data['site']:
        alerts = data['site'][0].get('alerts', [])

    total = len(alerts)
    print(f"Total Alerts Found: {total}")

    risk_counts = {'High': 0, 'Medium': 0, 'Low': 0, 'Informational': 0}
    for a in alerts:
        r = a.get('riskdesc', 'Informational').split()[0]
        if r in risk_counts:
            risk_counts[r] += 1

    print('Vulnerabilities by Risk Level:')
    for k in ['High', 'Medium', 'Low', 'Informational']:
        print(f"  {k}: {risk_counts[k]}")

    print('\nTop issues:')
    for alert in alerts[:10]:
        name = alert.get('name', 'Unknown')
        risk = alert.get('riskdesc', 'N/A')
        url = alert.get('instances', [{}])[0].get('uri', 'N/A')
        print(f"- {name} | {risk} | {url}")

except Exception as e:
    print('Error parsing results:', e)
    sys.exit(1)
