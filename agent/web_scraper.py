"""
🌐 Web Scraper Module
Handles internet search and article content extraction.
"""

import os
import re
import time
import requests
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS


class WebScraper:
    """
    Web scraper that:
    - Searches the internet using DuckDuckGo or Tavily
    - Extracts clean article content from URLs
    - Handles rate limiting and errors gracefully
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        })
        self.timeout = 15
        self.max_content_length = 10000  # chars per article
        self.search_provider = os.getenv("SEARCH_PROVIDER", "duckduckgo").lower()

        if self.search_provider == "tavily":
            from tavily import TavilyClient
            self.tavily_client = TavilyClient()

    def search(self, query: str, num_results: int = 8) -> List[str]:
        """
        Search the internet and return URLs.

        Uses DuckDuckGo by default, or Tavily if SEARCH_PROVIDER=tavily.

        Args:
            query: Search query string
            num_results: Number of URLs to return

        Returns:
            List of URLs
        """
        if self.search_provider == "tavily":
            return self._search_tavily(query, num_results)
        return self._search_duckduckgo(query, num_results)

    def _search_duckduckgo(self, query: str, num_results: int) -> List[str]:
        """Search using DuckDuckGo and return URLs."""
        urls = []
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(
                    query,
                    max_results=num_results * 2,  # Extra in case some fail
                    region="wt-wt",
                    safesearch="moderate"
                ))
            for r in results:
                url = r.get("href", "")
                if url and self._is_valid_url(url):
                    urls.append(url)
                    if len(urls) >= num_results:
                        break
        except Exception as e:
            print(f"   Search error: {e}")
            # Fallback: try news search
            try:
                with DDGS() as ddgs:
                    results = list(ddgs.news(query, max_results=num_results))
                urls = [r.get("url", "") for r in results if r.get("url")]
            except Exception as e2:
                print(f"   Fallback search error: {e2}")

        return urls[:num_results]

    def _search_tavily(self, query: str, num_results: int) -> List[str]:
        """Search using Tavily and return URLs."""
        urls = []
        try:
            response = self.tavily_client.search(
                query=query,
                max_results=num_results,
                search_depth="basic",
            )
            for r in response.get("results", []):
                url = r.get("url", "")
                if url and self._is_valid_url(url):
                    urls.append(url)
        except Exception as e:
            print(f"   Tavily search error: {e}")

        return urls[:num_results]

    def scrape(self, url: str) -> Optional[Dict]:
        """
        Scrape article content from a URL.

        Args:
            url: URL to scrape

        Returns:
            Dict with title, url, content, or None on failure
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            content_type = response.headers.get("content-type", "")
            if "text/html" not in content_type:
                return None

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove unwanted elements
            for tag in soup(["script", "style", "nav", "footer", "header",
                              "aside", "advertisement", "noscript", "iframe"]):
                tag.decompose()

            # Try to get the title
            title = self._extract_title(soup, url)

            # Try to get main content
            content = self._extract_content(soup)

            if not content or len(content) < 100:
                return None

            # Truncate to max length
            content = content[:self.max_content_length]

            return {
                "url": url,
                "title": title,
                "content": content,
                "domain": urlparse(url).netloc,
                "scraped_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            }

        except requests.exceptions.RequestException as e:
            print(f"   HTTP error for {url}: {type(e).__name__}")
            return None
        except Exception as e:
            print(f"   Scrape error for {url}: {type(e).__name__}")
            return None

    def _extract_title(self, soup: BeautifulSoup, url: str) -> str:
        """Extract the best title from the page."""
        # Try Open Graph title first
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            return og_title["content"].strip()

        # Then regular title tag
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.get_text().strip()
            # Clean up common title suffixes like " | Site Name"
            title = re.split(r" [\|\-–—] ", title)[0]
            return title

        # Fallback to h1
        h1 = soup.find("h1")
        if h1:
            return h1.get_text().strip()

        return urlparse(url).netloc

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main article content from the page."""
        # Priority order of content containers
        content_selectors = [
            "article",
            '[role="main"]',
            "main",
            ".article-content",
            ".post-content",
            ".entry-content",
            ".content",
            "#content",
            ".story-body",
        ]

        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                text = self._clean_text(element.get_text())
                if len(text) > 200:
                    return text

        # Fallback: get all paragraph text
        paragraphs = soup.find_all("p")
        text = " ".join(p.get_text() for p in paragraphs)
        return self._clean_text(text)

    def _clean_text(self, text: str) -> str:
        """Clean extracted text."""
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)
        # Remove very short lines (often navigation/UI text)
        lines = [line.strip() for line in text.split(".") if len(line.strip()) > 30]
        return ". ".join(lines).strip()

    def _is_valid_url(self, url: str) -> bool:
        """Check if a URL is valid and scrapeable."""
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https"):
                return False
            # Skip PDFs, images, etc.
            skip_extensions = (".pdf", ".jpg", ".png", ".gif", ".mp4", ".zip")
            if any(parsed.path.lower().endswith(ext) for ext in skip_extensions):
                return False
            return True
        except Exception:
            return False
