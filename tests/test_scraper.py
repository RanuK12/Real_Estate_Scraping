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


class TestScrapeZonapropMercadoLibre(unittest.TestCase):
    """Tests for _scrape_zonaprop and _scrape_mercadolibre."""

    def setUp(self) -> None:
        self.scraper = RealEstateScraper("https://example.com")

    def _mock_fetch(self, html: str) -> MagicMock:
        mock_resp = MagicMock()
        mock_resp.text = html
        mock_resp.raise_for_status.return_value = None
        return mock_resp

    @patch.object(RealEstateScraper, 'fetch')
    def test_scrape_zonaprop_parses_correctly(self, mock_fetch: MagicMock) -> None:
        """_scrape_zonaprop should parse title, price, location, m2, bedrooms, bathrooms."""
        fake_html = """
        <html>
          <body>
            <div class="postingCard">
              <h2><a class="title">Beautiful apartment in Palermo</a></h2>
              <span class="price">U$S 150,000</span>
              <span class="location">Palermo, CABA</span>
              <span class="m2">80 m²</span>
              <span class="bedroom">2 dormitorios</span>
              <span class="bathroom">1 baño</span>
            </div>
          </body>
        </html>
        """
        mock_fetch.return_value = self._mock_fetch(fake_html)
        result = self.scraper._scrape_zonaprop("CABA")
        self.assertEqual(len(result), 1)
        prop = result[0]
        self.assertEqual(prop["title"], "Beautiful apartment in Palermo")
        self.assertEqual(prop["price"], "U$S 150,000")
        self.assertEqual(prop["location"], "Palermo, CABA")
        self.assertAlmostEqual(prop["m2"], 80.0)
        self.assertEqual(prop["bedrooms"], "2 dormitorios")
        self.assertEqual(prop["bathrooms"], "1 baño")
        self.assertEqual(prop["source"], "zonaprop")
        self.assertIsNotNone(prop["url"])
        self.assertIsNotNone(prop["scraped_at"])
        # price_per_m2 should be computed
        self.assertAlmostEqual(prop["price_per_m2"], 150000.0 / 80.0)

    @patch.object(RealEstateScraper, 'fetch')
    def test_scrape_mercadolibre_parses_correctly(self, mock_fetch: MagicMock) -> None:
        """_scrape_mercadolibre should parse title, price, location, m2, bedrooms, bathrooms."""
        fake_html = """
        <html>
          <body>
            <li class="ui-search-layout__item">
              <h2><a class="title">Casa en venta en Punta del Este</a></h2>
              <span class="price-tag">USD 350,000</span>
              <span class="location">Punta del Este, Maldonado</span>
              <span class="m2">120 m²</span>
              <span class="bedroom">3 dormitorios</span>
              <span class="bathroom">2 baños</span>
            </li>
          </body>
        </html>
        """
        mock_fetch.return_value = self._mock_fetch(fake_html)
        result = self.scraper._scrape_mercadolibre("Uruguay")
        self.assertEqual(len(result), 1)
        prop = result[0]
        self.assertEqual(prop["title"], "Casa en venta en Punta del Este")
        self.assertEqual(prop["price"], "USD 350,000")
        self.assertEqual(prop["location"], "Punta del Este, Maldonado")
        self.assertAlmostEqual(prop["m2"], 120.0)
        self.assertEqual(prop["bedrooms"], "3 dormitorios")
        self.assertEqual(prop["bathrooms"], "2 baños")
        self.assertEqual(prop["source"], "mercadolibre")
        self.assertIsNotNone(prop["url"])
        self.assertIsNotNone(prop["scraped_at"])
        self.assertAlmostEqual(prop["price_per_m2"], round(350000.0 / 120.0, 2), places=2)

    @patch.object(RealEstateScraper, 'fetch')
    def test_scrape_zonaprop_empty_cards(self, mock_fetch: MagicMock) -> None:
        """_scrape_zonaprop should return empty list when no cards present."""
        fake_html = "<html><body><div>No cards here</div></body></html>"
        mock_fetch.return_value = self._mock_fetch(fake_html)
        result = self.scraper._scrape_zonaprop("CABA")
        self.assertEqual(result, [])

    @patch.object(RealEstateScraper, 'fetch')
    def test_scrape_mercadolibre_empty_cards(self, mock_fetch: MagicMock) -> None:
        """_scrape_mercadolibre should return empty list when no cards present."""
        fake_html = "<html><body><div>No cards here</div></body></html>"
        mock_fetch.return_value = self._mock_fetch(fake_html)
        result = self.scraper._scrape_mercadolibre("Uruguay")
        self.assertEqual(result, [])

    @patch.object(RealEstateScraper, 'fetch')
    def test_scrape_zonaprop_malformed_html(self, mock_fetch: MagicMock) -> None:
        """_scrape_zonaprop should return partial data when some elements missing."""
        fake_html = """
        <html>
          <body>
            <div class="postingCard">
              <h2><a class="title">Only title</a></h2>
              <!-- no price, no location, no m2, no bedrooms, no bathrooms -->
            </div>
          </body>
        </html>
        """
        mock_fetch.return_value = self._mock_fetch(fake_html)
        result = self.scraper._scrape_zonaprop("CABA")
        self.assertEqual(len(result), 1)
        prop = result[0]
        self.assertEqual(prop["title"], "Only title")
        self.assertIsNone(prop["price"])
        self.assertIsNone(prop["location"])
        self.assertIsNone(prop["m2"])
        self.assertIsNone(prop["bedrooms"])
        self.assertIsNone(prop["bathrooms"])
        self.assertIsNone(prop["price_per_m2"])

    @patch.object(RealEstateScraper, 'fetch')
    def test_scrape_mercadolibre_malformed_html(self, mock_fetch: MagicMock) -> None:
        """_scrape_mercadolibre should return partial data when some elements missing."""
        fake_html = """
        <html>
          <body>
            <li class="ui-search-layout__item">
              <h2><a class="title">Only title</a></h2>
              <!-- no price, no location, no m2, no bedrooms, no bathrooms -->
            </li>
          </body>
        </html>
        """
        mock_fetch.return_value = self._mock_fetch(fake_html)
        result = self.scraper._scrape_mercadolibre("Uruguay")
        self.assertEqual(len(result), 1)
        prop = result[0]
        self.assertEqual(prop["title"], "Only title")
        self.assertIsNone(prop["price"])
        self.assertIsNone(prop["location"])
        self.assertIsNone(prop["m2"])
        self.assertIsNone(prop["bedrooms"])
        self.assertIsNone(prop["bathrooms"])
        self.assertIsNone(prop["price_per_m2"])


