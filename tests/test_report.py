"""
Unit tests for the market report generator (src/report.py).
"""

import csv
import json
import os
import tempfile
import unittest

from src.report import build_zone_stats, generate_pdf, load_records


class TestLoadRecords(unittest.TestCase):
    def test_loads_csv_and_json_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = os.path.join(tmp, "properties_20260801_000000.csv")
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["title", "location", "price_per_m2", "scraped_at"])
                writer.writeheader()
                writer.writerow({"title": "Depto A", "location": "CABA", "price_per_m2": "3000", "scraped_at": "2026-08-01T00:00:00"})

            json_path = os.path.join(tmp, "properties_20260802_000000.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(
                    [{"title": "Depto B", "location": "CABA", "price_per_m2": 3300, "scraped_at": "2026-08-02T00:00:00"}],
                    f,
                )

            records = load_records(tmp)
            self.assertEqual(len(records), 2)
            titles = {r["title"] for r in records}
            self.assertEqual(titles, {"Depto A", "Depto B"})

    def test_empty_dir_returns_empty_list(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(load_records(tmp), [])


class TestBuildZoneStats(unittest.TestCase):
    def test_stock_and_average_price(self) -> None:
        records = [
            {"location": "CABA", "price_per_m2": "3000", "scraped_at": "2026-08-01"},
            {"location": "CABA", "price_per_m2": "3200", "scraped_at": "2026-08-01"},
            {"location": "Suburbs", "price_per_m2": "2000", "scraped_at": "2026-08-01"},
        ]
        stats = build_zone_stats(records)
        self.assertEqual(stats["CABA"]["stock"], 2)
        self.assertEqual(stats["CABA"]["avg_price_per_m2"], 3100.0)
        self.assertEqual(stats["Suburbs"]["stock"], 1)

    def test_variation_between_two_snapshot_dates(self) -> None:
        records = [
            {"location": "CABA", "price_per_m2": "3000", "scraped_at": "2026-08-01"},
            {"location": "CABA", "price_per_m2": "3300", "scraped_at": "2026-08-02"},
        ]
        stats = build_zone_stats(records)
        self.assertAlmostEqual(stats["CABA"]["variation_pct"], 10.0)

    def test_variation_is_none_with_single_snapshot(self) -> None:
        records = [{"location": "CABA", "price_per_m2": "3000", "scraped_at": "2026-08-01"}]
        stats = build_zone_stats(records)
        self.assertIsNone(stats["CABA"]["variation_pct"])

    def test_missing_location_falls_back_to_default_zone(self) -> None:
        records = [{"price_per_m2": "3000", "scraped_at": "2026-08-01"}]
        stats = build_zone_stats(records)
        self.assertIn("Sin especificar", stats)

    def test_missing_price_per_m2_averages_over_available_values(self) -> None:
        records = [
            {"location": "CABA", "price_per_m2": "", "scraped_at": "2026-08-01"},
            {"location": "CABA", "price_per_m2": "3000", "scraped_at": "2026-08-01"},
        ]
        stats = build_zone_stats(records)
        self.assertEqual(stats["CABA"]["stock"], 2)
        self.assertEqual(stats["CABA"]["avg_price_per_m2"], 3000.0)


class TestGeneratePdf(unittest.TestCase):
    def test_creates_valid_pdf_file(self) -> None:
        stats = {
            "CABA": {"stock": 2, "avg_price_per_m2": 3100.0, "variation_pct": 10.0},
            "Suburbs": {"stock": 1, "avg_price_per_m2": None, "variation_pct": None},
        }
        with tempfile.TemporaryDirectory() as tmp:
            output_path = os.path.join(tmp, "report.pdf")
            result_path = generate_pdf(stats, output_path)
            self.assertEqual(result_path, output_path)
            self.assertTrue(os.path.exists(output_path))
            with open(output_path, "rb") as f:
                self.assertTrue(f.read(5).startswith(b"%PDF-"))


if __name__ == "__main__":
    unittest.main()
