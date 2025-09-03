import asyncio
import re
import random
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Browser, Page
from urllib.parse import urljoin, quote
import time

class PlaywrightMovieScraper:
    def __init__(self):
        self.base_url = "https://www.5movierulz.irish"
        self.browser = None
        self.context = None
        
        # User agents to rotate
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15"
        ]
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start_browser()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close_browser()
    
    async def start_browser(self):
        """Initialize browser with anti-detection measures"""
        self.playwright = await async_playwright().start()
        
        # Launch browser with stealth settings
        self.browser = await self.playwright.chromium.launch(
            headless=True,  # Set to False for debugging
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu',
                '--disable-features=VizDisplayCompositor',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding'
            ]
        )
        
        # Create context with random user agent
        self.context = await self.browser.new_context(
            user_agent=random.choice(self.user_agents),
            viewport={'width': 1920, 'height': 1080},
            locale='en-US',
            timezone_id='America/New_York'
        )
        
        # Add stealth scripts
        await self.context.add_init_script("""
            // Override the navigator.webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            // Override the navigator.plugins property
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            // Override the navigator.languages property
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
            
            // Override the screen properties
            Object.defineProperty(screen, 'colorDepth', {
                get: () => 24,
            });
        """)
    
    async def close_browser(self):
        """Close browser and cleanup"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
    
    async def search_movies(self, query: str, max_results: int = 20) -> List[Dict]:
        """
        Search for movies with comprehensive error handling
        """
        try:
            if not self.browser:
                await self.start_browser()
            
            clean_query = query.strip().lower()
            if not clean_query:
                return []
            
            results = []
            
            # Try multiple search strategies
            search_methods = [
                self._search_via_search_page,
                self._search_via_homepage_browse,
                self._search_via_category_pages
            ]
            
            for method in search_methods:
                try:
                    method_results = await method(clean_query)
                    if method_results:
                        results.extend(method_results)
                        if len(results) >= max_results:
                            break
                except Exception as e:
                    print(f"Search method failed: {str(e)}")
                    continue
            
            # Remove duplicates and limit results
            unique_results = self._remove_duplicates(results)
            return unique_results[:max_results]
            
        except Exception as e:
            print(f"Error in search_movies: {str(e)}")
            return []
    
    async def _search_via_search_page(self, query: str) -> List[Dict]:
        """Search using the website's search functionality"""
        page = await self.context.new_page()
        
        try:
            # Block ads and unnecessary resources
            await page.route("**/*", self._block_resources)
            
            # Use the specific search URL pattern
            search_url = f"{self.base_url}/search_movies?s={quote(query)}"
            print(f"🔍 Searching URL: {search_url}")
            
            # Navigate directly to search results
            await page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
            await self._handle_popups_and_redirects(page)
            
            # Wait for content to load
            await asyncio.sleep(3)
            
            # Parse results
            results = await self._parse_movie_results(page, query)
            return results
            
        except Exception as e:
            print(f"Search page method failed: {str(e)}")
            return []
        finally:
            await page.close()
    
    async def _search_via_homepage_browse(self, query: str) -> List[Dict]:
        """Browse homepage for movie listings"""
        page = await self.context.new_page()
        
        try:
            await page.route("**/*", self._block_resources)
            await page.goto(self.base_url, wait_until='domcontentloaded', timeout=30000)
            await self._handle_popups_and_redirects(page)
            
            # Wait for content to load
            await asyncio.sleep(3)
            
            # Look for movie links
            movie_links = await page.query_selector_all('a[href*="movie"], a[href*="film"], a[href*="watch"]')
            
            results = []
            for link in movie_links[:50]:  # Limit to first 50 links
                try:
                    title = await link.inner_text()
                    if title and query.lower() in title.lower():
                        href = await link.get_attribute('href')
                        if href:
                            movie_url = urljoin(self.base_url, href)
                            
                            # Try to find poster image nearby
                            poster_url = await self._find_poster_near_element(page, link)
                            
                            movie_data = {
                                'title': title.strip(),
                                'url': movie_url,
                                'source': '5movierulz',
                                'year': self._extract_year(title),
                                'poster': poster_url,
                                'genre': 'Unknown',
                                'rating': 'N/A'
                            }
                            results.append(movie_data)
                except:
                    continue
            
            return results
            
        except Exception as e:
            print(f"Homepage browse failed: {str(e)}")
            return []
        finally:
            await page.close()
    
    async def _search_via_category_pages(self, query: str) -> List[Dict]:
        """Search through category/genre pages"""
        page = await self.context.new_page()
        
        try:
            await page.route("**/*", self._block_resources)
            await page.goto(self.base_url, wait_until='domcontentloaded', timeout=30000)
            await self._handle_popups_and_redirects(page)
            
            # Look for category/menu links
            category_links = await page.query_selector_all('a[href*="category"], a[href*="genre"], nav a, .menu a')
            
            results = []
            for category_link in category_links[:5]:  # Check first 5 categories
                try:
                    href = await category_link.get_attribute('href')
                    if href and 'category' in href.lower():
                        category_url = urljoin(self.base_url, href)
                        category_results = await self._search_in_category_page(category_url, query)
                        results.extend(category_results)
                        
                        if len(results) >= 10:  # Limit category results
                            break
                except:
                    continue
            
            return results
            
        except Exception as e:
            print(f"Category search failed: {str(e)}")
            return []
        finally:
            await page.close()
    
    async def _search_in_category_page(self, category_url: str, query: str) -> List[Dict]:
        """Search within a specific category page"""
        page = await self.context.new_page()
        
        try:
            await page.route("**/*", self._block_resources)
            await page.goto(category_url, wait_until='domcontentloaded', timeout=20000)
            await asyncio.sleep(2)
            
            results = await self._parse_movie_results(page, query)
            return results
            
        except:
            return []
        finally:
            await page.close()
    
    async def _parse_movie_results(self, page: Page, query: str) -> List[Dict]:
        """Parse movie results from a page"""
        results = []
        
        try:
            print("🔍 Parsing movie results...")
            
            # Wait for content to load
            await page.wait_for_load_state('networkidle', timeout=10000)
            
            # Get page content for debugging
            content = await page.content()
            print(f"📄 Page title: {await page.title()}")
            
            # Try multiple approaches to find all movies
            all_movie_elements = []
            
            # Approach 1: Look for specific movie containers (prioritize the working ones)
            movie_selectors = [
                'div[class*="film"]',  # This one worked in debug - put it first
                '.post',
                '.entry', 
                'article',
                '.movie-item',
                '.film-item',
                '.search-result',
                '.result-item',
                'div[class*="post"]',
                'div[class*="movie"]',
                'li[class*="post"]',
                'li[class*="movie"]',
                # More specific selectors for this site
                '.film-poster',
                '.movie-poster',
                '.content-box',
                '.movie-box'
            ]
            
            for selector in movie_selectors:
                elements = await page.query_selector_all(selector)
                if elements:
                    print(f"✅ Found {len(elements)} elements with selector: {selector}")
                    all_movie_elements.extend(elements)
            
            # Approach 2: Look for movie links directly
            link_selectors = [
                'a[href*="movie"]',
                'a[href*="watch"]',
                'a[href*="download"]',
                'a[href*="online"]',
                'a[title*=""]',
                'h1 a', 'h2 a', 'h3 a', 'h4 a'
            ]
            
            for selector in link_selectors:
                elements = await page.query_selector_all(selector)
                if elements:
                    print(f"🔗 Found {len(elements)} links with selector: {selector}")
                    all_movie_elements.extend(elements)
            
            # Remove duplicates while preserving order
            seen_elements = set()
            movie_elements = []
            for element in all_movie_elements:
                element_html = await element.inner_html()
                if element_html not in seen_elements:
                    seen_elements.add(element_html)
                    movie_elements.append(element)
            
            print(f"📊 Total unique elements to process: {len(movie_elements)}")
            
            for i, element in enumerate(movie_elements[:100]):  # Check many more elements
                try:
                    # Try different ways to get the title
                    title = ""
                    
                    # Method 1: Get the full text content of the element first
                    full_text = await element.inner_text()
                    
                    # Method 2: Look for title in various elements
                    title_selectors = ['h1', 'h2', 'h3', 'h4', '.title', '.movie-title', '.post-title', '.entry-title']
                    for title_sel in title_selectors:
                        title_elem = await element.query_selector(title_sel)
                        if title_elem:
                            title = await title_elem.inner_text()
                            break
                    
                    # Method 3: If no specific title found, extract from full text
                    if not title and full_text:
                        # Split by lines and take the first meaningful line
                        lines = [line.strip() for line in full_text.split('\n') if line.strip()]
                        if lines:
                            # Look for movie title patterns
                            for line in lines:
                                # Skip very short lines or lines that look like metadata
                                if len(line) > 3 and not line.lower().startswith(('watch', 'download', 'free', 'online')):
                                    title = line
                                    break
                    
                    # Method 4: If still no title, try the element itself or its link
                    if not title:
                        if await element.get_attribute('href'):  # It's a link
                            title = await element.inner_text()
                        else:
                            link_elem = await element.query_selector('a')
                            if link_elem:
                                title = await link_elem.inner_text()
                    
                    # Method 5: Try title attribute
                    if not title:
                        title = await element.get_attribute('title') or ""
                    
                    # Clean and validate title
                    title = title.strip()
                    
                    # Clean up common suffixes/prefixes
                    title = re.sub(r'\s*\|\s*Search Results.*$', '', title, flags=re.IGNORECASE)
                    title = re.sub(r'\s*\|\s*MovieRulz.*$', '', title, flags=re.IGNORECASE)
                    title = re.sub(r'\s*\|\s*Watch.*$', '', title, flags=re.IGNORECASE)
                    title = re.sub(r'\s*\|\s*Download.*$', '', title, flags=re.IGNORECASE)
                    title = re.sub(r'\s*\|\s*Free.*$', '', title, flags=re.IGNORECASE)
                    title = title.strip()
                    
                    if not title or len(title) < 2:
                        continue
                    
                    # Check if title matches query (more flexible matching)
                    query_words = query.lower().split()
                    title_lower = title.lower()
                    
                    # More flexible matching - check if any query word is in title OR title contains query
                    matches = False
                    if query.lower() in title_lower:  # Direct substring match
                        matches = True
                    elif any(word in title_lower for word in query_words):  # Any word match
                        matches = True
                    elif any(title_word.startswith(word[:3]) for word in query_words for title_word in title_lower.split() if len(word) >= 3):  # Partial word match
                        matches = True
                    
                    if not matches:
                        continue
                    
                    print(f"🎬 Found potential movie: {title}")
                    
                    # Special handling for elements that contain multiple movies
                    all_links = await element.query_selector_all('a')
                    all_images = await element.query_selector_all('img')
                    
                    # If this element has multiple links, it might contain multiple movies
                    if len(all_links) > 1 and len(all_images) > 1:
                        print(f"🎭 Processing multi-movie element with {len(all_links)} links")
                        
                        # Process each link-image pair as a separate movie
                        for link_idx, link in enumerate(all_links):
                            try:
                                link_href = await link.get_attribute('href')
                                if not link_href:
                                    continue
                                
                                # Try to find corresponding image
                                img_elem = all_images[link_idx] if link_idx < len(all_images) else all_images[0]
                                poster_src = await img_elem.get_attribute('src') if img_elem else ""
                                poster_url = urljoin(self.base_url, poster_src) if poster_src and not poster_src.startswith('data:') else ""
                                
                                # Extract title from image alt or URL
                                movie_title = ""
                                if img_elem:
                                    movie_title = await img_elem.get_attribute('alt') or ""
                                
                                # If no title from image, try to extract from URL
                                if not movie_title and link_href:
                                    # Extract movie name from URL pattern
                                    url_parts = link_href.split('/')
                                    for part in url_parts:
                                        if 'movie-watch' in part or any(word in part.lower() for word in query.lower().split()):
                                            movie_title = part.replace('-', ' ').replace('movie watch online free', '').strip()
                                            break
                                
                                if movie_title and query.lower() in movie_title.lower():
                                    movie_url = urljoin(self.base_url, link_href)
                                    year = self._extract_year(movie_title)
                                    
                                    movie_data = {
                                        'title': movie_title,
                                        'url': movie_url,
                                        'source': '5movierulz',
                                        'year': year,
                                        'poster': poster_url,
                                        'genre': 'Unknown',
                                        'rating': 'N/A'
                                    }
                                    results.append(movie_data)
                                    print(f"✅ Added movie from multi-element: {movie_title} ({year})")
                                    
                            except Exception as e:
                                print(f"❌ Error processing link {link_idx}: {str(e)}")
                                continue
                    else:
                        # Single movie element - original logic
                        movie_url = ""
                        href = await element.get_attribute('href')
                        if href:
                            movie_url = urljoin(self.base_url, href)
                        else:
                            link_elem = await element.query_selector('a')
                            if link_elem:
                                href = await link_elem.get_attribute('href')
                                if href:
                                    movie_url = urljoin(self.base_url, href)
                        
                        # Get poster image
                        poster_url = ""
                        img_elem = await element.query_selector('img')
                        if img_elem:
                            poster_src = await img_elem.get_attribute('src')
                            if poster_src and not poster_src.startswith('data:'):
                                poster_url = urljoin(self.base_url, poster_src)
                        
                        # Extract additional info if available
                        year = self._extract_year(title)
                        
                        # Try to get genre or other info
                        genre = "Unknown"
                        genre_elem = await element.query_selector('.genre, .category, .meta')
                        if genre_elem:
                            genre_text = await genre_elem.inner_text()
                            if genre_text:
                                genre = genre_text.strip()
                        
                        movie_data = {
                            'title': title,
                            'url': movie_url,
                            'source': '5movierulz',
                            'year': year,
                            'poster': poster_url,
                            'genre': genre,
                            'rating': 'N/A'
                        }
                        results.append(movie_data)
                        print(f"✅ Added movie: {title} ({year})")
                    
                except Exception as e:
                    print(f"❌ Error processing element {i}: {str(e)}")
                    continue
            
            print(f"🎯 Total movies found: {len(results)}")
            
        except Exception as e:
            print(f"❌ Error parsing results: {str(e)}")
        
        return results
    
    async def _handle_popups_and_redirects(self, page: Page):
        """Handle popups, ads, and redirects"""
        try:
            # Wait a bit for any popups to appear
            await asyncio.sleep(2)
            
            # Common popup/modal selectors to close
            popup_selectors = [
                '.popup-close',
                '.modal-close',
                '.close-button',
                '[aria-label="Close"]',
                '.overlay-close',
                '.ad-close'
            ]
            
            for selector in popup_selectors:
                try:
                    close_button = await page.query_selector(selector)
                    if close_button:
                        await close_button.click()
                        await asyncio.sleep(1)
                except:
                    continue
            
            # Handle any alert dialogs
            page.on('dialog', lambda dialog: asyncio.create_task(dialog.accept()))
            
        except Exception as e:
            print(f"Error handling popups: {str(e)}")
    
    async def _block_resources(self, route):
        """Block ads, trackers, and unnecessary resources"""
        url = route.request.url
        resource_type = route.request.resource_type
        
        # Block ads, trackers, and heavy resources
        blocked_domains = [
            'googletagmanager.com',
            'google-analytics.com',
            'googlesyndication.com',
            'doubleclick.net',
            'facebook.com',
            'twitter.com',
            'instagram.com',
            'ads',
            'analytics',
            'tracking'
        ]
        
        blocked_types = ['font', 'media']  # Block fonts and media to speed up
        
        if any(domain in url for domain in blocked_domains) or resource_type in blocked_types:
            await route.abort()
        else:
            await route.continue_()
    
    async def _find_poster_near_element(self, page: Page, element) -> str:
        """Find poster image near a movie link element"""
        try:
            # Look for image in parent or sibling elements
            parent = await element.query_selector('xpath=..')
            if parent:
                img = await parent.query_selector('img')
                if img:
                    src = await img.get_attribute('src')
                    if src:
                        return urljoin(self.base_url, src)
        except:
            pass
        return ''
    
    def _extract_year(self, title: str) -> str:
        """Extract year from movie title"""
        year_match = re.search(r'\b(19|20)\d{2}\b', title)
        return year_match.group() if year_match else 'N/A'
    
    def _remove_duplicates(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate movies based on title"""
        seen_titles = set()
        unique_results = []
        
        for movie in results:
            title_key = movie['title'].lower().strip()
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_results.append(movie)
        
        return unique_results

# Async wrapper for easy use
async def search_movies_async(query: str, max_results: int = 20) -> List[Dict]:
    """Async function to search movies"""
    async with PlaywrightMovieScraper() as scraper:
        return await scraper.search_movies(query, max_results)

# Sync wrapper for FastAPI integration
def search_movies_sync(query: str, max_results: int = 20) -> List[Dict]:
    """Synchronous wrapper for async movie search"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(search_movies_async(query, max_results))

# Test function
async def test_scraper():
    """Test the movie scraper"""
    test_queries = ['inception', 'avengers', 'batman']
    
    async with PlaywrightMovieScraper() as scraper:
        for query in test_queries:
            print(f"\n🔍 Testing search for: {query}")
            results = await scraper.search_movies(query, max_results=5)
            
            if results:
                print(f"✅ Found {len(results)} results:")
                for i, movie in enumerate(results, 1):
                    print(f"  {i}. {movie['title']} ({movie['year']})")
                    print(f"     URL: {movie['url']}")
                    if movie['poster']:
                        print(f"     Poster: {movie['poster']}")
            else:
                print("❌ No results found")
            
            await asyncio.sleep(2)  # Be respectful with requests

if __name__ == "__main__":
    asyncio.run(test_scraper())