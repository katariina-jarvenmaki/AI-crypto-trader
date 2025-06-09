# scripts/platform_selection.py

from configs.config import SUPPORTED_PLATFORMS, DEFAULT_PLATFORM

# Create a case-insensitive mapping
platform_lookup = {p.lower(): p for p in SUPPORTED_PLATFORMS}

def get_selected_platform(arg_list):
    if len(arg_list) > 0:
        user_input = arg_list[0].lower()
        if user_input in platform_lookup:
            return platform_lookup[user_input]
        else:
            raise ValueError(f"Unsupported platform '{arg_list[0]}'. Supported: {', '.join(SUPPORTED_PLATFORMS)}")
    return DEFAULT_PLATFORM
