# FastAPI main application file
from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from . import models, deps
from typing import Optional, List

app = FastAPI(title="Event Search API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Event Search API - API Only Version"}

@app.get("/events", response_model=List[models.Event])
async def get_events(
    query: Optional[str] = Query(None, description="Search query"),
    location: Optional[str] = Query(None, description="Location filter"),
    category: Optional[str] = Query(None, description="Category filter"),
    client: deps.get_http_client = Depends()
):
    """Get events from external APIs based on search criteria"""
    try:
        # Validate search parameters
        deps.validate_search_params(query, location, category)
        
        # Fetch events from external APIs
        events_data = await deps.fetch_external_events(
            client=client,
            query=query,
            location=location,
            category=category
        )
        
        return events_data["events"]
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching events: {str(e)}")

@app.get("/events/search", response_model=models.EventSearch)
async def search_events(
    query: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    max_price: Optional[float] = Query(None)
):
    """Advanced event search with multiple filters"""
    search_params = models.EventSearch(
        query=query,
        location=location,
        category=category,
        date_from=date_from,
        date_to=date_to,
        max_price=max_price
    )
    return search_params

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "event-search-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)