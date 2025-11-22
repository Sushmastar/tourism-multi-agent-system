"""
Tourism AI Agent - Parent Agent
Orchestrates the child agents (Weather Agent and Places Agent).
"""
import re
from typing import Dict, Optional
from agents.weather_agent import WeatherAgent
from agents.places_agent import PlacesAgent
from utils.geocoding import get_coordinates


class TourismAgent:
    """Parent agent that orchestrates weather and places agents."""
    
    def __init__(self):
        self.weather_agent = WeatherAgent()
        self.places_agent = PlacesAgent()
    
    def extract_place_name(self, user_input: str) -> Optional[str]:
        """
        Extract place name from user input.
        
        Args:
            user_input: User's input text
            
        Returns:
            Extracted place name or None
        """
        # Strip and clean input
        user_input = user_input.strip()
        
        # If input is very short (1-3 words) and contains a capitalized word, it might be just a place name
        words = user_input.split()
        if len(words) <= 3:
            # Check if it's a simple place name query
            capitalized = [w.rstrip(',.?!') for w in words if w and w[0].isupper() and len(w.rstrip(',.!?')) > 2]
            if capitalized:
                common_words = {'I', 'I\'m', 'Let', 'Let\'s', 'What', 'The', 'And', 'Are', 'Can', 'Go', 'To', 'In'}
                place_words = [w for w in capitalized if w not in common_words]
                if place_words:
                    return ' '.join(place_words)
        
        # Common patterns for place mentions
        patterns = [
            r"going to (?:go to )?([A-Z][a-zA-Z\s]+?)(?:,|\.|$|\s+what|\s+let)",
            r"visit ([A-Z][a-zA-Z\s]+?)(?:,|\.|$|\s+what|\s+let)",
            r"trip to ([A-Z][a-zA-Z\s]+?)(?:,|\.|$|\s+what|\s+let)",
            r"in ([A-Z][a-zA-Z\s]+?)(?:,|\.|$|\s+what|\s+let)",
            r"to ([A-Z][a-zA-Z\s]+?)(?:,|\.|$|\s+what|\s+let)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                place = match.group(1).strip()
                # Clean up common words
                place = re.sub(r'\b(?:the|a|an)\b', '', place, flags=re.IGNORECASE).strip()
                if place:
                    return place
        
        # Fallback: try to find capitalized words (city names are usually capitalized)
        capitalized = [w.rstrip(',.?!') for w in words if w and w[0].isupper() and len(w.rstrip(',.!?')) > 2]
        if capitalized:
            # Filter out common capitalized words that aren't place names
            common_words = {'I', 'I\'m', 'Let', 'Let\'s', 'What', 'The', 'And', 'Are', 'Can', 'Go', 'To', 'In'}
            place_words = [w for w in capitalized if w not in common_words]
            if place_words:
                return ' '.join(place_words[:2])  # Take first 1-2 capitalized words
        
        return None
    
    def determine_intent(self, user_input: str) -> Dict[str, bool]:
        """
        Determine what the user wants: weather, places, or both.
        
        Args:
            user_input: User's input text
            
        Returns:
            Dictionary with 'weather' and 'places' boolean flags
        """
        user_lower = user_input.lower()
        
        # Check for weather-related keywords
        wants_weather = any(keyword in user_lower for keyword in [
            'temperature', 'weather', 'rain', 'temperature there', 'weather there',
            'temp', 'how hot', 'how cold', 'degrees'
        ])
        
        # Check for places-related keywords
        wants_places = any(keyword in user_lower for keyword in [
            'places', 'attractions', 'visit', 'tourist', 'plan my trip', 'can go',
            'sightseeing', 'sights', 'what to see', 'where to go', 'landmarks'
        ])
        
        # If query explicitly asks for both (using "and" or "also")
        if 'and' in user_lower or 'also' in user_lower:
            # If one is mentioned, assume both are wanted
            if wants_weather or wants_places:
                wants_weather = True
                wants_places = True
        
        # If neither is explicitly mentioned, default to places
        if not wants_weather and not wants_places:
            wants_places = True
        
        return {
            'weather': wants_weather,
            'places': wants_places
        }
    
    def process_request(self, user_input: str) -> str:
        """
        Process user request and coordinate child agents.
        
        Args:
            user_input: User's input text
            
        Returns:
            Formatted response string
        """
        # Extract place name
        place_name = self.extract_place_name(user_input)
        if not place_name:
            return "I couldn't identify the place you want to visit. Please specify a place name."
        
        # Verify place exists by trying to get coordinates
        coords = get_coordinates(place_name)
        if not coords:
            return f"I don't know this place exists. Could you please check the spelling or provide more details about the location?"
        
        # Determine user intent
        intent = self.determine_intent(user_input)
        
        responses = []
        
        # Get weather information if requested
        if intent['weather']:
            weather_data = self.weather_agent.get_weather(coords[0], coords[1])
            if weather_data:
                weather_response = self.weather_agent.format_weather_response(place_name, weather_data)
                responses.append(weather_response)
        
        # Get places information if requested
        if intent['places']:
            places = self.places_agent.get_tourist_places(place_name)
            if places:
                places_response = self.places_agent.format_places_response(place_name, places)
                responses.append(places_response)
        
        # Combine responses
        if responses:
            # Format based on whether both are present
            if len(responses) == 2:
                # Extract just the places list from the places response
                weather_part = responses[0].rstrip('.')  # Remove trailing period
                places_part = responses[1]
                # Remove the "In {place_name} these are the places you can go," part
                places_list = places_part.split('\n', 1)[1] if '\n' in places_part else places_part
                return f"{weather_part}. And these are the places you can go:\n{places_list}"
            else:
                return responses[0]
        else:
            return f"Sorry, I couldn't fetch information for {place_name}."

