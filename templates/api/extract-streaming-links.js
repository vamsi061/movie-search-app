export default async function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  // Handle preflight requests
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  // Only allow GET requests
  if (req.method !== 'GET') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  const { url } = req.query;

  if (!url) {
    res.status(400).json({ error: 'URL parameter is required' });
    return;
  }

  try {
    console.log('Extracting streaming links from:', url);
    
    // Fetch the movie page
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.5movierulz.villas/',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch movie page: ${response.status}`);
    }

    const html = await response.text();
    console.log('Movie page fetched, length:', html.length);

    // Extract all streaming links from the HTML
    const streamingLinks = extractAllStreamingLinks(html);
    
    console.log('Found streaming links:', streamingLinks.length);

    res.status(200).json({
      url: url,
      streamingLinks: streamingLinks,
      total: streamingLinks.length,
      message: `Found ${streamingLinks.length} streaming links`
    });

  } catch (error) {
    console.error('Streaming link extraction error:', error);
    res.status(500).json({ 
      error: 'Failed to extract streaming links',
      message: error.message 
    });
  }
}

function extractAllStreamingLinks(html) {
  const streamingLinks = [];
  
  try {
    // Comprehensive patterns for different streaming services
    const streamingPatterns = [
      // StreamLare patterns
      {
        pattern: /href=[\"']([^\"']*(?:streamlare|vcdnlare)\.com[^\"']*)[\"']/gi,
        service: 'streamlare',
        priority: 1,
        quality: 'HD'
      },
      
      // DoodStream patterns
      {
        pattern: /href=[\"']([^\"']*doodstream\.com[^\"']*)[\"']/gi,
        service: 'doodstream',
        priority: 2,
        quality: 'HD'
      },
      
      // MixDrop patterns
      {
        pattern: /href=[\"']([^\"']*mixdrop\.co[^\"']*)[\"']/gi,
        service: 'mixdrop',
        priority: 2,
        quality: 'HD'
      },
      
      // NetuTV/Waaw patterns
      {
        pattern: /href=[\"']([^\"']*waaw\/\?l=[^\"']*)[\"']/gi,
        service: 'netutv',
        priority: 1,
        quality: 'HD'
      },
      
      // Uperbox patterns
      {
        pattern: /href=[\"']([^\"']*uperbox\.io[^\"']*)[\"']/gi,
        service: 'uperbox',
        priority: 1,
        quality: 'HD'
      },
      
      // VidCloud patterns
      {
        pattern: /href=[\"']([^\"']*vidcloud[^\"']*)[\"']/gi,
        service: 'vidcloud',
        priority: 2,
        quality: 'HD'
      },
      
      // StreamHub patterns
      {
        pattern: /href=[\"']([^\"']*streamhub[^\"']*)[\"']/gi,
        service: 'streamhub',
        priority: 2,
        quality: 'HD'
      },
      
      // Torrent/Magnet patterns
      {
        pattern: /href=[\"']([^\"']*magnet:[^\"']*)[\"']/gi,
        service: 'torrent',
        priority: 3,
        quality: 'Various'
      },
      
      // Generic streaming patterns (catch-all)
      {
        pattern: /href=[\"']([^\"']*\/(?:watch|stream|play)[^\"']*)[\"']/gi,
        service: 'generic',
        priority: 4,
        quality: 'Unknown'
      }
    ];

    const foundUrls = new Set();

    // Extract URLs using patterns
    for (const patternObj of streamingPatterns) {
      let match;
      while ((match = patternObj.pattern.exec(html)) !== null) {
        let streamUrl = match[1];
        
        // Clean and validate URL
        if (streamUrl.startsWith('//')) {
          streamUrl = 'https:' + streamUrl;
        } else if (streamUrl.startsWith('/')) {
          streamUrl = 'https://www.5movierulz.villas' + streamUrl;
        }
        
        // Skip invalid URLs
        if (streamUrl.includes('javascript:') || streamUrl.includes('mailto:') || 
            streamUrl.includes('#') || streamUrl.length < 10) {
          continue;
        }
        
        // Avoid duplicates
        if (!foundUrls.has(streamUrl)) {
          foundUrls.add(streamUrl);
          
          // Try to extract quality from URL or surrounding context
          let quality = patternObj.quality;
          const qualityMatch = streamUrl.match(/\b(720p|1080p|4K|HD|HDRip|BluRay|DVDRip|WebRip|CAM|TS)\b/i);
          if (qualityMatch) {
            quality = qualityMatch[0];
          }
          
          streamingLinks.push({
            url: streamUrl,
            service: patternObj.service,
            priority: patternObj.priority,
            quality: quality,
            type: patternObj.service === 'torrent' ? 'torrent' : 'stream'
          });
        }
      }
    }

    // Look for embedded players and iframes
    const iframePatterns = [
      /<iframe[^>]*src=[\"']([^\"']+)[\"'][^>]*>/gi,
      /<embed[^>]*src=[\"']([^\"']+)[\"'][^>]*>/gi
    ];

    for (const pattern of iframePatterns) {
      let match;
      while ((match = pattern.exec(html)) !== null) {
        let embedUrl = match[1];
        
        if (embedUrl.startsWith('//')) {
          embedUrl = 'https:' + embedUrl;
        } else if (embedUrl.startsWith('/')) {
          embedUrl = 'https://www.5movierulz.villas' + embedUrl;
        }
        
        // Check if it's a known streaming service
        if ((embedUrl.includes('streamlare') || embedUrl.includes('doodstream') || 
             embedUrl.includes('mixdrop') || embedUrl.includes('vidcloud')) &&
            !foundUrls.has(embedUrl)) {
          
          foundUrls.add(embedUrl);
          
          let service = 'embedded';
          if (embedUrl.includes('streamlare')) service = 'streamlare';
          else if (embedUrl.includes('doodstream')) service = 'doodstream';
          else if (embedUrl.includes('mixdrop')) service = 'mixdrop';
          else if (embedUrl.includes('vidcloud')) service = 'vidcloud';
          
          streamingLinks.push({
            url: embedUrl,
            service: service,
            priority: 2,
            quality: 'HD',
            type: 'embedded'
          });
        }
      }
    }

    // Sort by priority (lower number = higher priority)
    streamingLinks.sort((a, b) => a.priority - b.priority);

  } catch (error) {
    console.error('Error extracting streaming links:', error);
  }

  return streamingLinks;
}