import os, json, requests
BASE = os.environ["PROJECTX_BASE_URL"]
TOK  = os.environ.get("PROJECTX_API_KEY","")
hdrs = {"accept":"text/plain","Content-Type":"application/json"}
if TOK: hdrs["Authorization"] = f"Bearer {TOK}"
r = requests.post(f"{BASE}/api/Account/search", headers=hdrs, json={})
print("HTTP", r.status_code)
print(r.text)
