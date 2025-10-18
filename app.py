from flask import Flask, render_template, jsonify
from flask_cors import CORS
import requests
from datetime import datetime, timedelta
from sentence_transformers import SentenceTransformer, util
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin
import re

load_dotenv()

app = Flask(__name__)
CORS(app)

# Load the NLP model for deduplication
model = SentenceTransformer('all-MiniLM-L6-v2')

# API Keys from environment variables
MEETUP_API_KEY = os.getenv('MEETUP_API_KEY', '')
EVENTBRITE_TOKEN = os.getenv('EVENTBRITE_TOKEN', '')

# Common headers for scraping
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}


def extract_event_from_jsonld(soup, base_url):
    """Extract a single event from JSON-LD if present."""
    try:
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            raw = script.string or script.get_text() or ""
            if not raw.strip():
                continue
            try:
                data = json.loads(raw)
            except Exception:
                continue
            items = data if isinstance(data, list) else [data]
            for item in items:
                types = item.get('@type')
                if isinstance(types, str):
                    types = [types]
                if types and 'Event' in types:
                    name = item.get('name') or 'Untitled Event'
                    url = item.get('url') or base_url
                    start = item.get('startDate') or ''
                    loc = item.get('location') or {}
                    venue = ''
                    if isinstance(loc, dict):
                        venue = loc.get('name') or venue
                    return {
                        'title': name,
                        'description': (item.get('description') or '').strip(),
                        'url': url,
                        'date': start,
                        'venue': venue or 'San Francisco, CA',
                    }
    except Exception:
        pass
    return None

def get_date_range():
    """Get current date and date 2 weeks from now"""
    start_date = datetime.now()
    end_date = start_date + timedelta(days=14)
    return start_date, end_date


def fetch_meetup_events():
    """
    Fetch events from Meetup via web scraping (no API).
    Uses a search page scoped to SF and tech keywords.
    """
    try:
        start_date, end_date = get_date_range()

        # Meetup search for SF with tech-related keywords
        url = (
            "https://www.meetup.com/find/?source=EVENTS&distance=ten&location=us--ca--San%20Francisco"
            "&keywords=ai%2C%20machine%20learning%2C%20software%2C%20developer%2C%20startup%2C%20engineering"
        )
        headers = DEFAULT_HEADERS

        allow_keywords = [
            'ai','artificial intelligence','machine learning','ml','data','database','big data','llm',
            'developer','dev','engineering','engineer','software','coding','programming','hack','hackathon',
            'startup','founder','product','web3','blockchain','crypto','cloud','kubernetes','docker','devops',
            'python','javascript','typescript','react','node','go','rust','java','swift','ios','android',
            'meetup','tech','technology'
        ]
        deny_keywords = [
            'pickleball','padel','tennis','basketball','baseball','football','soccer','bike','cycling',
            'backgammon','party','festival','music','concert','yoga','comedy','dance','theater','theatre'
        ]

        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            print(f"Meetup scraping error: {resp.status_code}")
            return []

        soup = BeautifulSoup(resp.content, 'html.parser')
        events = []

        for a in soup.find_all('a', href=True):
            href = a['href']
            # Normalize relative Meetup links
            full_url = href
            if href.startswith('/'):
                full_url = f"https://www.meetup.com{href}"
            if '/events/' in full_url and 'meetup.com' in full_url:
                title = a.get_text(strip=True) or 'Untitled Event'
                text = f"{title} {full_url}".lower()
                if any(k in text for k in deny_keywords):
                    continue
                if not any(k in text for k in allow_keywords):
                    continue
                events.append({
                    'title': title,
                    'description': 'Tech event in San Francisco',
                    'url': full_url,
                    'date': '',
                    'venue': 'San Francisco, CA',
                    'source': 'Meetup'
                })

        # De-dup within this source by URL
        seen = set()
        unique = []
        for e in events:
            if e['url'] in seen:
                continue
            seen.add(e['url'])
            unique.append(e)

        print(f"Meetup: Found {len(unique)} events via web scraping")
        return unique[:30]
    except Exception as e:
        print(f"Error fetching Meetup events: {e}")
        return []


