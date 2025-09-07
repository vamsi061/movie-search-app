# N8N Movie Scraper Troubleshooting Guide

## Common Issues and Solutions

### 1. "Connection was aborted, perhaps the server is offline"

This error typically occurs when the target website blocks the request. Here are several solutions:

#### Solution A: Enhanced Headers (Already Applied)
The workflow now includes comprehensive browser headers to mimic a real browser request:
- User-Agent
- Accept headers
- Language preferences
- Security headers

#### Solution B: Add Delay Before Request
Add a "Wait" node before the HTTP request:

1. **Add Wait Node**:
   - Type: `Wait`
   - Duration: `3-5 seconds`
   - Place between "Start" and "Fetch Movie Search Page"

#### Solution C: Use Alternative Approach with Webhook Test
Instead of directly accessing the site, test with a known working endpoint first:

```json
{
  "url": "https://httpbin.org/get",
  "method": "GET"
}
```

#### Solution D: Proxy Configuration
If available, configure a proxy in the HTTP Request node:
- Add proxy settings in the "Options" section
- Use rotating proxies if needed

### 2. Website Blocking Detection

The updated workflow now checks for common blocking patterns:
- Access Denied messages
- Cloudflare protection
- 403 Forbidden responses

### 3. Alternative Scraping Approaches

#### Option 1: Use Your Existing Python Scraper
Instead of scraping directly in n8n, trigger your existing Python scraper:

```json
{
  "url": "http://your-app.com/api/search",
  "method": "GET",
  "qs": {
    "query": "{{ $json.query }}"
  }
}
```

#### Option 2: Browser Automation (If Available)
If your n8n instance supports browser automation:
- Use Puppeteer or Playwright nodes
- These are less likely to be blocked

### 4. Testing Steps

#### Step 1: Test Basic Connectivity
1. Replace the URL with `https://httpbin.org/get`
2. Execute the workflow
3. Verify you get a response

#### Step 2: Test Target Site Accessibility
1. Use a simple GET request to `https://www.5movierulz.chat`
2. Check if you get HTML content
3. Look for blocking messages

#### Step 3: Gradual URL Testing
1. Start with the main site: `https://www.5movierulz.chat`
2. Then try: `https://www.5movierulz.chat/search_movies`
3. Finally: `https://www.5movierulz.chat/search_movies?s=test`

### 5. Alternative Workflow Design

If the direct approach doesn't work, here's an alternative:

#### Workflow A: Use Your FastAPI App as Proxy
```
N8N → Your FastAPI App → 5movierulz.chat → Return Results → N8N
```

1. Create endpoint in your FastAPI app: `/api/proxy-search`
2. This endpoint uses your existing scraper
3. N8N calls your endpoint instead of the site directly

#### Workflow B: Scheduled Scraping
```
N8N Cron → Your App Scraper → Store in Database → API Returns Cached Results
```

### 6. Quick Fix Implementation

Here's a modified workflow that uses your existing app:

```json
{
  "name": "Movie Search via FastAPI Proxy",
  "nodes": [
    {
      "parameters": {
        "url": "http://your-app.com/api/search",
        "options": {
          "queryParameters": {
            "parameters": [
              {
                "name": "query",
                "value": "={{ $json.query }}"
              }
            ]
          }
        }
      },
      "name": "Search via Your App",
      "type": "n8n-nodes-base.httpRequest"
    }
  ]
}
```

### 7. Debugging Commands

To debug the connection issue:

#### Test from Command Line:
```bash
curl -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
     "https://www.5movierulz.chat/search_movies?s=lokah"
```

#### Test from Your App:
```python
import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

response = requests.get(
    'https://www.5movierulz.chat/search_movies?s=lokah',
    headers=headers,
    timeout=30
)

print(f"Status: {response.status_code}")
print(f"Content length: {len(response.text)}")
```

### 8. Recommended Next Steps

1. **Immediate Fix**: Use your existing Python scraper via API
2. **Test Connectivity**: Try the debugging commands above
3. **Alternative Sites**: Consider other movie databases
4. **Proxy Solution**: Implement if direct access fails

### 9. Updated Workflow Configuration

The workflow has been updated with:
- ✅ Enhanced browser headers
- ✅ Longer timeout (45 seconds)
- ✅ Redirect following
- ✅ Error detection for blocking
- ✅ Better error handling

Try importing the updated `n8n_movie_scraper_workflow.json` file again.

### 10. Contact Support

If issues persist:
1. Check n8n logs for detailed error messages
2. Verify your n8n instance has internet access
3. Test with a simple HTTP request to a known working site
4. Consider using your existing Python scraper as a proxy

The most reliable approach is often to use your existing, working scraper through an API endpoint rather than trying to replicate the scraping logic in n8n.