"""
Robust Python scraper structure for real estate data.

Provides a base abstract scraper class with retry logic, logging,
and BeautifulSoup parsing.  Subclass it to implement site‑specific logic.
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

import requests
from bs4 import BeautifulSoup


class BaseScraper(ABC):
    """
    Abstract base scraper that handles HTTP requests, retries, and logging.

    Parameters
    ----------
    base_url : str
        The root URL of the site being scraped.
    headers : dict or None
        Custom HTTP headers (e.g., User‑Agent).  If None, a minimal default
        is used.
    timeout : int
        Timeout in seconds for each HTTP request.
    max_retries : int
        Maximum number of retry attempts for failed requests.
    backoff_factor : float
        Multiplier for exponential backoff (seconds).
    """

    def __init__(
        self,
        base_url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 10,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

        # Default headers if none provided
        self.headers = headers or {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }

        # Reusable session for connection pooling
        self.session = requests.Session()
        self.session.headers.update(self.headers)

        # Logger
        self.logger = self._get_logger()

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    def _get_logger(self) -> logging.Logger:
        """Return a logger named after the class."""
        logger = logging.getLogger(self.__class__.__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    # ------------------------------------------------------------------
    # HTTP fetching with retries
    # ------------------------------------------------------------------
    def _fetch(self, url: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        """
        Perform an HTTP GET request with automatic retries and exponential
        backoff.

        Parameters
        ----------
        url : str
            Full URL to fetch.
        params : dict or None
            Query string parameters.

        Returns
        -------
        requests.Response
            The final successful response.

        Raises
        ------
        requests.exceptions.RequestException
            If all retry attempts fail.
        """
        last_exception: Optional[Exception] = None

        for attempt in range(1, self.max_retries + 1):
            try:
                self.logger.info(
                    "Fetching %s (attempt %d/%d)", url, attempt, self.max_retries
                )
                response = self.session.get(
                    url, params=params, timeout=self.timeout
                )
                response.raise_for_status()  # Raise for 4xx/5xx
                self.logger.info(
                    "Successfully fetched %s (status %d)", url, response.status_code
                )
                return response

            except requests.exceptions.RequestException as exc:
                last_exception = exc
                self.logger.warning(
                    "Attempt %d/%d failed for %s: %s",
                    attempt,
                    self.max_retries,
                    url,
                    exc,
                )

                if attempt < self.max_retries:
                    sleep_time = self.backoff_factor * (2 ** (attempt - 1))
                    self.logger.info("Sleeping %.2f seconds before retry", sleep_time)
                    time.sleep(sleep_time)

        # All attempts exhausted
        self.logger.error(
            "All %d attempts failed for %s", self.max_retries, url
        )
        raise last_exception  # type: ignore[misc]

    # ------------------------------------------------------------------
    # HTML parsing
    # ------------------------------------------------------------------
    def _parse(self, html: str) -> BeautifulSoup:
        """
        Parse raw HTML into a BeautifulSoup object (using 'html.parser').

        Parameters
        ----------
        html : str
            Raw HTML content.

        Returns
        -------
        BeautifulSoup
        """
        return BeautifulSoup(html, "html.parser")

    # ------------------------------------------------------------------
    # Abstract method – subclasses must implement
    # ------------------------------------------------------------------
    @abstractmethod
    def scrape(self) -> None:
        """
        Site‑specific scraping logic.

        This method should be overridden in a concrete subclass to
        implement the actual data extraction for a particular real‑estate
        website.
        """
        ...


# ======================================================================
# Concrete subclass for real‑estate property scraping
# ======================================================================
class RealEstateScraper(BaseScraper):
    """
    Scraper for a real‑estate site that can extract property details
    from individual listing pages.

    Parameters
    ----------
    base_url : str
        The root URL of the site being scraped.
    selectors : dict or None
        CSS selectors used to locate the title, price, and location
        elements on a property page.  If None, sensible defaults are used.
    **kwargs
        Additional keyword arguments forwarded to :class:`BaseScraper`.
    """

    DEFAULT_SELECTORS = {
        "title": "h1.property-title",
        "price": "span.price",
        "location": "span.location",
    }

    def __init__(
        self,
        base_url: str,
        selectors: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(base_url, **kwargs)
        self.selectors = selectors or self.DEFAULT_SELECTORS.copy()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def scrape_property(self, property_url: str) -> Dict[str, Optional[str]]:
        """
        Fetch a property listing page and extract its title, price, and
        location.

        Parameters
        ----------
        property_url : str
            Full URL of the property listing page.

        Returns
        -------
        dict
            A dictionary with keys ``title``, ``price``, and ``location``.
            Any value that cannot be found will be ``None``.
        """
        self.logger.info("Scraping property at %s", property_url)

        try:
            response = self._fetch(property_url)
        except requests.exceptions.RequestException as exc:
            self.logger.error("Failed to fetch property page: %s", exc)
            return {"title": None, "price": None, "location": None}

        soup = self._parse(response.text)

        title = self._extract_text(soup, self.selectors["title"])
        price = self._extract_text(soup, self.selectors["price"])
        location = self._extract_text(soup, self.selectors["location"])

        self.logger.info(
            "Extracted – title: %s, price: %s, location: %s",
            title,
            price,
            location,
        )
        return {"title": title, "price": price, "location": location}

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------
    @staticmethod
    def _extract_text(soup: BeautifulSoup, selector: str) -> Optional[str]:
        """Return the stripped text of the first element matching *selector*,
        or ``None`` if no element is found."""
        element = soup.select_one(selector)
        if element is None:
            return None
        return element.get_text(strip=True)

    # ------------------------------------------------------------------
    # Backward‑compatible scrape method (optional)
    # ------------------------------------------------------------------
    def scrape(self) -> None:
        """
        Example implementation: fetch the homepage and log the title.
        """
        self.logger.info("Starting scrape of %s", self.base_url)

        try:
            response = self._fetch(self.base_url)
            soup = self._parse(response.text)
            title = soup.title.string.strip() if soup.title else "No title found"
            self.logger.info("Page title: %s", title)
        except requests.exceptions.RequestException as exc:
            self.logger.error("Scrape failed: %s", exc)


# ======================================================================
# Quick test when run directly
# ======================================================================
if __name__ == "__main__":
    # Example usage – replace with a real URL when testing
    scraper = RealEstateScraper("https://example.com")
    scraper.scrape()
