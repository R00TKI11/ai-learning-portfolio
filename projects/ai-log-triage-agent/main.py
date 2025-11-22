#!/usr/bin/env python3
"""
AI Log Triage Agent - Convenience Wrapper

This is a convenience wrapper for running the CLI from the project root.
For installed package usage, use 'ai-log-triage' command or 'python -m ai_log_triage'.

Usage:
    python main.py --input data/webserver_error.log
    python main.py --all --dry-run
"""

import sys

# Add src to path for development mode
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ai_log_triage.cli import main

if __name__ == "__main__":
    sys.exit(main())
