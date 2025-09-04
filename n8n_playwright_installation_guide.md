# N8N Playwright Node Installation Guide

## 🎯 **Method 1: Using N8N Community Nodes (Recommended)**

### **Step 1: Access Your N8N Instance**
1. Go to your n8n instance: `https://n8n-7j94.onrender.com`
2. Log in to your n8n dashboard

### **Step 2: Install Community Node**
1. **Go to Settings** → **Community Nodes**
2. **Click "Install a community node"**
3. **Enter package name**: `n8n-nodes-playwright`
4. **Click "Install"**

### **Step 3: Restart N8N**
- Your n8n instance will automatically restart
- The Playwright node will be available in the node palette

---

## 🎯 **Method 2: Manual Installation (If Method 1 Doesn't Work)**

### **Step 1: SSH/Access Your N8N Server**
```bash
# If you have SSH access to your n8n server
ssh your-server

# Navigate to n8n directory
cd /path/to/your/n8n/installation
```

### **Step 2: Install Playwright Node**
```bash
# Install the community node
npm install n8n-nodes-playwright

# Install Playwright browsers
npx playwright install
```

### **Step 3: Restart N8N Service**
```bash
# Restart n8n service
pm2 restart n8n
# or
systemctl restart n8n
# or
docker restart n8n-container
```

---

## 🎯 **Method 3: Alternative - Use HTTP Request + Code Nodes**

If you can't install the Playwright node, we can use the existing **HTTP Request** and **Code** nodes to achieve similar results:

### **Workflow Structure:**
1. **Webhook** → Receive search query
2. **HTTP Request** → Fetch the search page HTML
3. **Code Node** → Parse HTML and extract movie data
4. **Respond** → Return results

---

## 🔧 **Verification Steps**

### **After Installation:**
1. **Check Node Palette**: Look for "Playwright" in the node list
2. **Create Test Workflow**: Try adding a Playwright node
3. **Test Execution**: Run a simple page navigation test

### **Test Code:**
```javascript
// Simple test in Playwright node
return await page.evaluate(() => {
  return {
    title: document.title,
    url: window.location.href
  };
});
```

---

## 🚨 **Troubleshooting**

### **If Installation Fails:**
1. **Check n8n version** - Ensure you're running a recent version
2. **Check permissions** - Make sure you have admin access
3. **Check logs** - Look for error messages in n8n logs
4. **Try alternative method** - Use HTTP Request + Code approach

### **Common Issues:**
- **Permission denied**: Run with sudo or check user permissions
- **Network issues**: Check if your server can access npm registry
- **Version conflicts**: Update n8n to latest version

---

## 🎬 **Next Steps After Installation**

1. **Import the Playwright workflow** I created
2. **Test with a simple query** like "rrr"
3. **Verify real poster extraction** is working
4. **Update your main application** to use the new endpoint

---

## 💡 **Benefits You'll Get**

✅ **Real-time data extraction**
✅ **Actual movie posters from the website**
✅ **Dynamic search results**
✅ **No more hardcoded data**
✅ **Better reliability and performance**

Let me know which method works for you, and I'll help you with the next steps!