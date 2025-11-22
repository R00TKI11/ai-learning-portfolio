#!/usr/bin/env python3
"""
Run the AI Log Triage Agent API server

This script starts the FastAPI server using uvicorn.

SPDX-License-Identifier: MIT
Copyright (c) 2025 R00TKI11

Usage:
    python run_api.py                    # Development mode with auto-reload
    python run_api.py --production       # Production mode
    python run_api.py --port 5000        # Custom port
"""

import argparse
import sys
from pathlib import Path

# Add src to path for development mode
sys.path.insert(0, str(Path(__file__).parent / "src"))


def main():
    parser = argparse.ArgumentParser(
        description="Run the AI Log Triage Agent API server"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )
    parser.add_argument(
        "--production",
        action="store_true",
        help="Run in production mode (no auto-reload)"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes (production only, default: 1)"
    )

    args = parser.parse_args()

    try:
        import uvicorn
    except ImportError:
        print("Error: uvicorn is not installed.")
        print("Install it with: pip install uvicorn[standard]")
        sys.exit(1)

    # Configuration
    config = {
        "app": "ai_log_triage.api:app",
        "host": args.host,
        "port": args.port,
    }

    if args.production:
        print(f"Starting API server in PRODUCTION mode on {args.host}:{args.port}")
        print(f"Workers: {args.workers}")
        config.update({
            "workers": args.workers,
            "reload": False,
            "log_level": "info"
        })
    else:
        print(f"Starting API server in DEVELOPMENT mode on {args.host}:{args.port}")
        print("Auto-reload is ENABLED")
        config.update({
            "reload": True,
            "log_level": "debug"
        })

    print("\nAPI Documentation:")
    print(f"  - Swagger UI: http://{args.host}:{args.port}/docs")
    print(f"  - ReDoc:      http://{args.host}:{args.port}/redoc")
    print(f"  - Health:     http://{args.host}:{args.port}/health")
    print()

    uvicorn.run(**config)


if __name__ == "__main__":
    main()
