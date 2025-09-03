# Movie Search App

A modern FastAPI-based web application for searching movies from multiple sources with a beautiful, responsive UI.

## Features

- 🎬 Clean, centered search interface
- 🔍 Real-time search with debouncing
- 📱 Fully responsive design
- ⚡ Fast FastAPI backend
- 🎨 Modern gradient design with glassmorphism effects
- 🏷️ Popular search suggestions
- 📊 Search results with movie cards
- 🌟 Movie ratings and source information

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd movie-search-app
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python main.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Open your browser**
   Navigate to: `http://localhost:8000`

## Project Structure

```
movie-search-app/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── templates/
│   └── index.html         # Main HTML template
├── static/
│   ├── css/
│   │   └── style.css      # Main stylesheet
│   ├── js/
│   │   └── app.js         # Frontend JavaScript
│   └── images/
│       └── .gitkeep       # Placeholder for images
```

## API Endpoints

- `GET /` - Main search page
- `GET /api/search?query={search_term}` - Search movies (to be implemented)

## Development

### Testing the UI

You can test the search interface with demo data by opening the browser console and running:
```javascript
demoSearch()
```

This will populate the results with sample movie data to test the UI components.

### Next Steps

The backend search functionality is ready to be implemented. The current `/api/search` endpoint returns a placeholder response. You can integrate with various movie APIs such as:

- TMDB (The Movie Database)
- OMDB API
- IMDb API
- Netflix API
- Amazon Prime API
- Hulu API

## Technologies Used

- **Backend**: FastAPI, Uvicorn
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Styling**: Custom CSS with gradients and glassmorphism
- **Icons**: Font Awesome
- **Fonts**: Google Fonts (Inter)

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.