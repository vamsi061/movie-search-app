#!/usr/bin/env python3
"""
Direct webhook test to verify n8n connectivity
"""

import requests
import json

def test_webhook_direct():
    """Test the n8n webhook directly"""
    
    webhook_url = "https://n8n-7j94.onrender.com/webhook/movie-scraper"
    
    print(f"🧪 Testing webhook: {webhook_url}")
    print("=" * 60)
    
    # Test different methods
    test_cases = [
        ("GET", None, {"query": "batman"}),
        ("POST", {"query": "batman"}, None),
        ("POST", {"data": {"query": "batman"}}, None),
        ("POST", "batman", None),
    ]
    
    for method, json_data, params in test_cases:
        try:
            print(f"\n🔍 Testing {method} request...")
            
            if method == "GET":
                response = requests.get(
                    webhook_url,
                    params=params,
                    timeout=10
                )
            else:
                if isinstance(json_data, str):
                    response = requests.post(
                        webhook_url,
                        data=json_data,
                        headers={"Content-Type": "text/plain"},
                        timeout=10
                    )
                else:
                    response = requests.post(
                        webhook_url,
                        json=json_data,
                        headers={"Content-Type": "application/json"},
                        timeout=10
                    )
            
            print(f"   Status: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
            
            if response.text:
                print(f"   Response: {response.text[:200]}...")
            
            if response.status_code in [200, 201, 202]:
                print("   ✅ SUCCESS!")
                return True
            elif response.status_code == 404:
                print("   ❌ Webhook not found")
            else:
                print(f"   ⚠️ Unexpected status: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ Timeout after 10 seconds")
        except requests.exceptions.ConnectionError as e:
            print(f"   🔌 Connection error: {e}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Direct webhook test completed")
    
    # Additional debugging
    print("\n🔍 Additional debugging:")
    try:
        # Try to access the base n8n URL
        base_response = requests.get("https://n8n-7j94.onrender.com/", timeout=5)
        print(f"   Base n8n URL status: {base_response.status_code}")
    except Exception as e:
        print(f"   Base n8n URL error: {e}")
    
    return False

if __name__ == "__main__":
    print("🚀 Direct N8N Webhook Test")
    print("This will test the webhook directly without FastAPI")
    print("Press Enter to continue...")
    input()
    
    success = test_webhook_direct()
    
    if success:
        print("\n✅ Webhook is working! The issue might be in the FastAPI integration.")
    else:
        print("\n❌ Webhook is not responding. Check:")
        print("1. Is the n8n workflow active?")
        print("2. Is the webhook node configured correctly?")
        print("3. Is the n8n instance running?")