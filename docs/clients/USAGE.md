# ProjectX Client (Agent C)

Expose:
- get_positions(account_id)->List[Position]
- get_orders(account_id)->List[Order]
- get_day_pnl(account_id)->float
- cancel_orders(account_id, symbol?)
- place_market(account_id, symbol, qty, side)

Use env:
- PROJECTX_BASE_URL
- PROJECTX_API_KEY

Simulator: set PX_SIM=1 to bypass network.
