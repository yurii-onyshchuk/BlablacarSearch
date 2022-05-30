from geopy.geocoders import Nominatim
import requests, time, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from main.models import Task, TaskInfo, Trip


def get_city_coordinate(city: str):
    geolocator = Nominatim(user_agent="Django")
    location = geolocator.geocode(city)
    if location:
        latitude = location.latitude
        longitude = location.longitude
        return f'{latitude},{longitude}'


class TripParser:
    def __init__(self, task):
        self.task = task
        self.response = requests.get(task.get_url()).json()

    def get_search_link(self):
        return self.response['link']

    def get_search_info(self):
        return self.response['search_info']

    def get_trips_list(self):
        return self.response['trips']

    def get_trip_link(self, item):
        return self.response['trips'][item]['link']

    def get_departure_time(self, item):
        return self.response['trips'][item]["waypoints"][0]["date_time"]

    def get_from_city(self, item):
        return self.response['trips'][item]["waypoints"][0]["place"]['city']

    def get_from_address(self, item):
        try:
            return self.response['trips'][item]["waypoints"][0]["place"]['address']
        except KeyError:
            return None

    def get_to_city(self, item):
        return self.response['trips'][item]["waypoints"][1]["place"]['city']

    def get_to_address(self, item):
        try:
            return self.response['trips'][item]["waypoints"][1]["place"]['address']
        except KeyError:
            return None

    def get_arrival_time(self, item):
        return self.response['trips'][item]["waypoints"][1]["date_time"]

    def get_price(self, item):
        return f'{self.response["trips"][item]["price"]["amount"]} {self.response["trips"][item]["price"]["currency"]}'

    def get_vehicle(self, item):
        try:
            return f'{self.response["trips"][item]["vehicle"]["make"]} {self.response["trips"][item]["vehicle"]["model"]}'
        except KeyError:
            return None

    def add_trip_to_db(self, item, task):
        trip = Trip(link=self.get_trip_link(item),
                    from_city=self.get_from_city(item),
                    from_address=self.get_from_address(item),
                    departure_time=self.get_departure_time(item),
                    to_city=self.get_to_city(item),
                    to_address=self.get_to_address(item),
                    arrival_time=self.get_arrival_time(item),
                    price=self.get_price(item),
                    vehicle=self.get_vehicle(item),
                    task=task)
        trip.save()

    def add_task_info_to_db(self, task):
        task_info = TaskInfo(link=self.get_search_link(),
                             count=self.get_search_info()['count'],
                             full_trip_count=self.get_search_info()['full_trip_count'],
                             task=task)
        task_info.save()


class Checker:
    @staticmethod
    def send_message(password, from_email, to_email, subject, message):
        msg = MIMEMultipart()
        password = password
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        message = message
        msg.attach(MIMEText(message, 'plain'))
        server = smtplib.SMTP('smtp.gmail.com: 587')
        server.starttls()
        server.login(msg['From'], password)
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        server.quit()

    @staticmethod
    def check_task(task):
        parser = TripParser(task)
        parser.add_task_info_to_db(Task.objects.get(id=task.id))
        trip_list = parser.get_trips_list()
        for item in range(len(trip_list)):
            if parser.get_from_city(item) == task.from_city and parser.get_to_city(item) == task.to_city:
                try:
                    Trip.objects.get(link=parser.get_trip_link(item))
                except Trip.DoesNotExist:
                    parser.add_trip_to_db(item, task)
                    message = f'{parser.get_trip_link(item)}\n{parser.get_from_city(item)} : {parser.get_to_city(item)}\n'
                    message_data = ('argentum123TITEL95', 'yura.onyshchuk@gmail.com', f'{task.user.email}',
                                    'Нова поїздка BlaBlaCar', message)
                    return message_data

    def run_check_cycle(self):
        while True:
            tasks = Task.objects.all()
            for task in tasks:
                message_data = self.check_task(task)
                self.send_message(*message_data)
            time.sleep(120)
