from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _

from autoslug import AutoSlugField

from .managers import CustomUserManager

username_validator = UnicodeUsernameValidator()


class User(AbstractUser):
    username = models.CharField(_("username"), max_length=150, unique=True, validators=[username_validator],
                                error_messages={"unique": _("A user with that username already exists."), })
    first_name = models.CharField(_("first name"), max_length=150)
    last_name = models.CharField(_("last name"), max_length=150)
    slug = AutoSlugField(_("slug"), populate_from='username', unique=True)
    email = models.EmailField(_("email"), unique=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Користувач'
        verbose_name_plural = 'Користувачі'

    def __str__(self):
        return str(self.email)


class APIKey(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Користувач')
    API_key = models.CharField(verbose_name='API ключ', max_length=32, blank=True)

    class Meta:
        verbose_name = 'API-ключ'
        verbose_name_plural = 'API-ключі'

    def __str__(self):
        return str(self.API_key)
