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
            const response = await fetch(`/api/search?query=${encodeURIComponent(query)}`);
            const data = await response.json();
            
            this.hideLoading();
            
            if (data.results && data.results.length > 0) {
                this.displayResults(data.results, query);
            } else {
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
        
        // Extract language from title or URL
        const language = this.extractLanguage(movie.title, movie.url);
        
        // Extract quality from title
        const quality = this.extractQuality(movie.title);
        
        // Clean title
        const cleanTitle = this.cleanMovieTitle(movie.title);
        
        card.innerHTML = `
            <div class="movie-poster">
                <img src="${movie.poster || 'https://via.placeholder.com/300x450/667eea/ffffff?text=No+Poster'}" 
                     alt="${cleanTitle}" 
                     onerror="this.src='https://via.placeholder.com/300x450/667eea/ffffff?text=No+Poster'">
                <div class="watch-overlay">
                    <i class="fas fa-play"></i> Watch Now
                </div>
                ${language ? `<div class="movie-language">${language}</div>` : ''}
            </div>
            <div class="movie-info">
                <h3 class="movie-title">${cleanTitle}</h3>
                <div class="movie-meta">
                    <span class="movie-year">${movie.year || 'N/A'}</span>
                    ${quality ? `<span class="movie-quality">${quality}</span>` : ''}
                </div>
                <div class="movie-rating">
                    <i class="fas fa-star"></i>
                    <span>${movie.rating || '8.5'}</span>
                </div>
                <div class="movie-sources">
                    <span class="source-tag">${movie.source || '5movierulz'}</span>
                </div>
            </div>
        `;
        
        // Add click handler to open movie
        card.addEventListener('click', () => {
            if (movie.url) {
                window.open(movie.url, '_blank');
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
        
        const titleLower = title.toLowerCase();
        const urlLower = url.toLowerCase();
        
        for (const [lang, code] of Object.entries(languages)) {
            if (titleLower.includes(lang) || urlLower.includes(lang)) {
                return code;
            }
        }
        
        return null;
    }

    extractQuality(title) {
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