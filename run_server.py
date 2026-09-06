#!/usr/bin/env python
"""
Exoplanet Atlas - REST API Server Runner.

Launches the FastAPI backend service with Uvicorn.

Usage:
    python run_server.py [--host 127.0.0.1] [--port 8000] [--reload]
"""
import argparse
import sys
import uvicorn

from src.core.config import settings


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Launch Exoplanet Atlas FastAPI Backend Server",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--host", type=str, default=settings.HOST, help="Bind host address")
    parser.add_argument("--port", type=int, default=settings.PORT, help="Bind port number")
    parser.add_argument("--reload", action="store_true", default=settings.DEBUG, help="Enable auto-reload")

    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("STARTING EXOPLANET ATLAS REST API SERVICE")
    print("=" * 60)
    print(f"API Base URL    : http://{args.host}:{args.port}")
    print(f"Swagger Docs UI : http://{args.host}:{args.port}/docs")
    print(f"ReDoc UI        : http://{args.host}:{args.port}/redoc")
    print(f"OpenAPI Schema  : http://{args.host}:{args.port}{settings.API_V1_STR}/openapi.json")
    print("=" * 60 + "\n")

    uvicorn.run(
        "src.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main()

