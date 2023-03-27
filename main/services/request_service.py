import json
import requests

from django.conf import settings

from accounts.utils import get_API_key


def request_to_Blablacar(query_params):
    response = requests.get(settings.BLABLACAR_API_URL, query_params)
    if response.status_code == 200:
        print(f'Request to {response.url}')
        return response
    else:
        raise response.raise_for_status()


def get_Blablacar_response_data(user=None, data=None, query_params=None) -> dict:
    if not query_params:
        query_params = get_query_params(user, data)
    json_data = request_to_Blablacar(query_params=query_params).text
    return json.loads(json_data)


def get_query_params(user, data: dict):
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
