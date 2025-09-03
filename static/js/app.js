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
        
        card.innerHTML = `
            <div class="movie-poster">
                <img src="${movie.poster || '/static/images/no-poster.jpg'}" 
                     alt="${movie.title}" 
                     onerror="this.src='/static/images/no-poster.jpg'">
            </div>
            <div class="movie-info">
                <h3 class="movie-title">${movie.title}</h3>
                <p class="movie-year">${movie.year || 'N/A'}</p>
                <p class="movie-genre">${movie.genre || 'Unknown'}</p>
                <div class="movie-rating">
                    <i class="fas fa-star"></i>
                    <span>${movie.rating || 'N/A'}</span>
                </div>
                <div class="movie-sources">
                    ${movie.sources ? movie.sources.map(source => 
                        `<span class="source-tag">${source}</span>`
                    ).join('') : ''}
                </div>
            </div>
        `;
        
        return card;
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