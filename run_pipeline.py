#!/usr/bin/env python
"""
Exoplanet Atlas: Data Pipeline

Launcher script
    python run_pipeline.py [--curated | --full] [--limit 100] [--strict]
"""
from src.pipeline import main

if __name__ == "__main__":
    main()

