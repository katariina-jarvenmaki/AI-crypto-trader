# main.py

import sys
from scripts.platform_selection import get_selected_platform

# Platform selection
try:
    selected_platform = get_selected_platform(sys.argv[1:])
except ValueError as e:
    print(f"[ERROR] {e}")

# Printing to console
print(f"Selected platform: {selected_platform}")
print("Select coinpair")
