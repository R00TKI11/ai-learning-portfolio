"""
AI Log Triage Agent - Package Entry Point

This module allows the package to be executed as:
    python -m ai_log_triage
"""

import sys
from .cli import main

if __name__ == "__main__":
    sys.exit(main())
