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


def get_response(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)


class Massager:
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
    def get_single_message_text(trip):
        message_text = f'{Parser.get_trip_link(trip)}\n' \
                       f'{Parser.get_from_city(trip)} : {Parser.get_to_city(trip)}\n'
        return message_text

    @staticmethod
    def get_several_message_text(trip_list: list):
        message_text = ''
        for trip in trip_list:
            trip_message_text = Massager.get_single_message_text(trip)
            message_text += f'{trip_message_text}\n\n'
        return message_text

    @staticmethod
    def get_message_data(task, message_text: str):
        return {'password': 'argentum123TITEL95',
                'from_email': 'yura.onyshchuk@gmail.com',
                'to_email': f'{task.user.email}',
                'subject': "Нова поїздка BlaBlaCar",
                'message': message_text}


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
    @staticmethod
    def trip_accord_to_task(task, trip):
        return Parser.get_from_city(trip) == task.from_city and Parser.get_to_city(trip) == task.to_city

    @staticmethod
    def trip_exists(trip):
        return Trip.objects.filter(link=Parser.get_trip_link(trip)).exists()

    @staticmethod
    def single_check(task):
        # response_json = {
        #     "link": "https://www.blablacar.com.ua/search?fc=50.4500336,30.5241361&tc=50.2598298,28.6692345&fn=Київ&tn=Житомир&db=2022-06-01&de=2022-06-01&fpa=true",
        #     "search_info": {"count": 26, "full_trip_count": 5}, "trips": [
        #         {"link": "https://www.blablacar.com.ua/trip?source=CARPOOLING&id=2490053120-kiv-zhitomir",
        #          "waypoints": [{"date_time": "2022-06-01T16:10:00",
        #                         "place": {"city": "Київ", "address": "Залізничний вокзал Київ, Київ",
        #                                   "latitude": 50.4404947, "longitude": 30.4896335, "country_code": "UA"}},
        #                        {"date_time": "2022-06-01T18:10:00",
        #                         "place": {"city": "Житомир", "address": "Площа Перемоги", "latitude": 50.257525,
        #                                   "longitude": 28.658062, "country_code": "UA"}}],
        #          "price": {"amount": "190.00", "currency": "UAH"}, "vehicle": {"make": "VOLKSWAGEN", "model": "CADDY"},
        #          "distance_in_meters": 138745, "duration_in_seconds": 7200},
        #         {"link": "https://www.blablacar.com.ua/trip?source=CARPOOLING&id=2488136580-kijiv-zhitomir",
        #          "waypoints": [{"date_time": "2022-06-01T16:20:00",
        #                         "place": {"city": "Київ", "address": "пл. Вокзальна, 2, Київ, Київська область",
        #                                   "latitude": 50.4413871, "longitude": 30.4896118, "country_code": "UA"}},
        #                        {"date_time": "2022-06-01T18:20:00", "place": {"city": "Житомир",
        #                                                                       "address": "вул. Покровська, 166, Житомир, Житомирська область",
        #                                                                       "latitude": 50.298372,
        #                                                                       "longitude": 28.657277,
        #                                                                       "country_code": "UA"}}],
        #          "price": {"amount": "200.00", "currency": "UAH"}, "distance_in_meters": 140993,
        #          "duration_in_seconds": 7200},
        #         {"link": "https://www.blablacar.com.ua/trip?source=CARPOOLING&id=2489750970-kijiv-zhitomir",
        #          "waypoints": [{"date_time": "2022-06-01T16:30:00",
        #                         "place": {"city": "Київ", "address": "Автостанція \"Видубичі\"", "latitude": 50.4019908,
        #                                   "longitude": 30.5589082, "country_code": "UA"}},
        #                        {"date_time": "2022-06-01T19:00:00", "place": {"city": "Житомир",
        #                                                                       "address": "вул. Перемоги, 6, Житомир, Житомирська область",
        #                                                                       "latitude": 50.2623068,
        #                                                                       "longitude": 28.6509062,
        #                                                                       "country_code": "UA"}}],
        #          "price": {"amount": "140.00", "currency": "UAH"}, "distance_in_meters": 148175,
        #          "duration_in_seconds": 9000},
        #         {"link": "https://www.blablacar.com.ua/trip?source=CARPOOLING&id=2490031140-kiv-zhitomir",
        #          "waypoints": [{"date_time": "2022-06-01T17:00:00",
        #                         "place": {"city": "Київ", "address": "Житомирська, Київ", "latitude": 50.4562451,
        #                                   "longitude": 30.3654504, "country_code": "UA"}},
        #                        {"date_time": "2022-06-01T18:40:00",
        #                         "place": {"city": "Житомир", "address": "Центральний універмаг, Житомир",
        #                                   "latitude": 50.258256, "longitude": 28.6688132, "country_code": "UA"}}],
        #          "price": {"amount": "140.00", "currency": "UAH"}, "vehicle": {"make": "SKODA", "model": "OCTAVIA"},
        #          "distance_in_meters": 127075, "duration_in_seconds": 6000},
        #         {"link": "https://www.blablacar.com.ua/trip?source=CARPOOLING&id=2490123470-kiv-zhitomir",
        #          "waypoints": [{"date_time": "2022-06-01T17:00:00",
        #                         "place": {"city": "Київ", "address": "Житомирська", "latitude": 50.456245,
        #                                   "longitude": 30.36545, "country_code": "UA"}},
        #                        {"date_time": "2022-06-01T18:40:00",
        #                         "place": {"city": "Житомир", "address": "вул. Київська, 77, Житомир, Житомирська обл.",
        #                                   "latitude": 50.265559, "longitude": 28.685957, "country_code": "UA"}}],
        #          "price": {"amount": "150.00", "currency": "UAH"}, "vehicle": {"make": "HONDA", "model": "CIVIC"},
        #          "distance_in_meters": 125510, "duration_in_seconds": 6000},
        #         {"link": "https://www.blablacar.com.ua/trip?source=CARPOOLING&id=2489919195-kiv-zhitomir",
        #          "waypoints": [{"date_time": "2022-06-01T17:10:00",
        #                         "place": {"city": "Київ", "address": "вулиця Хрещатик, 22, Київ, Україна",
        #                                   "latitude": 50.449924, "longitude": 30.523163, "country_code": "UA"}},
        #                        {"date_time": "2022-06-01T19:10:00", "place": {"city": "Житомир",
        #                                                                       "address": "проспект Миру, 16, Житомир, Житомирська область, 10002",
        #                                                                       "latitude": 50.279718,
        #                                                                       "longitude": 28.631794,
        #                                                                       "country_code": "UA"}}],
        #          "price": {"amount": "105.00", "currency": "UAH"}, "distance_in_meters": 141918,
        #          "duration_in_seconds": 7200},
        #         {"link": "https://www.blablacar.com.ua/trip?source=CARPOOLING&id=2488995140-kijiv-zhitomir",
        #          "waypoints": [{"date_time": "2022-06-01T17:30:00", "place": {"city": "Київ",
        #                                                                       "address": "вул. Велика Васильківська/вул. Басейна, 1/3-2, Київ, Киівська область",
        #                                                                       "latitude": 50.441904,
        #                                                                       "longitude": 30.52097,
        #                                                                       "country_code": "UA"}},
        #                        {"date_time": "2022-06-01T19:30:00",
        #                         "place": {"city": "Житомир", "address": "пл. Соборна, 6, Житомир, Житомирська область",
        #                                   "latitude": 50.253809, "longitude": 28.658891, "country_code": "UA"}}],
        #          "price": {"amount": "190.00", "currency": "UAH"}, "distance_in_meters": 140285,
        #          "duration_in_seconds": 7200},
        #         {"link": "https://www.blablacar.com.ua/trip?source=CARPOOLING&id=2490205165-kijiv-zhitomir",
        #          "waypoints": [{"date_time": "2022-06-01T17:50:00",
        #                         "place": {"city": "Київ", "address": "Житомирська, Київ", "latitude": 50.456245,
        #                                   "longitude": 30.36545, "country_code": "UA"}},
        #                        {"date_time": "2022-06-01T19:30:00",
        #                         "place": {"city": "Житомир", "address": "вул. Київська, 77, Житомир, Житомирська обл.",
        #                                   "latitude": 50.265559, "longitude": 28.685957, "country_code": "UA"}}],
        #          "price": {"amount": "130.00", "currency": "UAH"}, "distance_in_meters": 125510,
        #          "duration_in_seconds": 6000},
        #         {"link": "https://www.blablacar.com.ua/trip?source=CARPOOLING&id=2489305250-kiv-zhitomir",
        #          "waypoints": [{"date_time": "2022-06-01T18:00:00",
        #                         "place": {"city": "Київ", "address": "ст. м. \"Житомирська\"", "latitude": 50.455901,
        #                                   "longitude": 30.365032, "country_code": "UA"}},
        #                        {"date_time": "2022-06-01T20:00:00", "place": {"city": "Житомир",
        #                                                                       "address": "ТЦ \"Глобал\", Житомир, Житомирська область, Україна",
        #                                                                       "latitude": 50.265586,
        #                                                                       "longitude": 28.686989,
        #                                                                       "country_code": "UA"}}],
        #          "price": {"amount": "170.00", "currency": "UAH"}, "vehicle": {"make": "HONDA", "model": "CIVIC"},
        #          "distance_in_meters": 133386, "duration_in_seconds": 7200},
        #         {"link": "https://www.blablacar.com.ua/trip?source=CARPOOLING&id=2489844635-kijiv-zhitomir",
        #          "waypoints": [{"date_time": "2022-06-01T18:20:00",
        #                         "place": {"city": "Київ", "address": "Авто-Актив Infiniti, Київ",
        #                                   "latitude": 50.4565046, "longitude": 30.3674061, "country_code": "UA"}},
        #                        {"date_time": "2022-06-01T20:10:00", "place": {"city": "Житомир",
        #                                                                       "address": "вул. Перемоги, 6, Житомир, Житомирська область",
        #                                                                       "latitude": 50.2623068,
        #                                                                       "longitude": 28.6509062,
        #                                                                       "country_code": "UA"}}],
        #          "price": {"amount": "190.00", "currency": "UAH"}, "distance_in_meters": 129087,
        #          "duration_in_seconds": 6600},
        #         {"link": "https://www.blablacar.com.ua/trip?source=CARPOOLING&id=2488243755-kijiv-zhitomir",
        #          "waypoints": [{"date_time": "2022-06-01T18:30:09", "place": {"city": "Київ",
        #                                                                       "address": "проспект Академіка Глушкова, 13Б, Київ, Україна, 03187",
        #                                                                       "latitude": 50.367998,
        #                                                                       "longitude": 30.458417,
        #                                                                       "country_code": "UA"}},
        #                        {"date_time": "2022-06-01T20:30:09",
        #                         "place": {"city": "Житомир", "address": "АЗК БРСМ Нафта, Житомир",
        #                                   "latitude": 50.269107, "longitude": 28.692893, "country_code": "UA"}}],
        #          "price": {"amount": "195.00", "currency": "UAH"}, "distance_in_meters": 140259,
        #          "duration_in_seconds": 7200},
        #         {"link": "https://www.blablacar.com.ua/trip?source=CARPOOLING&id=2489493140-kijiv-zhitomir-1",
        #          "waypoints": [{"date_time": "2022-06-01T19:10:00",
        #                         "place": {"city": "Київ", "address": "Шулявська, Київ", "latitude": 50.454228,
        #                                   "longitude": 30.448622, "country_code": "UA"}},
        #                        {"date_time": "2022-06-01T21:00:00",
        #                         "place": {"city": "Житомир", "address": "ТРЦ Глобал UA", "latitude": 50.266794,
        #                                   "longitude": 28.686032, "country_code": "UA"}}],
        #          "price": {"amount": "170.00", "currency": "UAH"}, "vehicle": {"make": "KIA", "model": "CERATO"},
        #          "distance_in_meters": 131781, "duration_in_seconds": 6600},
        #         {"link": "https://www.blablacar.com.ua/trip?source=CARPOOLING&id=2489712300-kijiv-zhitomir",
        #          "waypoints": [{"date_time": "2022-06-01T19:20:00", "place": {"city": "Київ",
        #                                                                       "address": "вул. Велика Васильківська/вул. Басейна, 1/3-2, Київ, Киівська область",
        #                                                                       "latitude": 50.441904,
        #                                                                       "longitude": 30.52097,
        #                                                                       "country_code": "UA"}},
        #                        {"date_time": "2022-06-02T01:10:00", "place": {"city": "Житомир",
        #                                                                       "address": "вул. Перемоги, 6, Житомир, Житомирська область",
        #                                                                       "latitude": 50.2623068,
        #                                                                       "longitude": 28.6509062,
        #                                                                       "country_code": "UA"}}],
        #          "price": {"amount": "310.00", "currency": "UAH"}, "distance_in_meters": 391836,
        #          "duration_in_seconds": 21000},
        #         {"link": "https://www.blablacar.com.ua/trip?source=CARPOOLING&id=2489162640-kijiv-zhitomir",
        #          "waypoints": [{"date_time": "2022-06-01T19:30:00",
        #                         "place": {"city": "Київ", "address": "проспект Перемоги, 134/1, Київ, Україна",
        #                                   "latitude": 50.456374, "longitude": 30.363063, "country_code": "UA"}},
        #                        {"date_time": "2022-06-01T21:10:00", "place": {"city": "Житомир",
        #                                                                       "address": "майд. Станишівський, Житомир, Житомирська область",
        #                                                                       "latitude": 50.2273125,
        #                                                                       "longitude": 28.7155847,
        #                                                                       "country_code": "UA"}}],
        #          "price": {"amount": "150.00", "currency": "UAH"}, "distance_in_meters": 129138,
        #          "duration_in_seconds": 6000},
        #         {"link": "https://www.blablacar.com.ua/trip?source=CARPOOLING&id=2488991060-kiv-zhitomir",
        #          "waypoints": [{"date_time": "2022-06-01T20:00:00",
        #                         "place": {"city": "Київ", "address": "Житомирська", "latitude": 50.4562451,
        #                                   "longitude": 30.3654504, "country_code": "UA"}},
        #                        {"date_time": "2022-06-01T21:40:00",
        #                         "place": {"city": "Житомир", "address": "Автовокзал \"Житомир\" (Житомирська АС-1)",
        #                                   "latitude": 50.2686869, "longitude": 28.692171, "country_code": "UA"}}],
        #          "price": {"amount": "170.00", "currency": "UAH"}, "vehicle": {"make": "HYUNDAI", "model": "SONATA"},
        #          "distance_in_meters": 125043, "duration_in_seconds": 6000},
        #         {"link": "https://www.blablacar.com.ua/trip?source=CARPOOLING&id=2490176975-kiv-zhitomir",
        #          "waypoints": [{"date_time": "2022-06-01T20:00:36",
        #                         "place": {"city": "Київ", "address": "Житомирська", "latitude": 50.4562451,
        #                                   "longitude": 30.3654504, "country_code": "UA"}},
        #                        {"date_time": "2022-06-01T21:40:36",
        #                         "place": {"city": "Житомир", "address": "Автовокзал \"Житомир\" (Житомирська АС-1)",
        #                                   "latitude": 50.2686869, "longitude": 28.692171, "country_code": "UA"}}],
        #          "price": {"amount": "150.00", "currency": "UAH"}, "distance_in_meters": 125043,
        #          "duration_in_seconds": 6000},
        #         {"link": "https://www.blablacar.com.ua/trip?source=CARPOOLING&id=2489995480-kijiv-zhitomir",
        #          "waypoints": [{"date_time": "2022-06-01T20:10:00",
        #                         "place": {"city": "Київ", "address": "Цирк, Київ", "latitude": 50.447856,
        #                                   "longitude": 30.492546, "country_code": "UA"}},
        #                        {"date_time": "2022-06-01T22:10:00", "place": {"city": "Житомир",
        #                                                                       "address": "проспект Незалежності, 95, Житомир, Житомирська область, Україна, 10002",
        #                                                                       "latitude": 50.269107,
        #                                                                       "longitude": 28.692893,
        #                                                                       "country_code": "UA"}}],
        #          "price": {"amount": "195.00", "currency": "UAH"}, "distance_in_meters": 136603,
        #          "duration_in_seconds": 7200},
        #         {"link": "https://www.blablacar.com.ua/trip?source=CARPOOLING&id=2488535890-kiv-zhitomir",
        #          "waypoints": [{"date_time": "2022-06-01T21:10:00",
        #                         "place": {"city": "Київ", "address": "Метро Теремки, Київ", "latitude": 50.367156,
        #                                   "longitude": 30.454286, "country_code": "UA"}},
        #                        {"date_time": "2022-06-01T23:10:00",
        #                         "place": {"city": "Житомир", "address": "Автовокзал \"Житомир\" (Житомирська АС-1)",
        #                                   "latitude": 50.2686869, "longitude": 28.692171, "country_code": "UA"}}],
        #          "price": {"amount": "150.00", "currency": "UAH"}, "distance_in_meters": 138656,
        #          "duration_in_seconds": 7200},
        #         {"link": "https://www.blablacar.com.ua/trip?source=CARPOOLING&id=2490006790-kiv-zhitomir",
        #          "waypoints": [{"date_time": "2022-06-01T21:10:45", "place": {"city": "Київ",
        #                                                                       "address": "вул. Велика Васильківська/вул. Басейна, 1/3-2, Київ, Киівська область",
        #                                                                       "latitude": 50.441904,
        #                                                                       "longitude": 30.52097,
        #                                                                       "country_code": "UA"}},
        #                        {"date_time": "2022-06-01T23:30:45", "place": {"city": "Житомир",
        #                                                                       "address": "проспект Миру, 16, Житомир, Житомирська область, 10002",
        #                                                                       "latitude": 50.279718,
        #                                                                       "longitude": 28.631794,
        #                                                                       "country_code": "UA"}}],
        #          "price": {"amount": "130.00", "currency": "UAH"}, "distance_in_meters": 141650,
        #          "duration_in_seconds": 8400},
        #         {"link": "https://www.blablacar.com.ua/trip?source=CARPOOLING&id=2490152785-kijiv-zhitomir",
        #          "waypoints": [{"date_time": "2022-06-01T22:30:00",
        #                         "place": {"city": "Київ", "address": "pereulok Ally Gorskoy, 6, Kyiv, Ukraine",
        #                                   "latitude": 50.4462222, "longitude": 30.4979036, "country_code": "UA"}},
        #                        {"date_time": "2022-06-02T00:20:00",
        #                         "place": {"city": "Житомир", "address": "Житомир, Житомир", "latitude": 50.26879,
        #                                   "longitude": 28.69759, "country_code": "UA"}}],
        #          "price": {"amount": "135.00", "currency": "UAH"}, "vehicle": {"make": "OPEL", "model": "VITA"},
        #          "distance_in_meters": 135009, "duration_in_seconds": 6600},
        #         {"link": "https://www.blablacar.com.ua/trip?source=CARPOOLING&id=2489542620-kiv-zhitomir",
        #          "waypoints": [{"date_time": "2022-06-01T23:30:00",
        #                         "place": {"city": "Київ", "address": "Вокзальна площа, 1, Київ, Україна, 02000",
        #                                   "latitude": 50.440494, "longitude": 30.489633, "country_code": "UA"}},
        #                        {"date_time": "2022-06-02T01:30:00",
        #                         "place": {"city": "Житомир", "address": "Житомирська панчішна фабрика",
        #                                   "latitude": 50.279718, "longitude": 28.631794, "country_code": "UA"}}],
        #          "price": {"amount": "130.00", "currency": "UAH"}, "distance_in_meters": 140198,
        #          "duration_in_seconds": 7200}]}
        # parser = Parser(response_json)
        response = get_response(task.get_url())
        parser = Parser(response.json())
        task_info = parser.get_task_info()
        TaskInfo(task=task, **task_info).save()
        trips_list = parser.get_trips_list()
        found_trip = [trip for trip in trips_list if
                      Checker.trip_accord_to_task(task, trip) and not Checker.trip_exists(trip)]
        trip_info_list = [parser.get_trip_info(trip) for trip in found_trip]
        Trip.objects.bulk_create([Trip(task=task, **trip_info) for trip_info in trip_info_list])
        return found_trip

    @staticmethod
    def run_check_cycle():
        while True:
            tasks = Task.objects.all()
            for task in tasks:
                found_trip = Checker.single_check(task)
                if found_trip:
                    message_text = Massager.get_several_message_text(found_trip)
                    message_data = Massager.get_message_data(task, message_text)
                    Massager.send_message(**message_data)
            time.sleep(120)
