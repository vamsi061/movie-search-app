# n8n Integration Guide

## 🚀 n8n Workflow Setup

### Step 1: Import the Workflow
1. **Open your n8n instance**: https://n8n-7j94.onrender.com/
2. **Go to Workflows** → **Import from File**
3. **Upload**: `n8n_movie_search_workflow.json`
4. **Activate the workflow**

### Step 2: Configure the Webhook
1. **Open the Webhook node** in the imported workflow
2. **Copy the webhook URL** (should be something like):
   ```
   https://n8n-7j94.onrender.com/webhook/search-movies
   ```
3. **Update the URL** in `integrate_n8n_backend.py` if different

### Step 3: Test the Workflow
```bash
# Test the n8n webhook directly
curl "https://n8n-7j94.onrender.com/webhook/search-movies?query=rrr&max_results=5"
```

## 🔧 Workflow Components

### 1. **Webhook Trigger**
- **Path**: `/search-movies`
- **Method**: GET
- **Parameters**: `query`, `max_results`

### 2. **Extract Parameters**
- Extracts query and max_results from webhook
- Sets defaults if not provided

### 3. **Fetch Movie Search Page**
- Makes HTTP request to 5movierulz.irish
- Searches for movies based on query

### 4. **Parse Movies**
- Uses Cheerio to parse HTML
- Extracts movie titles, URLs, posters
- Filters results based on query

### 5. **Fetch Movie Page**
- Gets individual movie pages
- Runs for each found movie

### 6. **Extract Streaming URL**
- Finds direct streaming links (Streamlare, vcdnlare)
- Extracts video player URLs

### 7. **Format Response**
- Structures the final JSON response
- Includes movie data and metadata

## 🎯 Integration Benefits

### **Dual Source Architecture**
- **Playwright**: Direct browser automation
- **n8n**: Cloud-based workflow processing
- **Combined**: More comprehensive results

### **Performance**
- **Concurrent execution**: Both sources run simultaneously
- **Faster results**: Parallel processing
- **Fallback**: If one source fails, other continues

### **Scalability**
- **n8n cloud**: Handles heavy processing
- **Local Playwright**: Direct control
- **Load distribution**: Balanced workload

## 📊 API Response Format

```json
{
  "query": "rrr",
  "results": [
    {
      "title": "RRR (2022) BRRip Telugu Movie",
      "url": "https://ww7.vcdnlare.com/v/a1PgUCxbY3scYRn",
      "source": "n8n-5movierulz",
      "year": "2022",
      "poster": "https://www.5movierulz.irish/uploads/RRR-Telugu.jpg",
      "language": "TEL",
      "quality": "BRRip",
      "data_source": "n8n"
    }
  ],
  "total": 8,
  "sources": {
    "playwright": 5,
    "n8n": 3,
    "combined": 8
  },
  "message": "Found 8 movies from multiple sources"
}
```

## 🔧 Troubleshooting

### **n8n Workflow Not Working**
1. Check if workflow is **activated**
2. Verify **webhook URL** is correct
3. Test webhook directly with curl
4. Check n8n execution logs

### **No Results from n8n**
1. Verify **5movierulz.irish** is accessible from n8n
2. Check **HTML parsing** in Parse Movies node
3. Increase **timeout** values
4. Test with different queries

### **Integration Issues**
1. Check **integrate_n8n_backend.py** URL
2. Verify **network connectivity**
3. Check **error logs** in FastAPI
4. Test both sources independently

## 🚀 Deployment

### **Local Development**
```bash
# Start FastAPI with n8n integration
python main.py
```

### **Production**
1. **Deploy n8n workflow** to cloud
2. **Update webhook URLs** in integration
3. **Configure environment variables**
4. **Test end-to-end functionality**

## 📈 Monitoring

### **Check Sources**
- Monitor both Playwright and n8n success rates
- Track response times
- Log errors and failures

### **Performance Metrics**
- Total movies found per source
- Average response time
- Success/failure ratios

Your movie search app now uses **dual-source architecture** for maximum reliability and comprehensive results! 🎬