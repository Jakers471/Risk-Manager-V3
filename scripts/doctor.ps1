param([switch]$Live)

Write-Host "== Risk Manager Doctor ==" -ForegroundColor Cyan

# Show key env (mask token)
function Mask([string]$s){ if(-not $s){return "<empty>"} if($s.Length -gt 12){ return $s.Substring(0,12) + "..."} return $s }
$info = [ordered]@{
  PX_SIM             = $env:PX_SIM
  PROJECTX_BASE_URL  = $env:PROJECTX_BASE_URL
  PROJECTX_API_KEY   = Mask($env:PROJECTX_API_KEY)
  ACCT               = $env:ACCT
  PX_CONNECT_TIMEOUT = $env:PX_CONNECT_TIMEOUT
  PX_READ_TIMEOUT    = $env:PX_READ_TIMEOUT
}
$info.GetEnumerator() | ForEach-Object { "{0} = {1}" -f $_.Key,$_.Value } | Out-Host

# Check client endpoints
Write-Host "--- endpoints in core/client.py ---" -ForegroundColor Yellow
Select-String -Path .\risk_manager_v2\core\client.py `
  -Pattern "/api/Position/searchOpen|/api/Order/search|/api/Trade/search|/api/Order/place" `
  | ForEach-Object { $_.Line } | Out-Host

# Prepare artifacts
New-Item -ItemType Directory -Force -Path artifacts\doctor | Out-Null

# Policy selftest (always quick)
python -m risk_manager_v2.cli.policy selftest *> artifacts\doctor\policy.txt

# Engine one bounded tick
if ($Live) { $env:PX_SIM="0" } else { $env:PX_SIM="1" }
python -m risk_manager_v2.cli.monitoring tick --max-ticks 1 *> artifacts\doctor\engine.txt

# Live account list (only if -Live)
if ($Live) {
  @'
import os, requests
from risk_manager_v2.core.auth import auth_headers
BASE=os.environ.get("PROJECTX_BASE_URL","https://api.topstepx.com")
r=requests.post(f"{BASE}/api/Account/search", headers=auth_headers(), json={}, timeout=(2,5))
print("HTTP", r.status_code); print(r.text)
'@ | Set-Content -Encoding UTF8 scripts\accounts.py
  python .\scripts\accounts.py *> artifacts\doctor\accounts.txt
}

Write-Host "== Saved outputs to artifacts\doctor ==" -ForegroundColor Green
Get-ChildItem artifacts\doctor | Out-Host
