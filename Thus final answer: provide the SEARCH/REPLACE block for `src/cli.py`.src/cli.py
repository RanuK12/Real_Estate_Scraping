"""
Command‑line interface for the real‑estate scraper.

This module re‑exports the ``main`` function from ``src.scraper``,
which provides a full argparse‑based CLI.
"""

from src.scraper import main

if __name__ == "__main__":
    main()
