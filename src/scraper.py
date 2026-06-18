"""
Robust Python scraper structure for real estate data.

Provides a base abstract scraper class with retry logic, logging,
and BeautifulSoup parsing. Subclass it to implement site-specific logic.
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
        Custom HTTP headers (e.g., User-Agent). If None, a minimal default
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

        # Initialize session and headers
        self.session = requests.Session()
        if headers:
            self.session.headers.update(headers)
        else:
            self.session.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            })

    @abstractmethod
    def scrape(self) -> Dict[str, Any]:
        pass

    def fetch(self, endpoint: str) -> requests.Response:
        url = f"{self.base_url}{endpoint}"
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response
            except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
                logging.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(self.backoff_factor * (2 ** attempt))

class RealEstateScraper(BaseScraper):
    """
    Concrete implementation for scraping real estate listings.
    """

    def scrape(self) -> Dict[str, Any]:
        # This is a placeholder for the actual scraping logic
        # which will be implemented in specific site scrapers.
        logging.info("Starting scrape...")
        return {"status": "success", "data": []}

    def scrape_property(self, property_id: str) -> Dict[str, Any]:
        """
        Scrape details for a specific property.
        """
        endpoint = f"/properties/{property_id}"
        response = self.fetch(endpoint)
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Example parsing logic
        title = soup.find("h1").get_text(strip=True) if soup.find("h1") else "N/A"
        price = soup.find("span", class_="price").get_text(strip=True) if soup.find("span", class_="price") else "N/A"
        
        return {
            "id": property_id,
            "title": title,
            "price": price
        }