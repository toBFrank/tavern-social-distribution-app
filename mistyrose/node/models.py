from django.db import models

class Node(models.Model):
    host = models.URLField(max_length=200)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    team = models.IntegerField(default=0)
    isconnected = models.BooleanField(default=True)