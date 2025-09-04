# N8N Workflow Debugging Guide

## 🔍 **Current Issue Analysis**

Looking at the logs, the n8n workflow is working correctly but only finding 1 movie:

```
"processing": {
  "total_pages_fetched": 1,
  "successful_extractions": 1
}
```

This means the workflow is only extracting 1 movie URL from the search results page.

## 🎯 **Root Cause**

The issue is in the URL extraction logic. For "rrr" search, the workflow is being too strict with the query matching:

```javascript
// Current logic (too strict):
if (urlLower.includes(queryLower)) {
  // Only matches URLs that contain "rrr" exactly
}
```

But the search results might have movies like:
- `grrr-2024-malayalam` (contains "rrr" but not exact match)
- `rrr-2022-telugu` (exact match)
- `rrr-behind-beyond` (exact match)

## 🔧 **Solutions**

### **Solution 1: Debug the N8N Workflow**

Add this to the "Extract Movie URLs" node to see what's happening:

```javascript
// Debug: Log all found URLs
console.log(`🔍 All movie links found:`);
allMatches.forEach((url, index) => {
  console.log(`  ${index + 1}. ${url}`);
});

// Debug: Log query matching
console.log(`🎯 Query: "${query}" (looking for matches)`);
allMatches.forEach((url, index) => {
  const matches = url.toLowerCase().includes(query.toLowerCase());
  console.log(`  ${index + 1}. ${url} - Match: ${matches}`);
});
```

### **Solution 2: More Flexible Query Matching**

Update the query matching logic:

```javascript
// More flexible matching
const urlLower = url.toLowerCase();
const queryLower = query.toLowerCase();

// Match if:
// 1. URL contains the exact query
// 2. URL contains any word from the query
// 3. Query contains any part of the URL
const isMatch = urlLower.includes(queryLower) || 
                queryLower.split(' ').some(word => urlLower.includes(word)) ||
                urlLower.split('-').some(part => queryLower.includes(part));
```

### **Solution 3: Fallback to All Movies**

If strict matching finds few results, include more movies:

```javascript
// If less than 3 movies found, be more lenient
if (movieUrls.length < 3) {
  console.log(`🔄 Only ${movieUrls.length} movies found, adding more...`);
  
  for (let i = 0; i < Math.min(allMatches.length, 5); i++) {
    const url = allMatches[i];
    const moviePageUrl = url.startsWith('http') ? url : `${baseUrl}${url}`;
    
    if (!processedUrls.has(moviePageUrl)) {
      movieUrls.push({
        movieUrl: moviePageUrl,
        query: query,
        baseUrl: baseUrl,
        userAgent: userAgent,
        index: movieUrls.length
      });
    }
  }
}
```

## 🎬 **Expected Behavior**

For "rrr" search, the workflow should find and process:
1. `grrr-2024-malayalam` ✅
2. `grrr-2024-telugu` ✅
3. `grrr-2024-tamil` ✅
4. `rrr-2022-telugu` ✅
5. `rrr-behind-beyond` ✅

This should result in:
```
"processing": {
  "total_pages_fetched": 5,
  "successful_extractions": 5
}
```

## 🚀 **Quick Fix**

The easiest solution is to make the query matching less strict in the n8n workflow. The current logic is probably only finding 1 exact match instead of all related movies.

## 📋 **Next Steps**

1. **Test the n8n workflow directly** to see the debug logs
2. **Update the query matching logic** to be more flexible
3. **Add fallback logic** to include more movies if few are found
4. **Verify the results** show multiple movies

The Playwright scraper finds 6 movies for "rrr", so the n8n workflow should be able to find at least 3-5 movies from the same search results page.