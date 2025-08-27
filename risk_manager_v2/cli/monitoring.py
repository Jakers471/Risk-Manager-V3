import time
import click
from risk_manager_v2.engine.monitor import RiskMonitor

@click.group()
def cli(): ...

@cli.command()
@click.option("--max-ticks", default=1, show_default=True, type=int, help="How many ticks to run")
@click.option("--interval",  default=5, show_default=True, type=float, help="Seconds between ticks")
def tick(max_ticks: int, interval: float):
    """Run monitoring/evaluation/enforcement for a bounded number of ticks."""
    mon = RiskMonitor()
    try:
        for _ in range(max_ticks):
            mon.tick()
            if max_ticks > 1:
                time.sleep(interval)
    except KeyboardInterrupt:
        print("Stopped by user.")

if __name__ == "__main__":
    cli()
