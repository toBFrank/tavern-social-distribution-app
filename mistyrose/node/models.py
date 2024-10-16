from django.db import models

class Node(models.Model):
    host = models.URLField(max_length=200)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    name = models.CharField(primary_key=True, max_length=200)
    is_active = models.BooleanField(default=True)
    is_authenticated = models.BooleanField(default=True)