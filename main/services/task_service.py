import copy
import os
from datetime import datetime, time
from typing import Iterable

from django.core.mail import send_mail
from django.db.models import Q
from django.template.loader import get_template

from main.models import Task, Trip
from main.services.request_service import get_Blablacar_response_data, get_query_params
from main.services.trip_service import TripParser


class TaskChecker:
    def __init__(self, task, response_data):
        self.task = task
        self.saved_trip = Trip.objects.filter(task=self.task)
        self.response_data = response_data

    def get_actual_trip_links(self) -> set:
        return set(trip['link'] for trip in self.response_data['trips'])

    def get_saved_trip_links(self) -> set:
        return set(self.saved_trip.values_list('link', flat=True))

    def get_new_unsaved_trip_links(self) -> set:
        return self.get_actual_trip_links().difference(self.get_saved_trip_links())

    def get_not_actual_saved_trip_links(self) -> set:
        return self.get_saved_trip_links().difference(self.get_actual_trip_links())

    def get_new_relevant_trip_list(self) -> list[dict]:
        return [trip for trip in self.response_data['trips']
                if trip['link'] in self.get_new_unsaved_trip_links() and self.trip_accord_to_task(trip)]

    def exact_from_city_match(self, trip: dict) -> bool:
        if self.task.only_from_city:
            return TripParser(trip).get_from_city() == self.task.from_city
        else:
            return True

    def exact_to_city_match(self, trip: dict) -> bool:
        if self.task.only_to_city:
            return TripParser(trip).get_to_city() == self.task.to_city
        else:
            return True

    def exact_city_match(self, trip: dict) -> bool:
        return self.exact_from_city_match(trip) and self.exact_to_city_match(trip)

    def trip_accord_to_task(self, trip: dict) -> bool:
        return self.exact_city_match(trip)

    def filter_response_accord_to_task(self) -> dict:
        filter_response_data = copy.deepcopy(self.response_data)
        for trip in self.response_data['trips']:
            if not self.trip_accord_to_task(trip):
                filter_response_data['trips'].remove(trip)
        return filter_response_data

    def delete_not_actual_saved_trips(self, trip_links: Iterable):
        Trip.objects.filter(task=self.task, link__in=trip_links).delete()

    def save_new_trips(self, trip_list: list[dict]):
        Trip_objs = [Trip(task=self.task, **TripParser(trip).get_trip_info()) for trip in trip_list]
        Trip.objects.bulk_create(Trip_objs)

    def update_saved_trips(self):
        not_actual_saved_trip_links = self.get_not_actual_saved_trip_links()
        new_relevant_trips = self.get_new_relevant_trip_list()
        if not_actual_saved_trip_links:
            self.delete_not_actual_saved_trips(not_actual_saved_trip_links)
        if new_relevant_trips:
            self.save_new_trips(new_relevant_trips)


def check_new_trips():
    tasks = get_active_tasks()
    for task in tasks:
        query_params = get_query_params(task.user, task.__dict__)
        response_data = get_Blablacar_response_data(query_params)
        task_checker = TaskChecker(task, response_data)
        new_relevant_trip_list = task_checker.get_new_relevant_trip_list()
        if new_relevant_trip_list:
            task_checker.save_new_trips(new_relevant_trip_list)
            for trip in new_relevant_trip_list:
                send_notification(task, trip)


def send_notification(task, trip: dict):
    subject = "Нова поїздка BlaBlaCar"
    from_email = os.getenv('EMAIL_HOST_USER')
    recipient_list = [task.user.email]
    context = TripParser(trip).get_trip_info()
    html_message = get_template('main/new_trip_email.html').render(context)
    send_mail(subject=subject, message='', from_email=from_email, recipient_list=recipient_list,
              html_message=html_message)


def get_active_tasks():
    return Task.objects.filter(Q(notification=True) & Q_obj_actual_task_time())


def get_actual_user_tasks(user):
    return Task.objects.filter(Q(user=user) & Q_obj_actual_task_time())


def get_archived_user_tasks(user):
    return Task.objects.filter(Q(user=user) & ~Q_obj_actual_task_time())


def Q_obj_actual_task_time():
    start_of_today = datetime.combine(datetime.today(), time.min)
    return ~Q(
        Q(end_date_local__lte=datetime.now()) |
        Q(start_date_local__lte=start_of_today, end_date_local__isnull=True)
    )
