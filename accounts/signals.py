import uuid

from django.contrib.auth import get_user_model
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify

UserModel = get_user_model()


@receiver(pre_save, sender=UserModel)
def generate_username(sender, instance, **kwargs):
    """Generate a unique username based on the user's email address.

    Args:
        sender: The sender of the signal.
        instance (User): The User instance being saved.
        kwargs: Additional keyword arguments.

    This signal handler is connected to the pre_save signal of the User model.
    It generates a unique username by extracting the part of the user's email address
    before the "@" symbol and using it as the username. If the generated username
    already exists in the database, a random hexadecimal string is appended to ensure uniqueness.
    """
    if not instance.id:
        username = str(instance.email).split('@')[0]
        while UserModel.objects.filter(username=username).exists():
            username = f'{username}{uuid.uuid4().hex[:10]}'
        instance.username = username


@receiver(pre_save, sender=UserModel)
def generate_slug(sender, instance, **kwargs):
    """Generate a unique slug for the user based on their username.

    Args:
        sender: The sender of the signal.
        instance (User): The User instance being saved.
        kwargs: Additional keyword arguments.

    This signal handler is connected to the pre_save signal of the User model.
    It generates a unique slug for the user based on their username. The slug is generated
    using the slugify function, which converts the username to a URL-friendly format.
    """
    instance.slug = slugify(instance.username)
