param([string]$m = "wip")
python -m risk_manager_v2.cli.policy selftest
python -m risk_manager_v2.cli.monitoring tick
git add -A
git commit -m $m
git push
