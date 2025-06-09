from datetime import datetime
import os

LOG_FILE = "signals.log"

def log_signal(signal_type: str, source: str, extra_info: dict = None):
    """Kirjaa signaalin tiedostoon ja tulostaa sen konsoliin."""
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    message = f"[{now}] SIGNAL from {source}: {signal_type.upper()}"

    if extra_info:
        details = " | ".join(f"{k}: {v}" for k, v in extra_info.items())
        message += f" | {details}"

    print(message)

    # Luo logitiedosto, jos sitä ei ole
    with open(LOG_FILE, "a") as f:
        f.write(message + "\n")