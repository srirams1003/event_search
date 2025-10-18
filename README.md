# SF Tech Events Aggregator 🚀

A single-page web application that aggregates tech events in San Francisco from multiple platforms, providing a unified view of all tech events happening in the next two weeks.

## Overview

This application queries 5 popular event platforms to compile a comprehensive list of tech events in San Francisco:

1. **Meetup** - Community-driven tech meetups
2. **Eventbrite** - Professional events and conferences
3. **Luma** - Modern event platform for tech community
4. **Cerebral Valley** - SF-specific AI/tech events
5. **Ticketmaster** - Large-scale tech conferences and events

### Key Features

✨ **Multi-Source Aggregation**: Pulls events from 5 different platforms  
🤖 **AI-Powered Deduplication**: Uses NLP (Sentence Transformers) to detect and remove duplicate events  
🎯 **Location-Specific**: Focuses on San Francisco and surrounding areas (10-25 mile radius)  
📅 **Time-Bound**: Shows events for the next 2 weeks  
🔍 **Smart Search**: Filter events by title, description, venue, or source  
📱 **Responsive Design**: Beautiful, modern UI that works on all devices  
⚡ **Real-Time**: Fetches fresh data on every load  

## Tech Stack

### Backend
- **Python 3.8+**
- **Flask** - Web framework
- **Sentence Transformers** - NLP for duplicate detection
- **Requests** - HTTP library for API calls
- **BeautifulSoup4** - Web scraping (for platforms without APIs)

### Frontend
- **Vanilla HTML/CSS/JavaScript** - No frameworks, pure performance
- **Modern CSS Grid** - Responsive layout
- **Fetch API** - Async data loading

## Project Structure

```
event_search/
├── app.py                      # Main Flask application
├── templates/
│   └── index.html             # Frontend single-page app
├── requirements.txt           # Python dependencies
├── env.example               # Example environment variables
├── API_DOCUMENTATION.md      # Detailed API documentation
└── README.md                 # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- API keys from event platforms (see [Getting API Keys](#getting-api-keys))

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd event_search
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: First-time installation will download the Sentence Transformer model (~90MB). This is normal and only happens once.

### Step 4: Configure API Keys

1. Copy the example environment file:
```bash
cp env.example .env
```

2. Edit `.env` and add your API keys:
```bash
MEETUP_API_KEY=your_actual_meetup_key
EVENTBRITE_TOKEN=your_actual_eventbrite_token
LUMA_TOKEN=your_actual_luma_token
CEREBRALVALLEY_TOKEN=your_actual_cerebralvalley_token
TICKETMASTER_API_KEY=your_actual_ticketmaster_key
```

See [Getting API Keys](#getting-api-keys) section for detailed instructions.

### Step 5: Run the Application

```bash
python app.py
```

The application will start at `http://localhost:5000`

## Getting API Keys

### 1. Meetup API Key

**Difficulty**: ⚠️ Moderate (requires Meetup Pro)

1. Visit https://www.meetup.com/api/
2. Sign up for a Meetup account
3. Subscribe to **Meetup Pro** (paid service, ~$15-30/month)
4. Go to https://secure.meetup.com/meetup_api/oauth_consumers/
5. Create a new OAuth consumer
6. Generate OAuth 2.0 Bearer token
7. Copy token to `.env` as `MEETUP_API_KEY`

**Note**: Meetup deprecated their free API. OAuth 2.0 is now required.

### 2. Eventbrite OAuth Token

**Difficulty**: ✅ Easy (free)

1. Visit https://www.eventbrite.com/platform/
2. Sign up for an Eventbrite account
3. Go to **Account Settings** → **Developer Links**
4. Click **"Create New Token"**
5. Copy the OAuth token
6. Paste into `.env` as `EVENTBRITE_TOKEN`

**Note**: Free tier is sufficient for this use case.

### 3. Luma API Token

**Difficulty**: ⚠️ Difficult (limited public API)

1. Visit https://lu.ma/
2. Contact Luma support directly
3. Request API access for event aggregation
4. If granted, add token to `.env` as `LUMA_TOKEN`

**Alternative**: You may need to implement web scraping for Luma events.

### 4. Cerebral Valley

**Difficulty**: ❌ No Public API

Cerebral Valley does not provide a public API. Options:

1. **Web Scraping**: Implement scraping (requires BeautifulSoup/Selenium)
2. **Manual Curation**: Manually add their events
3. **Contact Them**: Reach out to request data access

Current implementation includes placeholder code for future integration.

### 5. Ticketmaster API Key

**Difficulty**: ✅ Very Easy (free)

1. Visit https://developer.ticketmaster.com/
2. Click **"Get Your API Key"**
3. Sign up for a free developer account
4. API key is provided immediately upon signup
5. Copy to `.env` as `TICKETMASTER_API_KEY`

**Limits**: 5,000 requests/day (more than sufficient)

## Usage

### Starting the Server

```bash
python app.py
```

Visit `http://localhost:5000` in your browser.

### Using the Web Interface

1. **Loading**: The page automatically fetches events on load
2. **Search**: Use the search box to filter by title, description, or venue
3. **Filter by Source**: Use dropdown to show events from specific platforms
4. **View Details**: Click "View Details" on any event to go to the source page

### API Endpoint

The backend exposes a REST API endpoint:

**GET** `/api/events`

