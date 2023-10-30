from django.apps import AppConfig


class MainConfig(AppConfig):
    """Configuration class for the 'main' app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'
    verbose_name = 'Основний додаток'
