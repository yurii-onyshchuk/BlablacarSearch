from geopy.geocoders import Nominatim


def get_city_coordinate(city: str):
    geolocator = Nominatim(user_agent="Django")
    location = geolocator.geocode(city)
    if location:
        latitude = location.latitude
        longitude = location.longitude
        return f'{latitude},{longitude}'
