"""
Render.com Optimized Backend - 512MB RAM / 1 vCPU
Ultra-lightweight with aggressive memory management
"""
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
import uvicorn
import httpx
import asyncio
import gc
import psutil
import os
from typing import List, Dict, Optional
import time
import json
import hashlib

async def cleanup():
    """Cleanup on shutdown"""
    global browser_instance
    if browser_instance:
        await browser_instance.close()
        print("🔒 Browser cleaned up")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 FastAPI app starting up...")
    yield
    # Shutdown
    await cleanup()

app = FastAPI(title="Render Optimized Movie Search", lifespan=lifespan)

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
    
    def set(self, key: str, value: List[Dict], ttl: int = None):
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

async def trigger_n8n_workflow(query: str):
    """Trigger n8n workflow to scrape results"""
    try:
        n8n_webhook_url = "https://n8n-instance-vnyx.onrender.com/webhook/movie-scraper-villas"
        
        # Try different HTTP methods and payload formats
        methods_to_try = [
            ("POST", {"query": query}),
            ("GET", None),
            ("POST", {"data": {"query": query}}),
            ("POST", query)  # Just send the query string
        ]
        
        for method, payload in methods_to_try:
            try:
                async with httpx.AsyncClient(timeout=20.0) as client:
                    if method == "GET":
                        # Try GET with query parameter
                        response = await client.get(
                            f"{n8n_webhook_url}?query={query}",
                            headers={"User-Agent": "FastAPI-Movie-Search/1.0"}
                        )
                    else:
                        # Try POST with different payloads
                        if isinstance(payload, str):
                            response = await client.post(
                                n8n_webhook_url,
                                content=payload,
                                headers={"Content-Type": "text/plain"}
                            )
                        else:
                            response = await client.post(
                                n8n_webhook_url,
                                json=payload,
                                headers={"Content-Type": "application/json"}
                            )
                    
                    print(f"🧪 Tried {method} with payload {type(payload).__name__}: {response.status_code}")
                    
                    if response.status_code in [200, 201, 202]:
                        print(f"🚀 N8N workflow triggered successfully!")
                        print(f"   Method: {method}")
                        print(f"   Status: {response.status_code}")
                        print(f"   Response: {response.text[:200]}...")
                        return True
                    elif response.status_code == 404:
                        print(f"⚠️ 404 - Webhook not found or not active")
                    else:
                        print(f"⚠️ Unexpected status: {response.status_code}")
                        print(f"   Response: {response.text[:200]}...")
                        
            except Exception as e:
                print(f"❌ {method} request failed: {e}")
                continue
        
        print("❌ All request methods failed")
        return False
                
    except Exception as e:
        print(f"❌ Error triggering N8N workflow: {e}")
        return False

async def wait_for_n8n_results(query: str, max_wait: int = 10):
    """Wait for n8n results to be cached"""
    cache_key = f"n8n_results_{query.lower()}"
    
    for i in range(max_wait):
        await asyncio.sleep(1)
        cached_data = cache.get(cache_key)
        if cached_data and cached_data.get('movies'):
            print(f"✅ N8N results received after {i+1} seconds")
            return cached_data['movies']
    
    print(f"⏰ N8N results timeout after {max_wait} seconds")
    return []

