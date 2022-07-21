from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Task, TaskInfo, Trip
from .utils import get_request_url, query_params_from_db_task


class TaskInfoInline(admin.StackedInline):
    model = TaskInfo
    readonly_fields = ('count', 'full_trip_count', 'link_URL')
    exclude = ('link',)

    def link_URL(self, obj):
        return mark_safe(f'<a href="{obj.link}">{obj.link}</a>')

    link_URL.short_description = "Посилання"


class TripInline(admin.StackedInline):
    model = Trip
    readonly_fields = (
        'task', 'from_city', 'from_address', 'departure_time', 'to_city', 'to_address', 'arrival_time',
        'price', 'vehicle', 'link_URL')
    exclude = ('link',)
    extra = 0

    def link_URL(self, obj):
        return mark_safe(f'<a href="{obj.link}">{obj.link}</a>')

    link_URL.short_description = "Посилання на поїздку"


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('from_city', 'to_city', 'start_date_local', 'end_date_local', 'requested_seats',
                    'radius_in_kilometers', 'user', 'id', 'URL')
    list_display_links = ('from_city', 'to_city',)
    readonly_fields = ('URL',)
    inlines = [TaskInfoInline, TripInline]
    save_on_top = True
    save_as = True

    def URL(self, obj):
        return mark_safe(
            f'<a href="{get_request_url(**query_params_from_db_task(obj))}">{get_request_url(**query_params_from_db_task(obj))}</a>')

    URL.short_description = "API-посилання"


@admin.register(TaskInfo)
class TaskInfoAdmin(admin.ModelAdmin):
    readonly_fields = ('task', 'link_URL', 'count', 'full_trip_count',)
    exclude = ('link',)

    def link_URL(self, obj):
        return mark_safe(f'<a href="{obj.link}">{obj.link}</a>')

    link_URL.short_description = "Посилання"


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

    link_URL.short_description = "Посилання на поїздку"
