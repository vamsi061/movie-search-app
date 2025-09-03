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
    """API endpoint for movie search"""
    if not query.strip():
        return {"query": query, "results": [], "message": "Please enter a search term"}
    
    try:
        # Import the simplified scraper
        from movie_scraper_simple import search_movies_simple
        
        # Search for movies using the working simple scraper
        results = await search_movies_simple(query, max_results=20)
        
        return {
            "query": query,
            "results": results,
            "total": len(results),
            "message": f"Found {len(results)} movies" if results else "No movies found"
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