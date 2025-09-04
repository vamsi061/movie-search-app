"""
Optimized Movie Search Backend with Resource Management
"""
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import asyncio
from typing import List, Dict
import time

# Import optimizations
from cache_manager import get_cached_or_search, movie_cache

app = FastAPI(title="Optimized Movie Search App", description="Resource-efficient movie search")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Global browser instance for reuse
browser_instance = None
browser_lock = asyncio.Lock()

async def get_shared_browser():
    """Get or create a shared browser instance"""
    global browser_instance
    
    async with browser_lock:
        if browser_instance is None:
            from playwright.async_api import async_playwright
            print("🚀 Creating shared browser instance...")
            
            playwright = await async_playwright().start()
            browser_instance = {
                'playwright': playwright,
                'browser': await playwright.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-accelerated-2d-canvas',
                        '--no-first-run',
                        '--no-zygote',
                        '--disable-gpu',
                        '--memory-pressure-off',
                        '--max_old_space_size=512'
                    ]
                )
            }
            print("✅ Shared browser instance created")
        
        return browser_instance

async def optimized_search_movies(query: str, max_results: int = 15) -> List[Dict]:
    """Optimized movie search using shared browser"""
    browser_data = await get_shared_browser()
    browser = browser_data['browser']
    
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    
    try:
        return await perform_search_with_context(context, query, max_results)
    finally:
        await context.close()

async def perform_search_with_context(context, query: str, max_results: int) -> List[Dict]:
    """Perform search with given browser context"""
    from urllib.parse import quote
    import re
    
    page = await context.new_page()
    results = []
    
    try:
        base_url = "https://www.5movierulz.chat"
        search_url = f"{base_url}/search_movies?s={quote(query)}"
        
        print(f"🔍 Optimized search: {search_url}")
        await page.goto(search_url, wait_until='domcontentloaded', timeout=20000)
        await asyncio.sleep(2)  # Reduced wait time
        
        # Get film elements efficiently
        film_elements = await page.query_selector_all('div[class*="film"]')
        print(f"📦 Found {len(film_elements)} film elements")
        
        # Process elements with early termination
        for i, element in enumerate(film_elements[:max_results * 2]):  # Limit processing
            try:
                full_text = await element.inner_text()
                
                if query.lower() not in full_text.lower():
                    continue
                
                print(f"🎬 Processing element {i+1}")
                
                # Get links efficiently
                links = await element.query_selector_all('a')
                
                for link in links[:3]:  # Limit links per element
                    try:
                        href = await link.get_attribute('href')
                        if not href or 'movie-watch-online-free' not in href:
                            continue
                        
                        # Extract title efficiently
                        movie_title = await extract_title_fast(element, href, query)
                        
                        if movie_title and query.lower() in movie_title.lower():
                            # Extract streaming URL (with timeout)
                            streaming_url = await extract_streaming_url_fast(context, href)
                            
                            movie_data = {
                                'title': movie_title,
                                'url': streaming_url or href,
                                'movie_page': href,
                                'source': '5movierulz-optimized',
                                'year': extract_year(movie_title),
                                'poster': f"https://picsum.photos/300/450?random={len(results)+1}",
                                'genre': 'Action',
                                'rating': 'N/A'
                            }
                            
                            # Check for duplicates
                            if not any(existing['url'] == movie_data['url'] for existing in results):
                                results.append(movie_data)
                                print(f"✅ Added: {movie_title}")
                                
                                if len(results) >= max_results:
                                    print(f"🎯 Reached target: {max_results} results")
                                    return results
                        
                    except Exception:
                        continue
                        
            except Exception:
                continue
        
        return results
        
    finally:
        await page.close()

async def extract_title_fast(element, href: str, query: str) -> str:
    """Fast title extraction"""
    try:
        text = await element.inner_text()
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Look for lines with query and movie indicators
        for line in lines:
            if (query.lower() in line.lower() and 
                any(indicator in line.lower() for indicator in ['hdrip', 'brrip', '2024', '2023', '2022'])):
                return line
        
        # Fallback: extract from URL
        url_parts = href.split('/')
        for part in url_parts:
            if query.lower() in part.lower():
                return part.replace('-', ' ').title()
        
        return f"Movie {query.title()}"
        
    except Exception:
        return f"Movie {query.title()}"

async def extract_streaming_url_fast(context, movie_url: str) -> str:
    """Fast streaming URL extraction with timeout"""
    try:
        page = await context.new_page()
        
        try:
            # Quick navigation with short timeout
            await page.goto(movie_url, wait_until='domcontentloaded', timeout=10000)
            await asyncio.sleep(1)  # Minimal wait
            
            # Quick search for streaming URLs
            selectors = [
                'a[href*="streamlare"]',
                'a[href*="vcdnlare"]',
                'a[href*="stream"]'
            ]
            
            for selector in selectors:
                elements = await page.query_selector_all(selector)
                for element in elements[:2]:  # Check only first 2
                    href = await element.get_attribute('href')
                    if href and ('streamlare' in href or 'vcdnlare' in href):
                        return href
            
            return None
            
        finally:
            await page.close()
            
    except Exception:
        return None

def extract_year(title: str) -> str:
    """Extract year from title"""
    import re
    match = re.search(r'\b(20\d{2})\b', title)
    return match.group(1) if match else 'N/A'

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main search page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/search")
async def search_movies_optimized(query: str = "", background_tasks: BackgroundTasks = None):
    """Optimized API endpoint with caching and resource management"""
    if not query.strip():
        return {"query": query, "results": [], "message": "Please enter a search term"}
    
    start_time = time.time()
    
    try:
        print(f"🔍 Optimized search for: {query}")
        
        # Use cache-aware search
        results = await get_cached_or_search(
            query, 
            max_results=15, 
            search_function=optimized_search_movies
        )
        
        search_time = time.time() - start_time
        
        # Add background task to clean up cache periodically
        if background_tasks:
            background_tasks.add_task(cleanup_cache_if_needed)
        
        return {
            "query": query,
            "results": results,
            "total": len(results),
            "search_time": round(search_time, 2),
            "cached": movie_cache.get(query, 15) is not None,
            "cache_stats": movie_cache.stats(),
            "message": f"Found {len(results)} movies in {search_time:.2f}s"
        }
        
    except Exception as e:
        print(f"Search error: {str(e)}")
        return {
            "query": query,
            "results": [],
            "error": "Search temporarily unavailable",
            "message": "Please try again later"
        }

async def cleanup_cache_if_needed():
    """Background task to clean up expired cache entries"""
    stats = movie_cache.stats()
    if stats['expired_keys'] > 10:  # Clean if too many expired keys
        movie_cache.clear()
        print("🧹 Cache cleaned up")

@app.get("/api/cache/stats")
async def cache_stats():
    """Get cache statistics"""
    return movie_cache.stats()

@app.post("/api/cache/clear")
async def clear_cache():
    """Clear cache manually"""
    movie_cache.clear()
    return {"message": "Cache cleared successfully"}

@app.on_event("shutdown")
async def cleanup():
    """Cleanup resources on shutdown"""
    global browser_instance
    if browser_instance:
        await browser_instance['browser'].close()
        await browser_instance['playwright'].stop()
        print("🔒 Browser instance cleaned up")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)