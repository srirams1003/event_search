# Pydantic models for the Event Search API
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class EventBase(BaseModel):
    title: str = Field(..., description="Event title")
    description: str = Field(..., description="Event description")
    location: str = Field(..., description="Event location")
    date: str = Field(..., description="Event date in ISO format")
    price: Optional[float] = Field(None, description="Event price")
    category: str = Field(..., description="Event category")

class Event(EventBase):
    id: int = Field(..., description="Unique event identifier")
    source: Optional[str] = Field(None, description="Source API provider")
    url: Optional[str] = Field(None, description="Event URL")
    image_url: Optional[str] = Field(None, description="Event image URL")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Jazz Night at Blue Note",
                "description": "Experience an evening of smooth jazz",
                "location": "Blue Note Cafe, Downtown",
                "date": "2024-12-18T20:00:00Z",
                "price": 25.0,
                "category": "Music",
                "source": "Eventbrite",
                "url": "https://example.com/event/1",
                "image_url": "https://example.com/image.jpg"
            }
        }

class EventSearch(BaseModel):
    query: Optional[str] = Field(None, description="Search query")
    location: Optional[str] = Field(None, description="Location filter")
    category: Optional[str] = Field(None, description="Category filter")
    date_from: Optional[str] = Field(None, description="Start date filter")
    date_to: Optional[str] = Field(None, description="End date filter")
    max_price: Optional[float] = Field(None, description="Maximum price filter")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "jazz music",
                "location": "New York",
                "category": "Music",
                "date_from": "2024-12-01",
                "date_to": "2024-12-31",
                "max_price": 50.0
            }
        }

class EventResponse(BaseModel):
    events: List[Event] = Field(..., description="List of events")
    total: int = Field(..., description="Total number of events found")
    page: int = Field(1, description="Current page number")
    limit: int = Field(20, description="Number of events per page")
    
class APIError(BaseModel):
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")
    status_code: int = Field(..., description="HTTP status code")