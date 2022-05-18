from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    API_key = models.CharField(verbose_name='API ключ', max_length=32)

    class Meta:
        verbose_name = 'Користувач'
        verbose_name_plural = 'Користувачі'

    def __str__(self):
        return self.username