**Response:**
```json
{
  "success": true,
  "total_events": 42,
  "events": [
    {
      "title": "SF Tech Networking Night",
      "description": "Join us for an evening of networking...",
      "url": "https://...",
      "date": "2025-10-25T18:00:00",
      "venue": "Tech Hub SF",
      "source": "Meetup"
    },
    ...
  ]
}
```

## How It Works

### 1. Event Fetching

The application queries each API in parallel:

```python
# Fetch from all sources
all_events = []
all_events.extend(fetch_meetup_events())
all_events.extend(fetch_eventbrite_events())
all_events.extend(fetch_luma_events())
all_events.extend(fetch_cerebralvalley_events())
all_events.extend(fetch_ticketmaster_events())
```

### 2. NLP-Based Deduplication

Events are compared using semantic similarity:

```python
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')

def is_duplicate(event1, event2, threshold=0.75):
    text1 = f"{event1['title']} {event1['description']}"
    text2 = f"{event2['title']} {event2['description']}"
    
    embedding1 = model.encode(text1, convert_to_tensor=True)
    embedding2 = model.encode(text2, convert_to_tensor=True)
    
    similarity = util.pytorch_cos_sim(embedding1, embedding2).item()
    
    return similarity > threshold
```

**How Deduplication Works**:
- Combines event title + description into single text
- Generates semantic embeddings using Sentence Transformers
- Calculates cosine similarity between embeddings
- If similarity > 75% (or 70% for same-date events), marks as duplicate
- Keeps only the first occurrence

### 3. Date Range Calculation

```python
from datetime import datetime, timedelta

start_date = datetime.now()
end_date = start_date + timedelta(days=14)
```

### 4. Location Filtering

All APIs are configured to search within San Francisco:
- Latitude: 37.7749
- Longitude: -122.4194
- Radius: 10-25 miles (varies by API)

## Configuration

### Adjusting the Date Range

Edit `app.py`:

```python
def get_date_range():
    start_date = datetime.now()
    end_date = start_date + timedelta(days=14)  # Change 14 to desired days
    return start_date, end_date
```

### Adjusting Deduplication Threshold

Edit `app.py`:

```python
def is_duplicate(event1, event2, threshold=0.75):  # Adjust 0.75
    # Higher = fewer duplicates detected (stricter)
    # Lower = more duplicates detected (looser)
```

Recommended ranges:
- **0.80-0.90**: Very strict (may miss some duplicates)
- **0.70-0.80**: Balanced (recommended)
- **0.60-0.70**: Loose (may remove some unique events)

### Changing Location

Edit API calls in `app.py`:

```python
# For Meetup (GraphQL)
variables = {
    "lat": 37.7749,  # Change to your latitude
    "lon": -122.4194,  # Change to your longitude
}

# For Eventbrite
params = {
    "location.address": "San Francisco, CA",  # Change city
}

# For Ticketmaster
params = {
    "city": "San Francisco",  # Change city
    "stateCode": "CA",  # Change state
}
```

## Troubleshooting

### No Events Showing Up

1. **Check API Keys**: Ensure all API keys are correctly set in `.env`
2. **Check Console**: Open browser console (F12) for error messages
3. **Check Server Logs**: Look at terminal output for API errors
4. **Test Individual APIs**: Run individual fetch functions to isolate issues

```bash
python -c "from app import fetch_ticketmaster_events; print(fetch_ticketmaster_events())"
```

### Model Download Fails

If Sentence Transformers fails to download:

```bash
# Manually download model
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### API Rate Limits

If you hit rate limits:

1. **Add Delays**: Implement delays between API calls
2. **Cache Results**: Add Redis caching
3. **Reduce Frequency**: Don't refresh too often

### Port Already in Use

If port 5000 is occupied:

```python
# Change port in app.py
if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Change to available port
```

## API Request Examples

See `API_DOCUMENTATION.md` for complete API documentation, including:

- Exact API endpoints for each platform
- Request/response formats
- Parameter details
- Authentication methods
- Rate limits

## Performance

### Typical Load Times

- **API Calls**: 2-5 seconds (parallel execution)
- **Deduplication**: 1-3 seconds (depends on event count)
- **Total**: 3-8 seconds for full refresh

### Optimization Tips

1. **Caching**: Implement Redis to cache results for 30-60 minutes
2. **Background Jobs**: Use Celery for async processing
3. **Pagination**: Limit events returned from each API
4. **Lazy Loading**: Load events on scroll (infinite scroll)

## Future Enhancements

- [ ] Add event calendar view
- [ ] Export events to Google Calendar / iCal
- [ ] User authentication and saved events
- [ ] Email notifications for new events
- [ ] Advanced filters (date range, keywords, organizers)
- [ ] Event recommendations based on user preferences
- [ ] Historical analytics and trends
- [ ] Mobile app (React Native)
- [ ] Implement Cerebral Valley web scraping
- [ ] Add more event sources (LinkedIn, Facebook, etc.)

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - feel free to use for personal or commercial projects.

## Disclaimer

This application aggregates publicly available event data. Please respect:
- API terms of service for each platform
- Rate limits
- Data usage policies
- robots.txt for web scraping

The developers are not responsible for misuse of this tool.

## Support

For issues, questions, or suggestions:
- Open a GitHub issue
- Check `API_DOCUMENTATION.md` for API-specific questions
- Review Troubleshooting section above

## Acknowledgments

- **Sentence Transformers**: For excellent NLP library
- **Flask**: For simple, powerful web framework
- Event platforms: Meetup, Eventbrite, Luma, Cerebral Valley, Ticketmaster

---

**Built with ❤️ for the SF tech community**
