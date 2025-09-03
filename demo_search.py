#!/usr/bin/env python3
"""
Demo script to test the movie search API
"""
import requests
import json
import time

def test_api_search():
    """Test the FastAPI search endpoint"""
    base_url = "http://localhost:8000"
    
    print("🎬 Testing Movie Search API")
    print("=" * 50)
    
    # Test queries
    test_queries = ["batman", "inception", "avengers"]
    
    for query in test_queries:
        print(f"\n🔍 Searching for: '{query}'")
        print("-" * 30)
        
        try:
            response = requests.get(f"{base_url}/api/search", params={"query": query}, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ Status: {response.status_code}")
                print(f"📊 Query: {data.get('query', 'N/A')}")
                print(f"📈 Total Results: {data.get('total', 0)}")
                print(f"💬 Message: {data.get('message', 'N/A')}")
                
                results = data.get('results', [])
                if results:
                    print(f"\n🎥 First {min(3, len(results))} results:")
                    for i, movie in enumerate(results[:3], 1):
                        print(f"  {i}. {movie.get('title', 'Unknown')} ({movie.get('year', 'N/A')})")
                        print(f"     Source: {movie.get('source', 'Unknown')}")
                        if movie.get('poster'):
                            print(f"     Poster: ✅")
                        print(f"     URL: {movie.get('url', 'N/A')[:60]}...")
                else:
                    print("❌ No movies found")
                    
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                
        except requests.exceptions.Timeout:
            print("⏰ Request timed out (this is normal for first requests)")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print("\n" + "="*50)
        time.sleep(2)  # Wait between requests

if __name__ == "__main__":
    test_api_search()