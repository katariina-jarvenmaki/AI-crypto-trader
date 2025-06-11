# scripts/signal_loggeer.py
from datetime import datetime
from configs.config import SIGNAL_LOG_TEXT

def log_signal(signal_type: str, source: str, extra_info: dict = None):
    """Writes signal to the log and then prints message to console."""
    from configs.config import TIMEZONE
    now = datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S %Z")
    message = f"[{now}] SIGNAL from {source}: {signal_type.upper()}"

    if extra_info:
        details = " | ".join(f"{k}: {v}" for k, v in extra_info.items())
        message += f" | {details}"

    print(message)

    with open(SIGNAL_LOG_TEXT, "a") as f:
        f.write(message + "\n")