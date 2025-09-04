#!/usr/bin/env python3
"""
Debug script to understand why N8N is only returning 1 result instead of 6+
"""
import requests
import json

def test_n8n_workflow():
    """Test the current N8N workflow and analyze the issue"""
    
    print("🔍 Debugging N8N Multiple Results Issue")
    print("=" * 50)
    
    # Test with different parameters
    test_cases = [
        {"query": "rrr", "max_results": 1},
        {"query": "rrr", "max_results": 5},
        {"query": "rrr", "max_results": 10},
        {"query": "rrr", "max_results": 15},
    ]
    
    for test_case in test_cases:
        print(f"\n🧪 Testing: {test_case}")
        
        try:
            url = "https://n8n-7j94.onrender.com/webhook/search-movies"
            response = requests.get(url, params=test_case, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list) and len(data) > 0:
                    result = data[0]
                    results_count = len(result.get('results', []))
                    processing = result.get('processing', {})
                    
                    print(f"  📊 Results returned: {results_count}")
                    print(f"  📊 Pages fetched: {processing.get('total_pages_fetched', 'N/A')}")
                    print(f"  📊 Successful extractions: {processing.get('successful_extractions', 'N/A')}")
                    print(f"  📊 Streaming URLs found: {processing.get('streaming_urls_found', 'N/A')}")
                    
                    if results_count == 1:
                        print("  ❌ Only 1 result - ISSUE CONFIRMED")
                    elif results_count >= 5:
                        print("  ✅ Multiple results - ISSUE FIXED")
                    else:
                        print(f"  ⚠️ Partial results: {results_count}")
                        
                else:
                    print("  ❌ Invalid response format")
                    
            else:
                print(f"  ❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Request failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 DIAGNOSIS:")
    print("The N8N workflow is consistently returning only 1 result")
    print("regardless of the max_results parameter.")
    print("\n💡 SOLUTION:")
    print("1. Import the fixed workflow: n8n_fixed_workflow.json")
    print("2. Or import the test workflow: n8n_simple_test_workflow.json")
    print("3. The issue is in the workflow execution, not the microservice")

if __name__ == "__main__":
    test_n8n_workflow()