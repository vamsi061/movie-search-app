# N8N Movie Scraper Workflow - Quick Setup Summary

## 🎯 What You Get

I've created a complete n8n workflow that:
- ✅ Scrapes movie search results from https://www.5movierulz.chat/search_movies?s=lokah
- ✅ Extracts movie titles, URLs, images, ratings, years, and genres
- ✅ Removes duplicates and sorts by relevance
- ✅ Sends results to your FastAPI app
- ✅ Caches results for quick retrieval

## 📁 Files Created

1. **`n8n_movie_scraper_workflow.json`** - Complete n8n workflow (import this into n8n)
2. **`n8n_integration_guide.md`** - Detailed setup instructions
3. **Updated `main.py`** - Added endpoints to receive n8n data
4. **`tmp_rovodev_test_n8n_integration.py`** - Test script

## 🚀 Quick Setup (3 Steps)

### Step 1: Import Workflow to N8N
1. Go to https://n8n-7j94.onrender.com/
2. Create new workflow
3. Copy-paste contents of `n8n_movie_scraper_workflow.json`
4. Save as "5MovieRulz Movie Scraper"

### Step 2: Configure Your App URL
In the n8n workflow, update the "Send to Your App" node URL to:
```
https://your-deployed-app.onrender.com/api/append-results
```

### Step 3: Test the Workflow
1. Click "Execute Workflow" in n8n
2. Enter search query: "lokah" (or any movie name)
3. Watch it scrape and send results to your app

## 🔧 New API Endpoints Added

Your FastAPI app now has:

### POST `/api/append-results`
- Receives scraped data from n8n
- Caches results for 1 hour
- Returns success confirmation

### GET `/api/n8n-results/{query}`
- Retrieves cached n8n results
- Example: `/api/n8n-results/lokah`

## 📊 Expected Output Format

```json
{
  "searchQuery": "lokah",
  "totalResults": 15,
  "source": "5MovieRulz",
  "scrapedAt": "2024-01-01T12:00:00.000Z",
  "movies": [
    {
      "title": "Lokah Samastha",
      "url": "https://www.5movierulz.chat/movie/lokah-samastha",
      "image": "https://www.5movierulz.chat/images/lokah.jpg",
      "year": "2023",
      "rating": "7.5",
      "genre": "Drama",
      "source": "5MovieRulz"
    }
  ]
}
```

## 🎮 Usage Examples

### Manual Trigger in N8N
1. Open workflow in n8n
2. Click "Execute Workflow"
3. Enter search term
4. Results sent to your app automatically

### Webhook Trigger (External)
```bash
curl -X POST "https://n8n-7j94.onrender.com/webhook/movie-scraper" \
  -H "Content-Type: application/json" \
  -d '{"query": "avengers"}'
```

### From Your Frontend JavaScript
```javascript
// Trigger n8n scraping
fetch('https://n8n-7j94.onrender.com/webhook/movie-scraper', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: 'batman' })
});

// Get cached results
fetch('/api/n8n-results/batman')
    .then(response => response.json())
    .then(data => console.log(data.movies));
```

## 🔍 How It Works

1. **N8N Workflow Triggers** → Receives search query
2. **HTTP Request** → Fetches 5movierulz.chat search page
3. **JavaScript Parser** → Extracts movie data using Cheerio
4. **Filter & Format** → Cleans and structures data
5. **Send to App** → Posts results to your FastAPI endpoint
6. **Cache & Store** → Your app caches results for quick access

## 🛠️ Customization Options

- **Change Target Site**: Update URL in HTTP Request node
- **Modify Parsing**: Edit JavaScript code in Parse Movie Data node
- **Add More Fields**: Enhance extraction logic for additional metadata
- **Schedule Runs**: Add Cron trigger for automatic scraping
- **Error Handling**: Add error notification nodes

## 🧪 Testing

Run the test script to verify integration:
```bash
python3 tmp_rovodev_test_n8n_integration.py
```

This will simulate n8n sending data to your app and verify everything works.

## 📝 Next Steps

1. **Import the workflow** into your n8n instance
2. **Update the app URL** in the workflow
3. **Test with different search queries**
4. **Integrate with your frontend** to trigger scraping
5. **Monitor and optimize** based on usage

The workflow is production-ready and will efficiently scrape movie data from 5movierulz.chat and append it to your search results! 🎬