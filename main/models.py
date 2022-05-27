from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime


class User(AbstractUser):
    API_key = models.CharField(verbose_name='API ключ', max_length=32)

    class Meta:
        verbose_name = 'Користувач'
        verbose_name_plural = 'Користувачі'

    def __str__(self):
        return self.username


class Trip(models.Model):
    link = models.URLField(verbose_name='Посилання на поїздку')

    from_city = models.CharField(verbose_name='Пункт відправлення', max_length=40)
    from_address = models.CharField(verbose_name='Адреса відправлення', max_length=40, blank=True)
    departure_time = models.CharField(verbose_name='Час відправлення', max_length=40)

    to_city = models.CharField(verbose_name='Пункт прибуття', max_length=40)
    to_address = models.CharField(verbose_name='Адреса прибуття', max_length=40, blank=True)
    arrival_time = models.CharField(verbose_name='Час прибуття', max_length=40)

    price = models.CharField(verbose_name='Ціна', max_length=40)
    vehicle = models.CharField(verbose_name='Автомобіль', max_length=40, blank=True)

    class Meta:
        verbose_name = 'Знайдена поїздок'
        verbose_name_plural = 'Знайдені поїздки'


class Task(models.Model):
    from_city = models.CharField(verbose_name='Звідки?', max_length=40)
    to_city = models.CharField(verbose_name='Куди?', max_length=40)
    from_coordinate = models.CharField(verbose_name='Координата відправлення', max_length=22)
    to_coordinate = models.CharField(verbose_name='Координата прибуття', max_length=22)
    locale = models.CharField(verbose_name='Локалізація', default='uk-UA', max_length=5)
    currency = models.CharField(verbose_name='Валюта', default='UAH', max_length=3)
    start_date_local = models.DateTimeField(verbose_name='Починаючи з часу', default=datetime.now)
    end_date_local = models.DateTimeField(verbose_name='Закінчуючи часом', blank=True, null=True)
    requested_seats = models.IntegerField(verbose_name='Кількість місць', default=1)
    radius_in_meters = models.IntegerField(verbose_name='Радіус пошуку, м', blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Користувач')
    found_trips = models.ForeignKey(Trip, on_delete=models.CASCADE, verbose_name='Знайдені поїздки', blank=True,
                                    null=True)

    base_api_url = 'https://public-api.blablacar.com'
    base_search_path = '/api/v3/trips'
    count = 100

    class Meta:
        verbose_name = 'Пошук поїздок'
        verbose_name_plural = 'Пошук поїздок'

    def __str__(self):
        return f'{self.from_city}-{self.to_city}: {self.start_date_local.strftime("%d.%m.%Y %H:%M")}'

    def get_url(self):
        url = f'{self.base_api_url}{self.base_search_path}?' \
              f'key={User.objects.get(username=self.user).API_key}&' \
              f'from_coordinate={self.from_coordinate}&' \
              f'to_coordinate={self.to_coordinate}&' \
              f'locale={self.locale}&' \
              f'currency={self.currency}&' \
              f'start_date_local={self.start_date_local.strftime("%Y-%m-%dT%H:%M")}&' \
              f'requested_seats={self.requested_seats}&' \
              f'count={self.count}'
        if self.end_date_local:
            url += f'&end_date_local={self.end_date_local.strftime("%Y-%m-%dT%H:%M")}'
        if self.radius_in_meters:
            url += f'&radius_in_meters={self.radius_in_meters}'
        return url
