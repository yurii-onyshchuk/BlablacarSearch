from datetime import datetime


class TripParser:
    def __init__(self, trip):
        self.trip_data = trip

    def get_trip_info(self):
        return {'link': self.get_trip_link(),
                'from_city': self.get_from_city(),
                'from_address': self.get_from_address(),
                'departure_time': datetime.fromisoformat(self.get_departure_time()),
                'to_city': self.get_to_city(),
                'to_address': self.get_to_address(),
                'arrival_time': datetime.fromisoformat(self.get_arrival_time()),
                'price': self.get_price(),
                'vehicle': self.get_vehicle()}

    def get_trip_link(self):
        return self.trip_data['link']

    def get_departure_time(self):
        return self.trip_data["waypoints"][0]["date_time"]

    def get_from_city(self):
        return self.trip_data["waypoints"][0]["place"]['city']

    def get_from_address(self):
        try:
            return self.trip_data["waypoints"][0]["place"]['address']
        except KeyError:
            return None

    def get_to_city(self):
        return self.trip_data["waypoints"][1]["place"]['city']

    def get_to_address(self):
        try:
            return self.trip_data["waypoints"][1]["place"]['address']
        except KeyError:
            return None

    def get_arrival_time(self):
        return self.trip_data["waypoints"][1]["date_time"]

    def get_price(self):
        return f'{self.trip_data["price"]["amount"]} {self.trip_data["price"]["currency"]}'

    def get_vehicle(self):
        try:
            return f'{self.trip_data["vehicle"]["make"]} {self.trip_data["vehicle"]["model"]}'
        except KeyError:
            return None
