import hashlib
from datetime import datetime


class TripParser:
    def __init__(self, trip: dict):
        self.trip = trip

    def get_trip_info(self):
        return {'link': self.get_trip_link(),
                'from_city': self.get_from_city(),
                'from_address': self.get_from_address(),
                'departure_time': datetime.fromisoformat(self.get_departure_time()),
                'to_city': self.get_to_city(),
                'to_address': self.get_to_address(),
                'arrival_time': datetime.fromisoformat(self.get_arrival_time()),
                'price': self.get_price(),
                'vehicle': self.get_vehicle(),
                'trip_hash': self.get_trip_hash()}

    def get_trip_hash(self):
        trip = self.trip.copy()
        del trip['link']
        return hashlib.sha256(str(trip).encode()).hexdigest()

    def get_trip_link(self):
        return self.trip['link']

    def get_departure_time(self):
        return self.trip["waypoints"][0]["date_time"]

    def get_from_city(self):
        return self.trip["waypoints"][0]["place"]['city']

    def get_from_address(self):
        try:
            return self.trip["waypoints"][0]["place"]['address']
        except KeyError:
            return None

    def get_to_city(self):
        return self.trip["waypoints"][1]["place"]['city']

    def get_to_address(self):
        try:
            return self.trip["waypoints"][1]["place"]['address']
        except KeyError:
            return None

    def get_arrival_time(self):
        return self.trip["waypoints"][1]["date_time"]

    def get_price(self):
        return f'{self.trip["price"]["amount"]} {self.trip["price"]["currency"]}'

    def get_vehicle(self):
        try:
            return f'{self.trip["vehicle"]["make"]} {self.trip["vehicle"]["model"]}'
        except KeyError:
            return None
