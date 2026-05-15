# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Ensure username is unique (handled by AbstractUser by default)
    # Add your custom RFID string property
    rfid = models.CharField(max_length=100, unique=True, blank=True, null=True)

    def __str__(self):
        return self.username