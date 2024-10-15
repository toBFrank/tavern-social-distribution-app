from django.db import models
import uuid

# Create your models here.
class Post(models.Model):
    VISIBILITY_CHOICES = [
      ('FRIENDS', 'Friends Only'),
      ('PUBLIC', 'Public'),
      ('UNLISTED', 'Unlisted'),
    ]
    
    CONTENT_TYPE_CHOICES = [
      ('text/plain', 'Plain Text'),
      ('text/markdown', 'Markdown'),
      ('image', 'Image'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) 
    author_id = models.ForeignKey('users.Author', on_delete=models.CASCADE, related_name='posts')  # TODO: replace 'users.Author' with the path to the Author model (OR set to settings.AUTH_USER_MODEL)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    plain_or_markdown_content = models.TextField(blank=True, null=True)
    image_content = models.ImageField(upload_to='images/', blank=True, null=True)
    content_type = models.CharField(max_length=50, choices=CONTENT_TYPE_CHOICES, default='text/plain')
    published = models.DateTimeField(auto_now_add=True)
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='PUBLIC')

    def __str__(self):
        return self.title
      
class Like(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author_id = models.ForeignKey('users.Author', on_delete=models.CASCADE, related_name='likes')  # TODO: replace 'users.Author' with the path to the Author model (OR set to settings.AUTH_USER_MODEL)
    