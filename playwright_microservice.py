#!/usr/bin/env python3
"""
Playwright Microservice for Streaming URL Extraction
Provides a FastAPI service that uses Playwright to extract streaming URLs from movie pages
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from playwright.async_api import async_playwright
import asyncio
import uvicorn
import logging
import re
from typing import Optional, List, Dict, Any
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Playwright Streaming URL Extractor",
    description="Microservice to extract streaming URLs from movie pages using Playwright",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MoviePageRequest(BaseModel):
    url: str
    title: Optional[str] = None
    timeout: Optional[int] = 30000

class StreamingURLResponse(BaseModel):
    url: str
    title: Optional[str] = None
    streaming_url: Optional[str] = None
    movie_page: str
    success: bool
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}

class BulkRequest(BaseModel):
    urls: List[str]
    timeout: Optional[int] = 30000

# Global Playwright browser instance
browser = None
context = None

async def get_browser():
    """Get or create browser instance"""
    global browser, context
    if browser is None:
        try:
            playwright = await async_playwright().start()
            browser = await playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu'
                ]
            )
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            logger.info("✅ Browser instance created successfully")
        except Exception as e:
            logger.error(f"❌ Failed to create browser: {e}")
            if "Executable doesn't exist" in str(e):
                logger.error("💡 Playwright browsers not installed. Run: playwright install chromium")
            raise e
    return context

async def extract_streaming_url(movie_url: str, timeout: int = 30000) -> Dict[str, Any]:
    """
    Extract streaming URL from a movie page using Playwright
    Replicates the logic from movie_scraper_simple.py
    """
    try:
        logger.info(f"🔍 Extracting streaming URL from: {movie_url}")
        
        context = await get_browser()
        page = await context.new_page()
        
        # Navigate to movie page
        await page.goto(movie_url, wait_until='domcontentloaded', timeout=timeout)
        await asyncio.sleep(3)  # Wait for dynamic content
        
        # Extract streaming URL using the same patterns as Python code
        streaming_url = None
        
        # Pattern 1: Look for streamlare/vcdnlare links
        streaming_patterns = [
            'a[href*="streamlare"]',
            'a[href*="vcdnlare"]', 
            'iframe[src*="streamlare"]',
            'iframe[src*="vcdnlare"]',
            'a[href*="stream"][href*="/v/"]'
        ]
        
        for pattern in streaming_patterns:
            try:
                elements = await page.query_selector_all(pattern)
                for element in elements:
                    href = await element.get_attribute('href') or await element.get_attribute('src')
                    if href and ('streamlare' in href or 'vcdnlare' in href or '/v/' in href):
                        streaming_url = href
                        logger.info(f"    ✅ Found streaming URL: {streaming_url}")
                        break
                if streaming_url:
                    break
            except Exception as e:
                continue
        
        # Pattern 2: Look in page source for streaming URLs
        if not streaming_url:
            try:
                content = await page.content()
                
                # Regex patterns for streaming URLs
                url_patterns = [
                    r'href=["\']([^"\']*streamlare[^"\']*)["\']',
                    r'href=["\']([^"\']*vcdnlare[^"\']*)["\']',
                    r'src=["\']([^"\']*streamlare[^"\']*)["\']',
                    r'src=["\']([^"\']*vcdnlare[^"\']*)["\']',
                    r'href=["\']([^"\']*stream[^"\']*v/[^"\']*)["\']'
                ]
                
                for pattern in url_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        streaming_url = matches[0]
                        logger.info(f"    ✅ Found streaming URL in source: {streaming_url}")
                        break
            except Exception as e:
                logger.error(f"    ❌ Error searching page source: {e}")
        
        # Extract additional metadata
        metadata = {}
        try:
            title_element = await page.query_selector('title')
            if title_element:
                metadata['page_title'] = await title_element.inner_text()
            
            # Look for movie info
            year_match = re.search(r'\b(19|20)\d{2}\b', await page.content())
            if year_match:
                metadata['year'] = year_match.group()
                
            # Language detection
            content_lower = (await page.content()).lower()
            if 'telugu' in content_lower:
                metadata['language'] = 'Telugu'
            elif 'hindi' in content_lower:
                metadata['language'] = 'Hindi'
            elif 'tamil' in content_lower:
                metadata['language'] = 'Tamil'
            elif 'malayalam' in content_lower:
                metadata['language'] = 'Malayalam'
            elif 'english' in content_lower:
                metadata['language'] = 'English'
                
        except Exception as e:
            logger.warning(f"    ⚠️ Error extracting metadata: {e}")
        
        await page.close()
        
        if streaming_url:
            logger.info(f"    🎬 Successfully extracted streaming URL")
            return {
                'streaming_url': streaming_url,
                'success': True,
                'metadata': metadata
            }
        else:
            logger.warning(f"    ❌ No streaming URL found")
            return {
                'streaming_url': None,
                'success': False,
                'error': 'No streaming URL found',
                'metadata': metadata
            }
            
    except Exception as e:
        logger.error(f"    ❌ Error extracting streaming URL: {str(e)}")
        return {
            'streaming_url': None,
            'success': False,
            'error': str(e),
            'metadata': {}
        }

@app.on_event("startup")
async def startup_event():
    """Initialize browser on startup"""
    logger.info("🚀 Starting Playwright microservice...")
    try:
        await get_browser()
        logger.info("✅ Playwright browser initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize browser: {e}")
        logger.error("💡 Make sure to run: playwright install chromium")
        # Don't fail startup - let the service start and handle errors per request
        pass

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup browser on shutdown"""
    global browser
    if browser:
        await browser.close()
        logger.info("🔒 Playwright browser closed")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Playwright Streaming URL Extractor",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "extract": "/extract?url=<movie_page_url>",
            "extract_bulk": "/extract/bulk (POST with JSON)",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "browser_ready": browser is not None}

