"""
Integration script to combine n8n workflow results with existing movie search
"""
import requests
import asyncio
from typing import List, Dict

async def fetch_from_n8n(query: str, max_results: int = 20) -> List[Dict]:
    """
    Fetch movie results from n8n workflow
    """
    try:
        import aiohttp
        
        # n8n webhook URL - replace with your actual webhook URL
        n8n_url = "https://n8n-7j94.onrender.com/webhook/search-movies"
        
        # Parameters for the n8n workflow
        params = {
            "query": query,
            "max_results": max_results
        }
        
        print(f"🔗 Fetching from n8n: {n8n_url}")
        
        # Make async request to n8n workflow
        async with aiohttp.ClientSession() as session:
            async with session.get(n8n_url, params=params, timeout=60) as response:
                if response.status == 200:
                    data = await response.json()
                    results = data.get('results', [])
                    print(f"✅ n8n returned {len(results)} movies")
                    return results
                else:
                    print(f"❌ n8n request failed: {response.status}")
                    return []
            
    except Exception as e:
        print(f"❌ Error fetching from n8n: {str(e)}")
        return []

async def combine_results(playwright_results: List[Dict], n8n_results: List[Dict]) -> List[Dict]:
    """
    Combine results from both Playwright scraper and n8n workflow
    """
    combined = []
    seen_urls = set()
    
    # Add Playwright results first
    for movie in playwright_results:
        if isinstance(movie, dict) and 'url' in movie:
            if movie['url'] not in seen_urls:
                movie['data_source'] = 'playwright'
                combined.append(movie)
                seen_urls.add(movie['url'])
    
    # Add n8n results (avoiding duplicates) with better error handling
    for movie in n8n_results:
        try:
            if isinstance(movie, dict):
                # Handle different n8n response formats
                if 'url' in movie:
                    movie_url = movie['url']
                elif 'json' in movie and isinstance(movie['json'], dict) and 'url' in movie['json']:
                    # n8n sometimes wraps results in 'json' property
                    movie = movie['json']
                    movie_url = movie['url']
                else:
                    print(f"⚠️ Skipping n8n movie - no URL found: {movie}")
                    continue
                
                if movie_url not in seen_urls:
                    movie['data_source'] = 'n8n'
                    combined.append(movie)
                    seen_urls.add(movie_url)
        except Exception as e:
            print(f"❌ Error processing n8n movie: {str(e)} - {movie}")
            continue
    
    print(f"🔄 Combined results: {len(playwright_results)} from Playwright + {len(n8n_results)} from n8n = {len(combined)} total")
    
    return combined

# Test function
async def test_n8n_integration():
    """Test the n8n integration"""
    query = "rrr"
    
    print(f"🧪 Testing n8n integration for query: {query}")
    
    # Test n8n fetch
    n8n_results = await fetch_from_n8n(query, max_results=10)
    
    if n8n_results:
        print(f"✅ n8n integration working!")
        for i, movie in enumerate(n8n_results[:3], 1):
            print(f"  {i}. {movie.get('title', 'Unknown')} - {movie.get('url', 'No URL')}")
    else:
        print("❌ n8n integration failed")

if __name__ == "__main__":
    asyncio.run(test_n8n_integration())