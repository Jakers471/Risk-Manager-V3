from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

@dataclass
class Position:
    symbol: str
    qty: float
    entry_price: float
    unrealized_pnl: float
    side: str  # long|short

@dataclass
class Order:
    id: str
    symbol: str
    side: str
    qty: float
    type: str
    status: str

@dataclass
class EvaluationContext:
    ts: datetime
    account_id: str
    day_pnl: float
    max_drawdown_today: float
    risk_tier: str  # t0|t1|t2
    positions: List[Position] = field(default_factory=list)
    orders: List[Order] = field(default_factory=list)
    env: Dict[str, Any] = field(default_factory=dict)  # market_hours, news, etc.
