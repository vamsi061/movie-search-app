# N8N 5MovieRulz.Villas Integration Setup Guide

## 🎯 Overview

This guide will help you set up an n8n workflow that scrapes movie search results from `https://www.5movierulz.villas/search_movies?s=rrr` and integrates them with your current movie search UI. The workflow uses Playwright to bypass ads, bots, and blockers.

## 📋 Prerequisites

1. **N8N Instance**: Access to https://n8n-instance-vnyx.onrender.com/workflow/new?projectId=4GFWNyNRZNSnlBCc
2. **Your Movie App**: Running FastAPI application with n8n integration endpoints
3. **Playwright Node**: Ensure your n8n instance has the Playwright node available

## 🚀 Step-by-Step Setup

### Step 1: Import the N8N Workflow

1. **Go to your N8N instance**: https://n8n-instance-vnyx.onrender.com/workflow/new?projectId=4GFWNyNRZNSnlBCc

2. **Create a new workflow** or open an existing one

3. **Import the workflow JSON**:
   - Copy the contents of `n8n_5movierulz_villas_workflow.json`
   - In n8n, click on the menu (three dots) → "Import from JSON"
   - Paste the JSON content
   - Click "Import"

4. **Save the workflow** with name: "5MovieRulz Villas Advanced Scraper"

### Step 2: Configure the Workflow

#### Update the "Send to Your App" Node

1. **Click on the "Send to Your App" node**
2. **Update the URL** to your deployed app:
   ```
   https://your-app-domain.com/api/append-results
   ```
   Replace `your-app-domain.com` with your actual domain

#### Configure Webhook (Optional)

The workflow includes a webhook trigger. The webhook URL will be:
```
https://n8n-instance-vnyx.onrender.com/webhook/movie-scraper-villas
```

### Step 3: Test the Workflow

#### Manual Test
1. **Click "Execute Workflow"** in n8n
2. **Enter test data**:
   ```json
   {
     "query": "rrr"
   }
   ```
3. **Watch the execution** - it should:
   - Prepare search data
   - Scrape 5movierulz.villas using Playwright
   - Parse movie results
   - Filter valid movies
   - Format results
   - Send to your app

#### Expected Output
The workflow should find 6 movies for "rrr" and send them to your app in this format:
```json
{
  "searchQuery": "rrr",
  "totalResults": 6,
  "source": "5movierulz.villas",
  "scrapedAt": "2024-01-01T12:00:00.000Z",
  "scrapeMethod": "playwright-advanced",
  "status": "success",
  "movies": [
    {
      "title": "RRR",
      "url": "https://www.5movierulz.villas/movie/rrr-2022",
      "image": "https://www.5movierulz.villas/images/rrr.jpg",
      "year": "2022",
      "rating": "8.8",
      "genre": "Action",
      "source": "5movierulz.villas",
      "searchQuery": "rrr",
      "scrapedAt": "2024-01-01T12:00:00.000Z"
    }
  ]
}
```

## 🔧 How It Works

### Workflow Flow
1. **Webhook Trigger** → Receives search query
2. **Prepare Search Data** → Validates query and builds URL
3. **Playwright Advanced Scrape** → Fetches page with anti-bot measures
4. **Parse Movie Results** → Extracts movie data using regex patterns
5. **Filter Valid Movies** → Removes invalid entries
6. **Format Final Results** → Structures data and removes duplicates
7. **Send to Your App** → Posts results to your FastAPI endpoint
8. **Webhook Response** → Returns success confirmation

### Anti-Bot Features
- **Stealth Mode**: Playwright runs in stealth mode
- **Real Browser Headers**: Mimics actual browser requests
- **Wait Strategies**: Waits for content to load
- **Scroll Simulation**: Simulates user scrolling
- **Extended Timeout**: 60-second timeout for slow loading

### Frontend Integration
Your updated JavaScript will:
1. **Trigger n8n workflow** when user searches
2. **Show loading indicator** for additional results
3. **Poll for results** every 5 seconds
4. **Append new movies** with visual separator
5. **Animate new results** with fade-in effect

## 🎮 Usage Examples

### From Your Frontend
When a user searches for "rrr", your app will:
1. Show existing results immediately
2. Trigger n8n scraping in background
3. Display "Searching 5movierulz.villas..." indicator
4. Append new results when available

### Direct Webhook Call
```bash
curl -X POST "https://n8n-instance-vnyx.onrender.com/webhook/movie-scraper-villas" \
  -H "Content-Type: application/json" \
  -d '{"query": "rrr"}'
```

### From Your App API
```bash
curl -X POST "https://your-app-domain.com/api/trigger-n8n" \
  -H "Content-Type: application/json" \
  -d '{"query": "rrr"}'
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Playwright Node Not Available
- Ensure your n8n instance supports Playwright
- Alternative: Use HTTP Request with enhanced headers

#### 2. Site Blocking Requests
- The workflow includes anti-bot measures
- If still blocked, try different user agents
- Consider using proxy servers

#### 3. No Results Found
- Check if the site structure changed
- Verify the parsing regex patterns
- Test with different search queries

#### 4. App Integration Fails
- Verify your app URL in "Send to Your App" node
- Check if `/api/append-results` endpoint exists
- Ensure proper CORS settings

### Debug Steps

1. **Test Individual Nodes**:
   - Execute "Prepare Search Data" alone
   - Check "Playwright Advanced Scrape" output
   - Verify "Parse Movie Results" extraction

2. **Check Logs**:
   - Look at n8n execution logs
   - Check your app logs for incoming requests
   - Monitor browser console for frontend errors

3. **Validate Data Flow**:
   - Ensure webhook receives correct data
   - Verify parsing extracts movie information
   - Check if results reach your app

## 📊 Performance Optimization

### Caching Strategy
- Results cached for 1 hour in your app
- Duplicate detection prevents redundant entries
- Polling stops after finding results

### Resource Management
- Playwright runs headless for efficiency
- 60-second timeout prevents hanging
- Stealth mode reduces detection

## 🔄 Customization Options

### Modify Search Target
Update the URL in "Prepare Search Data":
```javascript
const targetUrl = `https://www.5movierulz.villas/search_movies?s=${encodeURIComponent(query)}`;
```

### Adjust Parsing Logic
Modify regex patterns in "Parse Movie Results" for different site structures.

### Change Polling Frequency
Update polling interval in your frontend:
```javascript
await new Promise(resolve => setTimeout(resolve, 5000)); // 5 seconds
```

## ✅ Success Indicators

- ✅ Workflow executes without errors
- ✅ Finds 6 movies for "rrr" search
- ✅ Results appear in your app UI
- ✅ No duplicate movies shown
- ✅ Smooth animations for new results

## 🎬 Final Result

After setup, when users search for "rrr":
1. **Immediate results** from your existing sources
2. **Loading indicator** appears
3. **6 additional movies** from 5movierulz.villas
4. **Visual separator** shows new source
5. **Smooth animations** for better UX

The integration provides a seamless experience where users get comprehensive movie results from multiple sources!