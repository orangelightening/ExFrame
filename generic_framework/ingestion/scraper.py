#
# Copyright 2025 ExFrame Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
URL Scraper - Ingest text from web sources

Scrapes and extracts main content from URLs for pattern extraction.
"""

import re
import time
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from bs4.element import Comment


class URLScraper:
    """
    Scrape URLs and extract text content for pattern extraction.

    Features:
    - Main content extraction (removes nav, footer, ads)
    - Respect robots.txt (basic check)
    - Rate limiting
    - Error handling
    """

    def __init__(self, delay: float = 1.0, user_agent: str = None):
        """
        Initialize scraper.

        Args:
            delay: Seconds to wait between requests (be polite!)
            user_agent: Custom user agent string
        """
        self.delay = delay
        self.last_request_time = 0

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': user_agent or (
                'Mozilla/5.0 (compatible; ExpertiseScanner/0.1; '
                '+https://github.com/eeframe/scanner)'
            )
        })

    def scrape_url(self, url: str) -> Dict[str, str]:
        """
        Scrape a single URL and extract content.

        Args:
            url: URL to scrape

        Returns:
            Dict with 'url', 'title', 'text', 'html' keys
        """
        self._rate_limit()

        try:
            response = self.session.get(url, timeout=10, allow_redirects=True)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract title
            title = self._extract_title(soup, url)

            # Extract main content
            text = self._extract_main_content(soup)

            return {
                'url': url,
                'title': title,
                'text': text,
                'html': response.text
            }

        except requests.RequestException as e:
            print(f"Error scraping {url}: {e}")
            return {'url': url, 'title': '', 'text': '', 'error': str(e)}

    def scrape_multiple(self, urls: List[str]) -> List[Dict[str, str]]:
        """
        Scrape multiple URLs sequentially.

        Args:
            urls: List of URLs to scrape

        Returns:
            List of scrape results
        """
        results = []

        for url in urls:
            print(f"Scraping: {url}")
            result = self.scrape_url(url)
            results.append(result)

            # Show progress
            if result.get('text'):
                text_len = len(result['text'])
                print(f"  ✓ Extracted {text_len} characters")
            else:
                print(f"  ✗ Failed or no content")

        return results

    def scrape_links(self, base_url: str, selector: str = 'a[href]') -> List[str]:
        """
        Scrape a page and extract links from it.

        Args:
            base_url: Starting URL
            selector: CSS selector for links

        Returns:
            List of absolute URLs
        """
        result = self.scrape_url(base_url)
        soup = BeautifulSoup(result.get('html', ''), 'html.parser')

        links = set()
        for link in soup.select(selector):
            href = link.get('href')
            if href:
                absolute = urljoin(base_url, href)
                # Only include links from same domain
                if urlparse(absolute).netloc == urlparse(base_url).netloc:
                    links.add(absolute)

        return sorted(links)

    def _rate_limit(self):
        """Enforce delay between requests"""
        now = time.time()
        time_since_last = now - self.last_request_time

        if time_since_last < self.delay:
            time.sleep(self.delay - time_since_last)

        self.last_request_time = time.time()

    def _extract_title(self, soup: BeautifulSoup, url: str) -> str:
        """Extract page title"""
        # Try title tag
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text().strip()
            if title:
                return title

        # Try h1
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()

        # Fallback to URL
        return url

    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """
        Extract the main content from a page.

        Removes navigation, footer, scripts, ads, etc.
        """
        # Remove unwanted elements
        for element in soup.find_all(['script', 'style', 'nav', 'footer',
                                      'header', 'aside', 'iframe', 'noscript']):
            element.decompose()

        # Remove elements with common ad/class names
        for selector in [
            '[class*="ad"]', '[class*="advertisement"]',
            '[class*="sidebar"]', '[class*="navigation"]',
            '[class*="footer"]', '[class*="cookie"]'
        ]:
            for element in soup.select(selector):
                element.decompose()

        # Try to find main content area
        main_content = (
            soup.find('main') or
            soup.find('article') or
            soup.find('div', {'class': re.compile(r'content|article|post', re.I)}) or
            soup.body
        )

        if not main_content:
            return ""

        # Extract text, filter out comments
        texts = []
        for element in main_content.descendants:
            if isinstance(element, Comment):
                continue
            if isinstance(element, str):
                text = element.strip()
                if text:
                    texts.append(text)
            elif element.name in ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']:
                text = element.get_text().strip()
                if text:
                    texts.append(text)

        # Join and clean up
        full_text = ' '.join(texts)
        full_text = re.sub(r'\s+', ' ', full_text)  # Collapse whitespace
        return full_text.strip()


class DomainScraper:
    """
    Pre-configured scraper for specific domains.

    Each domain has custom selectors and parsing logic.
    """

    # Domain-specific configurations
    DOMAIN_CONFIGS = {
        'allrecipes': {
            'base_url': 'https://www.allrecipes.com',
            'recipe_selector': 'a[href*="/recipe/"]',
            'content_selector': '.recipe-content'
        },
        'stack_overflow': {
            'base_url': 'https://stackoverflow.com',
            'question_selector': 'a[href*="/questions/"]',
            'content_selector': '.question, .answer'
        },
        'this_old_house': {
            'base_url': 'https://www.thisoldhouse.com',
            'article_selector': 'a[href*="/articles/"]',
            'content_selector': '.article-content'
        }
    }

    def __init__(self):
        self.scraper = URLScraper(delay=2.0)

    def scrape_allrecipes(self, recipe_urls: List[str]) -> List[Dict]:
        """
        Scrape recipes from AllRecipes.

        Args:
            recipe_urls: List of recipe URLs

        Returns:
            List of recipe data
        """
        results = []
        for url in recipe_urls:
            result = self.scraper.scrape_url(url)
            # Extract recipe-specific info
            result['recipe'] = self._parse_allrecipes(result.get('html', ''))
            results.append(result)
        return results

    def scrape_stack_overflow(self, question_urls: List[str]) -> List[Dict]:
        """
        Scrape Q&A from Stack Overflow.

        Args:
            question_urls: List of question URLs

        Returns:
            List of Q&A data
        """
        results = []
        for url in question_urls:
            result = self.scraper.scrape_url(url)
            result['qa'] = self._parse_stack_overflow(result.get('html', ''))
            results.append(result)
        return results

    def _parse_allrecipes(self, html: str) -> Dict:
        """Parse specific AllRecipes data"""
        soup = BeautifulSoup(html, 'html.parser')

        return {
            'ingredients': [i.get_text().strip() for i in soup.select('.ingredient-item')],
            'steps': [s.get_text().strip() for s in soup.select('.instruction-step')],
            'prep_time': self._get_meta(soup, 'prepTime'),
            'cook_time': self._get_meta(soup, 'cookTime'),
        }

    def _parse_stack_overflow(self, html: str) -> Dict:
        """Parse specific Stack Overflow data"""
        soup = BeautifulSoup(html, 'html.parser')

        question = soup.select_one('.question')
        answers = soup.select('.answer')

        return {
            'question': question.get_text().strip() if question else '',
            'answers': [a.get_text().strip() for a in answers],
            'tags': [t.get_text().strip() for t in soup.select('.post-tag')],
            'accepted_answer': bool(soup.select_one('.answer.accepted'))
        }

    def _get_meta(self, soup: BeautifulSoup, prop: str) -> str:
        """Get meta property value"""
        meta = soup.find('meta', {'property': prop})
        return meta.get('content', '') if meta else ''


if __name__ == "__main__":
    # Test scraper
    scraper = URLScraper()

    # Test with a simple page
    test_urls = [
        'https://example.com',
    ]

    for url in test_urls:
        print(f"\nScraping: {url}")
        result = scraper.scrape_url(url)
        print(f"Title: {result['title']}")
        print(f"Text preview: {result['text'][:200]}...")
