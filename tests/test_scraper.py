"""
Unit tests for the RealEstateScraper class.
"""

import unittest
from unittest.mock import patch, MagicMock

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


if __name__ == "__main__":
    unittest.main()
