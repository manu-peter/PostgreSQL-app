from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="3-Tier Demo API")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {
        "message": "3-Tier Application API (Demo Mode)",
        "version": "1.0",
        "endpoints": ["/", "/health", "/api/items"],
        "note": "Using mock data - no database connection"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "backend"}

@app.get("/api/items")
async def get_items():
    # Mock data - simulating database results
    return {
        "items": [
            {"id": 1, "name": "Sample Item 1", "description": "This is a demo item from mock data"},
            {"id": 2, "name": "Sample Item 2", "description": "Another demo item without database"},
            {"id": 3, "name": "Sample Item 3", "description": "Third item in our demo dataset"}
        ],
        "count": 3,
        "source": "mock_data"
    }

@app.get("/api/status")
async def api_status():
    return {
        "backend": "running",
        "database": "not_connected_demo_mode",
        "mode": "demo"
    }
