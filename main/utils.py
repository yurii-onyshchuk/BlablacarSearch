import os
import requests
from datetime import datetime, time

from geopy.geocoders import Nominatim

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import Q
from django.template.loader import get_template

from accounts.utils import get_API_key
from main.models import Task, TaskInfo, Trip

User = get_user_model()


def get_city_coordinate(city: str):
    geolocator = Nominatim(user_agent="Django")
    location = geolocator.geocode(city)
    if location:
        latitude = location.latitude
        longitude = location.longitude
        return f'{latitude},{longitude}'


def get_query_params(user, data):
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


def get_Blablacar_response(params):
    response = requests.get(settings.BLABLACAR_API_URL, params)
    if response.status_code == 200:
        print(f'Request to {response.url}')
        return response
    else:
        raise response.raise_for_status()


def get_trip_list_from_response(params):
    response = get_Blablacar_response(params)
    parser = TripParser(response.json())
    trips = parser.get_trips()
    trip_list = [parser.get_single_trip(trip) for trip in trips]
    return trip_list


def Q_obj_actual_task_time():
    start_of_today = datetime.combine(datetime.today(), time.min)
    return ~Q(
        Q(end_date_local__lte=datetime.now()) |
        Q(start_date_local__lte=start_of_today, end_date_local__isnull=True)
    )


def get_actual_user_tasks(user):
    tasks = Task.objects.filter(Q(user=user) & Q_obj_actual_task_time())
    return tasks


def get_archived_user_tasks(user):
    tasks = Task.objects.filter(Q(user=user) & ~Q_obj_actual_task_time())
    return tasks


def get_active_tasks():
    tasks = Task.objects.filter(Q(notification=True) & Q_obj_actual_task_time())
    return tasks


class TripParser:
    def __init__(self, json_response):
        self.json_response = json_response

    def get_task_info(self):
        return {'link': self.get_search_link(),
                'count': self.get_search_info()['count'],
                'full_trip_count': self.get_search_info()['full_trip_count']}

    def get_single_trip(self, trip):
        return {'link': self.get_trip_link(trip),
                'from_city': self.get_from_city(trip),
                'from_address': self.get_from_address(trip),
                'departure_time': datetime.fromisoformat(self.get_departure_time(trip)),
                'to_city': self.get_to_city(trip),
                'to_address': self.get_to_address(trip),
                'arrival_time': datetime.fromisoformat(self.get_arrival_time(trip)),
                'price': self.get_price(trip),
                'vehicle': self.get_vehicle(trip)}

    def get_search_link(self):
        return self.json_response['link']

    def get_search_info(self):
        return self.json_response['search_info']

    def get_trips(self):
        return self.json_response['trips']

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


class TaskChecker:
    def __init__(self, task):
        self.task = task
        self.query_params = get_query_params(task.user, task.__dict__)
        self.json_response = get_Blablacar_response(self.query_params).json()
        self.parser = TripParser(self.json_response)

    def exact_from_city_match(self, trip) -> bool:
        if self.task.only_from_city:
            return TripParser.get_from_city(trip) == self.task.from_city
        else:
            return True

    def exact_to_city_match(self, trip) -> bool:
        if self.task.only_to_city:
            return TripParser.get_to_city(trip) == self.task.to_city
        else:
            return True

    def exact_city_match(self, trip) -> bool:
        return self.exact_from_city_match(trip) and self.exact_to_city_match(trip)

    def trip_accord_to_task(self, trip) -> bool:
        return self.exact_city_match(trip)

    def get_exists_trip_links_list(self):
        exists_trip_links_list = [i[0] for i in Trip.objects.filter(task=self.task).values_list('link')]
        return exists_trip_links_list

    def get_trip_info_list(self):
        get_trip_info_list = [self.parser.get_single_trip(trip) for trip in self.get_suitable_trips()]
        return get_trip_info_list

    def get_suitable_trips(self):
        available_trip_list = self.parser.get_trips()
        exists_trip_links_list = self.get_exists_trip_links_list()
        new_found_trips = [trip for trip in available_trip_list if
                           self.parser.get_trip_link(trip) not in exists_trip_links_list]
        suitable_trips = [trip for trip in new_found_trips if self.trip_accord_to_task(trip)]
        return suitable_trips

    def get_unavailable_trip_links(self):
        available_trip_list = self.parser.get_trips()
        available_trip_links_list = [self.parser.get_trip_link(trip) for trip in available_trip_list]
        exists_trip_links_list = self.get_exists_trip_links_list()
        return [trip_link for trip_link in exists_trip_links_list if trip_link not in available_trip_links_list]

    def update_data_at_db(self):
        TaskInfo(task=self.task, **self.parser.get_task_info()).save()
        Trip.objects.filter(task=self.task, link__in=self.get_unavailable_trip_links()).delete()
        new = [Trip(task=self.task, **trip_info) for trip_info in self.get_trip_info_list()]
        Trip.objects.bulk_create(new)

    def send_notification(self, task, trip):
        subject = "Нова поїздка BlaBlaCar"
        from_email = os.getenv('EMAIL_HOST_USER')
        recipient_list = [task.user.email]
        context = self.parser.get_single_trip(trip)
        html_message = get_template('main/new_trip_email.html').render(context)
        send_mail(subject=subject, message='', from_email=from_email, recipient_list=recipient_list,
                  html_message=html_message)


def check_new_trips():
    tasks = get_active_tasks()
    for task in tasks:
        task_checker = TaskChecker(task)
        suitable_trip = task_checker.get_suitable_trips()
        if suitable_trip:
            task_checker.update_data_at_db()
            for trip in suitable_trip:
                task_checker.send_notification(task, trip)
