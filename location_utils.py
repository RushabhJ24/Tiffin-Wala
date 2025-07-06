import os
import math

def calculate_distance(lat1, lng1, lat2, lng2):
    """
    Calculate the distance between two points on Earth using Haversine formula
    Returns distance in kilometers
    """
    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lng1_rad = math.radians(lng1)
    lat2_rad = math.radians(lat2)
    lng2_rad = math.radians(lng2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlng = lng2_rad - lng1_rad
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of Earth in kilometers
    r = 6371
    
    return c * r

def is_location_serviceable(lat, lng):
    """
    Check if a location is within the serviceable area (5km radius)
    """
    central_lat = float(os.environ.get("CENTRAL_LAT", "28.6139"))
    central_lng = float(os.environ.get("CENTRAL_LNG", "77.2090"))
    max_distance = float(os.environ.get("SERVICE_RADIUS_KM", "5"))
    
    distance = calculate_distance(central_lat, central_lng, lat, lng)
    return distance <= max_distance

def get_location_from_address(address):
    """
    This is a placeholder for geocoding functionality.
    In a real application, you would use a geocoding service like Google Maps API
    or OpenStreetMap Nominatim to convert address to lat/lng coordinates.
    For now, we'll return default coordinates.
    """
    # Default coordinates (Central Delhi)
    return {
        'latitude': 28.6139,
        'longitude': 77.2090,
        'formatted_address': address
    }
