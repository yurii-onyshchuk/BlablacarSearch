import json

import requests
from django.conf import settings
from geopy.geocoders import Nominatim


class GeoPyService:
    user_agent = "Django"

    def get_city_coordinate(self, city: str):
        """Get the coordinates (latitude and longitude) of a city using the Nominatim geocoder.

        This function takes a city name as input and uses
        the Nominatim geocoder to retrieve its coordinates.
        """
        geolocator = Nominatim(user_agent=self.user_agent)
        location = geolocator.geocode(city)
        if location:
            latitude = location.latitude
            longitude = location.longitude
            return f'{latitude},{longitude}'


class NovaPoshtaGeoService:
    api_key = settings.NOVA_POSHTA_API_KEY
    api_url = settings.NOVA_POSHTA_API_URL

    def __init__(self, data: dict):
        self.data = data

    def post_request_to_api(self, url: str, request_data: dict):
        """Send a request to an external API and return the response"""
        response = requests.post(url=url, json=request_data)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            raise response.raise_for_status()

    def get_response_from_API(self) -> dict:
        """Fetch city name suggestions based on user input.

        This method queries an external API to retrieve city name
        suggestions matching the user's input.
        """
        response = self.post_request_to_api(self.api_url, self.query_params())
        return response

    def query_params(self) -> dict:
        request_data = {
            "apiKey": f"{self.api_key}",
            "modelName": "AddressGeneral",
            "calledMethod": "getSettlements",
            "methodProperties": {
                "FindByString": f"{self.data['query']}",
                "Limit": "100",
                "Page": "1"
            }
        }
        return request_data
