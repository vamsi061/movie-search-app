"""
Database-backed Movie Search for Ultimate Resource Efficiency
"""
import sqlite3
import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import aiofiles
import aiosqlite

class MovieDatabase:
    """SQLite database for caching movie results"""
    
    def __init__(self, db_path: str = "movies.db"):
        self.db_path = db_path
    
    async def init_db(self):
        """Initialize database tables"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS movies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    movie_page TEXT,
                    source TEXT DEFAULT '5movierulz',
                    year TEXT,
                    poster TEXT,
                    genre TEXT DEFAULT 'Unknown',
                    rating TEXT DEFAULT 'N/A',
                    query_keywords TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_verified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS search_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    results_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    hit_count INTEGER DEFAULT 0
                )
            """)
            
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_movies_keywords ON movies(query_keywords)
            """)
            
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_search_cache_query ON search_cache(query)
            """)
            
            await db.commit()
            print("✅ Database initialized")
    
    async def search_movies(self, query: str, max_results: int = 15) -> List[Dict]:
        """Search movies from database first, fallback to live search"""
        
        # Try cache first
        cached_results = await self.get_cached_search(query)
        if cached_results:
            return cached_results[:max_results]
        
        # Search in database
        db_results = await self.search_in_database(query, max_results)
        if len(db_results) >= 3:  # If we have decent results from DB
            await self.cache_search_results(query, db_results)
            return db_results
        
        # Fallback to live search and store results
        print(f"🔍 Database miss, performing live search for: {query}")
        live_results = await self.perform_live_search(query, max_results)
        
        if live_results:
            await self.store_movies(live_results, query)
            await self.cache_search_results(query, live_results)
        
        return live_results
    
    async def get_cached_search(self, query: str) -> Optional[List[Dict]]:
        """Get cached search results"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT results_json, hit_count FROM search_cache 
                WHERE query = ? AND expires_at > datetime('now')
                ORDER BY created_at DESC LIMIT 1
            """, (query.lower(),))
            
            row = await cursor.fetchone()
            if row:
                # Update hit count
                await db.execute("""
                    UPDATE search_cache SET hit_count = hit_count + 1 
                    WHERE query = ?
                """, (query.lower(),))
                await db.commit()
                
                results = json.loads(row[0])
                print(f"🚀 Database cache HIT for: {query} (hits: {row[1] + 1})")
                return results
        
        return None
    
    async def search_in_database(self, query: str, max_results: int) -> List[Dict]:
        """Search existing movies in database"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT title, url, movie_page, source, year, poster, genre, rating
                FROM movies 
                WHERE is_active = 1 
                AND (query_keywords LIKE ? OR title LIKE ?)
                AND last_verified > datetime('now', '-7 days')
                ORDER BY created_at DESC
                LIMIT ?
            """, (f"%{query.lower()}%", f"%{query}%", max_results))
            
            rows = await cursor.fetchall()
            results = []
            
            for row in rows:
                results.append({
                    'title': row[0],
                    'url': row[1],
                    'movie_page': row[2],
                    'source': row[3] + '-db',
                    'year': row[4],
                    'poster': row[5],
                    'genre': row[6],
                    'rating': row[7]
                })
            
            if results:
                print(f"📊 Database search found {len(results)} movies for: {query}")
            
            return results
    
    async def store_movies(self, movies: List[Dict], query: str):
        """Store movies in database"""
        async with aiosqlite.connect(self.db_path) as db:
            for movie in movies:
                # Check if movie already exists
                cursor = await db.execute("""
                    SELECT id FROM movies WHERE url = ?
                """, (movie['url'],))
                
                if not await cursor.fetchone():
                    await db.execute("""
                        INSERT INTO movies 
                        (title, url, movie_page, source, year, poster, genre, rating, query_keywords)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        movie['title'],
                        movie['url'],
                        movie.get('movie_page', movie['url']),
                        movie.get('source', '5movierulz'),
                        movie.get('year', 'N/A'),
                        movie.get('poster', ''),
                        movie.get('genre', 'Unknown'),
                        movie.get('rating', 'N/A'),
                        f"{query.lower()} {movie['title'].lower()}"
                    ))
            
            await db.commit()
            print(f"💾 Stored {len(movies)} movies in database")
    
    async def cache_search_results(self, query: str, results: List[Dict]):
        """Cache search results"""
        expires_at = datetime.now() + timedelta(hours=6)  # 6 hour cache
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO search_cache (query, results_json, expires_at)
                VALUES (?, ?, ?)
            """, (query.lower(), json.dumps(results), expires_at))
            await db.commit()
    
    async def perform_live_search(self, query: str, max_results: int) -> List[Dict]:
        """Perform live search using optimized Playwright"""
        try:
            # Import here to avoid loading Playwright unless needed
            from optimized_main import optimized_search_movies
            return await optimized_search_movies(query, max_results)
        except Exception as e:
            print(f"❌ Live search failed: {e}")
            return []
    
    async def cleanup_old_data(self):
        """Clean up old cache and inactive movies"""
        async with aiosqlite.connect(self.db_path) as db:
            # Remove expired cache
            await db.execute("""
                DELETE FROM search_cache WHERE expires_at < datetime('now')
            """)
            
            # Mark old movies as inactive
            await db.execute("""
                UPDATE movies SET is_active = 0 
                WHERE last_verified < datetime('now', '-30 days')
            """)
            
            await db.commit()
            print("🧹 Database cleanup completed")
    
    async def get_stats(self) -> Dict:
        """Get database statistics"""
        async with aiosqlite.connect(self.db_path) as db:
            # Movie stats
            cursor = await db.execute("SELECT COUNT(*) FROM movies WHERE is_active = 1")
            active_movies = (await cursor.fetchone())[0]
            
            # Cache stats
            cursor = await db.execute("SELECT COUNT(*) FROM search_cache WHERE expires_at > datetime('now')")
            active_cache = (await cursor.fetchone())[0]
            
            # Popular queries
            cursor = await db.execute("""
                SELECT query, hit_count FROM search_cache 
                WHERE expires_at > datetime('now')
                ORDER BY hit_count DESC LIMIT 5
            """)
            popular_queries = await cursor.fetchall()
            
            return {
                "active_movies": active_movies,
                "active_cache_entries": active_cache,
                "popular_queries": [{"query": q[0], "hits": q[1]} for q in popular_queries]
            }

# Global database instance
movie_db = MovieDatabase()

# FastAPI integration
from fastapi import FastAPI, BackgroundTasks

app = FastAPI(title="Database-Backed Movie Search")

@app.on_event("startup")
async def startup():
    await movie_db.init_db()

@app.get("/api/search")
async def search_movies_db(query: str = "", background_tasks: BackgroundTasks = None):
    """Database-backed search endpoint"""
    if not query.strip():
        return {"query": query, "results": [], "message": "Please enter a search term"}
    
    try:
        results = await movie_db.search_movies(query, max_results=15)
        
        # Background cleanup
        if background_tasks:
            background_tasks.add_task(movie_db.cleanup_old_data)
        
        return {
            "query": query,
            "results": results,
            "total": len(results),
            "source": "database-optimized",
            "message": f"Found {len(results)} movies"
        }
        
    except Exception as e:
        return {
            "query": query,
            "results": [],
            "error": str(e),
            "message": "Search failed"
        }

@app.get("/api/db/stats")
async def database_stats():
    """Get database statistics"""
    return await movie_db.get_stats()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)