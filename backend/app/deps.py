# Dependencies for the Event Search API
from fastapi import Depends, HTTPException, status
import httpx
import os
from typing import Dict, Any

async def get_http_client():
    """Get HTTP client for external API calls"""
    async with httpx.AsyncClient() as client:
        yield client

def get_current_user():
    # Placeholder for user authentication
    # In a real application, this would validate JWT tokens or session data
    return {"user_id": 1, "username": "demo_user"}

def validate_search_params(query: str = None, location: str = None, category: str = None):
    # Validate search parameters
    if not any([query, location, category]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one search parameter is required"
        )
    return {"query": query, "location": location, "category": category}

async def fetch_external_events(
    client: httpx.AsyncClient,
    query: str = None,
    location: str = None,
    category: str = None
) -> Dict[str, Any]:
    """Fetch events from external APIs"""
    # This would integrate with external event APIs like Eventbrite, Ticketmaster, etc.
    # For now, return mock data
    return {
        "events": [
            {
                "id": 1,
                "title": "Jazz Night at Blue Note",
                "description": "Experience an evening of smooth jazz with talented local musicians.",
                "location": "Blue Note Cafe, Downtown",
                "date": "2024-12-18T20:00:00Z",
                "price": 25,
                "category": "Music"
            },
            {
                "id": 2,
                "title": "Startup Pitch Competition",
                "description": "Watch innovative startups pitch their ideas to a panel of investors.",
                "location": "Innovation Hub",
                "date": "2024-12-19T14:00:00Z",
                "price": 0,
                "category": "Business"
            }
        ]
    }