import time
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


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


class Trips:
    base_api_url = 'https://public-api.blablacar.com'
    base_search_path = '/api/v3/trips'

    def __init__(self, from_coordinate, to_coordinate, locale, currency, start_date_local, key, count, requested_seats):
        self.from_coordinate = from_coordinate
        self.to_coordinate = to_coordinate
        self.locale = locale
        self.currency = currency
        self.start_date_local = start_date_local
        self.key = key
        self.count = count
        self.requested_seats = requested_seats

    def get_url(self):
        return f'{self.base_api_url}{self.base_search_path}?' \
               f'from_coordinate={self.from_coordinate}&' \
               f'to_coordinate={self.to_coordinate}&' \
               f'locale={self.locale}&' \
               f'currency={self.currency}&' \
               f'start_date_local={self.start_date_local}&' \
               f'key={self.key}&' \
               f'count={self.count}&' \
               f'requested_seats={self.requested_seats}'

    def get_response(self):
        response = requests.get(self.get_url())
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


from_city = 'Київ'
to_city = 'Ізяслав'
trip_instance = Trips('50.4493468,30.4515337', '50.1197187,26.8223376', 'uk-UA', 'UAH', '2022-05-20T00:00:00',
                      'UJMue3Gsfmxy1DUdtowaO1RBSdHS7Clz', 100, 1)

sent_trip = []
while True:
    trip_list = trip_instance.get_trips_list()
    for trip in trip_list:
        if not Trips.get_trip_link(trip) in sent_trip:
            if Trips.get_from_city(trip) == from_city and Trips.get_to_city(trip) == to_city:
                message = f'{Trips.get_trip_link(trip)}\n{Trips.get_from_city(trip)} : {Trips.get_to_city(trip)} \n'
                send_message('argentum123TITEL95', 'yura.onyshchuk@gmail.com', 'yura.onyshchuk@gmail.com',
                             'My BlaBlaCar Check', message)
                sent_trip.append(Trips.get_trip_link(trip))
    print(sent_trip)
    time.sleep(120)
