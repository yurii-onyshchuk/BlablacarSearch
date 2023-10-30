from geopy.geocoders import Nominatim


def get_city_coordinate(city: str):
    """Get the coordinates (latitude and longitude) of a city using the Nominatim geocoder.

    This function takes a city name as input and uses
    the Nominatim geocoder to retrieve its coordinates.
    """
    geolocator = Nominatim(user_agent="Django")
    location = geolocator.geocode(city)
    if location:
        latitude = location.latitude
        longitude = location.longitude
        return f'{latitude},{longitude}'
