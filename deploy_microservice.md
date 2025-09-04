# Playwright Microservice Deployment Guide

## 🚀 **Quick Solutions to Make Microservice Public**

### **Option 1: Use Render.com (Recommended - Free)**

1. **Create account** at https://render.com
2. **Connect your GitHub** repository
3. **Create new Web Service**:
   - Build Command: `pip install -r requirements_microservice.txt && playwright install chromium`
   - Start Command: `python playwright_microservice.py`
   - Port: `8002`
4. **Deploy** - you'll get a public URL like `https://your-app.onrender.com`

### **Option 2: Use Railway.app (Free)**

1. **Create account** at https://railway.app
2. **Deploy from GitHub**
3. **Add environment variables** if needed
4. **Get public URL**

### **Option 3: Use ngrok (Local tunnel)**

```bash
# Install ngrok
brew install ngrok  # macOS
# or download from https://ngrok.com

# Start tunnel
ngrok http 8002

# Copy the public URL (e.g., https://abc123.ngrok.io)
```

### **Option 4: Use localtunnel (Simple)**

```bash
# Install localtunnel
npm install -g localtunnel

# Start tunnel
lt --port 8002

# Copy the public URL
```

## 🔧 **Update N8N Workflow**

Once you have a public URL, update the microservice URL in the n8n workflow:

```javascript
microserviceUrl: 'https://your-public-url.com'  // Replace with your actual URL
```

## 🎯 **Test the Setup**

1. **Test microservice directly**:
   ```bash
   curl "https://your-public-url.com/health"
   ```

2. **Test streaming extraction**:
   ```bash
   curl "https://your-public-url.com/extract?url=https://www.5movierulz.chat/grrr-2024-malayalam/movie-watch-online-free-3209.html"
   ```

3. **Test n8n workflow**:
   ```bash
   curl "https://n8n-7j94.onrender.com/webhook/search-movies?query=rrr"
   ```

## 🚀 **Quick Start with ngrok**

If you want to test immediately:

```bash
# Terminal 1: Start microservice
python3 playwright_microservice.py

# Terminal 2: Start ngrok tunnel
ngrok http 8002

# Copy the ngrok URL and update n8n workflow
# Import and activate the updated workflow
```

## 📋 **Files Needed for Deployment**

- `playwright_microservice.py` - Main service
- `requirements_microservice.txt` - Dependencies
- `n8n_with_microservice_workflow.json` - N8N workflow

## 🎬 **Expected Results**

Once deployed, you should get:
- **Real streaming URLs** extracted by Playwright
- **Multiple movies** from dynamic scraping
- **Reliable extraction** without n8n JavaScript limitations