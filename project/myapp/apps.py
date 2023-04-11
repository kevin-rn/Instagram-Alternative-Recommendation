"""Module for handling the application configuration."""
from django.apps import AppConfig


class MyappConfig(AppConfig):
    """Register the myapp folder"""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'
