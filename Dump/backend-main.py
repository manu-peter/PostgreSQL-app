from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import os
from typing import Optional

app = FastAPI(title="3-Tier Demo API")

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration from environment variables
DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "postgres-service"),
    "database": os.getenv("POSTGRES_DB", "appdb"),
    "user": os.getenv("POSTGRES_USER", "appuser"),
    "password": os.getenv("POSTGRES_PASSWORD", "apppassword"),
    "port": os.getenv("POSTGRES_PORT", "5432")
}

def get_db_connection():
    """Create database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create a sample table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert sample data if table is empty
        cursor.execute("SELECT COUNT(*) FROM items")
        count = cursor.fetchone()[0]
        
        if count == 0:
            sample_items = [
                ("Item 1", "First sample item"),
                ("Item 2", "Second sample item"),
                ("Item 3", "Third sample item")
            ]
            cursor.executemany(
                "INSERT INTO items (name, description) VALUES (%s, %s)",
                sample_items
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"⚠️ Database initialization failed: {e}")

@app.get("/")
async def read_root():
    """Root endpoint"""
    return {
        "message": "3-Tier Application API",
        "version": "1.0",
        "endpoints": ["/", "/health", "/api/items", "/api/db-status"]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "backend"}

@app.get("/api/db-status")
async def database_status():
    """Check database connectivity"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        return {
            "status": "connected",
            "database": DB_CONFIG["database"],
            "host": DB_CONFIG["host"],
            "version": db_version
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/items")
async def get_items():
    """Get all items from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, description, created_at FROM items ORDER BY id")
        
        items = []
        for row in cursor.fetchall():
            items.append({
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "created_at": str(row[3])
            })
        
        cursor.close()
        conn.close()
        
        return {"items": items, "count": len(items)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/items")
async def create_item(name: str, description: Optional[str] = None):
    """Create a new item"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO items (name, description) VALUES (%s, %s) RETURNING id",
            (name, description)
        )
        item_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"id": item_id, "name": name, "description": description}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
