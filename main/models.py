from datetime import datetime

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

User = get_user_model()


class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Користувач')
    from_city = models.CharField(verbose_name='Звідки?', max_length=32)
    to_city = models.CharField(verbose_name='Куди?', max_length=32)
    from_coordinate = models.CharField(verbose_name='Координата відправлення', max_length=32)
    to_coordinate = models.CharField(verbose_name='Координата прибуття', max_length=32)
    start_date_local = models.DateTimeField(verbose_name='Починаючи з часу', default=datetime.now)
    end_date_local = models.DateTimeField(verbose_name='Закінчуючи часом', blank=True, null=True)
    requested_seats = models.PositiveSmallIntegerField(verbose_name='Кількість місць', default=1)
    radius_in_meters = models.PositiveIntegerField(verbose_name='Радіус пошуку, м', blank=True, null=True)
    notification = models.BooleanField(verbose_name='Отримувати сповіщення про нові поїздки', default=False)
    only_from_city = models.BooleanField(verbose_name='Пошук тільки у ваказному місті відправлення', default=False)
    only_to_city = models.BooleanField(verbose_name='Пошук тільки у ваказному місті прибуття', default=False)

    class Meta:
        verbose_name = 'Запланована поїздка'
        verbose_name_plural = 'Заплановані поїздки'

    def __str__(self):
        return f'{self.from_city}-{self.to_city}: {self.start_date_local.strftime("%d.%m.%Y %H:%M")}'

    def get_absolute_url(self):
        return reverse('task_detail', kwargs={'pk': self.pk})

    def get_query_params(self):
        query_params = {'key': self.user.API_key}
        query_params_key = ['from_coordinate', 'to_coordinate', 'start_date_local', 'end_date_local', 'requested_seats',
                            'radius_in_meters']
        for key in query_params_key:
            value = self.__dict__[key]
            if value:
                if key == 'start_date_local':
                    value = value.isoformat()
                if key == 'end_date_local':
                    value = value.isoformat()
                if key == 'radius_in_meters':
                    value = value
                query_params[key] = value
        query_params['locale'] = 'uk-UA'
        query_params['currency'] = 'UAH'
        query_params['count'] = 100
        return query_params


class TaskInfo(models.Model):
    task = models.OneToOneField(Task, on_delete=models.CASCADE, primary_key=True, verbose_name='Завдання')
    link = models.URLField(verbose_name='Посилання на пошук поїздку', blank=True, null=True)
    count = models.PositiveSmallIntegerField(verbose_name='Загальна кількість знайдених поїздок', blank=True, null=True)
    full_trip_count = models.PositiveSmallIntegerField(verbose_name='Загальна кількість знайдених повних поїздок',
                                                       blank=True, null=True)

    class Meta:
        verbose_name = 'Інформація по запланованій поїздці'
        verbose_name_plural = 'Інформація по запланованих поїздках'

    def __str__(self):
        return f'{self.task.from_city}-{self.task.to_city}: {self.task.start_date_local.strftime("%d.%m.%Y %H:%M")}'


class Trip(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, verbose_name='Завдання')
    link = models.URLField(verbose_name='Посилання на поїздку')
    from_city = models.CharField(verbose_name='Пункт відправлення', max_length=32)
    from_address = models.CharField(verbose_name='Адреса відправлення', max_length=128, blank=True, null=True)
    departure_time = models.DateTimeField(verbose_name='Час відправлення')
    to_city = models.CharField(verbose_name='Пункт прибуття', max_length=32)
    to_address = models.CharField(verbose_name='Адреса прибуття', max_length=128, blank=True, null=True)
    arrival_time = models.DateTimeField(verbose_name='Час прибуття')
    price = models.CharField(verbose_name='Ціна', max_length=16)
    vehicle = models.CharField(verbose_name='Автомобіль', max_length=32, blank=True, null=True)

    class Meta:
        verbose_name = 'Доступна поїздка'
        verbose_name_plural = 'Доступні поїздки'
        ordering = ('departure_time',)

    def __str__(self):
        return f'{self.from_city}-{self.to_city}: {self.departure_time.strftime("%d.%m.%Y %H:%M")}'
