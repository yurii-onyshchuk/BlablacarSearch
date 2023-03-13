from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Task, TaskInfo, Trip


class TaskInfoInline(admin.StackedInline):
    model = TaskInfo
    readonly_fields = ('url', 'count', 'full_trip_count',)
    exclude = ('link',)

    def url(self, obj):
        return mark_safe(f'<a href="{obj.link}">{obj.link}</a>')

    url.short_description = "Доступні поїздки за посиланням на Blablacar"


class TripInline(admin.StackedInline):
    model = Trip
    readonly_fields = ('url', 'task', 'from_city', 'from_address', 'departure_time', 'to_city', 'to_address',
                       'arrival_time', 'price', 'vehicle')
    exclude = ('link',)
    extra = 0

    def url(self, obj):
        return mark_safe(f'<a href="{obj.link}">{obj.link}</a>')

    url.short_description = "Посилання на поїздку"


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('from_city', 'to_city', 'start_date_local', 'end_date_local', 'requested_seats',
                    'radius_in_kilometers', 'user', 'id',)
    list_display_links = ('from_city', 'to_city',)
    inlines = [TaskInfoInline, TripInline]
    save_on_top = True
    save_as = True


@admin.register(TaskInfo)
class TaskInfoAdmin(admin.ModelAdmin):
    list_display = ('task', 'url',)
    readonly_fields = ('task', 'url', 'count', 'full_trip_count',)
    exclude = ('link',)

    def url(self, obj):
        return mark_safe(f'<a href="{obj.link}">{obj.link}</a>')

    url.short_description = "Доступні поїздки за посиланням на Blablacar"


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
