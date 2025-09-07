#!/usr/bin/env python3
"""
Test script for N8N integration
Run this to test the complete workflow
"""

import requests
import json
import time

def test_n8n_integration():
    """Test the complete n8n integration"""
    
    print("🧪 Testing N8N Integration")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Manual N8N trigger
    print("\n1️⃣ Testing manual N8N trigger...")
    try:
        response = requests.post(
            f"{base_url}/api/trigger-n8n",
            json={"query": "batman"},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Manual trigger: {result['status']}")
            print(f"   Query: {result['query']}")
            print(f"   Results: {result.get('total_results', 0)} movies")
            print(f"   Message: {result['message']}")
        else:
            print(f"❌ Manual trigger failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Manual trigger error: {e}")
    
    # Test 2: Search endpoint (should use n8n)
    print("\n2️⃣ Testing search endpoint...")
    try:
        response = requests.get(
            f"{base_url}/api/search?query=batman",
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Search endpoint: {result.get('total', 0)} results")
            print(f"   Source: {result.get('source', 'unknown')}")
            print(f"   Cached: {result.get('cached', False)}")
            print(f"   Message: {result.get('message', 'No message')}")
            
            # Show first few results
            if result.get('results'):
                print(f"   First 3 movies:")
                for i, movie in enumerate(result['results'][:3], 1):
                    title = movie.get('title', 'No title')
                    year = movie.get('year', 'Unknown')
                    print(f"     {i}. {title} ({year})")
        else:
            print(f"❌ Search failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Search error: {e}")
    
    # Test 3: Check cached results
    print("\n3️⃣ Testing cached results...")
    try:
        response = requests.get(f"{base_url}/api/n8n-results/batman")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('found'):
                movies = result['data'].get('movies', [])
                print(f"✅ Cached results: {len(movies)} movies found")
                print(f"   Source: {result['data'].get('source', 'unknown')}")
                print(f"   Search query: {result['data'].get('searchQuery', 'unknown')}")
            else:
                print("ℹ️ No cached results found")
        else:
            print(f"❌ Cache check failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Cache check error: {e}")
    
    # Test 4: Test with different query
    print("\n4️⃣ Testing with different query (lokah)...")
    try:
        response = requests.get(
            f"{base_url}/api/search?query=lokah",
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Lokah search: {result.get('total', 0)} results")
            print(f"   Source: {result.get('source', 'unknown')}")
            print(f"   Time: {result.get('search_time', 0)}s")
        else:
            print(f"❌ Lokah search failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Lokah search error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Integration test completed!")
    print("\nNext steps:")
    print("1. Import n8n_movie_scraper_workflow.json into your n8n instance")
    print("2. Update the webhook URL in the workflow")
    print("3. Test the workflow manually in n8n")
    print("4. Check that the webhook URL matches what's in your code")

if __name__ == "__main__":
    print("🚀 Starting N8N Integration Test")
    print("Make sure your FastAPI app is running on localhost:8000")
    print("Press Enter to continue or Ctrl+C to cancel...")
    input()
    
    test_n8n_integration()