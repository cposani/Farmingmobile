from geopy.geocoders import Nominatim

def geocode_address(address):
    geolocator = Nominatim(user_agent="shop_app")
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    return None, None
