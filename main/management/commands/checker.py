import requests, time, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.core.management import BaseCommand
from main.models import Task


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


class TripChecker:
    def __init__(self, url):
        self.url = url

    def get_response(self):
        response = requests.get(self.url)
        return response

    def get_dict_response(self):
        return self.get_response().json()

    def get_trips_list(self):
        return self.get_dict_response()['trips']

    @staticmethod
    def get_from_city(trip):
        return trip["waypoints"][0]["place"]['city']

    @staticmethod
    def get_to_city(trip):
        return trip["waypoints"][1]["place"]['city']

    @staticmethod
    def get_trip_link(trip):
        return trip['link']


class Command(BaseCommand):
    help = 'Перевірка наявності необхідних поїздок'

    @staticmethod
    def start_check():
        sent_trip = []
        tasks = Task.objects.all()
        while True:
            for task in tasks:
                task.trip = TripChecker(task.get_url())
                trip_list = task.trip.get_trips_list()
                for trip in trip_list:
                    if not TripChecker.get_trip_link(trip) in sent_trip:
                        if TripChecker.get_from_city(trip) == task.from_city and TripChecker.get_to_city(
                                trip) == task.to_city:
                            message = f'{TripChecker.get_trip_link(trip)}\n{TripChecker.get_from_city(trip)} : {TripChecker.get_to_city(trip)} \n'
                            send_message('argentum123TITEL95', 'yura.onyshchuk@gmail.com',
                                         f'{task.user.email}',
                                         'My BlaBlaCar Check', message)
                            print(f'Надіслано для {task.user.email}')
                            sent_trip.append(TripChecker.get_trip_link(trip))
            print(sent_trip)
            time.sleep(30)

    def handle(self, *args, **options):
        return self.start_check()
