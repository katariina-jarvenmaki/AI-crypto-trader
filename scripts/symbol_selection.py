import importlib

def get_selected_symbols(platform: str, symbol_args: list):
    # Ladataan oikea config-moduuli dynaamisesti
    config_module_name = f"configs.{platform.lower()}_config"
    try:
        platform_config = importlib.import_module(config_module_name)
    except ImportError:
        raise ImportError(f"Config module '{config_module_name}' not found for platform '{platform}'")

    if not hasattr(platform_config, "SUPPORTED_SYMBOLS") or not hasattr(platform_config, "DEFAULT_SYMBOL"):
        raise AttributeError(f"{config_module_name} is missing SUPPORTED_SYMBOLS or DEFAULT_SYMBOL")

    supported_symbols = platform_config.SUPPORTED_SYMBOLS
    default_symbol = platform_config.DEFAULT_SYMBOL

    if symbol_args:
        invalid_symbols = [s for s in symbol_args if s not in supported_symbols]
        if invalid_symbols:
            raise ValueError(f"Unsupported symbols for {platform}: {', '.join(invalid_symbols)}. "
                             f"Supported: {', '.join(supported_symbols)}")
        return symbol_args
    else:
        return [default_symbol]
