
from django.db import models


class Author(models.Model):
    email = models.EmailField()
    name = models.CharField(max_length=200)
