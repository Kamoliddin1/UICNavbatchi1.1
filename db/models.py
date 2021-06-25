import sys

try:
    from django.db import models
except Exception:
    print('Exception: Django Not Found, please install it with "pip install django".')
    sys.exit()

from django.db import models
from django.utils import timezone


class Profile(models.Model):
    name = models.CharField(max_length=200)
    duty = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Navbatchi: {self.name}"
