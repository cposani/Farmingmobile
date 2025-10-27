from geopy.geocoders import Nominatim

def geocode_address(address):
    geolocator = Nominatim(user_agent="farm_app")
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    return None, None


from math import radians, cos, sin, asin, sqrt

def haversine(lat1, lon1, lat2, lon2):
    # convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6371 * c
    return km
