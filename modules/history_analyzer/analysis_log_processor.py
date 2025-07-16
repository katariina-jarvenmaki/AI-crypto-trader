
def process_log_entry(entry: dict):

    # Määritä haluttu tulostusjärjestys (analyysipainotteinen)
    priority_keys = [
        # Perustiedot
        "symbol",
        "timestamp",

        # --- Analyysi: Hinta ja muutokset ---
        "price",
        "price_change",
        "price_change_percent",

        # --- RSI ---
        "avg_rsi_all",
        "rsi_change",
        "rsi_change_percent",

        # --- EMA RSI ---
        "ema_rsi",
        "ema_rsi_change",
        "ema_rsi_change_percent",

        # --- MACD ---
        "macd_diff",
        "macd_diff_change",
        "macd_diff_change_percent",

        # --- Trendit ja tilat ---
        "macd_trend",
        "bollinger_status",
        "ema_trend",
        "signal_strength",
        "flag",

        # --- Muut analyysit ---
        "turnover_status",
        "rsi_divergence",
        "rsi_delta",

        # --- Perusdatan indikaattorit ---
        "change_24h",
        "high_price",
        "low_price",
        "volume",
        "turnover",

        # --- Tekninen rakenne (sarjalliset aikajaksot) ---
        "rsi",
        "ema",
        "macd",
        "macd_signal",
        "bb_upper",
        "bb_lower",
    ]

    print("=== Log Entry ===")
    
    # Tulosta analyysipainotteiset kentät ensin
    for key in priority_keys:
        if key in entry:
            print(f"{key}: {entry[key]}")

    # Tulosta loput kentät, joita ei käsitelty vielä
    remaining_keys = [k for k in entry if k not in priority_keys]
    if remaining_keys:
        print("\n--- Additional Data ---")
        for key in sorted(remaining_keys):  # valinnainen: aakkosjärjestys
            print(f"{key}: {entry[key]}")
    
    print("\n")

def analysis_log_processor(parsed_entries, analysis_results):

    analysis_dict = {entry['symbol']: entry for entry in analysis_results}

    for entry in parsed_entries:
        symbol = entry.get('symbol')
        analysis_data = analysis_dict.get(symbol)

        if analysis_data:
            merged_entry = {**entry, **analysis_data}
            process_log_entry(merged_entry)

