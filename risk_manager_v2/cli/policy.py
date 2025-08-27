import click
from datetime import datetime, timezone
from risk_manager_v2.policy.brain import PolicyBrain
from risk_manager_v2.schemas.evaluation_context import EvaluationContext

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
    print(plan)

if __name__ == "__main__":
    cli()
