#!/usr/bin/env python3
"""
Market Report Generator for Real Estate Scraping Project

Generates professional PDF market reports from scraped real estate data.
Includes temporal analysis and professional design.

Author: Emilio Ranucoli
License: MIT
"""

import argparse
import os
import sys
import glob
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from report import generate_pdf, build_zone_stats, load_records, load_file


def main():
    parser = argparse.ArgumentParser(description='Generate real estate market reports')
    parser.add_argument('--data-dir', default='data', help='Directory containing scraped data')
    parser.add_argument('--output', default='Real_Estate_Report.pdf', help='Output PDF file path')
    parser.add_argument('--input', help='Specific input file (CSV or JSON) to analyze')
    parser.add_argument('--verbose', action='store_true', help='Show detailed processing information')
    
    args = parser.parse_args()
    
    if args.verbose:
        print(f"Loading data from: {args.data_dir}")
        if args.input:
            print(f"Using specific input file: {args.input}")
    
    try:
        if args.input:
            # Load from a specific file
            records = load_file(args.input)
            if args.verbose:
                print(f"Loaded {len(records)} properties from {args.input}")
        else:
            # Load all files from data directory
            records = load_records(args.data_dir)
            if args.verbose:
                print(f"Loaded {len(records)} properties from {args.data_dir}")
        
        if not records:
            print("No property records found. Make sure you have scraped data files in the data directory.")
            sys.exit(1)
        
        # Build zone statistics
        zone_stats = build_zone_stats(records)
        
        if args.verbose:
            print(f"Analyzed data from {len(zone_stats)} zones")
            for zone, stats in zone_stats.items():
                print(f"  {zone}: {stats['stock']} properties, avg price/m²: ${stats['avg_price_per_m2']:,.2f}")
        
        # Generate PDF report
        output_path = generate_pdf(zone_stats, args.output)
        
        print(f"Report generated successfully: {output_path}")
        
        # Print summary
        total_properties = sum(s['stock'] for s in zone_stats.values())
        total_zones = len(zone_stats)
        
        print(f"\nSummary:")
        print(f"  Total properties analyzed: {total_properties}")
        print(f"  Zones covered: {total_zones}")
        print(f"  Report saved to: {output_path}")
        
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()