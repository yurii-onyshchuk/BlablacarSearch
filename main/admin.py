from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Task, TaskInfo, Trip


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('from_city', 'to_city', 'start_date_local', 'end_date_local', 'requested_seats', 'radius_in_meters',
                    'user', 'id', 'URL')
    list_display_links = ('from_city', 'to_city',)
    readonly_fields = ('URL',)

    def URL(self, obj):
        return mark_safe(f'<a href="{obj.get_api_url()}">{obj.get_api_url()}</a>')


@admin.register(TaskInfo)
class TaskInfoAdmin(admin.ModelAdmin):
    readonly_fields = ('task', 'link_URL', 'count', 'full_trip_count',)
    exclude = ('link',)

    def link_URL(self, obj):
        return mark_safe(f'<a href="{obj.link}">{obj.link}</a>')


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('from_city', 'to_city', 'departure_time', 'vehicle', 'price', 'link_URL')
    list_display_links = ('from_city', 'to_city')
    readonly_fields = (
        'task', 'link_URL', 'from_city', 'from_address', 'departure_time', 'to_city', 'to_address', 'arrival_time',
        'price', 'vehicle')
    exclude = ('link',)

    def link_URL(self, obj):
        return mark_safe(f'<a href="{obj.link}">{obj.link}</a>')
