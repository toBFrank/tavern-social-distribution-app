from django.db import models
import uuid
from django.contrib.auth.models import User

class Author(models.Model):
    # Each author will have a unique identifier (UUID).
    type = models.CharField(max_length=10, default="author")
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) # Unique UUID for author, which might be used in constructing the full URL in the serializer
    url = models.URLField(unique=True, editable=False) # identify author by full url
    host = models.URLField()  # Full API URL for author's node
    display_name = models.CharField(max_length=100)  # Display name of the author
    github = models.URLField(blank=True)  # Author's GitHub profile URL
    profile_image = models.URLField(blank=True)  # URL of the author's profile image
    page = models.URLField()  # URL of the author's HTML profile page
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the author was created
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp for when the author was last updated
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='author', null=True, blank=True)  # User object for the author

    def save(self, *args, **kwargs):
        # create url
        if not self.url:
            self.url = f"{self.host.rstrip('/')}/api/authors/{self.id}/"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.display_name
    
class Follows(models.Model):
    STATUS_CHOICES = [
      ('PENDING', 'Follow Request Pending'),
      ('ACCEPTED', 'Follow Request Accepted'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Unique UUID for Inbox purposes

    local_follower_id = models.ForeignKey(Author, on_delete=models.CASCADE, null=True, blank=True) # for local only - optional - can be null
    remote_follower_url = models.URLField(max_length=200, null=True, blank=True) # for remote only, optional

    followed_id = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='followers') # user being followed

    is_remote = models.BooleanField(default=False)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)

    def __str__(self):
      return f'{self.local_follower_id} is following or has requested to follow {self.followed_id}'
