# utils/get_symbols_to_use.py
# version 2.0, aug 2025

from utils.load_latest_entry import load_latest_entry

def get_symbols_to_use(module_config, module_log_path, mode=None):

    """
    Returns the set of symbols that should be used in the current context.

    Returns:
        {
            "message": str,              # A message describing what was done
            "symbols_to_trade": set[str],  # The final set of symbols to be used
            "all_symbols": set[str]      # All discovered symbols (before any mode-based filtering)
        }

    mode (optional):
    - "long_only": removes symbols from 'potential_to_short'
    - "short_only": removes symbols from 'potential_to_long'
    - "no_trade": returns an empty set of symbols_to_trade
    - None: returns all the symbols without limits 
    """

    symbol_keys = module_config['task_config']['symbol_keys']
    latest_entry = load_latest_entry(
        file_path=module_log_path,
        limit=1,
        use_timestamp=True
    )

    all_symbols = set()
    exclude_symbols = set()
    message = ""

    if latest_entry and isinstance(latest_entry, list) and isinstance(latest_entry[0], dict):
        entry = latest_entry[0]
        for key in symbol_keys:
            symbols = entry.get(key, [])
            if symbols:
                print(f"🔍 {key}: {symbols[:5]}... ({len(symbols)} total)")
            all_symbols.update(symbols)

        if mode == "long_only":
            exclude_symbols = set(entry.get("potential_to_short", []))
            message = f"🟢 Long-only mode: excluded {len(exclude_symbols)} short candidates."
        elif mode == "short_only":
            exclude_symbols = set(entry.get("potential_to_long", []))
            message = f"🔴 Short-only mode: excluded {len(exclude_symbols)} long candidates."
        elif mode == "no_trade":
            message = "⏸️  No-trade mode: not using any symbols."
        else:
            message = "✅ No mode: No current manual limits on trade."

    if not all_symbols:
        fallback_symbols = module_config.get("main_symbols", [])
        all_symbols.update(fallback_symbols)
        message = "⚠️ No valid symbols found in log. Falling back to main_symbols."

    if mode == "no_trade":
        symbols_to_trade = set()
    else:
        symbols_to_trade = all_symbols - exclude_symbols

    return {
        "message": message,
        "symbols_to_trade": symbols_to_trade,
        "all_symbols": all_symbols
    }

if __name__ == "__main__":

    from utils.load_configs_and_logs import load_configs_and_logs

    configs_and_logs = load_configs_and_logs([
        {
            "name": "symbol",
            "mid_folder": "analysis",
            "module_key": "symbol_data_fetcher",
            "extension": ".jsonl",
            "return": ["config", "full_log_path", "full_temp_log_path"]
        }
    ])

    # Asetetaan tarvittavat muuttujat aiemmista arvoista
    module_config = configs_and_logs["symbol_config"]
    module_log_path = configs_and_logs["symbol_full_log_path"]
    general_config = configs_and_logs["general_config"]

    mode = None
    # mode = "long_only"
    # mode = "short_only"
    # mode = "no_trade"

    result = get_symbols_to_use(module_config, module_log_path, mode=mode)
    print(f"Result:\n{result}")
