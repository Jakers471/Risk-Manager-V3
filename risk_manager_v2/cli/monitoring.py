"""
MonitoringMenu (start/stop/status + dry-run)
"""
from risk_manager_v2.core.config import ConfigStore
from risk_manager_v2.core.auth import AuthManager
from risk_manager_v2.core.logger import get_logger
try:
    from risk_manager_v2.core.clients.projectx import ProjectXClient
except Exception:
    from risk_manager_v2.core.client import ProjectXClient  # fallback
from risk_manager_v2.engine.monitor import RiskMonitor
try:
    from risk_manager_v2.utils.rate_limiter import TopStepXRateLimiter
except Exception:
    TopStepXRateLimiter = None

class MonitoringMenu:
    def __init__(self):
        self.log = get_logger(__name__)
        self.config = ConfigStore()
        self.auth = AuthManager(self.config)
        self.client = ProjectXClient(self.config, self.auth)
        self.monitor = RiskMonitor()
        self.dry_run = bool(self.config.get("monitor.dry_run", True))
        self.rate_limiter = TopStepXRateLimiter() if TopStepXRateLimiter else None

    def run(self):
        while True:
            self._display_menu()
            c = input("Choice: ").strip()
            if c == "1": self._start()
            elif c == "2": self._stop()
            elif c == "3": self._status()
            elif c == "4": self._toggle_dry_run()
            elif c == "0": break
            else: print("Invalid choice.")

    def _display_menu(self):
        s = "🟢 RUNNING" if self.monitor.is_running() else "🔴 STOPPED"
        print(f"\n=== MONITORING CONTROL [{s}] ===")
        print("1) Start Monitoring")
        print("2) Stop Monitoring")
        print("3) Monitoring Status")
        print(f"4) Toggle Dry Run (currently: {self.dry_run})")
        print("0) Back to main menu")

    def _start(self):
        if self.monitor.is_running(): 
            print("Already running.")
            return
        
        if not self.auth.is_authenticated():
            print("❌ Not authenticated. Use Setup first.")
            return
        
        ok = self.monitor.start_monitoring(self.client, self.rate_limiter, self.dry_run)
        print("✅ Started." if ok else "❌ Failed to start.")

    def _stop(self):
        ok = self.monitor.stop_monitoring()
        print("✅ Stopped." if ok else "❌ Failed to stop.")

    def _status(self):
        st = self.monitor.get_monitoring_status()
        m = st.get("metrics", {})
        print("\n=== STATUS ===")
        print("Status:", st.get("status"))
        print("Accounts:", st.get("monitored_accounts", []))
        print("Evaluations:", m.get("total_evaluations", 0))
        print("Actions:", m.get("total_actions", 0))
        v = m.get("violations_current", {})
        if v:
            print("Current violations by account:")
            for acct, n in v.items():
                print(f"  - {acct} : {n}")
        input("\nPress Enter to continue...")

    def _toggle_dry_run(self):
        self.dry_run = not self.dry_run
        try:
            self.config.set("monitor.dry_run", self.dry_run)
            self.config.save()
        except Exception:
            pass
        
        # Update monitor's dry_run setting
        self.monitor.dry_run = self.dry_run
        
        print("Dry run is now:", self.dry_run)