def fetch_eventbrite_events():
    """
    Fetch events from Eventbrite via web scraping (no API).
    Uses SF + Science & Tech category listing.
    """
    try:
        # Eventbrite SF Science & Tech search
        url = "https://www.eventbrite.com/d/ca--san-francisco/science-and-tech--events/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
        }

        allow_keywords = [
            'ai','artificial intelligence','machine learning','ml','data','database','big data','llm',
            'developer','dev','engineering','engineer','software','coding','programming','hack','hackathon',
            'startup','founder','product','web3','blockchain','crypto','cloud','kubernetes','docker','devops',
            'python','javascript','typescript','react','node','go','rust','java','swift','ios','android',
            'meetup','tech','technology'
        ]
        deny_keywords = [
            'pickleball','padel','tennis','basketball','baseball','football','soccer','bike','cycling',
            'backgammon','party','festival','music','concert','yoga','comedy','dance','theater','theatre'
        ]

        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            print(f"Eventbrite scraping error: {resp.status_code}")
            return []

        soup = BeautifulSoup(resp.content, 'html.parser')
        events = []

        # Collect candidate event links and fetch detail pages to parse JSON-LD
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '/e/' in href:
                links.append(urljoin('https://www.eventbrite.com', href))
        if not links:
            # Fallback: regex URLs from raw HTML (handles client-rendered listings)
            html = resp.text
            for m in re.findall(r"https?://www\.eventbrite\.com/e/[^\"'\s<>]+", html):
                links.append(m)
        links = list(dict.fromkeys(links))
        print(f"Eventbrite: candidate links {len(links)}")
        seen_links = []
        for link in links:
            if link in seen_links:
                continue
            seen_links.append(link)
            try:
                dresp = requests.get(link, headers=DEFAULT_HEADERS, timeout=10)
                if dresp.status_code != 200:
                    continue
                dsoup = BeautifulSoup(dresp.content, 'html.parser')
                parsed = extract_event_from_jsonld(dsoup, link)
                if parsed:
                    parsed['source'] = 'Eventbrite'
                    # Light deny-only filter to avoid obvious noise
                    text = (parsed['title'] + ' ' + parsed.get('description','')).lower()
                    if any(k in text for k in deny_keywords):
                        continue
                    events.append(parsed)
                else:
                    title = (dsoup.find('h1') or dsoup.title or {}).get_text(strip=True) if dsoup.find('h1') or dsoup.title else 'Untitled Event'
                    events.append({
                        'title': title,
                        'description': 'Tech event in San Francisco',
                        'url': link,
                        'date': '',
                        'venue': 'San Francisco, CA',
                        'source': 'Eventbrite'
                    })
                time.sleep(0.3)
            except Exception:
                continue

        # De-dup within this source by URL
        seen = set()
        unique = []
        for e in events:
            if e['url'] in seen:
                continue
            seen.add(e['url'])
            unique.append(e)

        print(f"Eventbrite: Found {len(unique)} events via web scraping")
        return unique[:30]
    except Exception as e:
        print(f"Error fetching Eventbrite events: {e}")
        return []


def fetch_luma_events():
    """
    Fetch events from Luma via web scraping
    URL: https://lu.ma/sf
    Note: No public API available, using web scraping
    """
    try:
        
        start_date, end_date = get_date_range()
        
        # Luma San Francisco events page
        url = "https://lu.ma/sf"
        headers = DEFAULT_HEADERS
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            events = []

            # Simple tech-only filtering using allowlist/denylist keywords
            allow_keywords = [
                'ai','artificial intelligence','machine learning','ml','data','database','big data','llm',
                'developer','dev','engineering','engineer','software','coding','programming','hack','hackathon',
                'startup','founder','product','web3','blockchain','crypto','cloud','kubernetes','docker','devops',
                'python','javascript','typescript','react','node','go','rust','java','swift','ios','android',
                'meetup','tech','technology'
            ]
            deny_keywords = [
                'pickleball','padel','tennis','basketball','baseball','football','soccer','bike','cycling',
                'backgammon','party','festival','music','concert','yoga','comedy','dance','theater','theatre'
            ]
            
            # Collect candidate event links from the city page
            links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                if '/event/' in href or '/e/' in href:
                    links.append(urljoin('https://lu.ma', href))
            if not links:
                html = response.text
                for m in re.findall(r"https?://lu\.ma/(?:event|e)/[^\"'\s<>]+", html):
                    links.append(m)
            links = list(dict.fromkeys(links))
            print(f"Luma: candidate links {len(links)}")

            # Visit detail pages and parse JSON-LD
            for link in links[:25]:
                try:
                    dresp = requests.get(link, headers=DEFAULT_HEADERS, timeout=10)
                    if dresp.status_code != 200:
                        continue
                    dsoup = BeautifulSoup(dresp.content, 'html.parser')
                    parsed = extract_event_from_jsonld(dsoup, link)
                    if parsed:
                        text_for_filter = (parsed['title'] + ' ' + parsed.get('description','')).lower()
                        if any(k in text_for_filter for k in deny_keywords):
                            continue
                        parsed['source'] = 'Luma'
                        events.append(parsed)
                    else:
                        title = (dsoup.find('h1') or dsoup.title or {}).get_text(strip=True) if dsoup.find('h1') or dsoup.title else 'Untitled Event'
                        if any(k in title.lower() for k in deny_keywords):
                            continue
                        events.append({
                            'title': title,
                            'description': 'Tech event in San Francisco',
                            'url': link,
                            'date': '',
                            'venue': 'San Francisco, CA',
                            'source': 'Luma'
                        })
                    time.sleep(0.3)
                except Exception:
                    continue
            
            print(f"Luma: Found {len(events)} events via web scraping")
            return events
        else:
            print(f"Luma scraping error: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching Luma events: {e}")
        return []


