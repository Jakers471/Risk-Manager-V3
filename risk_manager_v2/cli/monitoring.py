import click
from risk_manager_v2.engine.monitor import run_monitor_once

@click.group()
def cli(): ...

@cli.command()
def tick():
    """Run one monitoring/evaluation/enforcement tick."""
    run_monitor_once()

if __name__ == "__main__":
    cli()
