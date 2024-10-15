from django.db import models
import uuid

class Author(models.Model):
    # Each author will have a unique identifier (UUID).
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Unique UUID for author
    host = models.URLField()  # Full API URL for author's node
    display_name = models.CharField(max_length=100)  # Display name of the author
    github = models.URLField(blank=True)  # Author's GitHub profile URL
    profile_image = models.URLField(blank=True)  # URL of the author's profile image
    page = models.URLField()  # URL of the author's HTML profile page
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the author was created
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp for when the author was last updated

    def __str__(self):
        return self.display_name