def fetch_cerebralvalley_events():
    """
    Fetch events from Cerebral Valley via web scraping
    URL: https://cerebralvalley.ai/events
    Note: No public API available, using web scraping
    """
    try:
        from bs4 import BeautifulSoup
        
        start_date, end_date = get_date_range()
        
        # Cerebral Valley events page
        url = "https://cerebralvalley.ai/events"
        headers = DEFAULT_HEADERS
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            events = []
            
            # Collect candidate links from the events page
            links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                if '/events/' in href:
                    links.append(urljoin('https://cerebralvalley.ai', href))
            if not links:
                html = response.text
                for m in re.findall(r"https?://cerebralvalley\.ai/events/[^\"'\s<>]+", html):
                    links.append(m)
            links = list(dict.fromkeys(links))
            print(f"Cerebral Valley: candidate links {len(links)}")

            # Visit detail pages and parse JSON-LD
            for link in links[:25]:
                try:
                    dresp = requests.get(link, headers=DEFAULT_HEADERS, timeout=10)
                    if dresp.status_code != 200:
                        continue
                    dsoup = BeautifulSoup(dresp.content, 'html.parser')
                    parsed = extract_event_from_jsonld(dsoup, link)
                    if parsed:
                        parsed['source'] = 'CerebralValley'
                        events.append(parsed)
                    else:
                        title = (dsoup.find('h1') or dsoup.title or {}).get_text(strip=True) if dsoup.find('h1') or dsoup.title else 'Untitled Event'
                        events.append({
                            'title': title,
                            'description': 'AI/Tech event in San Francisco',
                            'url': link,
                            'date': '',
                            'venue': 'San Francisco, CA',
                            'source': 'CerebralValley'
                        })
                    time.sleep(0.3)
                except Exception:
                    continue

            print(f"Cerebral Valley: Found {len(events)} events via web scraping")
            return events
        else:
            print(f"Cerebral Valley scraping error: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching Cerebral Valley events: {e}")
        return []



def is_duplicate(event1, event2, threshold=0.75):
    """
    Check if two events are duplicates using NLP similarity
    
    Args:
        event1: First event dictionary
        event2: Second event dictionary
        threshold: Similarity threshold (0-1), default 0.75
    
    Returns:
        bool: True if events are duplicates
    """
    try:
        # Combine title and description for better comparison
        text1 = f"{event1['title']} {event1.get('description', '')}"
        text2 = f"{event2['title']} {event2.get('description', '')}"
        
        # Generate embeddings
        embedding1 = model.encode(text1, convert_to_tensor=True)
        embedding2 = model.encode(text2, convert_to_tensor=True)
        
        # Calculate cosine similarity
        similarity = util.pytorch_cos_sim(embedding1, embedding2).item()
        
        # Also check date similarity (same day makes duplicates more likely)
        date1 = event1.get('date', '')
        date2 = event2.get('date', '')
        same_date = date1[:10] == date2[:10] if date1 and date2 else False
        
        # If same date, lower the threshold slightly
        effective_threshold = threshold - 0.05 if same_date else threshold
        
        return similarity > effective_threshold
    except Exception as e:
        print(f"Error in duplicate detection: {e}")
        return False


def deduplicate_events(events):
    """
    Remove duplicate events from the list using NLP
    
    Args:
        events: List of event dictionaries
    
    Returns:
        List of unique events
    """
    unique_events = []
    
    for event in events:
        is_dup = False
        for unique_event in unique_events:
            if is_duplicate(event, unique_event):
                is_dup = True
                break
        
        if not is_dup:
            unique_events.append(event)
    
    return unique_events


@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')


@app.route('/api/events')
def get_events():
    """API endpoint to get all aggregated and deduplicated events"""
    try:
        print("Fetching events from all sources...")
        
        # Fetch events from all sources
        all_events = []
        
        print("Fetching from Meetup...")
        all_events.extend(fetch_meetup_events())
        
        print("Fetching from Eventbrite...")
        all_events.extend(fetch_eventbrite_events())
        
        print("Fetching from Luma...")
        all_events.extend(fetch_luma_events())
        
        print("Fetching from Cerebral Valley...")
        all_events.extend(fetch_cerebralvalley_events())

        
        print(f"Total events fetched: {len(all_events)}")
        
        # Deduplicate events
        print("Deduplicating events...")
        unique_events = deduplicate_events(all_events)
        print(f"Unique events after deduplication: {len(unique_events)}")
        
        # Sort by date
        unique_events.sort(key=lambda x: x.get('date', ''))
        
        return jsonify({
            'success': True,
            'total_events': len(unique_events),
            'events': unique_events
        })
    except Exception as e:
        print(f"Error in get_events: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'events': []
        }), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)

