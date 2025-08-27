from typing import List, Dict, Any, Optional
import os
from risk_manager_v2.schemas.evaluation_context import Position, Order

class ProjectXClient:
    def __init__(self, base_url: Optional[str]=None, api_key: Optional[str]=None):
        self.base_url = base_url or os.getenv("PROJECTX_BASE_URL","")
        self.api_key  = api_key  or os.getenv("PROJECTX_API_KEY","")

    # --- REST stubs (replace with real calls) ---
    def get_positions(self, account_id: str) -> List[Position]:
        return []

    def get_orders(self, account_id: str) -> List[Order]:
        return []

    def get_day_pnl(self, account_id: str) -> float:
        return 0.0

    def cancel_orders(self, account_id: str, symbol: Optional[str]=None) -> Dict[str,Any]:
        return {"status":"ok"}

    def place_market(self, account_id: str, symbol: str, qty: float, side: str) -> Dict[str,Any]:
        return {"status":"ok"}

    # --- Simulator fallback for off-hours ---
    def simulator(self) -> bool:
        return os.getenv("PX_SIM", "0") == "1"
