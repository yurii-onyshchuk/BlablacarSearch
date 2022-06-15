import requests
import time
from django.core.mail import send_mail
from geopy.geocoders import Nominatim
from main.models import Task, TaskInfo, Trip


def get_city_coordinate(city: str):
    geolocator = Nominatim(user_agent="Django")
    location = geolocator.geocode(city)
    if location:
        latitude = location.latitude
        longitude = location.longitude
        return f'{latitude},{longitude}'


def try_func():
    print('Hello from Celery')


def get_response(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        print('New request')
        return response
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)


def get_message_text(trip):
    message_text = f'{Parser.get_trip_link(trip)}\n' \
                   f'{Parser.get_from_city(trip)} : {Parser.get_to_city(trip)}\n'
    return message_text


def get_message_data(task, message_text: str):
    return {'subject': "Нова поїздка BlaBlaCar",
            'message': message_text,
            'from_email': 'yura.onyshchuk@gmail.com',
            'recipient_list': [task.user.email]}


class Parser:
    def __init__(self, response: dict):
        self.response = response

    def get_search_link(self):
        return self.response['link']

    def get_search_info(self):
        return self.response['search_info']

    def get_trips_list(self):
        return self.response['trips']

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


class Checker:
    def __init__(self, task):
        self.task = task

    def trip_accord_to_task(self, trip):
        return Parser.get_from_city(trip) == self.task.from_city and Parser.get_to_city(trip) == self.task.to_city

    def trip_exists_list(self):
        link_list = [i[0] for i in Trip.objects.filter(task=self.task).values_list('link')]
        return link_list

    def single_check(self):
        response = get_response(self.task.get_url())
        parser = Parser(response.json())

        task_info = parser.get_task_info()
        TaskInfo(task=self.task, **task_info).save()

        trips_list = parser.get_trips_list()
        trip_exists_list = self.trip_exists_list()
        found_trip = [trip for trip in trips_list if
                      self.trip_accord_to_task(trip) and not Parser.get_trip_link(trip) in trip_exists_list]
        trip_info_list = [parser.get_trip_info(trip) for trip in found_trip]
        Trip.objects.bulk_create([Trip(task=self.task, **trip_info) for trip_info in trip_info_list])

        return found_trip
