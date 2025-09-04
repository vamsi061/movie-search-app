from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

app = FastAPI(title="Movie Search App", description="Search movies from different sources")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main search page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/search")
async def search_movies(query: str = ""):
    """API endpoint for movie search - combines Playwright and n8n results"""
    if not query.strip():
        return {"query": query, "results": [], "message": "Please enter a search term"}
    
    try:
        # Import both scrapers
        from movie_scraper_simple import search_movies_simple
        from integrate_n8n_backend import fetch_from_n8n, combine_results
        import asyncio
        
        print(f"🔍 Searching for: {query}")
        
        # TEMPORARY: Use only Playwright until N8N workflow is fixed
        # N8N workflow only finds 1 film element instead of 7 like Playwright
        playwright_results = await search_movies_simple(query, max_results=20)
        n8n_results = []  # Disable N8N temporarily
        
        print(f"🔧 TEMPORARY: Using only Playwright results until N8N workflow is fixed")
        print(f"🔧 N8N issue: Finds 1 film element vs Playwright finds 7 elements")
        
        # Handle exceptions
        if isinstance(playwright_results, Exception):
            print(f"Playwright error: {playwright_results}")
            playwright_results = []
        
        if isinstance(n8n_results, Exception):
            print(f"n8n error: {n8n_results}")
            n8n_results = []
        
        # Combine results from both sources
        combined_results = await combine_results(playwright_results, n8n_results)
        
        # Limit final results
        final_results = combined_results[:20]
        
        return {
            "query": query,
            "results": final_results,
            "total": len(final_results),
            "sources": {
                "playwright": len(playwright_results),
                "n8n": len(n8n_results),
                "combined": len(final_results)
            },
            "message": f"Found {len(final_results)} movies from multiple sources" if final_results else "No movies found"
        }
        
    except Exception as e:
        print(f"Search error: {str(e)}")
        return {
            "query": query,
            "results": [],
            "error": "Search temporarily unavailable",
            "message": "Please try again later"
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)