import requests
from bs4 import BeautifulSoup
import re
import time
from typing import List, Dict, Optional
from urllib.parse import urljoin, quote

class MovieScraper:
    def __init__(self):
        self.base_url = "https://www.5movierulz.irish"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
    def search_movies(self, query: str, max_results: int = 20) -> List[Dict]:
        """
        Search for movies on the website
        """
        try:
            # Clean and prepare the search query
            clean_query = query.strip().lower()
            if not clean_query:
                return []
            
            # Try different search approaches
            results = []
            
            # Method 1: Try direct search if the site has a search endpoint
            search_results = self._search_via_search_page(clean_query)
            if search_results:
                results.extend(search_results[:max_results])
            
            # Method 2: Try browsing categories/pages if direct search doesn't work
            if len(results) < max_results:
                browse_results = self._search_via_browsing(clean_query)
                results.extend(browse_results[:max_results - len(results)])
            
            return results[:max_results]
            
        except Exception as e:
            print(f"Error searching movies: {str(e)}")
            return []
    
    def _search_via_search_page(self, query: str) -> List[Dict]:
        """
        Try to search using the website's search functionality
        """
        try:
            # Common search URL patterns
            search_urls = [
                f"{self.base_url}/search/{quote(query)}",
                f"{self.base_url}/?s={quote(query)}",
                f"{self.base_url}/search?q={quote(query)}",
            ]
            
            for search_url in search_urls:
                try:
                    response = self.session.get(search_url, timeout=10)
                    if response.status_code == 200:
                        results = self._parse_search_results(response.text, query)
                        if results:
                            return results
                except:
                    continue
                    
            return []
            
        except Exception as e:
            print(f"Error in search page method: {str(e)}")
            return []
    
    def _search_via_browsing(self, query: str) -> List[Dict]:
        """
        Search by browsing through movie listings
        """
        try:
            # Try to get the main page and look for movie listings
            response = self.session.get(self.base_url, timeout=10)
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for movie links and titles
            movie_elements = []
            
            # Common selectors for movie listings
            selectors = [
                'a[href*="movie"]',
                'a[href*="film"]',
                '.movie-item a',
                '.film-item a',
                '.post-title a',
                'h2 a',
                'h3 a',
                '.entry-title a'
            ]
            
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    movie_elements.extend(elements)
                    break
            
            # Filter results based on query
            results = []
            for element in movie_elements:
                title = element.get_text(strip=True)
                if query.lower() in title.lower():
                    movie_url = urljoin(self.base_url, element.get('href', ''))
                    
                    movie_data = {
                        'title': title,
                        'url': movie_url,
                        'source': '5movierulz',
                        'year': self._extract_year(title),
                        'poster': self._get_poster_from_page(movie_url),
                        'genre': 'Unknown',
                        'rating': 'N/A'
                    }
                    results.append(movie_data)
                    
                    if len(results) >= 10:  # Limit browsing results
                        break
            
            return results
            
        except Exception as e:
            print(f"Error in browsing method: {str(e)}")
            return []
    
    def _parse_search_results(self, html: str, query: str) -> List[Dict]:
        """
        Parse search results from HTML
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            results = []
            
            # Look for common movie result patterns
            movie_containers = soup.find_all(['div', 'article', 'li'], class_=re.compile(r'(movie|film|post|result)', re.I))
            
            for container in movie_containers:
                title_element = container.find(['h1', 'h2', 'h3', 'h4', 'a'], class_=re.compile(r'(title|name)', re.I))
                if not title_element:
                    title_element = container.find('a')
                
                if title_element:
                    title = title_element.get_text(strip=True)
                    if query.lower() in title.lower():
                        movie_url = urljoin(self.base_url, title_element.get('href', ''))
                        
                        # Try to find poster image
                        poster_img = container.find('img')
                        poster_url = ''
                        if poster_img:
                            poster_url = urljoin(self.base_url, poster_img.get('src', ''))
                        
                        movie_data = {
                            'title': title,
                            'url': movie_url,
                            'source': '5movierulz',
                            'year': self._extract_year(title),
                            'poster': poster_url,
                            'genre': 'Unknown',
                            'rating': 'N/A'
                        }
                        results.append(movie_data)
            
            return results
            
        except Exception as e:
            print(f"Error parsing search results: {str(e)}")
            return []
    
    def _extract_year(self, title: str) -> str:
        """
        Extract year from movie title
        """
        year_match = re.search(r'\b(19|20)\d{2}\b', title)
        return year_match.group() if year_match else 'N/A'
    
    def _get_poster_from_page(self, url: str) -> str:
        """
        Try to get poster image from movie page
        """
        try:
            response = self.session.get(url, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for poster images
                poster_selectors = [
                    'img[alt*="poster"]',
                    'img[class*="poster"]',
                    '.movie-poster img',
                    '.film-poster img',
                    'img[src*="poster"]'
                ]
                
                for selector in poster_selectors:
                    img = soup.select_one(selector)
                    if img:
                        return urljoin(self.base_url, img.get('src', ''))
                        
                # Fallback to first image
                first_img = soup.find('img')
                if first_img:
                    return urljoin(self.base_url, first_img.get('src', ''))
                    
        except:
            pass
        
        return ''

# Test function
def test_scraper():
    """
    Test the movie scraper
    """
    scraper = MovieScraper()
    
    test_queries = ['inception', 'avengers', 'batman']
    
    for query in test_queries:
        print(f"\nTesting search for: {query}")
        results = scraper.search_movies(query, max_results=5)
        
        if results:
            print(f"Found {len(results)} results:")
            for i, movie in enumerate(results, 1):
                print(f"{i}. {movie['title']} ({movie['year']}) - {movie['url']}")
        else:
            print("No results found")
        
        time.sleep(2)  # Be respectful with requests

if __name__ == "__main__":
    test_scraper()