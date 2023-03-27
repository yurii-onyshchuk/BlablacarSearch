from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Task, Trip


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'from_city', 'to_city', 'start_date_local', 'end_date_local', 'requested_seats',
                    'radius_in_kilometers', 'user',)
    list_display_links = ('id',)
    fields = ('user', 'from_city', 'only_from_city', 'to_city', 'only_to_city', 'from_coordinate', 'to_coordinate',
              'start_date_local', 'end_date_local', 'requested_seats', 'radius_in_kilometers', 'notification', 'url',)
    readonly_fields = (
        'user', 'from_city', 'to_city', 'from_coordinate', 'to_coordinate', 'start_date_local',
        'end_date_local', 'requested_seats', 'radius_in_kilometers', 'url',)

    def url(self, obj):
        return mark_safe(f'<a href="{obj.link}">{obj.link}</a>')

    url.short_description = "Посилання на пошук поїздок за завданням"


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('from_city', 'to_city', 'departure_time', 'vehicle', 'price', 'url')
    list_display_links = ('from_city', 'to_city',)
    readonly_fields = (
        'task', 'url', 'from_city', 'from_address', 'departure_time', 'to_city', 'to_address', 'arrival_time',
        'price', 'vehicle',)
    exclude = ('link',)

    def url(self, obj):
        return mark_safe(f'<a href="{obj.link}">{obj.link}</a>')

    url.short_description = "Посилання на поїздку"
