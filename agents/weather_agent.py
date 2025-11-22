"""
Weather Agent - Child Agent 1
Fetches current weather and forecast using Open-Meteo API.
"""
import requests
from typing import Optional, Dict, Tuple


class WeatherAgent:
    """Agent responsible for fetching weather information."""
    
    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1/forecast"
    
    def get_weather(self, latitude: float, longitude: float) -> Optional[Dict]:
        """
        Get current weather and forecast for given coordinates.
        
        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location
            
        Returns:
            Dictionary with weather information or None if error
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,precipitation_probability",
            "forecast_days": 1
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if "current" in data:
                return {
                    "temperature": data["current"].get("temperature_2m"),
                    "precipitation_probability": data["current"].get("precipitation_probability"),
                    "unit": data["current_units"].get("temperature_2m", "°C")
                }
            return None
        except Exception as e:
            print(f"Weather API error: {e}")
            return None
    
    def format_weather_response(self, place_name: str, weather_data: Dict) -> str:
        """
        Format weather data into a user-friendly response.
        
        Args:
            place_name: Name of the place
            weather_data: Weather data dictionary
            
        Returns:
            Formatted string response
        """
        if not weather_data:
            return f"Sorry, I couldn't fetch weather information for {place_name}."
        
        temp = weather_data.get("temperature")
        rain_chance = weather_data.get("precipitation_probability", 0)
        unit = weather_data.get("unit", "°C")
        
        return f"In {place_name} it's currently {temp}{unit} with a chance of {rain_chance}% to rain."

