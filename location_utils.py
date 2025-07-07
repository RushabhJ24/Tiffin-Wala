import os
import math
from dotenv import load_dotenv
load_dotenv()

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
    try:
        from models import Settings
        # Get dynamic central coordinates from database
        central_lat, central_lng = Settings.get_central_coordinates()
        service_radius = Settings.get_service_radius()
    except:
        # Fallback to environment variables if database not available
        central_lat = float(os.environ.get("CENTRAL_LAT", "20.457316"))
        central_lng = float(os.environ.get("CENTRAL_LNG", "75.016754"))
        service_radius = float(os.environ.get("SERVICE_RADIUS_KM", "5"))
    
    print(f"Loaded from settings: {central_lat} {central_lng}")
    print(f"{central_lat} {central_lng} {lat} {lng}")
    
    distance = calculate_distance(central_lat, central_lng, lat, lng)
    return distance <= service_radius

def get_location_from_address(address):
    """
    This is a placeholder for geocoding functionality.
    In a real application, you would use a geocoding service like Google Maps API
    or OpenStreetMap Nominatim to convert address to lat/lng coordinates.
    For now, we'll return default coordinates.
    """
    try:
        from models import Settings
        # Get dynamic central coordinates from database
        central_lat, central_lng = Settings.get_central_coordinates()
    except:
        # Fallback coordinates
        central_lat = 20.457316
        central_lng = 75.016754
    
    return {
        'latitude': central_lat,
        'longitude': central_lng,
        'formatted_address': address
    }
