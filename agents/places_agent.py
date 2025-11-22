"""
Places Agent - Child Agent 2
Fetches tourist attractions using Overpass API.
"""
import requests
from typing import Optional, List
from utils.geocoding import get_coordinates, get_coordinates_with_country


class PlacesAgent:
    """Agent responsible for fetching tourist attractions."""
    
    def __init__(self):
        self.base_url = "https://overpass-api.de/api/interpreter"
        self.target_country = None
    
    def _countries_match(self, country1: str, country2: str) -> bool:
        """Check if two country names refer to the same country."""
        # Normalize country names
        country1 = country1.lower().strip()
        country2 = country2.lower().strip()
        
        if country1 == country2:
            return True
        
        # Common country name variations
        country_variations = {
            "united states": ["usa", "united states of america", "us", "united states"],
            "united kingdom": ["uk", "great britain", "britain", "england", "united kingdom"],
            "russian federation": ["russia"],
            "south korea": ["korea", "republic of korea"],
            "north korea": ["korea", "democratic people's republic of korea"],
            "united arab emirates": ["uae", "emirates", "united arab emirates"],
        }
        
        # Check if either country matches a variation
        for standard, variations in country_variations.items():
            if country1 == standard and country2 in variations:
                return True
            if country2 == standard and country1 in variations:
                return True
            if country1 in variations and country2 in variations:
                return True
            # Also check if either contains the other
            if standard in country1 and any(v in country2 for v in variations):
                return True
            if standard in country2 and any(v in country1 for v in variations):
                return True
        
        return False
    
    def get_tourist_places(self, place_name: str, limit: int = 5) -> Optional[List[str]]:
        """
        Get tourist attractions for a given place.
        
        Args:
            place_name: Name of the place
            limit: Maximum number of places to return (default: 5)
            
        Returns:
            List of tourist place names or None if error
        """
        # First, get coordinates and country for the place
        coords_info = get_coordinates_with_country(place_name)
        if not coords_info:
            return None
        
        lat, lon, country = coords_info
        
        # Store country for filtering results later
        self.target_country = country.lower()
        
        places = []
        seen_names = set()
        
        # Try multiple search strategies to find well-known attractions
        # Strategy 1: Search for parks and gardens first (most common tourist spots)
        parks = self._search_parks_gardens(lat, lon, limit * 2, seen_names)
        places.extend(parks)
        
        # Strategy 2: Search for museums, zoos, and major attractions
        attractions = self._search_tourism_attractions(lat, lon, limit * 2, seen_names)
        places.extend(attractions)
        
        # Strategy 3: Search for historic sites and monuments
        historic = self._search_historic_sites(lat, lon, limit * 2, seen_names)
        places.extend(historic)
        
        # Strategy 4: Broader search for any leisure or amenity
        additional = self._get_additional_places(lat, lon, limit * 2, seen_names)
        places.extend(additional)
        
        # Remove duplicates and sort by priority, then return top results
        unique_places = []
        seen = set()
        for place in places:
            if place not in seen:
                unique_places.append(place)
                seen.add(place)
        
        # Sort by length and keywords (prioritize well-known places)
        def place_priority(name):
            priority = 0
            name_lower = name.lower()
            # Filter out hotels and non-tourist places
            exclude_keywords = ["hotel", "restaurant", "mall", "shopping", "resort", "inn", "lodge", "apartment"]
            if any(keyword in name_lower for keyword in exclude_keywords):
                return -100  # Heavily penalize these
            
            # Prioritize places with common tourist attraction keywords
            high_priority_keywords = ["national park", "palace", "planetarium"]
            medium_priority_keywords = ["museum", "zoo", "garden", "park"]
            
            for keyword in high_priority_keywords:
                if keyword in name_lower:
                    priority += 20
            for keyword in medium_priority_keywords:
                if keyword in name_lower:
                    priority += 10
            
            # Longer names often indicate specific places
            if len(name.split()) > 1:
                priority += 5
            return priority
        
        unique_places.sort(key=place_priority, reverse=True)
        
        return unique_places[:limit] if unique_places else None
    
    def _search_parks_gardens(self, lat: float, lon: float, limit: int, seen_names: set) -> List[str]:
        """Search for parks and gardens - most common tourist attractions."""
        # Reduced radius to 25km to avoid picking up places from neighboring countries
        query = f"""[out:json][timeout:30];
(
  node["leisure"~"^(park|garden)$"](around:25000,{lat},{lon});
  way["leisure"~"^(park|garden)$"](around:25000,{lat},{lon});
  relation["leisure"~"^(park|garden)$"](around:25000,{lat},{lon});
);
out body;
>;
out skel qt;"""
        
        return self._execute_query(query, limit, seen_names)
    
    def _search_tourism_attractions(self, lat: float, lon: float, limit: int, seen_names: set) -> List[str]:
        """Search for tourism attractions like museums, zoos, etc."""
        # Reduced radius to 25km to avoid picking up places from neighboring countries
        query = f"""[out:json][timeout:30];
(
  node["tourism"](around:25000,{lat},{lon});
  way["tourism"](around:25000,{lat},{lon});
  relation["tourism"](around:25000,{lat},{lon});
);
out body;
>;
out skel qt;"""
        
        return self._execute_query(query, limit, seen_names)
    
    def _search_historic_sites(self, lat: float, lon: float, limit: int, seen_names: set) -> List[str]:
        """Search for historic sites and monuments."""
        # Reduced radius to 25km to avoid picking up places from neighboring countries
        query = f"""[out:json][timeout:30];
(
  node["historic"](around:25000,{lat},{lon});
  way["historic"](around:25000,{lat},{lon});
  relation["historic"](around:25000,{lat},{lon});
);
out body;
>;
out skel qt;"""
        
        return self._execute_query(query, limit, seen_names)
    
    def _execute_query(self, query: str, limit: int, seen_names: set) -> List[str]:
        """Execute an Overpass query and extract place names."""
        places = []
        try:
            response = requests.post(
                self.base_url,
                data={"data": query},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            if "elements" in data:
                # Sort elements by importance (prefer places with more tags/info)
                elements = sorted(data["elements"], key=lambda x: len(x.get("tags", {})), reverse=True)
                
                for element in elements:
                    if "tags" in element and "name" in element["tags"]:
                        name = element["tags"]["name"]
                        if name and name not in seen_names:
                            # Filter out hotels, restaurants, and non-tourist places
                            name_lower = name.lower()
                            exclude_keywords = ["hotel", "restaurant", "mall", "shopping", "resort", "inn", "lodge", "apartment", "residential"]
                            if any(keyword in name_lower for keyword in exclude_keywords):
                                continue
                            
                            # Skip if it's tagged as accommodation
                            if element["tags"].get("tourism") in ["hotel", "hostel", "apartment", "guest_house"]:
                                continue
                            
                            # Verify country if available (filter out places from wrong country)
                            # This ensures we only get places from the same country as the queried location
                            if hasattr(self, 'target_country') and self.target_country:
                                element_country = element["tags"].get("addr:country", "")
                                
                                # Also check is_in field which sometimes has country info
                                if not element_country:
                                    is_in = element["tags"].get("is_in", "")
                                    if is_in:
                                        # Extract country from is_in (format: "city, state, country")
                                        parts = [p.strip() for p in is_in.split(",")]
                                        if parts:
                                            element_country = parts[-1]  # Last part is usually country
                                
                                # If country info is available and doesn't match, skip
                                if element_country:
                                    element_country = element_country.lower()
                                    # Normalize country names for comparison
                                    target_normalized = self.target_country.lower().strip()
                                    element_normalized = element_country.strip()
                                    
                                    # Skip if countries don't match
                                    if target_normalized != element_normalized:
                                        # Allow if country names are similar (e.g., "United States" vs "USA")
                                        if not self._countries_match(target_normalized, element_normalized):
                                            continue
                                # If no country info in element, allow it (many OSM elements don't have country tags)
                                # The search radius (25km) should be sufficient to keep results in the same country
                            
                            # Prioritize well-known places
                            priority = 0
                            if "tourism" in element["tags"]:
                                tourism_type = element["tags"].get("tourism", "")
                                if tourism_type in ["attraction", "museum", "zoo", "theme_park", "gallery"]:
                                    priority += 20
                                elif tourism_type in ["monument", "viewpoint"]:
                                    priority += 15
                                else:
                                    priority += 5
                            
                            # Boost priority for specific keywords
                            if any(keyword in name_lower for keyword in ["national park", "palace", "planetarium"]):
                                priority += 15
                            elif any(keyword in name_lower for keyword in ["park", "garden", "museum", "zoo"]):
                                priority += 10
                            
                            if len(name.split()) > 1:  # Multi-word names are often specific places
                                priority += 3
                            
                            places.append((priority, name))
                            seen_names.add(name)
                            if len(places) >= limit * 3:  # Get more candidates to sort
                                break
                
                # Sort by priority and return top results
                places.sort(key=lambda x: x[0], reverse=True)
                return [name for _, name in places[:limit]]
            
        except Exception as e:
            print(f"Query execution error: {e}")
        
        return []
    
    def _get_additional_places(self, lat: float, lon: float, limit: int, seen_names: set) -> List[str]:
        """Get additional places using a broader search."""
        # Reduced radius to 25km to avoid picking up places from neighboring countries
        query = f"""[out:json][timeout:30];
(
  node["amenity"~"^(theatre|cinema|stadium|planetarium)$"](around:25000,{lat},{lon});
  way["amenity"~"^(theatre|cinema|stadium|planetarium)$"](around:25000,{lat},{lon});
  relation["amenity"~"^(theatre|cinema|stadium|planetarium)$"](around:25000,{lat},{lon});
);
out body;
>;
out skel qt;"""
        
        return self._execute_query(query, limit, seen_names)
    
    def format_places_response(self, place_name: str, places: List[str]) -> str:
        """
        Format places list into a user-friendly response.
        
        Args:
            place_name: Name of the place
            places: List of tourist place names
            
        Returns:
            Formatted string response
        """
        if not places:
            return f"Sorry, I couldn't find tourist attractions for {place_name}."
        
        response = f"In {place_name} these are the places you can go,\n"
        for place in places:
            response += f"{place}\n"
        
        return response.strip()

