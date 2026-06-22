"""
Real‑Estate Scraping — Ranuk IT Solutions.

A robust, production‑ready scraper for real‑estate listings.
Supports Zonaprop (CABA) and MercadoLibre (Uruguay) with
proxy rotation, stealth browser fallback, and CSV/JSON export.

Typical usage::

    from src.scraper import RealEstateScraper

    scraper = RealEstateScraper()
    listings = scraper.scrape_real("zonaprop", zone="CABA")
    scraper.export_data(listings, "csv", "data/")
"""

__version__ = "0.2.0"
__author__ = "Emilio Ranucoli"
__license__ = "MIT"
