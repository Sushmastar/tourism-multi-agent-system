# Multi-Agent Tourism System

A multi-agent system that helps users plan their trips by providing weather information and tourist attraction suggestions for any place.

## Architecture

The system consists of:
- **Parent Agent**: Tourism AI Agent (orchestrates the system)
- **Child Agent 1**: Weather Agent (fetches current weather using Open-Meteo API)
- **Child Agent 2**: Places Agent (suggests tourist attractions using Overpass API)

## Features

- Extract place names from natural language input
- Get current weather and precipitation probability
- Find up to 5 tourist attractions near the specified location
- Handle errors gracefully for non-existent places
- Support queries for weather only, places only, or both
- **Works worldwide**: Identifies locations from India and any country globally
- **Smart geocoding**: Prioritizes India for ambiguous queries, but correctly handles any location worldwide

## APIs Used

1. **Nominatim API** (Geocoding): Converts place names to coordinates
   - Base URL: https://nominatim.openstreetmap.org/search
   
2. **Open-Meteo API** (Weather): Fetches current weather data
   - Base URL: https://api.open-meteo.com/v1/forecast
   
3. **Overpass API** (Places): Finds tourist attractions from OpenStreetMap
   - Base URL: https://overpass-api.de/api/interpreter

## Installation

1. Install Python 3.7 or higher
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Web Interface (Recommended)

Run the Flask web application:
```bash
python app.py
```

Then open your browser and navigate to:
```
http://localhost:5000
```

You'll see a beautiful web interface where you can:
- Enter queries in natural language
- See responses in a chat-like interface
- Get weather and places information for any location

### Command Line Interface

Alternatively, run the main script:
```bash
python main.py
```

Then enter your queries in natural language. Examples:
- "I'm going to go to Bangalore, let's plan my trip."
- "I'm going to go to Bangalore, what is the temperature there"
- "I'm going to go to Bangalore, what is the temperature there? And what are the places I can visit?"
- "New York" (simple place name)
- "What's the weather in London?"
- "Paris" (works for any location worldwide)

## Example Outputs

**Example 1: Places only**
```
Input: I'm going to go to Bangalore, let's plan my trip.
Output:
In Bangalore these are the places you can go,
Lalbagh
Sri Chamarajendra Park
Bangalore palace
Bannerghatta National Park
Jawaharlal Nehru Planetarium
```

**Example 2: Weather only**
```
Input: I'm going to go to Bangalore, what is the temperature there
Output:
In Bangalore it's currently 24°C with a chance of 35% to rain.
```

**Example 3: Both weather and places**
```
Input: I'm going to go to Bangalore, what is the temperature there? And what are the places I can visit?
Output:
In Bangalore it's currently 24°C with a chance of 35% to rain. And in bangalore these are the places you can go:
Lalbagh
Sri Chamarajendra Park
Bangalore palace
Bannerghatta National Park
Jawaharlal Nehru Planetarium
```

## Project Structure

```
multi-agenttourism/
├── agents/
│   ├── __init__.py
│   ├── tourism_agent.py    # Parent agent
│   ├── weather_agent.py     # Child agent 1
│   └── places_agent.py      # Child agent 2
├── utils/
│   ├── __init__.py
│   └── geocoding.py         # Geocoding utility
├── templates/
│   └── index.html           # Web frontend HTML
├── static/
│   ├── style.css            # Web frontend styles
│   └── script.js            # Web frontend JavaScript
├── app.py                   # Flask web application
├── main.py                  # CLI entry point
├── test_examples.py         # Test script for examples
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## Error Handling

- If a place doesn't exist or can't be found, the system responds: "I don't know this place exists. Could you please check the spelling or provide more details about the location?"
- API errors are handled gracefully with appropriate error messages

## Worldwide Location Support

The system can identify and provide information for:
- **All locations in India**: Major cities (Mumbai, Delhi, Bangalore, etc.), smaller cities, towns, and tourist destinations
- **Locations worldwide**: Major cities from any country (New York, London, Paris, Tokyo, Sydney, Dubai, etc.)
- **Any location in OpenStreetMap**: The system uses Nominatim geocoding which includes millions of locations globally

**Smart Prioritization**: 
- For ambiguous place names (e.g., "Hyderabad" exists in both India and Pakistan), the system prioritizes India
- For specific queries (e.g., "New York", "London"), it correctly identifies the location regardless of country
- The system filters tourist attractions to ensure they're from the same country as the queried location

## Notes

- The system uses open-source APIs that don't require API keys
- All APIs are rate-limited, so please use responsibly
- The Overpass API may take a few seconds to respond for some queries