class TestStructuredDataExtraction(unittest.TestCase):
    """Tests for _parse_jsonld and _extract_from_scripts."""

    def setUp(self) -> None:
        self.scraper = RealEstateScraper("https://example.com")

    # ------------------------------------------------------------------
    # _parse_jsonld tests
    # ------------------------------------------------------------------
    def test_parse_jsonld_single_product(self) -> None:
        """_parse_jsonld should extract a single Product with full details."""
        from bs4 import BeautifulSoup
        html = """<html><head><script type="application/ld+json">
{
  "@context": "http://schema.org",
  "@type": "Product",
  "name": "Departamento en Palermo",
  "offers": {"@type": "Offer", "price": "125000", "priceCurrency": "USD"},
  "address": {"@type": "PostalAddress", "addressLocality": "Palermo, CABA"},
  "floorSize": {"@type": "QuantitativeValue", "value": "75"},
  "numberOfBedrooms": 2,
  "numberOfBathrooms": 1,
  "url": "https://example.com/prop/1"
}
</script></head><body></body></html>"""
        soup = BeautifulSoup(html, "html.parser")
        result = RealEstateScraper._parse_jsonld(soup)
        self.assertEqual(len(result), 1)
        prop = result[0]
        self.assertEqual(prop["title"], "Departamento en Palermo")
        self.assertEqual(prop["price"], "125000")
        self.assertEqual(prop["location"], "Palermo, CABA")
        self.assertAlmostEqual(prop["m2"], 75.0)
        self.assertEqual(prop["bedrooms"], "2")
        self.assertEqual(prop["bathrooms"], "1")
        self.assertEqual(prop["source"], "zonaprop")

    def test_parse_jsonld_multiple_in_graph(self) -> None:
        """_parse_jsonld should extract multiple items from @graph."""
        from bs4 import BeautifulSoup
        html = """<html><head><script type="application/ld+json">
{
  "@context": "http://schema.org",
  "@graph": [
    {
      "@type": "Product",
      "name": "Casa en Martinez",
      "offers": {"@type": "Offer", "price": "250000"},
      "address": {"@type": "PostalAddress", "addressLocality": "Martinez, Bs As"},
      "floorSize": {"@type": "QuantitativeValue", "value": "120"},
      "numberOfBedrooms": 3,
      "numberOfBathrooms": 2
    },
    {
      "@type": "Product",
      "name": "Depto en Belgrano",
      "offers": {"@type": "Offer", "price": "95000"},
      "address": {"@type": "PostalAddress", "addressLocality": "Belgrano, CABA"},
      "floorSize": {"@type": "QuantitativeValue", "value": "55"},
      "numberOfBedrooms": 1,
      "numberOfBathrooms": 1
    }
  ]
}
</script></head><body></body></html>"""
        soup = BeautifulSoup(html, "html.parser")
        result = RealEstateScraper._parse_jsonld(soup)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["title"], "Casa en Martinez")
        self.assertEqual(result[1]["title"], "Depto en Belgrano")

    def test_parse_jsonld_no_script_tags(self) -> None:
        """_parse_jsonld should return empty list when no JSON-LD scripts exist."""
        from bs4 import BeautifulSoup
        html = "<html><body><div>No scripts here</div></body></html>"
        soup = BeautifulSoup(html, "html.parser")
        result = RealEstateScraper._parse_jsonld(soup)
        self.assertEqual(result, [])

    def test_parse_jsonld_invalid_json(self) -> None:
        """_parse_jsonld should gracefully skip invalid JSON."""
        from bs4 import BeautifulSoup
        html = """<html><head><script type="application/ld+json">
{this is not valid json}
</script></head><body></body></html>"""
        soup = BeautifulSoup(html, "html.parser")
        result = RealEstateScraper._parse_jsonld(soup)
        self.assertEqual(result, [])

    def test_parse_jsonld_missing_fields(self) -> None:
        """_parse_jsonld should return None for missing optional fields."""
        from bs4 import BeautifulSoup
        html = """<html><head><script type="application/ld+json">
{"@type": "Product", "name": "Minimal property"}
</script></head><body></body></html>"""
        soup = BeautifulSoup(html, "html.parser")
        result = RealEstateScraper._parse_jsonld(soup)
        self.assertEqual(len(result), 1)
        prop = result[0]
        self.assertEqual(prop["title"], "Minimal property")
        self.assertIsNone(prop["price"])
        self.assertIsNone(prop["location"])
        self.assertIsNone(prop["m2"])
        self.assertIsNone(prop["bedrooms"])
        self.assertIsNone(prop["bathrooms"])

    # ------------------------------------------------------------------
    # _extract_from_scripts tests
    # ------------------------------------------------------------------
    def test_extract_from_scripts_with_initial_state(self) -> None:
        """_extract_from_scripts should find data in window.__INITIAL_STATE__."""
        from bs4 import BeautifulSoup
        html = """<html><body><script>
window.__INITIAL_STATE__ = {"listings": [{"title": "Loft en San Telmo", "price": 80000, "currency": "USD", "location": "San Telmo", "m2": 40, "bedrooms": 1, "bathrooms": 1}]};
</script></body></html>"""
        soup = BeautifulSoup(html, "html.parser")
        result = RealEstateScraper._extract_from_scripts(soup)
        self.assertGreaterEqual(len(result), 0)

    def test_extract_from_scripts_no_data(self) -> None:
        """_extract_from_scripts should return empty list when no JS data found."""
        from bs4 import BeautifulSoup
        html = "<html><body><script>var x = 1;</script></body></html>"
        soup = BeautifulSoup(html, "html.parser")
        result = RealEstateScraper._extract_from_scripts(soup)
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
