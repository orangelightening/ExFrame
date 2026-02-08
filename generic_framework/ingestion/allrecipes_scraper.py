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
AllRecipes.com Scraper

Specialized scraper for AllRecipes with support for:
- Single recipe extraction
- Related recipe discovery
- Category crawling (via collections)
- Recipe search results

Updated to handle AllRecipes' new structure where categories contain
collection/roundup pages rather than direct recipe links.
"""

import re
import time
from typing import List, Dict, Optional, Set
from urllib.parse import urljoin, urlparse
import json
import requests
from bs4 import BeautifulSoup


class AllRecipesScraper:
    """
    Scrape recipes from AllRecipes.com

    AllRecipes now uses a 3-level structure:
    1. Category pages → contain collection URLs
    2. Collection pages → contain recipe URLs
    3. Recipe pages → contain actual recipe data

    Features:
    - Extract structured recipe data
    - Crawl categories via collections
    - Rate limiting and politeness
    """

    BASE_URL = "https://www.allrecipes.com"

    def __init__(self, delay: float = 2.0, max_recipes: int = 1000):
        self.delay = delay
        self.max_recipes = max_recipes
        self.recipes_seen: Set[str] = set()
        self.last_request_time = 0

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            ),
        })

    # ==========================================================================
    # CATEGORY CRAWLING (Main entry point)
    # ==========================================================================

    def scrape_category(self, category_url: str, max_pages: int = 5) -> List[str]:
        """
        Scrape recipe URLs from a category page.

        Handles the new AllRecipes structure where categories contain
        collection pages that then contain individual recipes.

        Args:
            category_url: Category page URL
            max_pages: Maximum category pages to check

        Returns:
            List of recipe URLs found
        """
        all_recipe_urls = []

        # Try each page of the category
        for page in range(1, max_pages + 1):
            if len(all_recipe_urls) >= self.max_recipes:
                break

            # Add page parameter
            parsed = urlparse(category_url)
            params = f"?page={page}" if page > 1 else ""
            page_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}{params}"

            print(f"Scraping category page {page}: {page_url}")

            self._rate_limit()

            try:
                response = self.session.get(page_url, timeout=15)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, 'html.parser')

                # Get URLs from JSON-LD ItemList
                urls_from_page = self._extract_jsonld_urls(soup)

                # Separate into recipes and collections
                recipe_urls = [u for u in urls_from_page if self._is_valid_recipe_url(u)]
                collection_urls = [u for u in urls_from_page if '/recipe/' not in u and 'recipes' in u]

                print(f"  Found {len(recipe_urls)} direct recipes, {len(collection_urls)} collections")

                # Add direct recipes
                for url in recipe_urls:
                    if url not in self.recipes_seen:
                        all_recipe_urls.append(url)
                        self.recipes_seen.add(url)

                # Scrape collections to get more recipes
                for coll_url in collection_urls:
                    if len(all_recipe_urls) >= self.max_recipes:
                        break

                    coll_recipes = self._scrape_collection_for_recipes(coll_url)
                    for url in coll_recipes:
                        if url not in self.recipes_seen:
                            all_recipe_urls.append(url)
                            self.recipes_seen.add(url)

                print(f"  Total so far: {len(all_recipe_urls)} recipes")

            except Exception as e:
                print(f"  Error scraping category page: {e}")
                break

        return all_recipe_urls

    def _scrape_collection_for_recipes(self, collection_url: str) -> List[str]:
        """Scrape a collection page and extract recipe URLs."""
        self._rate_limit()

        try:
            response = self.session.get(collection_url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # First try JSON-LD
            recipe_urls = self._extract_jsonld_urls(soup)

            # If JSON-LD didn't work, scrape HTML links
            if not recipe_urls:
                recipe_urls = self._extract_html_recipe_links(soup)

            # Filter to valid recipe URLs only
            return [u for u in recipe_urls if self._is_valid_recipe_url(u)]

        except Exception as e:
            print(f"    Error scraping collection: {e}")
            return []

    def _extract_html_recipe_links(self, soup: BeautifulSoup) -> List[str]:
        """Extract recipe URLs from HTML links (fallback for collection pages)."""
        urls = []

        for a in soup.find_all('a', href=True):
            href = a.get('href')
            if href and '/recipe/' in href:
                full_url = urljoin(self.BASE_URL, href)
                urls.append(full_url)

        return list(set(urls))  # Remove duplicates

    def _extract_jsonld_urls(self, soup: BeautifulSoup) -> List[str]:
        """Extract all URLs from JSON-LD ItemList data."""
        urls = []

        for script in soup.find_all('script', {'type': 'application/ld+json'}):
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict):
                            # Handle ItemList
                            if 'ItemList' in item.get('@type', []):
                                for elem in item.get('itemListElement', []):
                                    url = elem.get('url') or elem.get('item', {}).get('@id')
                                    if url:
                                        urls.append(url)
                            # Handle single Recipe
                            elif item.get('@type') == 'Recipe':
                                url = item.get('url')
                                if url:
                                    urls.append(url)
            except:
                pass

        return urls

    # ==========================================================================
    # SINGLE RECIPE SCRAPING
    # ==========================================================================

    def scrape_recipe(self, url: str) -> Dict:
        """
        Scrape a single recipe from AllRecipes.

        Args:
            url: Recipe URL

        Returns:
            Dict with recipe data
        """
        self._rate_limit()

        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Try to get data from JSON-LD first (more reliable)
            recipe_data = self._extract_from_jsonld(soup)

            # Fall back to HTML parsing if needed
            if not recipe_data.get('title'):
                recipe_data['title'] = self._extract_title(soup)
            if not recipe_data.get('ingredients'):
                recipe_data['ingredients'] = self._extract_ingredients(soup)
            if not recipe_data.get('steps'):
                recipe_data['steps'] = self._extract_steps(soup)

            recipe_data['url'] = url

            return recipe_data

        except Exception as e:
            print(f"Error scraping recipe {url}: {e}")
            return {'url': url, 'error': str(e)}

    def _extract_from_jsonld(self, soup: BeautifulSoup) -> Dict:
        """Extract recipe data from JSON-LD structured data."""
        recipe = {
            'title': '',
            'description': '',
            'ingredients': [],
            'steps': [],
            'prep_time': '',
            'cook_time': '',
            'total_time': '',
            'rating': 0.0,
            'review_count': 0,
            'category': '',
            'yield': '',
            'author': '',
            'images': [],
        }

        for script in soup.find_all('script', {'type': 'application/ld+json'}):
            try:
                data = json.loads(script.string)

                # Handle array of JSON-LD objects
                if isinstance(data, list):
                    for item in data:
                        if item.get('@type') == 'Recipe':
                            self._parse_recipe_jsonld(item, recipe)
                            break
                # Handle single Recipe object
                elif isinstance(data, dict) and data.get('@type') == 'Recipe':
                    self._parse_recipe_jsonld(data, recipe)
                    break

            except:
                pass

        return recipe

    def _parse_recipe_jsonld(self, data: dict, recipe: dict):
        """Parse Recipe JSON-LD data into recipe dict."""
        recipe['title'] = data.get('name', '')
        recipe['description'] = data.get('description', '')

        # Ingredients
        ingredients = data.get('recipeIngredient', [])
        if isinstance(ingredients, list):
            recipe['ingredients'] = [str(i) for i in ingredients]
        elif ingredients:
            recipe['ingredients'] = [str(ingredients)]

        # Steps
        instructions = data.get('recipeInstructions', [])
        if isinstance(instructions, list):
            recipe['steps'] = [
                inst.get('text', '') if isinstance(inst, dict) else str(inst)
                for inst in instructions
            ]
        elif instructions:
            recipe['steps'] = [str(instructions)]

        # Times
        recipe['prep_time'] = data.get('prepTime', '')
        recipe['cook_time'] = data.get('cookTime', '')
        recipe['total_time'] = data.get('totalTime', '')

        # Ratings
        agg_rating = data.get('aggregateRating', {})
        if isinstance(agg_rating, dict):
            recipe['rating'] = float(agg_rating.get('ratingValue', 0))
            recipe['review_count'] = int(agg_rating.get('ratingCount', 0))

        # Category
        recipe['category'] = data.get('recipeCategory', '')

        # Yield
        recipe['yield'] = data.get('recipeYield', '')

        # Author
        author = data.get('author', {})
        if isinstance(author, dict):
            recipe['author'] = author.get('name', '')
        elif isinstance(author, list) and author:
            recipe['author'] = author[0].get('name', '')

        # Images
        images = data.get('image', [])
        if isinstance(images, list):
            recipe['images'] = [str(i) for i in images]
        elif images:
            recipe['images'] = [str(images)]

    # ==========================================================================
    # HTML FALLBACK EXTRACTION
    # ==========================================================================

    def _extract_title(self, soup: BeautifulSoup) -> str:
        for selector in ['h1[class*="headline"]', 'h1[class*="title"]', 'h1']:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text().strip()
        return ""

    def _extract_ingredients(self, soup: BeautifulSoup) -> List[str]:
        ingredients = []
        for selector in [
            '[data-ingredient-name="true"]',
            '[class*="ingredient"]',
            'li[class*="ingredient"]',
        ]:
            elems = soup.select(selector)
            if elems:
                for elem in elems:
                    text = elem.get_text().strip()
                    if text and len(text) > 2:
                        ingredients.append(text)
                if ingredients:
                    break
        return ingredients

    def _extract_steps(self, soup: BeautifulSoup) -> List[str]:
        """
        Extract recipe steps/instructions from AllRecipes HTML.

        Handles AllRecipes' new HTML structure (2025+) with classes like:
        - mm-recipes-steps__content
        - mntl-sc-block
        - mntl-sc-block-group--OL
        """
        steps = []

        # Try new AllRecipes structure first (2025+)
        # Look for the main steps container
        steps_container = soup.find('div', class_=lambda x: x and 'mm-recipes-steps__content' in ' '.join(x))
        if steps_container:
            # Find all list items (OL) inside the container
            ol = steps_container.find('ol')
            if ol:
                for li in ol.find_all('li', recursive=False):
                    # Get text, but exclude nested elements like "I Made It" buttons
                    text_parts = []
                    for elem in li.descendants:
                        if elem.name in ['p', 'span', 'div']:
                            text = elem.get_text(strip=True)
                            if text and len(text) > 3:
                                # Skip button text and helper text
                                if 'button' not in str(elem.get('class', '')).lower():
                                    text_parts.append(text)
                        elif elem.name == '#text':
                            text = str(elem).strip()
                            if text and len(text) > 3:
                                text_parts.append(text)

                    if text_parts:
                        # Join unique non-empty parts
                        unique_parts = []
                        seen = set()
                        for part in text_parts:
                            if part and part not in seen:
                                seen.add(part)
                                unique_parts.append(part)

                        step_text = ' '.join(unique_parts)
                        if len(step_text) > 10:
                            steps.append(step_text)

        if steps:
            return steps

        # Fallback to older/newer selectors
        for selector in [
            'div.mm-recipes-steps__content ol li',
            'div.mntl-sc-block ol li',
            'ol[class*="instruction"] li',
            'li[class*="step"]',
            '[class*="instruction"]',
            'p[class*="instruction"]',
        ]:
            elems = soup.select(selector)
            if elems:
                for elem in elems:
                    # Get all text content, excluding buttons
                    text = elem.get_text(separator=' ', strip=True)
                    # Filter out common non-instruction text
                    skip_phrases = ['I Made It', 'Something went wrong', 'Please reload',
                                  'Add Photo', 'Show Full Nutrition', 'Hide Full Nutrition']
                    if text and len(text) > 5:
                        if not any(phrase in text for phrase in skip_phrases):
                            steps.append(text)
                if steps:
                    break
        return steps

    # ==========================================================================
    # UTILITY
    # ==========================================================================

    def _is_valid_recipe_url(self, url: str) -> bool:
        """Check if URL is a valid recipe URL (has /recipe/XXXXX pattern)"""
        return bool(re.search(r'/recipe/\d+', url))

    def _rate_limit(self):
        """Enforce delay between requests"""
        now = time.time()
        time_since_last = now - self.last_request_time

        if time_since_last < self.delay:
            time.sleep(self.delay - time_since_last)

        self.last_request_time = time.time()


if __name__ == "__main__":
    # Test the scraper
    scraper = AllRecipesScraper(delay=2.0)

    # Test category scraping
    category_url = "https://www.allrecipes.com/recipes/17562/dinner/"
    print(f"Testing category: {category_url}")
    print("=" * 60)

    recipes = scraper.scrape_category(category_url, max_pages=2)

    print(f"\nFound {len(recipes)} total recipe URLs")
    print("\nFirst 10:")
    for url in recipes[:10]:
        print(f"  - {url}")

    # Test single recipe
    if recipes:
        print(f"\nTesting recipe scrape: {recipes[0]}")
        recipe = scraper.scrape_recipe(recipes[0])
        print(f"Title: {recipe.get('title')}")
        print(f"Ingredients: {len(recipe.get('ingredients', []))}")
        print(f"Steps: {len(recipe.get('steps', []))}")
