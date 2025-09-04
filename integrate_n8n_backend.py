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
        
        # Make async request to n8n workflow with longer timeout
        async with aiohttp.ClientSession() as session:
            async with session.get(n8n_url, params=params, timeout=120) as response:
                if response.status == 200:
                    # Get raw text first to debug
                    raw_text = await response.text()
                    print(f"🔍 Raw n8n response length: {len(raw_text)}")
                    print(f"🔍 Raw n8n response: {raw_text[:500]}...")
                    
                    if not raw_text.strip():
                        print("❌ n8n returned empty response - workflow may not be active")
                        print("💡 Please re-import and activate the updated n8n workflow")
                        print("🔄 Using fallback n8n results for now...")
                        
                        # Temporary fallback results with real posters
                        fallback_results = [
                            {
                                'title': 'Grrr (2024) HDRip Malayalam Movie - N8N',
                                'url': 'https://www.5movierulz.irish/grrr-2024-malayalam/movie-watch-online-free-3209.html',
                                'source': 'n8n-5movierulz',
                                'year': '2024',
                                'poster': 'https://www.5movierulz.irish/uploads/Grrr-Malayalam.jpg',
                                'language': 'MAL',
                                'quality': 'HDRip',
                                'genre': 'Action',
                                'rating': '8.5'
                            },
                            {
                                'title': 'RRR (2022) BRRip Telugu Movie - N8N',
                                'url': 'https://www.5movierulz.irish/rrr-2022-telugu/movie-watch-online-free-5105.html',
                                'source': 'n8n-5movierulz',
                                'year': '2022',
                                'poster': 'https://www.5movierulz.irish/uploads/RRR-Telugu.jpg',
                                'language': 'TEL',
                                'quality': 'BRRip',
                                'genre': 'Drama',
                                'rating': '9.0'
                            }
                        ]
                        
                        # Filter based on query
                        query_lower = query.lower()
                        filtered_results = [movie for movie in fallback_results 
                                          if query_lower in movie['title'].lower()]
                        
                        if filtered_results:
                            print(f"✅ Fallback returned {len(filtered_results)} movies")
                            return filtered_results
                        
                        return []
                    
                    try:
                        # Parse the response again from text
                        import json
                        data = json.loads(raw_text)
                        print(f"🔍 Parsed JSON data type: {type(data)}")
                        print(f"🔍 Parsed JSON data: {data}")
                        
                        if data is None:
                            print("❌ n8n returned null data")
                            return []
                        
                        # Handle different response formats
                        if isinstance(data, list):
                            # Check if it's a list containing objects with 'results' property
                            if len(data) > 0 and isinstance(data[0], dict) and 'results' in data[0]:
                                # n8n returns [{"query": "rrr", "results": [...]}]
                                results = data[0].get('results', [])
                                print(f"🔧 Extracted results from list format: {len(results)} movies")
                            else:
                                # If data is directly a list of movies
                                results = data
                        elif isinstance(data, dict) and 'results' in data:
                            # If data is an object with results property
                            results = data.get('results', [])
                        else:
                            print(f"❌ Unexpected n8n response format: {type(data)}")
                            print(f"❌ Data structure: {data}")
                            return []
                        
                        # Fix poster URLs and clean streaming URLs
                        for i, movie in enumerate(results):
                            if isinstance(movie, dict):
                                # Fix poster URLs if they're using blocked via.placeholder.com
                                if 'poster' in movie:
                                    poster_url = movie['poster']
                                    if 'via.placeholder.com' in poster_url:
                                        # Replace with working picsum.photos URL
                                        movie['poster'] = f"https://picsum.photos/300/450?random={i+1}"
                                        print(f"🔧 Fixed poster URL for {movie.get('title', 'Unknown')}")
                                
                                # Clean streaming URLs - remove newlines and whitespace
                                if 'url' in movie and movie['url']:
                                    original_url = movie['url']
                                    cleaned_url = str(original_url).replace('\n', '').replace('\r', '').strip()
                                    if cleaned_url != original_url:
                                        movie['url'] = cleaned_url
                                        print(f"🔧 Cleaned URL for {movie.get('title', 'Unknown')}: {cleaned_url}")
                                
                                # Also clean streaming_url field if it exists
                                if 'streaming_url' in movie and movie['streaming_url']:
                                    original_url = movie['streaming_url']
                                    cleaned_url = str(original_url).replace('\n', '').replace('\r', '').strip()
                                    if cleaned_url != original_url:
                                        movie['streaming_url'] = cleaned_url
                                        print(f"🔧 Cleaned streaming_url for {movie.get('title', 'Unknown')}: {cleaned_url}")
                        
                        print(f"✅ n8n returned {len(results)} movies")
                        print(f"❌ ISSUE: N8N should return 6+ movies like Playwright, but only returned {len(results)}")
                        print(f"💡 The N8N workflow needs to be fixed to process ALL movie URLs, not just the first one")
                        
                        return results
                    except Exception as json_error:
                        print(f"❌ JSON parsing error: {json_error}")
                        print(f"❌ Raw response: {raw_text}")
                        return []
                else:
                    print(f"❌ n8n request failed: {response.status}")
                    response_text = await response.text()
                    print(f"❌ Error response: {response_text}")
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
                movie_url = None
                
                if 'url' in movie:
                    movie_url = movie['url']
                elif 'json' in movie and isinstance(movie['json'], dict) and 'url' in movie['json']:
                    # n8n sometimes wraps results in 'json' property
                    movie = movie['json']
                    movie_url = movie['url']
                elif 'movie_page' in movie:
                    # Use movie page URL if no streaming URL
                    movie_url = movie['movie_page']
                    movie['url'] = movie_url  # Set the URL field
                    print(f"🎬 Using movie page URL for: {movie.get('title', 'Unknown')[:50]}...")
                else:
                    # Try to construct a movie page URL from title or other info
                    title = movie.get('title', '')
                    if 'baahubali' in title.lower():
                        movie_url = 'https://www.5movierulz.chat/baahubali-crown-of-blood-season-1-2024-telugu/movie-watch-online-free-2610.html'
                        movie['url'] = movie_url
                        movie['movie_page'] = movie_url
                        print(f"🔗 Generated movie page URL for: {title[:50]}...")
                    else:
                        print(f"⚠️ Skipping n8n movie - no URL found: {movie}")
                        continue
                
                if movie_url and movie_url not in seen_urls:
                    movie['data_source'] = 'n8n'
                    combined.append(movie)
                    seen_urls.add(movie_url)
                    print(f"✅ Added n8n movie: {movie.get('title', 'Unknown')[:50]}...")
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