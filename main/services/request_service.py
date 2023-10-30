import json
import requests

from django.conf import settings

from accounts.services.user_service import get_API_key


def request_to_Blablacar(query_params):
    """Make a GET request to the BlaBlaCar API.

    This function sends a GET request to the BlaBlaCar API with the specified query parameters.

    Args:
        query_params (dict): A dictionary of query parameters to include in the request.
    Returns:
        requests.Response: The response object containing the API's response.
    """
    response = requests.get(settings.BLABLACAR_API_URL, query_params)
    print(f'Request to {response.url}')
    return response


def get_Blablacar_response_data(query_params) -> dict:
    """Get data from BlaBlaCar API based on provided query parameters.

    This function makes a request to the BlaBlaCar API using the provided query parameters and returns the response data
    as a dictionary. It checks the status code of the response and raises an exception if the status code is not 200.

    Args:
        query_params (dict): A dictionary containing the query parameters for the API request.
    Returns:
        dict: The response data from the BlaBlaCar API as a dictionary.
    """
    response = request_to_Blablacar(query_params)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        raise response.raise_for_status()


def get_query_params(user, data: dict):
    """Get query parameters for making a BlaBlaCar API request.

    This function constructs a dictionary of query parameters to be used in a BlaBlaCar API request based on the user
    and data provided. It converts certain data fields to the required format for the API.

    Args:
        user: The user for whom the request is being made.
        data (dict): A dictionary containing data to be used as query parameters.
    Returns:
        dict: A dictionary of query parameters ready to be used in a BlaBlaCar API request.
    """
    query_params = {'key': get_API_key(user=user)}
    query_params_key = ['from_coordinate', 'to_coordinate', 'start_date_local', 'end_date_local', 'requested_seats',
                        'radius_in_kilometers']
    for key in query_params_key:
        value = data[key]
        if value:
            if key == 'start_date_local' or key == 'end_date_local':
                value = value.isoformat()
            if key == 'radius_in_kilometers':
                key = 'radius_in_meters'
                value *= 1000
            query_params[key] = value
    query_params['locale'] = settings.BLABLACAR_LOCALE
    query_params['currency'] = settings.BLABLACAR_CURRENCY
    query_params['count'] = settings.BLABLACAR_DEFAULT_TRIP_COUNT
    return query_params
