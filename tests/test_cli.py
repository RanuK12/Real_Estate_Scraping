"""
Unit tests for the CLI entry point (src.scraper.main).
"""

import unittest
from unittest.mock import patch, MagicMock
import sys


class TestCliMain(unittest.TestCase):
    """Test suite for the CLI main() function in src.scraper."""

    def setUp(self) -> None:
        """Remove any pre‑existing scraper module reference."""
        for mod in list(sys.modules.keys()):
            if "src.scraper" in mod:
                del sys.modules[mod]

    @patch("src.scraper.RealEstateScraper")
    def test_main_default_args(self, mock_scraper_cls: MagicMock) -> None:
        """
        main() uses default arguments (zonaprop, CABA, csv) when
        none are provided.
        """
        mock_instance = MagicMock()
        mock_instance.scrape_real.return_value = [{"title": "Casa"}]
        mock_instance.export_data.return_value = "data/properties.csv"
        mock_scraper_cls.return_value = mock_instance

        test_args = ["real-estate-scraper"]
        with patch.object(sys, "argv", test_args):
            from src.scraper import main
            main()

        mock_scraper_cls.assert_called_once()
        mock_instance.scrape_real.assert_called_once_with(
            source="zonaprop", zone="CABA"
        )
        mock_instance.export_data.assert_called_once()

    @patch("src.scraper.RealEstateScraper")
    def test_main_mercadolibre_source(self, mock_scraper_cls: MagicMock) -> None:
        """
        main() passes --source mercadolibre to scrape_real().
        """
        mock_instance = MagicMock()
        mock_instance.scrape_real.return_value = [{"title": "Depto"}]
        mock_instance.export_data.return_value = "data/properties.csv"
        mock_scraper_cls.return_value = mock_instance

        test_args = ["real-estate-scraper", "--source", "mercadolibre"]
        with patch.object(sys, "argv", test_args):
            from src.scraper import main
            main()

        mock_instance.scrape_real.assert_called_once_with(
            source="mercadolibre", zone="CABA"
        )

    @patch("src.scraper.RealEstateScraper")
    def test_main_custom_zone(self, mock_scraper_cls: MagicMock) -> None:
        """
        main() passes --zone Uruguay to scrape_real().
        """
        mock_instance = MagicMock()
        mock_instance.scrape_real.return_value = [{"title": "Casa"}]
        mock_instance.export_data.return_value = "data/properties.csv"
        mock_scraper_cls.return_value = mock_instance

        test_args = ["real-estate-scraper", "--zone", "Uruguay"]
        with patch.object(sys, "argv", test_args):
            from src.scraper import main
            main()

        mock_instance.scrape_real.assert_called_once_with(
            source="zonaprop", zone="Uruguay"
        )

    @patch("src.scraper.RealEstateScraper")
    def test_main_export_json(self, mock_scraper_cls: MagicMock) -> None:
        """
        main() passes --export json to export_data().
        """
        mock_instance = MagicMock()
        mock_instance.scrape_real.return_value = [{"title": "Casa"}]
        mock_instance.export_data.return_value = "data/properties.json"
        mock_scraper_cls.return_value = mock_instance

        test_args = ["real-estate-scraper", "--export", "json"]
        with patch.object(sys, "argv", test_args):
            from src.scraper import main
            main()

        _, kwargs = mock_instance.export_data.call_args
        self.assertEqual(kwargs.get("format"), "json")

    @patch("src.scraper.RealEstateScraper")
    def test_main_custom_output_dir(self, mock_scraper_cls: MagicMock) -> None:
        """
        main() passes --output-dir to export_data().
        """
        mock_instance = MagicMock()
        mock_instance.scrape_real.return_value = [{"title": "Casa"}]
        mock_instance.export_data.return_value = "my_out/properties.csv"
        mock_scraper_cls.return_value = mock_instance

        test_args = ["real-estate-scraper", "--output-dir", "my_out"]
        with patch.object(sys, "argv", test_args):
            from src.scraper import main
            main()

        _, kwargs = mock_instance.export_data.call_args
        self.assertEqual(kwargs.get("output_dir"), "my_out")

    @patch("src.scraper.RealEstateScraper")
    def test_main_with_proxies(self, mock_scraper_cls: MagicMock) -> None:
        """
        main() passes --proxies to the scraper constructor.
        """
        mock_instance = MagicMock()
        mock_instance.scrape_real.return_value = [{"title": "Casa"}]
        mock_instance.export_data.return_value = "data/properties.csv"
        mock_scraper_cls.return_value = mock_instance

        test_args = [
            "real-estate-scraper",
            "--proxies", "http://p1:8080", "http://p2:8080",
        ]
        with patch.object(sys, "argv", test_args):
            from src.scraper import main
            main()

        _, kwargs = mock_scraper_cls.call_args
        self.assertEqual(kwargs.get("proxies"),
                         ["http://p1:8080", "http://p2:8080"])

    @patch("src.scraper.RealEstateScraper")
    def test_main_with_use_stealth(self, mock_scraper_cls: MagicMock) -> None:
        """
        main() passes --use-stealth to the scraper constructor.
        """
        mock_instance = MagicMock()
        mock_instance.scrape_real.return_value = [{"title": "Casa"}]
        mock_instance.export_data.return_value = "data/properties.csv"
        mock_scraper_cls.return_value = mock_instance

        test_args = ["real-estate-scraper", "--use-stealth"]
        with patch.object(sys, "argv", test_args):
            from src.scraper import main
            main()

        _, kwargs = mock_scraper_cls.call_args
        self.assertTrue(kwargs.get("use_stealth"))

    @patch("src.scraper.RealEstateScraper")
    def test_main_no_data_does_not_export(self, mock_scraper_cls: MagicMock) -> None:
        """
        When scrape_real() returns an empty list, export_data() should NOT
        be called (no data to export).
        """
        mock_instance = MagicMock()
        mock_instance.scrape_real.return_value = []
        mock_scraper_cls.return_value = mock_instance

        test_args = ["real-estate-scraper"]
        with patch.object(sys, "argv", test_args):
            from src.scraper import main
            main()

        mock_instance.export_data.assert_not_called()

    @patch("src.scraper.RealEstateScraper")
    def test_main_all_flags_combined(self, mock_scraper_cls: MagicMock) -> None:
        """
        All flags together: --source mercadolibre --zone Córdoba
        --export json --output-dir salida --proxies http://p:8080 --use-stealth.
        """
        mock_instance = MagicMock()
        mock_instance.scrape_real.return_value = [{"title": "Casa"}]
        mock_instance.export_data.return_value = "salida/properties.json"
        mock_scraper_cls.return_value = mock_instance

        test_args = [
            "real-estate-scraper",
            "--source", "mercadolibre",
            "--zone", "Córdoba",
            "--export", "json",
            "--output-dir", "salida",
            "--proxies", "http://p:8080",
            "--use-stealth",
        ]
        with patch.object(sys, "argv", test_args):
            from src.scraper import main
            main()

        mock_instance.scrape_real.assert_called_once_with(
            source="mercadolibre", zone="Córdoba"
        )
        _, kwargs = mock_instance.export_data.call_args
        self.assertEqual(kwargs.get("format"), "json")
        self.assertEqual(kwargs.get("output_dir"), "salida")

        _, ctor_kwargs = mock_scraper_cls.call_args
        self.assertEqual(ctor_kwargs.get("proxies"), ["http://p:8080"])
        self.assertTrue(ctor_kwargs.get("use_stealth"))


if __name__ == "__main__":
    unittest.main()