@app.get("/extract", response_model=StreamingURLResponse)
async def extract_single_url(
    url: str = Query(..., description="Movie page URL to extract streaming URL from"),
    title: Optional[str] = Query(None, description="Optional movie title"),
    timeout: int = Query(30000, description="Timeout in milliseconds")
):
    """
    Extract streaming URL from a single movie page
    
    Example: /extract?url=https://www.5movierulz.chat/grrr-2024-malayalam/movie-watch-online-free-3209.html
    """
    try:
        logger.info(f"📥 Single extraction request: {url}")
        
        result = await extract_streaming_url(url, timeout)
        
        return StreamingURLResponse(
            url=result.get('streaming_url', url),  # Use streaming URL or fallback to original
            title=title,
            streaming_url=result.get('streaming_url'),
            movie_page=url,
            success=result.get('success', False),
            error=result.get('error'),
            metadata=result.get('metadata', {})
        )
        
    except Exception as e:
        logger.error(f"❌ Error in single extraction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/extract/bulk")
async def extract_bulk_urls(request: BulkRequest):
    """
    Extract streaming URLs from multiple movie pages in parallel
    
    Example POST body:
    {
        "urls": [
            "https://www.5movierulz.chat/grrr-2024-malayalam/movie-watch-online-free-3209.html",
            "https://www.5movierulz.chat/rrr-2022-telugu/movie-watch-online-free-5105.html"
        ],
        "timeout": 30000
    }
    """
    try:
        logger.info(f"📥 Bulk extraction request: {len(request.urls)} URLs")
        
        # Process URLs in parallel
        tasks = [extract_streaming_url(url, request.timeout) for url in request.urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        responses = []
        for i, (url, result) in enumerate(zip(request.urls, results)):
            if isinstance(result, Exception):
                responses.append(StreamingURLResponse(
                    url=url,
                    streaming_url=None,
                    movie_page=url,
                    success=False,
                    error=str(result),
                    metadata={}
                ))
            else:
                responses.append(StreamingURLResponse(
                    url=result.get('streaming_url', url),
                    streaming_url=result.get('streaming_url'),
                    movie_page=url,
                    success=result.get('success', False),
                    error=result.get('error'),
                    metadata=result.get('metadata', {})
                ))
        
        logger.info(f"✅ Bulk extraction completed: {len(responses)} results")
        return {"results": responses, "total": len(responses)}
        
    except Exception as e:
        logger.error(f"❌ Error in bulk extraction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "playwright_microservice:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )