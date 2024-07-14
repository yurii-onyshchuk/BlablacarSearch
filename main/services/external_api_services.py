from abc import ABC

import requests

from django.conf import settings

from geopy.geocoders import Nominatim

from accounts.services.user_service import get_API_key


class APIService(ABC):
    """ Abstract base class for services interacting with external APIs."""

    def __init__(self, url: str):
        """Initialize APIService with the provided data."""

        self.url = url

    def send_api_request(self, query_data: dict, method: str):
        """Send a request to an external API and return the response."""

        headers = {'Content-Type': 'application/json'}
        if method == 'POST':
            response = requests.post(self.url, headers=headers, json=query_data)
        elif method == 'GET':
            response = requests.get(self.url, headers=headers, params=query_data)
        else:
            raise Exception(f"The method {method} is not allowed.")
        return response


class BlaBlaCarService(APIService):
    """Service for interacting with the BlaBlaCar API."""

    def __init__(self, data=None):
        """Initialize BlaBlaCarService with the provided data."""

        self.data = data
        self.url = settings.BLABLACAR_API_URL
        self.locale = settings.BLABLACAR_LOCALE
        self.currency = settings.BLABLACAR_CURRENCY
        self.count = settings.BLABLACAR_DEFAULT_TRIP_COUNT
        super().__init__(self.url)

    def get_query_params_for_quota(self) -> dict:
        """Prepare query parameters for making a BlaBlaCar API quota request."""

        query_params = {'key': self.data['key']}
        return query_params

    def get_query_params_for_searching(self) -> dict:
        """Prepare query parameters for making a BlaBlaCar API searching request."""

        query_params_key = ['key', 'from_coordinate', 'to_coordinate', 'start_date_local',
                            'end_date_local', 'requested_seats', 'radius_in_kilometers']
        query_params = {}
        for key in query_params_key:
            value = self.data.get(key)
            if value:
                if key in ['start_date_local', 'end_date_local']:
                    value = value.isoformat()
                if key == 'radius_in_kilometers':
                    key = 'radius_in_meters'
                    value *= 1000
                query_params[key] = value
            elif key == 'key':
                query_params[key] = get_API_key(self.data.get('user'))
        query_params['locale'] = self.locale
        query_params['currency'] = self.currency
        query_params['count'] = self.count
        return query_params


class NovaPoshtaGeoService(APIService):
    """Service for interacting with the Nova Poshta API."""

    def __init__(self, data):
        """Initialize NovaPoshtaGeoService with the provided data."""

        self.data = data
        self.url = settings.NOVA_POSHTA_API_URL
        self.api_key = settings.NOVA_POSHTA_API_KEY
        super().__init__(self.url)

    def get_query_params(self) -> dict:
        """Prepare query parameters for making a Nova Poshta API request."""

        return {"apiKey": self.api_key,
                "modelName": "AddressGeneral",
                "calledMethod": "getSettlements",
                "methodProperties": {
                    "FindByString": self.data.get('query', ''),
                    "Limit": "100",
                    "Page": "1"}
                }


class GeoPyService:
    """Service for geocoding using the Nominatim geocoder."""

    user_agent = "Django"

    def get_city_coordinate(self, city: str):
        """Get the coordinates (latitude and longitude) of a city using the Nominatim geocoder."""
        geolocator = Nominatim(user_agent=self.user_agent)
        location = geolocator.geocode(city)
        if location:
            latitude = location.latitude
            longitude = location.longitude
            return f'{latitude},{longitude}'
