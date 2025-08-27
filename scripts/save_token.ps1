param([string]$Token="")
if (-not $Token) { Write-Host "Usage: .\scripts\save_token.ps1 -Token <JWT>"; exit 1 }
New-Item -ItemType Directory -Force -Path runtime | Out-Null
@{"token"="$Token"} | ConvertTo-Json | Out-File -Encoding utf8 runtime\auth.json
Write-Host "Saved token to runtime\auth.json"
