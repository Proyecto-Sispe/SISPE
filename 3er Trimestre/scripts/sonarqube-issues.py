#!/usr/bin/env python3
"""Exporta bugs, vulnerabilidades y code smells de SonarQube a CSV y JSON."""
import csv
import json
import os
import sys
import urllib.parse
import urllib.request

BASE_URL = os.getenv("SONAR_HOST_URL", "http://localhost:9000").rstrip("/")
PROJECT_KEY = os.getenv("SONAR_PROJECT_KEY", "sispe-springboot")
TOKEN = os.getenv("SONAR_TOKEN")
OUTPUT_DIR = os.getenv("SONAR_REPORT_DIR", "target/sonarqube")

if not TOKEN:
    raise SystemExit("Define SONAR_TOKEN con un token de SonarQube antes de exportar la matriz.")

issues = []
page = 1
while True:
    query = urllib.parse.urlencode({
        "componentKeys": PROJECT_KEY,
        "resolved": "false",
        "types": "BUG,VULNERABILITY,CODE_SMELL",
        "ps": 500,
        "p": page,
    })
    request = urllib.request.Request(
        f"{BASE_URL}/api/issues/search?{query}",
        headers={"Authorization": f"Bearer {TOKEN}"},
    )
    with urllib.request.urlopen(request) as response:
        payload = json.load(response)
    issues.extend(payload.get("issues", []))
    paging = payload.get("paging", {})
    if page * paging.get("pageSize", 500) >= paging.get("total", 0):
        break
    page += 1

os.makedirs(OUTPUT_DIR, exist_ok=True)
fields = ["key", "type", "severity", "status", "message", "component", "line", "rule", "creationDate"]
rows = [{field: issue.get(field, "") for field in fields} for issue in issues]
with open(os.path.join(OUTPUT_DIR, "matriz-hallazgos.csv"), "w", newline="", encoding="utf-8") as output:
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
with open(os.path.join(OUTPUT_DIR, "matriz-hallazgos.json"), "w", encoding="utf-8") as output:
    json.dump(rows, output, ensure_ascii=False, indent=2)
print(f"Exportados {len(rows)} hallazgos a {OUTPUT_DIR}")
