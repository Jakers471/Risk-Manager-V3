from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class Action:
    kind: str           # flatten | reduce | cancel_orders | lockout | noop
    symbol: str = ""
    qty: float = 0.0
    reason: str = ""
    severity: str = "info"  # info|warn|crit

@dataclass
class ActionPlan:
    correlation_id: str
    actions: List[Action] = field(default_factory=list)
    notes: Dict[str, str] = field(default_factory=dict)  # extra explanations
