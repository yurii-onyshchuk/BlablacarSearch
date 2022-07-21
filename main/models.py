from django.db import models
from django.urls import reverse
from datetime import datetime
from accounts.models import User


class Task(models.Model):
    from_city = models.CharField(verbose_name='Звідки?', max_length=32)
    to_city = models.CharField(verbose_name='Куди?', max_length=32)
    from_coordinate = models.CharField(verbose_name='Координата відправлення', max_length=32)
    to_coordinate = models.CharField(verbose_name='Координата прибуття', max_length=32)
    locale = models.CharField(verbose_name='Локалізація', default='uk-UA', max_length=5)
    currency = models.CharField(verbose_name='Валюта', default='UAH', max_length=3)
    start_date_local = models.DateTimeField(verbose_name='Починаючи з часу', default=datetime.now)
    end_date_local = models.DateTimeField(verbose_name='Закінчуючи часом', blank=True, null=True)
    requested_seats = models.PositiveSmallIntegerField(verbose_name='Кількість місць', default=1)
    radius_in_kilometers = models.PositiveIntegerField(verbose_name='Радіус пошуку, км', blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Користувач')
    notification = models.BooleanField(verbose_name='Отримувати сповіщення про нові поїздки', default=False)

    class Meta:
        verbose_name = 'Запланована поїздка'
        verbose_name_plural = 'Заплановані поїздки'

    def __str__(self):
        return f'{self.from_city}-{self.to_city}: {self.start_date_local.strftime("%d.%m.%Y %H:%M")}'

    def get_absolute_url(self):
        return reverse('task_detail', kwargs={'pk': self.pk})


class TaskInfo(models.Model):
    link = models.URLField(verbose_name='Посилання на пошук поїздку', blank=True, null=True)
    count = models.PositiveSmallIntegerField(verbose_name='Загальна кількість знайдених поїздок', blank=True, null=True)
    full_trip_count = models.PositiveSmallIntegerField(verbose_name='Загальна кількість знайдених повних поїздок',
                                                       blank=True,
                                                       null=True)
    task = models.OneToOneField(Task, on_delete=models.CASCADE, primary_key=True, verbose_name='Завдання')

    class Meta:
        verbose_name = 'Інформація по запланованій поїздці'
        verbose_name_plural = 'Інформація по запланованих поїздках'

    def __str__(self):
        return f'{self.task.from_city}-{self.task.to_city}: {self.task.start_date_local.strftime("%d.%m.%Y %H:%M")}'


class Trip(models.Model):
    link = models.URLField(verbose_name='Посилання на поїздку')
    from_city = models.CharField(verbose_name='Пункт відправлення', max_length=32)
    from_address = models.CharField(verbose_name='Адреса відправлення', max_length=128, blank=True, null=True)
    departure_time = models.DateTimeField(verbose_name='Час відправлення')
    to_city = models.CharField(verbose_name='Пункт прибуття', max_length=32)
    to_address = models.CharField(verbose_name='Адреса прибуття', max_length=128, blank=True, null=True)
    arrival_time = models.DateTimeField(verbose_name='Час прибуття')
    price = models.CharField(verbose_name='Ціна', max_length=16)
    vehicle = models.CharField(verbose_name='Автомобіль', max_length=32, blank=True, null=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, verbose_name='Завдання')

    class Meta:
        verbose_name = 'Доступна поїздка'
        verbose_name_plural = 'Доступні поїздки'
        ordering = ('departure_time',)

    def __str__(self):
        return f'{self.from_city}-{self.to_city}: {self.departure_time.strftime("%d.%m.%Y %H:%M")}'
