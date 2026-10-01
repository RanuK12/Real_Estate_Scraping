#!/usr/bin/env python3
"""
Generate a market report PDF from the scraped real estate data.
This script is intended to be run from the project root.
"""

import os
import sys
import statistics
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional

# Add the src directory to the path so we can import from src.report
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from report import load_file, _to_float, _snapshot_date


def build_zone_stats_median(records: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Group records by zone (``location``) and compute, per zone:
      - stock: number of listings
      - avg_price: mean of price across listings that have it
      - avg_price_per_m2: median of price_per_m2 across listings that have it
      - avg_size: mean of m2 across listings that have it
      - variation_pct: % change in median price_per_m2 between the two most
        recent snapshot dates for that zone (None if fewer than 2 dates)
    """
    by_zone: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for r in records:
        zone = r.get("location") or "Sin especificar"
        by_zone[zone].append(r)

    stats: Dict[str, Dict[str, Any]] = {}
    for zone, rows in by_zone.items():
        # Average price (mean)
        prices = [p for p in (_to_float(r.get("price")) for r in rows) if p is not None]
        avg_price = round(statistics.mean(prices), 2) if prices else None

        # Median price per m2
        prices_m2 = [p for p in (_to_float(r.get("price_per_m2")) for r in rows) if p is not None]
        median_price_per_m2 = round(statistics.median(prices_m2), 2) if prices_m2 else None

        # Average size (mean)
        sizes = [s for s in (_to_float(r.get("m2")) for r in rows) if s is not None]
        avg_size = round(statistics.mean(sizes), 2) if sizes else None

        # Variation: median price per m2 over time
        by_date: Dict[str, List[float]] = defaultdict(list)
        for r in rows:
            date = _snapshot_date(r)
            price = _to_float(r.get("price_per_m2"))
            if date and price is not None:
                by_date[date].append(price)

        variation_pct = None
        dates = sorted(by_date)
        if len(dates) >= 2:
            # Calculate median for each of the two most recent dates
            prev_median = statistics.median(by_date[dates[-2]])
            last_median = statistics.median(by_date[dates[-1]])
            if prev_median:
                variation_pct = round((last_median - prev_median) / prev_median * 100, 2)

        stats[zone] = {
            "stock": len(rows),
            "avg_price": avg_price,
            "avg_price_per_m2": median_price_per_m2,
            "avg_size": avg_size,
            "variation_pct": variation_pct,
        }
    return stats


def generate_pdf(
    zone_stats: Dict[str, Dict[str, Any]],
    output_path: str,
) -> str:
    """Render zone_stats into a PDF market report. Returns the output path."""
    # We reuse the generate_pdf function from src.report because it's already formatted correctly.
    # However, note that the existing generate_pdf expects the keys we are providing.
    # We can import it directly.
    from report import generate_pdf as report_generate_pdf
    return report_generate_pdf(zone_stats, output_path)


def main() -> None:
    """Main function to run the market report generation."""
    # Ensure the reports directory exists
    reports_dir = os.path.join(os.path.dirname(__file__), '..', 'reports')
    os.makedirs(reports_dir, exist_ok=True)

    # Load records from the sample data file
    data_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'sample_properties.csv')
    records = load_file(data_file)
    if not records:
        print(f"No records found in {data_file}")
        sys.exit(1)

    # Build zone statistics with median price per m2
    zone_stats = build_zone_stats_median(records)

    # Generate output filename with today's date
    today = datetime.now().strftime('%Y-%m-%d')
    output_path = os.path.join(reports_dir, f'mercado_{today}.pdf')

    # Generate the PDF
    generated_path = generate_pdf(zone_stats, output_path)
    print(f"Market report generated at: {generated_path}")


if __name__ == '__main__':
    main()