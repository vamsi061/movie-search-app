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
                            movie_title = await img_elem.get_attribute('alt') or ""
                            poster_src = await img_elem.get_attribute('src') or ""
                            if poster_src and not poster_src.startswith('data:'):
                                poster_url = urljoin(base_url, poster_src)
                        
                        # If no title from image, extract from URL or text
                        if not movie_title:
                            # Try to extract from URL
                            url_parts = link_href.split('/')
                            for part in url_parts:
                                if any(word in part.lower() for word in query.lower().split()):
                                    movie_title = part.replace('-', ' ').replace('movie watch online free', '').strip()
                                    break
                        
                        # Check if this movie matches our query
                        if movie_title and query.lower() in movie_title.lower():
                            # Extract year
                            year_match = re.search(r'\b(19|20)\d{2}\b', movie_title)
                            year = year_match.group() if year_match else 'N/A'
                            
                            movie_data = {
                                'title': movie_title,
                                'url': urljoin(base_url, link_href),
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