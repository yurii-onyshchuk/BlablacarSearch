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


class Task(models.Model):
    from_city = models.CharField(verbose_name='Звідки?', max_length=40)
    to_city = models.CharField(verbose_name='Куди?', max_length=40)
    locale = models.CharField(verbose_name='Локалізація', default='uk-UA', max_length=5)
    currency = models.CharField(verbose_name='Валюта', default='UAH', max_length=3)
    start_date_local = models.DateTimeField(verbose_name='Починаючи з часу', default=datetime.now)
    end_date_local = models.DateTimeField(verbose_name='Закінчуючи часом', blank=True, null=True)
    requested_seats = models.IntegerField(verbose_name='Кількість місць', default=1)
    radius_in_meters = models.IntegerField(verbose_name='Радіус пошуку', blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Пошук поїздок'
        verbose_name_plural = 'Пошук поїздок'

    def __str__(self):
        return f'{self.from_city}-{self.to_city}: {self.start_date_local}'
