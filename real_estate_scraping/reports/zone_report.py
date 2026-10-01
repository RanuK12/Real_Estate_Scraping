#!/usr/bin/env python3
"""
Generate a market report PDF from the latest scraped real estate data.
Usage:
    python -m reports.zone_report [--input INPUT_FILE] [--output OUTPUT_FILE]
"""

import argparse
import glob
import os
from datetime import datetime

# Add the src directory to the path so we can import from src.report
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from report import load_file, build_zone_stats, generate_pdf


def find_latest_snapshot(data_dir: str) -> str:
    """Return the path to the most recent properties_*.csv file in data_dir."""
    list_of_files = glob.glob(os.path.join(data_dir, 'properties_*.csv'))
    if not list_of_files:
        raise FileNotFoundError(f"No CSV files found in {data_dir}")
    # Sort by modification time (most recent first)
    list_of_files.sort(key=os.path.getmtime, reverse=True)
    return list_of_files[0]


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a market report PDF from scraped real estate data.")
    parser.add_argument('--input', help='Path to the input CSV file (default: latest snapshot in data/)')
    parser.add_argument('--output', help='Path to the output PDF file (default: reports/informe_mercado_YYYYMMDD.pdf)')
    args = parser.parse_args()

    # Determine input file
    if args.input:
        input_file = args.input
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")
    else:
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        input_file = find_latest_snapshot(data_dir)

    # Load records
    records = load_file(input_file)
    if not records:
        print(f"No records found in {input_file}")
        sys.exit(1)

    # Build zone statistics (uses median price_per_m2 and computes variation)
    zone_stats = build_zone_stats(records)

    # Determine output file
    if args.output:
        output_file = args.output
    else:
        today = datetime.now().strftime('%Y%m%d')
        reports_dir = os.path.join(os.path.dirname(__file__), '..', 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        output_file = os.path.join(reports_dir, f'informe_mercado_{today}.pdf')

    # Generate PDF
    generated_path = generate_pdf(zone_stats, output_file)
    print(f"Market report generated at: {generated_path}")


if __name__ == '__main__':
    main()