@app.get("/api/search")
async def search_movies_render(query: str = "", use_n8n: bool = True):
    """N8N-powered search endpoint - saves resources by using n8n for scraping"""
    if not query.strip():
        return {"query": query, "results": [], "message": "Please enter a search term"}
    
    start_time = time.time()
    
    try:
        # Check if we have cached n8n results first
        n8n_cache_key = f"n8n_results_{query.lower()}"
        cached_n8n_data = cache.get(n8n_cache_key)
        
        if cached_n8n_data and cached_n8n_data.get('movies'):
            # Return cached n8n results immediately
            movies = cached_n8n_data['movies']
            search_time = time.time() - start_time
            
            print(f"⚡ Returning {len(movies)} cached n8n results for '{query}'")
            
            return {
                "query": query,
                "results": movies,
                "total": len(movies),
                "search_time": round(search_time, 2),
                "source": "n8n-cached",
                "cached": True,
                "message": f"Found {len(movies)} movies from n8n cache in {search_time:.1f}s"
            }
        
        if use_n8n:
            # Trigger n8n workflow and wait for results
            print(f"🚀 Triggering n8n workflow for fresh results: '{query}'")
            
            # Trigger the workflow
            n8n_triggered = await trigger_n8n_workflow(query)
            
            if n8n_triggered:
                # Wait for n8n results
                n8n_results = await wait_for_n8n_results(query, max_wait=15)
                
                if n8n_results:
                    search_time = time.time() - start_time
                    
                    return {
                        "query": query,
                        "results": n8n_results,
                        "total": len(n8n_results),
                        "search_time": round(search_time, 2),
                        "source": "n8n-live",
                        "cached": False,
                        "message": f"Found {len(n8n_results)} movies from n8n in {search_time:.1f}s"
                    }
        
        # Fallback to local scraper if n8n fails
        print(f"🔄 N8N failed, falling back to local scraper for '{query}'")
        results = await render_optimized_search(query, max_results=10)
        
        search_time = time.time() - start_time
        
        return {
            "query": query,
            "results": results,
            "total": len(results),
            "search_time": round(search_time, 2),
            "source": "local-fallback",
            "cached": cache.get(f"{query.lower()}_10") is not None,
            "message": f"Found {len(results)} movies (local fallback) in {search_time:.1f}s"
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

@app.post("/api/append-results")
async def append_movie_results(request: Request):
    """Receive scraped movie results from n8n workflow and append to search results"""
    try:
        data = await request.json()
        
        # Log the received data
        search_query = data.get('searchQuery', 'unknown')
        total_results = data.get('totalResults', 0)
        source = data.get('source', 'unknown')
        
        print(f"📥 Received {total_results} movies from {source} for query: '{search_query}'")
        
        # Store in cache for later retrieval
        cache_key = f"n8n_results_{search_query.lower()}"
        cache.set(cache_key, data)  # Cache for 1 hour
        
        # Format response
        response_data = {
            "status": "success",
            "message": f"Successfully received and cached {total_results} movies from {source}",
            "searchQuery": search_query,
            "totalResults": total_results,
            "source": source,
            "cacheKey": cache_key,
            "data": data
        }
        
        return response_data
        
    except Exception as e:
        print(f"❌ Error processing n8n results: {e}")
        return {
            "status": "error", 
            "message": f"Failed to process results: {str(e)}"
        }

@app.get("/api/n8n-results/{query}")
async def get_n8n_results(query: str):
    """Retrieve cached n8n results for a specific query"""
    try:
        cache_key = f"n8n_results_{query.lower()}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return {
                "status": "success",
                "found": True,
                "data": cached_data
            }
        else:
            return {
                "status": "success",
                "found": False,
                "message": f"No cached results found for query: '{query}'"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error retrieving results: {str(e)}"
        }

@app.post("/api/trigger-n8n")
async def manual_trigger_n8n(request: Request):
    """Manually trigger n8n workflow for testing"""
    try:
        data = await request.json()
        query = data.get('query', 'lokah')
        
        print(f"🧪 Manual n8n trigger for: '{query}'")
        
        # Trigger the workflow
        success = await trigger_n8n_workflow(query)
        
        if success:
            # Wait for results
            results = await wait_for_n8n_results(query, max_wait=20)
            
            return {
                "status": "success",
                "query": query,
                "triggered": True,
                "results_received": len(results) > 0,
                "total_results": len(results),
                "message": f"N8N workflow completed. Found {len(results)} movies."
            }
        else:
            return {
                "status": "error",
                "query": query,
                "triggered": False,
                "message": "Failed to trigger n8n workflow"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }

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