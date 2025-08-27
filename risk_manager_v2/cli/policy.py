import click
from datetime import datetime, timezone
from risk_manager_v2.policy.brain import PolicyBrain
from risk_manager_v2.schemas.evaluation_context import EvaluationContext, Position

@click.group()
def cli():
    ...

@cli.command()
def selftest():
    """Smoke-test policy defaults."""
    brain = PolicyBrain()
    ctx = EvaluationContext(
        ts=datetime.now(timezone.utc),
        account_id="demo",
        day_pnl=0.0,
        max_drawdown_today=0.0,
        risk_tier="t0",
        positions=[], orders=[], env={}
    )
    plan = brain.evaluate(ctx)
    print("=== Basic Selftest ===")
    print(f"Plan: {plan}")

@cli.command()
def scenarios():
    """Test 3 policy scenarios with detailed output."""
    brain = PolicyBrain()
    
    print("=== Policy Brain Scenarios Test ===\n")
    
    # Scenario 1: Loss Breach
    print("1. DAILY LOSS BREACH SCENARIO")
    print("-" * 40)
    ctx1 = EvaluationContext(
        ts=datetime.now(timezone.utc),
        account_id="demo",
        day_pnl=-200.0,  # Breaches t0 limit of -150
        max_drawdown_today=-250.0,
        risk_tier="t0",
        positions=[
            Position(symbol="ES", qty=2, entry_price=4500.0, unrealized_pnl=-150.0, side="long"),
            Position(symbol="NQ", qty=1, entry_price=15000.0, unrealized_pnl=-50.0, side="short")
        ],
        orders=[],
        env={}
    )
    plan1 = brain.evaluate(ctx1)
    print(f"Context: Day PnL=${ctx1.day_pnl}, Risk Tier={ctx1.risk_tier}")
    print(f"Actions: {len(plan1.actions)}")
    for action in plan1.actions:
        print(f"  - {action.kind}: {action.reason} ({action.severity})")
    print(f"Notes: {plan1.notes}")
    print()
    
    # Scenario 2: Oversize
    print("2. OVERSIZE SCENARIO")
    print("-" * 40)
    ctx2 = EvaluationContext(
        ts=datetime.now(timezone.utc),
        account_id="demo",
        day_pnl=50.0,
        max_drawdown_today=-25.0,
        risk_tier="t1",
        positions=[
            Position(symbol="ES", qty=3, entry_price=4500.0, unrealized_pnl=75.0, side="long"),  # Exceeds t1 limit of 2
        ],
        orders=[],
        env={}
    )
    plan2 = brain.evaluate(ctx2)
    print(f"Context: Day PnL=${ctx2.day_pnl}, Risk Tier={ctx2.risk_tier}")
    print(f"Actions: {len(plan2.actions)}")
    for action in plan2.actions:
        print(f"  - {action.kind}: {action.reason} ({action.severity})")
    print(f"Notes: {plan2.notes}")
    print()
    
    # Scenario 3: News Blackout
    print("3. NEWS BLACKOUT SCENARIO")
    print("-" * 40)
    ctx3 = EvaluationContext(
        ts=datetime.now(timezone.utc),
        account_id="demo",
        day_pnl=25.0,
        max_drawdown_today=-10.0,
        risk_tier="t2",
        positions=[
            Position(symbol="ES", qty=1, entry_price=4500.0, unrealized_pnl=25.0, side="long"),
        ],
        orders=[],
        env={"news_minutes_ago": 5}  # Within t2 blackout period of 30 min
    )
    plan3 = brain.evaluate(ctx3)
    print(f"Context: Day PnL=${ctx3.day_pnl}, Risk Tier={ctx3.risk_tier}")
    print(f"Actions: {len(plan3.actions)}")
    for action in plan3.actions:
        print(f"  - {action.kind}: {action.reason} ({action.severity})")
    print(f"Notes: {plan3.notes}")
    print()
    
    # Scenario 4: All Clear
    print("4. ALL CLEAR SCENARIO")
    print("-" * 40)
    ctx4 = EvaluationContext(
        ts=datetime.now(timezone.utc),
        account_id="demo",
        day_pnl=100.0,
        max_drawdown_today=-15.0,
        risk_tier="t0",
        positions=[
            Position(symbol="ES", qty=1, entry_price=4500.0, unrealized_pnl=100.0, side="long"),
        ],
        orders=[],
        env={"news_minutes_ago": 45, "session_minutes_left": 120}
    )
    plan4 = brain.evaluate(ctx4)
    print(f"Context: Day PnL=${ctx4.day_pnl}, Risk Tier={ctx4.risk_tier}")
    print(f"Actions: {len(plan4.actions)}")
    for action in plan4.actions:
        print(f"  - {action.kind}: {action.reason} ({action.severity})")
    print(f"Notes: {plan4.notes}")
    print()

if __name__ == "__main__":
    cli()
