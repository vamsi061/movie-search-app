"""
Render.com Optimized Backend - 512MB RAM / 1 vCPU
Ultra-lightweight with aggressive memory management
"""
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import asyncio
import gc
import psutil
import os
from typing import List, Dict, Optional
import time
import json
import hashlib

app = FastAPI(title="Render Optimized Movie Search")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Ultra-lightweight cache (in-memory only)
class UltraLightCache:
    def __init__(self, max_size: int = 50):  # Limit cache size
        self.cache = {}
        self.access_times = {}
        self.max_size = max_size
    
    def _cleanup_if_needed(self):
        """Remove oldest entries if cache is full"""
        if len(self.cache) >= self.max_size:
            # Remove 20% of oldest entries
            sorted_items = sorted(self.access_times.items(), key=lambda x: x[1])
            to_remove = sorted_items[:self.max_size // 5]
            
            for key, _ in to_remove:
                self.cache.pop(key, None)
                self.access_times.pop(key, None)
            
            gc.collect()  # Force garbage collection
    
    def get(self, key: str) -> Optional[List[Dict]]:
        if key in self.cache:
            self.access_times[key] = time.time()
            return self.cache[key]
        return None
    
    def set(self, key: str, value: List[Dict]):
        self._cleanup_if_needed()
        self.cache[key] = value
        self.access_times[key] = time.time()

# Global lightweight cache
cache = UltraLightCache(max_size=30)  # Very small cache for Render

# Single browser instance (shared across all requests)
browser_instance = None
browser_lock = asyncio.Lock()

async def get_lightweight_browser():
    """Get ultra-lightweight browser for Render"""
    global browser_instance
    
    async with browser_lock:
        if browser_instance is None:
            from playwright.async_api import async_playwright
            
            playwright = await async_playwright().start()
            browser_instance = await playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                    '--disable-features=TranslateUI',
                    '--disable-ipc-flooding-protection',
                    '--memory-pressure-off',
                    '--max_old_space_size=256',  # Limit Node.js memory
                    '--single-process',  # Use single process for minimal memory
                ]
            )
            print("✅ Ultra-lightweight browser created for Render")
        
        return browser_instance

async def render_optimized_search(query: str, max_results: int = 8) -> List[Dict]:
    """Ultra-optimized search for Render deployment"""
    
    # Check cache first
    cache_key = f"{query.lower()}_{max_results}"
    cached = cache.get(cache_key)
    if cached:
        print(f"🚀 Cache HIT: {query}")
        return cached
    
    print(f"🔍 Render search: {query}")
    
    browser = await get_lightweight_browser()
    context = None
    page = None
    
    try:
        # Create minimal context
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            viewport={'width': 800, 'height': 600},  # Minimal viewport
            ignore_https_errors=True,
            java_script_enabled=False,  # Disable JS for faster loading
        )
        
        page = await context.new_page()
        
        # Ultra-fast navigation
        from urllib.parse import quote
        search_url = f"https://www.5movierulz.chat/search_movies?s={quote(query)}"
        
        await page.goto(search_url, wait_until='domcontentloaded', timeout=15000)
        await asyncio.sleep(1)  # Minimal wait
        
        # Quick element extraction
        results = []
        
        # Get film elements with minimal processing
        film_elements = await page.query_selector_all('div[class*="film"]')
        print(f"📦 Found {len(film_elements)} elements")
        
        # Process only first few elements to save memory
        for i, element in enumerate(film_elements[:max_results + 2]):
            try:
                text = await element.inner_text()
                if query.lower() not in text.lower():
                    continue
                
                # Get first valid link quickly
                links = await element.query_selector_all('a')
                for link in links[:2]:  # Check only first 2 links
                    href = await link.get_attribute('href')
                    if href and 'movie-watch-online-free' in href:
                        
                        # Quick title extraction
                        title = extract_title_from_text_fast(text, query)
                        
                        if title:
                            # Quick streaming URL extraction (with very short timeout)
                            streaming_url = await extract_streaming_url_ultra_fast(context, href)
                            
                            movie_data = {
                                'title': title,
                                'url': streaming_url or href,
                                'movie_page': href,
                                'source': 'render-optimized',
                                'year': extract_year_fast(title),
                                'poster': f"https://picsum.photos/300/450?random={len(results)+1}",
                                'genre': 'Action',
                                'rating': 'N/A'
                            }
                            
                            results.append(movie_data)
                            print(f"✅ Added: {title[:30]}...")
                            
                            if len(results) >= max_results:
                                break
                
                if len(results) >= max_results:
                    break
                    
            except Exception:
                continue
        
        # Cache results
        if results:
            cache.set(cache_key, results)
        
        return results
        
    except Exception as e:
        print(f"❌ Search error: {e}")
        return []
        
    finally:
        # Aggressive cleanup
        if page:
            await page.close()
        if context:
            await context.close()
        
        # Force garbage collection
        gc.collect()

