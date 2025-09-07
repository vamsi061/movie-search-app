// Movie Search App JavaScript

class MovieSearchApp {
    constructor() {
        this.searchForm = document.getElementById('searchForm');
        this.searchInput = document.getElementById('searchInput');
        this.loadingSpinner = document.getElementById('loadingSpinner');
        this.searchResults = document.getElementById('searchResults');
        this.noResults = document.getElementById('noResults');
        this.resultsContainer = document.getElementById('resultsContainer');
        this.resultsTitle = document.getElementById('resultsTitle');
        this.resultsCount = document.getElementById('resultsCount');
        
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Search form submission
        this.searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.performSearch();
        });

        // Suggestion tags
        document.querySelectorAll('.suggestion-tag').forEach(tag => {
            tag.addEventListener('click', (e) => {
                const query = e.target.getAttribute('data-query');
                this.searchInput.value = query;
                this.performSearch();
            });
        });

        // Real-time search on input (debounced)
        let searchTimeout;
        this.searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            const query = e.target.value.trim();
            
            if (query.length > 2) {
                searchTimeout = setTimeout(() => {
                    this.performSearch();
                }, 500);
            } else if (query.length === 0) {
                this.hideAllResults();
            }
        });

        // Enter key handling
        this.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.performSearch();
            }
        });
    }

    async performSearch() {
        const query = this.searchInput.value.trim();
        
        if (!query) {
            this.hideAllResults();
            return;
        }

        this.showLoading();

        try {
            // First, get results from your existing API
            const response = await fetch(`/api/search?query=${encodeURIComponent(query)}`);
            const data = await response.json();
            
            console.log('🔍 Frontend received data:', data);
            console.log('🔍 Results array:', data.results);
            console.log('🔍 Results length:', data.results ? data.results.length : 'undefined');
            
            let allResults = data.results || [];
            
            // Trigger n8n workflow to get 5movierulz.villas results
            this.triggerN8nScraping(query);
            
            // Check for cached n8n results
            try {
                const n8nResponse = await fetch(`/api/n8n-results/${encodeURIComponent(query)}`);
                if (n8nResponse.ok) {
                    const n8nData = await n8nResponse.json();
                    if (n8nData.movies && n8nData.movies.length > 0) {
                        console.log('📺 Adding n8n results:', n8nData.movies.length);
                        // Convert n8n format to your app format
                        const n8nMovies = n8nData.movies.map(movie => ({
                            title: movie.title,
                            url: movie.url,
                            poster: movie.image,
                            year: movie.year,
                            rating: movie.rating,
                            genre: movie.genre,
                            source: movie.source || '5movierulz.villas'
                        }));
                        allResults = [...allResults, ...n8nMovies];
                    }
                }
            } catch (n8nError) {
                console.log('ℹ️ No cached n8n results yet:', n8nError.message);
            }
            
            this.hideLoading();
            
            if (allResults.length > 0) {
                console.log('✅ Displaying combined results:', allResults.length);
                this.displayResults(allResults, query);
                
                // Show loading indicator for additional results
                this.showAdditionalResultsLoading(query);
            } else {
                console.log('❌ No results to display');
                this.showNoResults();
            }
        } catch (error) {
            console.error('Search error:', error);
            this.hideLoading();
            this.showError('An error occurred while searching. Please try again.');
        }
    }

    showLoading() {
        this.hideAllResults();
        this.loadingSpinner.classList.remove('hidden');
    }

    hideLoading() {
        this.loadingSpinner.classList.add('hidden');
    }

    hideAllResults() {
        this.loadingSpinner.classList.add('hidden');
        this.searchResults.classList.add('hidden');
        this.noResults.classList.add('hidden');
    }

    displayResults(results, query) {
        this.hideAllResults();
        
        this.resultsTitle.textContent = `Results for "${query}"`;
        this.resultsCount.textContent = `${results.length} movie${results.length !== 1 ? 's' : ''} found`;
        
        this.resultsContainer.innerHTML = '';
        
        results.forEach(movie => {
            const movieCard = this.createMovieCard(movie);
            this.resultsContainer.appendChild(movieCard);
        });
        
        this.searchResults.classList.remove('hidden');
    }

    createMovieCard(movie) {
        const card = document.createElement('div');
        card.className = 'movie-card';
        
        // Ensure movie has required properties with defaults and clean them
        const movieTitle = (movie.title || 'Unknown Movie').toString().trim();
        const movieUrl = (movie.url || '#').toString().replace(/\s+/g, '').replace(/\n/g, '').replace(/\r/g, '').trim();
        const movieYear = (movie.year || 'N/A').toString().trim();
        
        // Extract year from original title BEFORE cleaning
        const year = this.extractYear(movieTitle, movieYear);
        
        // Extract language from title or URL
        const language = this.extractLanguage(movieTitle, movieUrl);
        
        // Extract quality from title
        const quality = this.extractQuality(movieTitle);
        
        // Clean title (this removes year, so we extract it first)
        const cleanTitle = this.cleanMovieTitle(movieTitle);
        
        card.innerHTML = `
            <div class="movie-poster">
                <img src="${movie.poster || 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjQwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjNjY3ZWVhIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxOCIgZmlsbD0iI2ZmZmZmZiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPk5vIFBvc3RlcjwvdGV4dD48L3N2Zz4='}" 
                     alt="${cleanTitle}" 
                     onerror="this.onerror=null; this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjQwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjNjY3ZWVhIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxOCIgZmlsbD0iI2ZmZmZmZiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPk5vIFBvc3RlcjwvdGV4dD48L3N2Zz4=';">
                <div class="watch-overlay">
                    <i class="fas fa-play"></i> Watch Now
                </div>
                ${quality ? `<div class="movie-language">${quality}</div>` : ''}
            </div>
            <div class="movie-info">
                <h3 class="movie-title">${cleanTitle}</h3>
                <div class="movie-meta">
                    ${language ? `<span class="movie-year">${language}</span>` : ''}
                    ${year && year !== 'N/A' ? `<span class="movie-year">${year}</span>` : ''}
                </div>
                <div class="movie-sources">
                    <span class="source-tag">${movie.source || '5movierulz'}</span>
                </div>
            </div>
        `;
        
        // Add click handler to open movie
        card.addEventListener('click', () => {
            if (movieUrl && movieUrl !== '#') {
                window.open(movieUrl, '_blank');
            }
        });
        
        return card;
    }

    extractLanguage(title, url) {
        const languages = {
            'malayalam': 'MAL',
            'telugu': 'TEL', 
            'tamil': 'TAM',
            'hindi': 'HIN',
            'english': 'ENG',
            'kannada': 'KAN',
            'bengali': 'BEN'
        };
        
        // Safety checks
        const titleLower = (title || '').toLowerCase();
        const urlLower = (url || '').toLowerCase();
        
        for (const [lang, code] of Object.entries(languages)) {
            if (titleLower.includes(lang) || urlLower.includes(lang)) {
                return code;
            }
        }
        
        return null;
    }

    extractQuality(title) {
        // Safety check
        if (!title || typeof title !== 'string') {
            return null;
        }
        
        const qualities = ['HDRip', 'BRRip', 'DVDRip', 'HD', 'CAM', 'TS', '4K', '1080p', '720p'];
        const titleUpper = title.toUpperCase();
        
        for (const quality of qualities) {
            if (titleUpper.includes(quality.toUpperCase())) {
                return quality;
            }
        }
        
        return null;
    }

    cleanMovieTitle(title) {
        // Remove common suffixes and clean up the title
        let cleanTitle = title
            .replace(/\s*\(?\d{4}\)?\s*(HDRip|BRRip|DVDRip|HD|CAM|TS)\s*/gi, '')
            .replace(/\s*(Malayalam|Telugu|Tamil|Hindi|English|Kannada|Bengali)\s*/gi, '')
            .replace(/\s*Movie\s*Watch\s*Online\s*Free\s*/gi, '')
            .replace(/\s*Download\s*/gi, '')
            .replace(/\s+/g, ' ')
            .trim();
        
        return cleanTitle || title;
    }

    extractYear(title, existingYear) {
        // If we already have a valid year, use it
        if (existingYear && existingYear !== 'N/A') {
            return existingYear;
        }
        
        // Check if title is valid
        if (!title || typeof title !== 'string') {
            return null;
        }
        
        // Extract year from title - look for patterns like (2024) or just 2024
        const yearPatterns = [
            /\((\d{4})\)/,  // Matches (2024)
            /\b(19|20)\d{2}\b/  // Matches any 4-digit year starting with 19 or 20
        ];
        
        try {
            for (const pattern of yearPatterns) {
                const yearMatch = title.match(pattern);
                if (yearMatch) {
                    const year = yearMatch[1] || yearMatch[0]; // Use captured group if available
                    const yearNum = parseInt(year);
                    // Validate year is reasonable (between 1900 and current year + 5)
                    if (yearNum >= 1900 && yearNum <= new Date().getFullYear() + 5) {
                        return year;
                    }
                }
            }
        } catch (error) {
            console.warn('Error extracting year from title:', title, error);
            return null;
        }
        
        return null;
    }

    showNoResults() {
        this.hideAllResults();
        this.noResults.classList.remove('hidden');
    }

    showError(message) {
        this.hideAllResults();
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.innerHTML = `
            <i class="fas fa-exclamation-triangle"></i>
            <h3>Error</h3>
            <p>${message}</p>
        `;
        
        // Insert error message temporarily
        const container = document.querySelector('.search-section');
        container.appendChild(errorDiv);
        
        // Remove error message after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.parentNode.removeChild(errorDiv);
            }
        }, 5000);
    }

    async triggerN8nScraping(query) {
        try {
            console.log('🚀 Triggering n8n scraping for:', query);
            const response = await fetch('/api/trigger-n8n', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: query })
            });
            
            if (response.ok) {
                console.log('✅ N8n scraping triggered successfully');
                // Set up polling for new results
                this.pollForAdditionalResults(query);
            } else {
                console.log('⚠️ N8n trigger failed:', response.status);
            }
        } catch (error) {
            console.log('❌ Error triggering n8n:', error);
        }
    }

    showAdditionalResultsLoading(query) {
        // Add a loading indicator for additional results
        const loadingDiv = document.createElement('div');
        loadingDiv.id = 'additional-loading';
        loadingDiv.className = 'additional-loading';
        loadingDiv.innerHTML = `
            <div class="loading-card">
                <div class="loading-spinner-small"></div>
                <p>Searching 5movierulz.villas for more results...</p>
            </div>
        `;
        
        // Add to results container
        this.resultsContainer.appendChild(loadingDiv);
    }

    hideAdditionalResultsLoading() {
        const loadingDiv = document.getElementById('additional-loading');
        if (loadingDiv) {
            loadingDiv.remove();
        }
    }

    async pollForAdditionalResults(query, attempts = 0, maxAttempts = 12) {
        if (attempts >= maxAttempts) {
            this.hideAdditionalResultsLoading();
            console.log('⏰ Stopped polling for additional results');
            return;
        }

        try {
            await new Promise(resolve => setTimeout(resolve, 5000)); // Wait 5 seconds
            
            const response = await fetch(`/api/n8n-results/${encodeURIComponent(query)}`);
            if (response.ok) {
                const n8nData = await response.json();
                if (n8nData.movies && n8nData.movies.length > 0) {
                    console.log('🎬 New results found from 5movierulz.villas:', n8nData.movies.length);
                    this.appendAdditionalResults(n8nData.movies, query);
                    this.hideAdditionalResultsLoading();
                    return;
                }
            }
            
            // Continue polling
            this.pollForAdditionalResults(query, attempts + 1, maxAttempts);
        } catch (error) {
            console.log('Error polling for results:', error);
            this.pollForAdditionalResults(query, attempts + 1, maxAttempts);
        }
    }

    appendAdditionalResults(newMovies, query) {
        this.hideAdditionalResultsLoading();
        
        // Get current results count
        const currentCards = this.resultsContainer.querySelectorAll('.movie-card').length;
        
        // Convert n8n format to your app format and filter duplicates
        const existingTitles = new Set();
        this.resultsContainer.querySelectorAll('.movie-title').forEach(titleEl => {
            existingTitles.add(titleEl.textContent.toLowerCase().trim());
        });
        
        const newResults = newMovies
            .filter(movie => !existingTitles.has(movie.title.toLowerCase().trim()))
            .map(movie => ({
                title: movie.title,
                url: movie.url,
                poster: movie.image,
                year: movie.year,
                rating: movie.rating,
                genre: movie.genre,
                source: movie.source || '5movierulz.villas'
            }));

        if (newResults.length > 0) {
            // Add separator
            const separator = document.createElement('div');
            separator.className = 'results-separator';
            separator.innerHTML = `
                <div class="separator-line"></div>
                <div class="separator-text">Additional results from 5movierulz.villas</div>
                <div class="separator-line"></div>
            `;
            this.resultsContainer.appendChild(separator);

            // Add new movie cards
            newResults.forEach(movie => {
                const movieCard = this.createMovieCard(movie);
                movieCard.classList.add('new-result');
                this.resultsContainer.appendChild(movieCard);
            });

            // Update results count
            const totalResults = currentCards + newResults.length;
            this.resultsCount.textContent = `${totalResults} movie${totalResults !== 1 ? 's' : ''} found`;

            // Add animation to new cards
            setTimeout(() => {
                this.resultsContainer.querySelectorAll('.new-result').forEach(card => {
                    card.classList.add('fade-in');
                });
            }, 100);

            console.log(`✨ Added ${newResults.length} new results from 5movierulz.villas`);
        }
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new MovieSearchApp();
});

// Add some demo functionality for testing
window.demoSearch = function() {
    const demoResults = [
        {
            title: "Inception",
            year: "2010",
            genre: "Sci-Fi, Thriller",
            rating: "8.8",
            poster: "https://via.placeholder.com/300x450/667eea/ffffff?text=Inception",
            sources: ["Netflix", "Amazon Prime"]
        },
        {
            title: "The Dark Knight",
            year: "2008",
            genre: "Action, Crime, Drama",
            rating: "9.0",
            poster: "https://via.placeholder.com/300x450/764ba2/ffffff?text=Dark+Knight",
            sources: ["HBO Max", "Amazon Prime"]
        },
        {
            title: "Interstellar",
            year: "2014",
            genre: "Adventure, Drama, Sci-Fi",
            rating: "8.6",
            poster: "https://via.placeholder.com/300x450/667eea/ffffff?text=Interstellar",
            sources: ["Netflix", "Hulu"]
        }
    ];
    
    const app = new MovieSearchApp();
    app.displayResults(demoResults, "demo search");
};