import os
import requests
from django.conf import settings
from datetime import datetime
from django.core.mail import send_mail
from django.template.loader import get_template
from geopy.geocoders import Nominatim
from main.models import Task, TaskInfo, Trip, User


def get_city_coordinate(city: str):
    geolocator = Nominatim(user_agent="Django")
    location = geolocator.geocode(city)
    if location:
        latitude = location.latitude
        longitude = location.longitude
        return f'{latitude},{longitude}'


def get_response(url, params):
    try:
        response = requests.get(url, params)
        response.raise_for_status()
        print(f'New request to {response.url}')
        return response
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)


def get_query_params(request, form):
    query_params = {'key': User.objects.get(pk=request.user.pk).API_key}
    query_params_key = ['from_coordinate', 'to_coordinate', 'start_date_local', 'end_date_local', 'requested_seats']
    for key in query_params_key:
        value = form.cleaned_data[key]
        if value:
            if key == 'start_date_local':
                value = value.isoformat()
            if key == 'end_date_local':
                value = value.isoformat()
            query_params[key] = value
    if form.cleaned_data['radius_in_kilometers']:
        query_params['radius_in_meters'] = form.cleaned_data['radius_in_kilometers'] * 1000
    query_params['locale'] = 'uk-UA'
    query_params['currency'] = 'UAH'
    query_params['count'] = 100
    return query_params


def get_trip_list_from_api(params):
    response_json = get_response(settings.BASE_BLABLACAR_API_URL, params).json()
    parser = Parser(response_json)
    trip_list = parser.get_trips_list()
    trip_info_list = [parser.get_trip_info(trip) for trip in trip_list]
    trip_list = [TripDeserializer(trip_info) for trip_info in trip_info_list]
    return trip_list


def check_new_trips():
    tasks = Task.objects.filter(notification=True)
    for task in tasks:
        task_checker = Checker(task)
        suitable_trip = task_checker.get_suitable_trips()
        if suitable_trip:
            task_checker.update_data_at_db()
            for trip in suitable_trip:
                send_notification(task, trip)


def send_notification(task, trip):
    subject = "Нова поїздка BlaBlaCar"
    from_email = os.getenv('EMAIL_HOST_USER')
    recipient_list = [task.user.email]
    context = {'link': Parser.get_trip_link(trip),
               'from_city': Parser.get_from_city(trip),
               'to_city': Parser.get_to_city(trip),
               'from_address': Parser.get_from_address(trip),
               'to_address': Parser.get_to_address(trip),
               'departure_time': datetime.fromisoformat(Parser.get_departure_time(trip)),
               'arrival_time': datetime.fromisoformat(Parser.get_arrival_time(trip)),
               'price': Parser.get_price(trip),
               'vehicle': Parser.get_vehicle(trip)}
    html_message = get_template('main/new_trip_email.html').render(context)
    send_mail(subject=subject, message='', from_email=from_email, recipient_list=recipient_list,
              html_message=html_message)


class Parser:
    def __init__(self, response_json: dict):
        self.response_json = response_json

    def get_search_link(self):
        return self.response_json['link']

    def get_search_info(self):
        return self.response_json['search_info']

    def get_trips_list(self):
        return self.response_json['trips']

    @staticmethod
    def get_trip_link(trip):
        return trip['link']

    @staticmethod
    def get_departure_time(trip):
        return trip["waypoints"][0]["date_time"]

    @staticmethod
    def get_from_city(trip):
        return trip["waypoints"][0]["place"]['city']

    @staticmethod
    def get_from_address(trip):
        try:
            return trip["waypoints"][0]["place"]['address']
        except KeyError:
            return None

    @staticmethod
    def get_to_city(trip):
        return trip["waypoints"][1]["place"]['city']

    @staticmethod
    def get_to_address(trip):
        try:
            return trip["waypoints"][1]["place"]['address']
        except KeyError:
            return None

    @staticmethod
    def get_arrival_time(trip):
        return trip["waypoints"][1]["date_time"]

    @staticmethod
    def get_price(trip):
        return f'{trip["price"]["amount"]} {trip["price"]["currency"]}'

    @staticmethod
    def get_vehicle(trip):
        try:
            return f'{trip["vehicle"]["make"]} {trip["vehicle"]["model"]}'
        except KeyError:
            return None

    def get_task_info(self):
        return {'link': self.get_search_link(),
                'count': self.get_search_info()['count'],
                'full_trip_count': self.get_search_info()['full_trip_count']}

    def get_trip_info(self, trip):
        return {'link': self.get_trip_link(trip),
                'from_city': self.get_from_city(trip),
                'from_address': self.get_from_address(trip),
                'departure_time': self.get_departure_time(trip),
                'to_city': self.get_to_city(trip),
                'to_address': self.get_to_address(trip),
                'arrival_time': self.get_arrival_time(trip),
                'price': self.get_price(trip),
                'vehicle': self.get_vehicle(trip)}


class TripDeserializer:
    def __init__(self, trip_info: dict):
        self.link = trip_info['link']
        self.from_city = trip_info['from_city']
        self.from_address = trip_info['from_address']
        self.departure_time = datetime.fromisoformat(trip_info['departure_time'])
        self.to_city = trip_info['to_city']
        self.to_address = trip_info['to_address']
        self.arrival_time = datetime.fromisoformat(trip_info['arrival_time'])
        self.price = trip_info['price']
        self.vehicle = trip_info['vehicle']


class Checker:
    def __init__(self, task):
        self.task = task
        self.parser = Parser(get_response(settings.BASE_BLABLACAR_API_URL, task.get_query_params()).json())

    def get_suitable_trips(self):
        available_trip_list = self.parser.get_trips_list()
        exists_trip_links_list = self.get_exists_trip_links_list()
        new_found_trips = [trip for trip in available_trip_list if
                           self.parser.get_trip_link(trip) not in exists_trip_links_list]
        suitable_trips = [trip for trip in new_found_trips if self.trip_accord_to_task(trip)]
        return suitable_trips

    def exact_from_city_match(self, trip) -> bool:
        if self.task.only_from_city:
            return Parser.get_from_city(trip) == self.task.from_city
        else:
            return True

    def exact_to_city_match(self, trip) -> bool:
        if self.task.only_to_city:
            return Parser.get_to_city(trip) == self.task.to_city
        else:
            return True

    def exact_city_match(self, trip) -> bool:
        return self.exact_from_city_match(trip) and self.exact_to_city_match(trip)

    def trip_accord_to_task(self, trip) -> bool:
        return self.exact_city_match(trip)

    def get_exists_trip_links_list(self):
        return [i[0] for i in Trip.objects.filter(task=self.task).values_list('link')]

    def get_task_info(self):
        return self.parser.get_task_info()

    def get_trip_info_list(self):
        return [self.parser.get_trip_info(trip) for trip in self.get_suitable_trips()]

    def get_unavailable_trip_links(self):
        available_trip_list = self.parser.get_trips_list()
        available_trip_links_list = [self.parser.get_trip_link(trip) for trip in available_trip_list]
        exists_trip_links_list = self.get_exists_trip_links_list()
        return [trip_link for trip_link in exists_trip_links_list if trip_link not in available_trip_links_list]

    def update_data_at_db(self):
        TaskInfo(task=self.task, **self.get_task_info()).save()
        Trip.objects.bulk_create([Trip(task=self.task, **trip_info) for trip_info in self.get_trip_info_list()])
        Trip.objects.filter(link__in=self.get_unavailable_trip_links()).delete()
