
import json
from modules.equity_manager.config_equity_manager import (
    LOG_FILE,
    ALLOWED_EQUITY_MARGIN_PERCENT,
    EQUITY_STOP_LOSS,
    USE_PNL_MARGIN_IF_HIGHER
)

def equity_stoploss():
    allowed_margin = ALLOWED_EQUITY_MARGIN_PERCENT
    stop_loss = EQUITY_STOP_LOSS
    use_pnl_margin = USE_PNL_MARGIN_IF_HIGHER  # True / False

    if allowed_margin is None or stop_loss is None:
        raise ValueError("Konfiguraatiosta puuttuu tarvittavat arvot.")

    margin_difference = stop_loss - allowed_margin 

    if not use_pnl_margin:
        # Käytetään vain konfiguraation erotusta
        return {
            "equity_stoploss": stop_loss,
            "equity_stoploss_margin": margin_difference,
            "equity_stoploss_margin_type": "config_only"
        }

    # Jos käytetään pnl-pohjaista tarkistusta:
    with open(LOG_FILE, "r") as file:
        last_line = None
        for line in file:
            if line.strip():
                last_line = line
        if last_line is None:
            raise ValueError("Logitiedosto on tyhjä.")

        log_data = json.loads(last_line)
        equity = log_data.get("equity")
        pnl = log_data.get("pnl")

        if equity is None or pnl is None:
            raise ValueError("Logiriviltä puuttuu equity tai pnl.")

        # Lasketaan pnl prosenttina equitystä
        pnl_percent = (pnl / equity) * 100 if pnl > 0 else 0

        if pnl_percent > margin_difference:
            used_margin = pnl_percent
            margin_type = "pnl_based"
        else:
            used_margin = margin_difference
            margin_type = "config"

        return {
            "equity_stoploss": stop_loss,
            "equity_stoploss_margin": used_margin,
            "equity_stoploss_margin_type": margin_type
        }
