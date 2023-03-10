import uuid

from django.contrib.auth import get_user_model
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify

UserModel = get_user_model()


@receiver(pre_save, sender=UserModel)
def generate_username(sender, instance, **kwargs):
    """
    Generate a unique username for the user based on their email address.
    """
    if not instance.id:
        username = str(instance.email).split('@')[0]
        while UserModel.objects.filter(username=username).exists():
            username = f'{username}{uuid.uuid4().hex[:10]}'
        instance.username = username


@receiver(pre_save, sender=UserModel)
def generate_slug(sender, instance, **kwargs):
    """
    Generate a slug for the user based on their username.
    """
    instance.slug = slugify(instance.username)
