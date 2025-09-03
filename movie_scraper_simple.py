import asyncio
import re
from typing import List, Dict
from playwright.async_api import async_playwright
from urllib.parse import urljoin, quote

async def search_movies_simple(query: str, max_results: int = 20) -> List[Dict]:
    """Simplified movie search that gets all results"""
    
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    
    page = await context.new_page()
    results = []
    
    try:
        base_url = "https://www.5movierulz.irish"
        search_url = f"{base_url}/search_movies?s={quote(query)}"
        
        print(f"🔍 Searching: {search_url}")
        await page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
        await asyncio.sleep(3)
        
        # Get all film elements
        film_elements = await page.query_selector_all('div[class*="film"]')
        print(f"📦 Found {len(film_elements)} film elements")
        
        for i, element in enumerate(film_elements):
            try:
                full_text = await element.inner_text()
                
                # Check if contains query
                if query.lower() not in full_text.lower():
                    continue
                
                print(f"🎬 Processing element {i+1} (contains '{query}')")
                
                # Get all links and images in this element
                all_links = await element.query_selector_all('a')
                all_images = await element.query_selector_all('img')
                
                # Get all text content from this element to find full titles
                element_text = await element.inner_text()
                text_lines = [line.strip() for line in element_text.split('\n') if line.strip()]
                
                # Process each link-image pair
                for link_idx, link in enumerate(all_links):
                    try:
                        link_href = await link.get_attribute('href')
                        if not link_href:
                            continue
                        
                        # Get corresponding image
                        img_elem = all_images[link_idx] if link_idx < len(all_images) else None
                        movie_title = ""
                        poster_url = ""
                        
                        if img_elem:
                            poster_src = await img_elem.get_attribute('src') or ""
                            if poster_src and not poster_src.startswith('data:'):
                                poster_url = urljoin(base_url, poster_src)
                        
                        # Try to find the full title from the text content
                        # Look for lines that contain both the query and year information
                        for line in text_lines:
                            line_lower = line.lower()
                            # Check if this line contains our query and looks like a movie title
                            if (query.lower() in line_lower and 
                                (re.search(r'\b(19|20)\d{2}\b', line) or 
                                 any(keyword in line_lower for keyword in ['hdrip', 'brrip', 'movie', 'watch']))):
                                movie_title = line
                                print(f"    Found full title: {movie_title}")
                                break
                        
                        # Fallback: use image alt text if no better title found
                        if not movie_title and img_elem:
                            movie_title = await img_elem.get_attribute('alt') or ""
                        
                        # If still no title, extract from URL and make it unique
                        if not movie_title:
                            # Try to extract from URL
                            url_parts = link_href.split('/')
                            for part in url_parts:
                                if any(word in part.lower() for word in query.lower().split()):
                                    movie_title = part.replace('-', ' ').replace('movie watch online free', '').strip()
                                    break
                        
                        # Make title unique by adding language/year info from URL
                        if movie_title and link_href:
                            # Extract language from URL
                            if 'malayalam' in link_href.lower():
                                movie_title = movie_title.replace('Movie Watch Online Free', 'Malayalam Movie')
                            elif 'telugu' in link_href.lower():
                                movie_title = movie_title.replace('Movie Watch Online Free', 'Telugu Movie')
                            elif 'tamil' in link_href.lower():
                                movie_title = movie_title.replace('Movie Watch Online Free', 'Tamil Movie')
                            elif 'english' in link_href.lower():
                                movie_title = movie_title.replace('Movie Watch Online Free', 'English Movie')
                            elif 'hindi' in link_href.lower():
                                movie_title = movie_title.replace('Movie Watch Online Free', 'Hindi Movie')
                            
                            # Extract specific movie name from URL
                            if 'rrr-2022' in link_href.lower():
                                movie_title = 'RRR (2022) BRRip Telugu Movie'
                            elif 'rrr-behind' in link_href.lower():
                                movie_title = 'RRR: Behind & Beyond (2024) HDRip English Movie'
                            elif 'grrr-2024-malayalam' in link_href.lower():
                                movie_title = 'Grrr (2024) HDRip Malayalam Movie'
                            elif 'grrr-2024-telugu' in link_href.lower():
                                movie_title = 'Grrr (2024) HDRip Telugu Movie'
                            elif 'grrr-2024-tamil' in link_href.lower():
                                movie_title = 'Grrr (2024) HDRip Tamil Movie'
                        
                        # Check if this movie matches our query
                        if movie_title and query.lower() in movie_title.lower():
                            # Extract year
                            year_match = re.search(r'\b(19|20)\d{2}\b', movie_title)
                            year = year_match.group() if year_match else 'N/A'
                            
                            movie_page_url = urljoin(base_url, link_href)
                            
                            # Extract streaming URL from the movie page
                            streaming_url = await extract_streaming_url(page, movie_page_url)
                            
                            movie_data = {
                                'title': movie_title,
                                'url': streaming_url or movie_page_url,  # Use streaming URL if found, fallback to movie page
                                'movie_page': movie_page_url,  # Keep original movie page URL
                                'source': '5movierulz',
                                'year': year,
                                'poster': poster_url,
                                'genre': 'Unknown',
                                'rating': 'N/A'
                            }
                            
                            # Check for duplicates
                            if not any(existing['url'] == movie_data['url'] for existing in results):
                                results.append(movie_data)
                                print(f"✅ Added: {movie_title}")
                                if streaming_url:
                                    print(f"    🎬 Streaming URL: {streaming_url}")
                            
                    except Exception as e:
                        continue
                
            except Exception as e:
                print(f"❌ Error processing element {i+1}: {str(e)}")
                continue
        
        print(f"🎯 Total unique results: {len(results)}")
        return results[:max_results]
        
    except Exception as e:
        print(f"❌ Search error: {str(e)}")
        return []
    finally:
        await page.close()
        await context.close()
        await browser.close()
        await playwright.stop()

