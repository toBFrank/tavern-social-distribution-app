from django.db import models

class Node(models.Model):
    host = models.URLField(primary_key=True)    
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    is_connected = models.BooleanField(default=True)