def extract_title_from_text_fast(text: str, query: str) -> str:
    """Ultra-fast title extraction"""
    lines = text.split('\n')
    for line in lines[:5]:  # Check only first 5 lines
        line = line.strip()
        if (query.lower() in line.lower() and 
            len(line) > 10 and len(line) < 100 and
            any(indicator in line.lower() for indicator in ['hdrip', 'brrip', '2024', '2023', '2022', 'movie'])):
            return line
    
    return f"{query.title()} Movie"

async def extract_streaming_url_ultra_fast(context, movie_url: str) -> Optional[str]:
    """Ultra-fast streaming URL extraction with aggressive timeout"""
    page = None
    try:
        page = await context.new_page()
        
        # Very aggressive timeout for Render
        await page.goto(movie_url, wait_until='domcontentloaded', timeout=8000)
        
        # Quick search for streaming URLs
        selectors = ['a[href*="streamlare"]', 'a[href*="vcdnlare"]']
        
        for selector in selectors:
            elements = await page.query_selector_all(selector)
            if elements:
                href = await elements[0].get_attribute('href')
                if href:
                    return href
        
        return None
        
    except Exception:
        return None
    finally:
        if page:
            await page.close()

def extract_year_fast(title: str) -> str:
    """Fast year extraction"""
    import re
    match = re.search(r'\b(20\d{2})\b', title)
    return match.group(1) if match else 'N/A'

def get_memory_usage():
    """Get current memory usage"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024  # MB

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/search")
async def search_movies_render(query: str = "", background_tasks: BackgroundTasks = None):
    """Render-optimized search endpoint"""
    if not query.strip():
        return {"query": query, "results": [], "message": "Please enter a search term"}
    
    start_time = time.time()
    memory_before = get_memory_usage()
    
    try:
        # Limit results for Render
        results = await render_optimized_search(query, max_results=6)
        
        search_time = time.time() - start_time
        memory_after = get_memory_usage()
        
        # Background cleanup
        if background_tasks:
            background_tasks.add_task(cleanup_memory)
        
        return {
            "query": query,
            "results": results,
            "total": len(results),
            "search_time": round(search_time, 2),
            "memory_usage": f"{memory_after:.1f}MB",
            "memory_delta": f"{memory_after - memory_before:+.1f}MB",
            "cached": cache.get(f"{query.lower()}_6") is not None,
            "message": f"Found {len(results)} movies in {search_time:.1f}s"
        }
        
    except Exception as e:
        print(f"Search error: {str(e)}")
        return {
            "query": query,
            "results": [],
            "error": "Search temporarily unavailable",
            "message": "Please try again later"
        }

async def cleanup_memory():
    """Background memory cleanup for Render"""
    try:
        # Clear old cache entries
        if len(cache.cache) > 20:
            cache._cleanup_if_needed()
        
        # Force garbage collection
        gc.collect()
        
        memory_usage = get_memory_usage()
        if memory_usage > 400:  # If using more than 400MB
            print(f"⚠️ High memory usage: {memory_usage:.1f}MB - clearing cache")
            cache.cache.clear()
            cache.access_times.clear()
            gc.collect()
        
    except Exception as e:
        print(f"Cleanup error: {e}")

@app.get("/api/health")
async def health_check():
    """Health check with memory monitoring"""
    memory_usage = get_memory_usage()
    cache_size = len(cache.cache)
    
    return {
        "status": "healthy",
        "memory_usage": f"{memory_usage:.1f}MB",
        "memory_limit": "512MB",
        "cache_entries": cache_size,
        "browser_active": browser_instance is not None
    }

@app.get("/api/cache/clear")
async def clear_cache():
    """Clear cache to free memory"""
    cache.cache.clear()
    cache.access_times.clear()
    gc.collect()
    
    return {
        "message": "Cache cleared",
        "memory_usage": f"{get_memory_usage():.1f}MB"
    }

@app.on_event("shutdown")
async def cleanup():
    """Cleanup on shutdown"""
    global browser_instance
    if browser_instance:
        await browser_instance.close()
        print("🔒 Browser cleaned up")

if __name__ == "__main__":
    # Render-optimized uvicorn settings
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=int(os.environ.get("PORT", 8000)),
        workers=1,  # Single worker for Render
        loop="asyncio",
        access_log=False,  # Disable access logs to save memory
    )