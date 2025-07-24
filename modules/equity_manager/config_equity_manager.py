# modules/equity_manager/config_equity_manager.py

# Allowed trade margin allocation
ALLOWED_TRADE_MARGIN_PERCENT = 25.0  # Should target to under 25.0

# Stop trading on loss limit
ALLOWED_EQUITY_MARGIN_PERCENT = 2.0 # Keep this under 25.0
ALLOWED_PREV_EQUITY_MARGIN_PERCENT = 18.00 # Keep this under 25.0

# Keep as same as in UI
COPYTRADE_MINIMUM_INVESTMENT = 100.0