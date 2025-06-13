# strategy/strategy_handler.py

class StrategyHandler:
    def __init__(self):
        # This dictionary defines which strategies are allowed in each market state.
        # If a strategy is not listed here, interval-based preference cannot select it.
        self.market_strategies = {
            "bull": {
                "name": "Bull market trend following strategy",
                "actions": ["hold", "hold_short", "swing", "swing_short", "scalp", "grid", "dca"],
                "note": "Using: Bull market trend following strategy"
            },
            "bear": {
                "name": "Bear market shorting strategy",
                "actions": ["hold", "hold_short", "swing", "swing_short", "scalp_short", "grid_short", "dca_short"],
                "note": "Using: Bear market shorting strategy"
            },
            "bull_consolidation": {
                "name": "Breakout anticipation strategy (NO shorts!)",
                "actions": ["hold", "swing", "swing_short", "scalp", "grid", "dca"],
                "note": "Using: Breakout anticipation strategy (NO shorts!)"
            },
            "bear_consolidation": {
                "name": "Breakdown anticipation strategy (NO long positions!)",
                "actions": ["hold_short", "swing", "swing_short", "scalp_short", "grid_short", "dca_short"],
                "note": "Using: Breakdown anticipation strategy (NO long positions!)"
            },
            "neutral_sideways": {
                "name": "Range trading / grid strategy",
                "actions": ["swing", "swing_short", "scalp", "scalp_short", "grid", "grid_short", "dca", "dca_short"],
                "note": "Using: Range trading / grid strategy"
            },
            "volatile": {
                "name": "Volatile market strategies",
                "actions": ["swing", "swing_short", "dca", "dca_short"],
                "note": "Using: Volatile market strategies"
            },
            "unknown": {
                "name": "Unknown market condition",
                "actions": ["hold", "hold_short", "swing", "swing_short", "scalp", "scalp_short", "grid", "grid_short", "dca", "dca_short"],
                "note": "Using: Default strategies"
            }
        }

    def determine_strategy(self, market_state, signal, mode, interval=None):
        preferred = self._get_interval_based_preferences(interval)

        # Convert to short versions if the signal is "sell"
        if signal == "sell":
            preferred = [self._to_short_version(s) for s in preferred]

        strategy_frame = self.market_strategies.get(market_state, self.market_strategies["unknown"])
        allowed = strategy_frame["actions"]

        # Handle override cases
        if mode == "override" or "strong" in mode.lower():
            if signal == "buy" and market_state in ["bear", "unknown"]:
                allowed += ["swing", "grid", "dca", "hold", "scalp"]
            elif signal == "sell" and market_state in ["bull", "unknown"]:
                allowed += ["swing_short", "grid_short", "dca_short", "hold_short", "scalp_short"]

        # Final strategy: intersection of interval-based preferences and allowed actions
        final_actions = [s for s in preferred if s in allowed]

        return {
            "market_strategy": strategy_frame["name"],
            "note": strategy_frame["note"],
            "selected_strategies": final_actions or allowed
        }

    def _get_interval_based_preferences(self, interval):
        if interval is None:
            return ["hold", "swing"]
        try:
            minutes = int(interval.replace("m", "").replace("h", "0"))  # crude parsing
            if "h" in interval:
                minutes = int(interval.replace("h", "")) * 60
        except Exception:
            return ["hold", "swing"]
            
        if minutes < 15:
            return ["scalp", "grid"]
        elif minutes <= 30:
            return ["swing", "grid"]
        elif minutes <= 120:
            return ["swing", "dca"]
        else:
            return ["hold", "swing"]

    def _to_short_version(self, strategy_name):
        if strategy_name.endswith("_short"):
            return strategy_name
        return f"{strategy_name}_short"
