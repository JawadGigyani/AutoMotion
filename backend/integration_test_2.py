import time
import requests
import json

base_url = "http://localhost:8000"
url = f"{base_url}/api/generate"
data = {"repo_url": "https://github.com/Abubakar0011/FYP-Agentic-Exam-Generation"}

print("Starting integration test...")
resp = requests.post(url, json=data)
if not resp.ok:
    print(f"Error starting: {resp.text}")
    exit(1)

job_id = resp.json().get("job_id")
print(f"Started job: {job_id}")

while True:
    status_resp = requests.get(f"{base_url}/api/status/{job_id}")
    status = status_resp.json()
    print(f"Status: {status.get('status')} | Step: {status.get('step')} | message: {status.get('message')}")
    if status.get('status') in ('completed', 'failed'):
        print(f"Final state: {json.dumps(status, indent=2)}")
        break
    time.sleep(10)
