"""
Base Scraper Class
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import asyncio
import httpx
from bs4 import BeautifulSoup

from app.core.config import settings


class BaseScraper(ABC):
    """Base class for all scrapers"""
    
    def __init__(self):
        self.timeout = settings.SCRAPING_TIMEOUT
        self.max_retries = settings.SCRAPING_MAX_RETRIES
        self.delay = settings.SCRAPING_DELAY
    
    async def fetch(
        self, url: str, method: str = "GET", **kwargs
    ) -> Optional[httpx.Response]:
        """Fetch URL with retries"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for attempt in range(self.max_retries):
                try:
                    if method == "GET":
                        response = await client.get(url, **kwargs)
                    elif method == "POST":
                        response = await client.post(url, **kwargs)
                    else:
                        raise ValueError(f"Unsupported method: {method}")
                    
                    response.raise_for_status()
                    
                    # Delay to respect rate limits
                    await asyncio.sleep(self.delay)
                    
                    return response
                
                except httpx.HTTPError as e:
                    if attempt == self.max_retries - 1:
                        raise
                    
                    # Exponential backoff
                    await asyncio.sleep(self.delay * (2 ** attempt))
        
        return None
    
    def parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML with BeautifulSoup"""
        return BeautifulSoup(html, "lxml")
    
    @abstractmethod
    async def search(self, *args, **kwargs) -> List[Dict[str, Any]]:
        """Search method to be implemented by subclasses"""
        pass
