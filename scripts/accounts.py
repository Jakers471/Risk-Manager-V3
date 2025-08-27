import os, json, requests
from risk_manager_v2.core.auth import auth_headers
BASE=os.environ["PROJECTX_BASE_URL"]
r=requests.post(f"{BASE}/api/Account/search", headers=auth_headers(), json={}, timeout=(2,5))
print("HTTP", r.status_code); print(r.text)
