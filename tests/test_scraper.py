"""
Unit tests for the RealEstateScraper class.
"""

import unittest
from unittest.mock import patch, MagicMock
import tempfile
import os
import json
import csv
import glob

from src.scraper import RealEstateScraper


class TestRealEstateScraper(unittest.TestCase):
    """Test suite for RealEstateScraper."""

    def setUp(self) -> None:
        """Create a scraper instance with a dummy base URL."""
        self.scraper = RealEstateScraper("https://example.com")

    @patch("src.scraper.requests.Session.get")
    def test_scrape_property_returns_expected_dict(self, mock_get: MagicMock) -> None:
        """
        Verify that scrape_property returns a dictionary with the correct
        keys and values when the HTML contains the expected elements.
        """
        # Arrange – create a fake HTML page with the selectors we expect
        fake_html = """
        <html>
          <body>
            <h1 class="property-title">Beautiful House</h1>
            <span class="price">$500,000</span>
            <span class="location">123 Main St, Anytown</span>
          </body>
        </html>
        """
        mock_response = MagicMock()
        mock_response.text = fake_html
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Act
        result = self.scraper.scrape_property("https://example.com/property/1")

        # Assert
        self.assertIsInstance(result, dict)
        self.assertIn("title", result)
        self.assertIn("price", result)
        self.assertIn("location", result)
        self.assertEqual(result["title"], "Beautiful House")
        self.assertEqual(result["price"], "$500,000")
        self.assertEqual(result["location"], "123 Main St, Anytown")

    @patch("src.scraper.requests.Session.get")
    def test_scrape_property_missing_elements(self, mock_get: MagicMock) -> None:
        """
        Verify that scrape_property returns None for missing elements.
        """
        # Arrange – HTML without the expected selectors
        fake_html = """
        <html>
          <body>
            <h1>No class here</h1>
            <div>Some content</div>
          </body>
        </html>
        """
        mock_response = MagicMock()
        mock_response.text = fake_html
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Act
        result = self.scraper.scrape_property("https://example.com/property/2")

        # Assert
        self.assertIsNone(result["title"])
        self.assertIsNone(result["price"])
        self.assertIsNone(result["location"])

    @patch("src.scraper.requests.Session.get")
    def test_scrape_property_handles_http_error(self, mock_get: MagicMock) -> None:
        """
        Verify that scrape_property returns a dict with None values when
        the HTTP request fails.
        """
        # Arrange – simulate a network error
        from requests.exceptions import ConnectionError

        mock_get.side_effect = ConnectionError("Connection refused")

        # Act
        result = self.scraper.scrape_property("https://example.com/property/3")

        # Assert
        self.assertIsInstance(result, dict)
        self.assertIsNone(result["title"])
        self.assertIsNone(result["price"])
        self.assertIsNone(result["location"])

    # ------------------------------------------------------------------
    # Tests for _parse_price static method
    # ------------------------------------------------------------------
    def test_parse_price_with_commas(self) -> None:
        """_parse_price should handle numbers with commas."""
        result = RealEstateScraper._parse_price("$500,000")
        self.assertAlmostEqual(result, 500000.0)

    def test_parse_price_with_currency_prefix(self) -> None:
        """_parse_price should handle 'USD 1,200'."""
        result = RealEstateScraper._parse_price("USD 1,200")
        self.assertAlmostEqual(result, 1200.0)

    def test_parse_price_with_u_prefix(self) -> None:
        """_parse_price should handle 'U$S 300,000'."""
        result = RealEstateScraper._parse_price("U$S 300,000")
        self.assertAlmostEqual(result, 300000.0)

    def test_parse_price_none(self) -> None:
        """_parse_price should return None when given None."""
        result = RealEstateScraper._parse_price(None)
        self.assertIsNone(result)

    def test_parse_price_invalid_string(self) -> None:
        """_parse_price should return None for strings that cannot be parsed."""
        result = RealEstateScraper._parse_price("not a price")
        self.assertIsNone(result)

    def test_parse_price_empty_string(self) -> None:
        """_parse_price should return None for an empty string."""
        result = RealEstateScraper._parse_price("")
        self.assertIsNone(result)

    def test_parse_price_argentino_con_punto_miles(self) -> None:
        """_parse_price should handle '$ 1.234,56' → 1234.56."""
        result = RealEstateScraper._parse_price("$ 1.234,56")
        self.assertAlmostEqual(result, 1234.56)

    def test_parse_price_internacional_con_coma_miles(self) -> None:
        """_parse_price should handle '1,234.56' → 1234.56."""
        result = RealEstateScraper._parse_price("1,234.56")
        self.assertAlmostEqual(result, 1234.56)

    def test_parse_price_entero_sin_separador(self) -> None:
        """_parse_price should handle '150000' → 150000.0."""
        result = RealEstateScraper._parse_price("150000")
        self.assertAlmostEqual(result, 150000.0)

    def test_parse_price_u(self) -> None:
        """_parse_price should handle 'U$S 500,000' → 500000.0."""
        result = RealEstateScraper._parse_price("U$S 500,000")
        self.assertAlmostEqual(result, 500000.0)

    def test_parse_price_usd(self) -> None:
        """_parse_price should handle 'USD 1.500,75' → 1500.75."""
        result = RealEstateScraper._parse_price("USD 1.500,75")
        self.assertAlmostEqual(result, 1500.75)

    @patch("src.scraper.time.sleep")
    @patch("src.scraper.requests.Session.get")
    def test_rate_limiter_llama_sleep(
        self,
        mock_get: MagicMock,
        mock_sleep: MagicMock,
    ) -> None:
        """Verify that fetch calls time.sleep when request_delay > 0."""
        # Arrange
        mock_response = MagicMock()
        mock_response.text = "<html></html>"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        scraper = RealEstateScraper(
            "https://example.com",
            request_delay=0.5,
        )

        # Act
        scraper.fetch("/test")

        # Assert
        mock_sleep.assert_called_once_with(0.5)

    # ------------------------------------------------------------------
    # Tests for _parse_m2 static method
    # ------------------------------------------------------------------
    def test_parse_m2_with_square_metre_symbol(self) -> None:
        """_parse_m2 should handle '100 m²'."""
        result = RealEstateScraper._parse_m2("100 m²")
        self.assertAlmostEqual(result, 100.0)

    def test_parse_m2_with_m2_abbreviation(self) -> None:
        """_parse_m2 should handle '85.5 m2'."""
        result = RealEstateScraper._parse_m2("85.5 m2")
        self.assertAlmostEqual(result, 85.5)

    def test_parse_m2_none(self) -> None:
        """_parse_m2 should return None when given None."""
        result = RealEstateScraper._parse_m2(None)
        self.assertIsNone(result)

    def test_parse_m2_invalid_string(self) -> None:
        """_parse_m2 should return None for strings that cannot be parsed."""
        result = RealEstateScraper._parse_m2("not a size")
        self.assertIsNone(result)

    def test_parse_m2_empty_string(self) -> None:
        """_parse_m2 should return None for an empty string."""
        result = RealEstateScraper._parse_m2("")
        self.assertIsNone(result)

    # ------------------------------------------------------------------
    # Tests for export_data method
    # ------------------------------------------------------------------
    def test_export_data_csv_creates_file_with_headers(self) -> None:
        """export_data should create a CSV file with correct headers."""
        data = [
            {"title": "House A", "price": 100000.0, "location": "Street 1"},
            {"title": "House B", "price": 200000.0, "location": "Street 2"},
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            self.scraper.export_data(data, format="csv", output_dir=tmpdir)
            csv_files = glob.glob(os.path.join(tmpdir, "properties_*.csv"))
            self.assertEqual(len(csv_files), 1)
            csv_path = csv_files[0]
            with open(csv_path, newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                headers = next(reader)
                self.assertIn("title", headers)
                self.assertIn("price", headers)
                self.assertIn("location", headers)

    def test_export_data_json_creates_valid_json(self) -> None:
        """export_data should create a valid JSON file."""
        data = [
            {"title": "House A", "price": 100000.0, "location": "Street 1"},
            {"title": "House B", "price": 200000.0, "location": "Street 2"},
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            self.scraper.export_data(data, format="json", output_dir=tmpdir)
            json_files = glob.glob(os.path.join(tmpdir, "properties_*.json"))
            self.assertEqual(len(json_files), 1)
            json_path = json_files[0]
            with open(json_path, encoding="utf-8") as f:
                loaded = json.load(f)
            self.assertEqual(loaded, data)

    def test_export_data_empty_data_creates_header_only_csv(self) -> None:
        """export_data with empty data should create a CSV with only headers."""
        data: list = []
        with tempfile.TemporaryDirectory() as tmpdir:
            self.scraper.export_data(data, format="csv", output_dir=tmpdir)
            csv_files = glob.glob(os.path.join(tmpdir, "properties_*.csv"))
            self.assertEqual(len(csv_files), 1)
            csv_path = csv_files[0]
            with open(csv_path, newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                rows = list(reader)
            # Should have exactly one row (the header)
            self.assertEqual(len(rows), 1)
            self.assertIn("title", rows[0])
            self.assertIn("price", rows[0])
            self.assertIn("location", rows[0])

    # ------------------------------------------------------------------
    # Tests for scrape_real method
    # ------------------------------------------------------------------
    @patch.object(RealEstateScraper, "_scrape_zonaprop")
    def test_scrape_real_calls_zonaprop(self, mock_zonaprop: MagicMock) -> None:
        """scrape_real should call _scrape_zonaprop for source='zonaprop'."""
        mock_zonaprop.return_value = [{"id": 1}]
        result = self.scraper.scrape_real(source="zonaprop", zone="CABA")
        mock_zonaprop.assert_called_once_with("CABA")
        self.assertEqual(result, [{"id": 1}])

    @patch.object(RealEstateScraper, "_scrape_mercadolibre")
    def test_scrape_real_calls_mercadolibre(self, mock_mercadolibre: MagicMock) -> None:
        """scrape_real should call _scrape_mercadolibre for source='mercadolibre'."""
        mock_mercadolibre.return_value = [{"id": 2}]
        result = self.scraper.scrape_real(source="mercadolibre", zone="Montevideo")
        mock_mercadolibre.assert_called_once_with("Montevideo")
        self.assertEqual(result, [{"id": 2}])

    def test_scrape_real_invalid_source_raises_value_error(self) -> None:
        """scrape_real should raise ValueError for an invalid source."""
        with self.assertRaises(ValueError):
            self.scraper.scrape_real(source="invalid_source", zone="CABA")


if __name__ == "__main__":
    unittest.main()
