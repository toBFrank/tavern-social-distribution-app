from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Post
from .utils import notifyOtherNodes

@receiver(post_save, sender=Post)
def postSaveRemote(sender, instance, created, **kwargs):
    if not created:  
        # print("triggered!") This gets the signal! 
        notifyOtherNodes(instance)