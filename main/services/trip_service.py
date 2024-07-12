import hashlib
from datetime import datetime


class TripParser:
    """A class for parsing and extracting information from a BlaBlaCar trip dictionary.

    This class takes a dictionary representing a BlaBlaCar trip and provides methods to extract
    various pieces of information from the trip.
    """

    def __init__(self, trip: dict):
        self.trip = trip

    def get_trip_info(self):
        """Extracts and returns various trip information in a structured format."""
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
        """Computes a hash of the trip (excluding the 'link' field)."""
        trip = self.trip.copy()
        del trip['link']
        return hashlib.sha256(str(trip).encode()).hexdigest()

    def get_trip_link(self):
        """Gets the link to the BlaBlaCar trip."""
        return self.trip['link']

    def get_departure_time(self):
        """Gets the departure time of the trip as a datetime object."""
        return self.trip["waypoints"][0]["date_time"]

    def get_from_city(self):
        """Gets the departure city of the trip."""
        return self.trip["waypoints"][0]["place"]['city']

    def get_from_address(self):
        """Gets the departure address of the trip (if available)."""
        try:
            return self.trip["waypoints"][0]["place"]['address']
        except KeyError:
            return None

    def get_to_city(self):
        """Gets the arrival city of the trip."""
        return self.trip["waypoints"][1]["place"]['city']

    def get_to_address(self):
        """Gets the arrival address of the trip (if available)."""
        try:
            return self.trip["waypoints"][1]["place"]['address']
        except KeyError:
            return None

    def get_arrival_time(self):
        """Gets the arrival time of the trip as a datetime object."""
        return self.trip["waypoints"][1]["date_time"]

    def get_price(self):
        """Gets the price of the trip as a formatted string."""
        return f'{self.trip["price"]["amount"]} {self.trip["price"]["currency"]}'

    def get_vehicle(self):
        """Gets the make and model of the vehicle (if available)."""
        try:
            return f'{self.trip["vehicle"]["make"]} {self.trip["vehicle"]["model"]}'
        except TypeError:
            return None
