from django.db import models

class Node(models.Model):
    host = models.URLField(max_length=200)  # remote node URL
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    name = models.CharField(primary_key=True, max_length=200)  # unique(?) name for the node
    # is_active = models.BooleanField(default=True)
    is_whitelisted = models.BooleanField(default=False)
    is_authenticated = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} ({self.host})"