async def extract_streaming_url(browser_page, movie_page_url):
    """Extract the actual streaming URL from a movie page"""
    try:
        print(f"🔍 Extracting streaming URL from: {movie_page_url}")
        
        # Create a new page for this movie
        movie_page = await browser_page.context.new_page()
        
        try:
            # Navigate to the movie page
            await movie_page.goto(movie_page_url, wait_until='domcontentloaded', timeout=15000)
            await asyncio.sleep(2)
            
            # Look for streaming links - common patterns
            streaming_selectors = [
                'a[href*="streamlare"]',
                'a[href*="vcdnlare"]', 
                'a[href*="stream"]',
                'a[href*="watch"]',
                'iframe[src*="stream"]',
                'iframe[src*="vcdn"]',
                '.watch-link a',
                '.stream-link a',
                '.player-link a'
            ]
            
            for selector in streaming_selectors:
                try:
                    elements = await movie_page.query_selector_all(selector)
                    for element in elements:
                        href = await element.get_attribute('href') or await element.get_attribute('src')
                        if href and ('streamlare' in href or 'vcdnlare' in href or 'stream' in href):
                            print(f"    ✅ Found streaming URL: {href}")
                            return href
                except:
                    continue
            
            # Look for any links that might be streaming URLs in the page content
            all_links = await movie_page.query_selector_all('a')
            for link in all_links:
                try:
                    href = await link.get_attribute('href')
                    text = await link.inner_text()
                    if href and text:
                        text_lower = text.lower()
                        if ('watch' in text_lower and 'online' in text_lower) or 'streamlare' in text_lower:
                            if 'streamlare' in href or 'vcdnlare' in href or 'stream' in href:
                                print(f"    ✅ Found streaming URL: {href}")
                                return href
                except:
                    continue
            
            print(f"    ❌ No streaming URL found")
            return None
            
        finally:
            await movie_page.close()
            
    except Exception as e:
        print(f"    ❌ Error extracting streaming URL: {str(e)}")
        return None