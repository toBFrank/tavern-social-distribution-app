import uuid
from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Node(models.Model):
    # url of the remote node
    remote_node_url = models.URLField(primary_key=True, max_length=200, default=f"https://tavern.com")
    
    # username and password for the remote node
    # - this is what WE use to access THEM
    remote_username = models.CharField(max_length=100, default="TavernToRemote")
    remote_password = models.CharField(max_length=100, default="Tavern-->Remote")
    
    # username and password for the local node
    # - this is what THEY use to access US
    # - this is what WE have to check in NodeAuthentication
    local_username = models.CharField(max_length=100, default="RemoteToTavern")
    local_password = models.CharField(max_length=100, default="Remote-->Tavern")
    
    # boolean to check if the remote node is whitelisted
    # - True --> WE can access THEM, THEY can access US
    # - False --> WE can't access THEM, THEY can't access US
    # - (Note: username and password still have to be sent for every request, this is just a preliminary check)
    is_whitelisted = models.BooleanField(default=False)
    
    @property
    def is_authenticated(self):
        return self.is_whitelisted
    
    def __str__(self):
        return f"{self.remote_username} {self.remote_node_url}"