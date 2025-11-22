"""
Geocoding utility using Nominatim API to get coordinates for places.
"""
import requests
from typing import Optional, Tuple, Dict


def get_coordinates(place_name: str) -> Optional[Tuple[float, float]]:
    """
    Get latitude and longitude for a place using Nominatim API.
    Works for any location worldwide. Prioritizes India for ambiguous queries.
    
    Args:
        place_name: Name of the place to geocode
        
    Returns:
        Tuple of (latitude, longitude) if found, None otherwise
    """
    base_url = "https://nominatim.openstreetmap.org/search"
    
    headers = {
        "User-Agent": "Tourism-Agent-System/1.0"
    }
    
    try:
        # Get multiple results to find the best match
        params = {
            "q": place_name,
            "format": "json",
            "limit": 10,  # Get more results to filter
            "addressdetails": 1
        }
        
        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data or len(data) == 0:
            return None
        
        # Check if place name contains country-specific indicators
        place_lower = place_name.lower()
        has_country_hint = any(country in place_lower for country in [
            "india", "usa", "united states", "uk", "united kingdom", "france", 
            "germany", "japan", "china", "australia", "canada", "spain", "italy"
        ])
        
        # If no country hint, prioritize India (for common Indian city names)
        # Otherwise, use the first (most relevant) result
        if not has_country_hint:
            # Look for India results first
            for result in data:
                address = result.get("address", {})
                country = address.get("country", "").lower()
                
                if "india" in country:
                    lat = float(result["lat"])
                    lon = float(result["lon"])
                    return (lat, lon)
        
        # Return first result (highest relevance from Nominatim)
        lat = float(data[0]["lat"])
        lon = float(data[0]["lon"])
        return (lat, lon)
            
    except Exception as e:
        print(f"Error in geocoding: {e}")
        return None


def get_coordinates_with_country(place_name: str) -> Optional[Tuple[float, float, str]]:
    """
    Get coordinates and country information for a place.
    Works for any location worldwide. Prioritizes India for ambiguous queries.
    
    Args:
        place_name: Name of the place to geocode
        
    Returns:
        Tuple of (latitude, longitude, country) if found, None otherwise
    """
    base_url = "https://nominatim.openstreetmap.org/search"
    
    headers = {
        "User-Agent": "Tourism-Agent-System/1.0"
    }
    
    try:
        params = {
            "q": place_name,
            "format": "json",
            "limit": 10,
            "addressdetails": 1
        }
        
        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data or len(data) == 0:
            return None
        
        # Check if place name contains country-specific indicators
        place_lower = place_name.lower()
        has_country_hint = any(country in place_lower for country in [
            "india", "usa", "united states", "uk", "united kingdom", "france", 
            "germany", "japan", "china", "australia", "canada", "spain", "italy",
            "uae", "united arab emirates", "dubai", "abu dhabi"
        ])
        
        # Well-known international cities that should not default to India
        international_cities = [
            "dubai", "london", "paris", "new york", "tokyo", "sydney", "singapore",
            "bangkok", "hong kong", "istanbul", "rome", "barcelona", "amsterdam",
            "berlin", "moscow", "cairo", "riyadh", "doha", "kuwait", "manama"
        ]
        
        is_international_city = any(city in place_lower for city in international_cities)
        
        # If it's a well-known international city, use first result (most relevant)
        # Otherwise, if no country hint, prioritize India (for common Indian city names)
        if is_international_city or has_country_hint:
            # Use first result (highest relevance from Nominatim)
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            country = data[0].get("address", {}).get("country", "Unknown")
            return (lat, lon, country)
        else:
            # For ambiguous queries, look for India results first
            for result in data:
                address = result.get("address", {})
                country = address.get("country", "")
                
                if "India" in country or "india" in country.lower():
                    lat = float(result["lat"])
                    lon = float(result["lon"])
                    return (lat, lon, country)
            
            # If no India result, return first result
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            country = data[0].get("address", {}).get("country", "Unknown")
            return (lat, lon, country)
        
    except Exception as e:
        print(f"Error in geocoding: {e}")
        return None

