import uuid
from django.db import models
import uuid

# Create your models here.
class Post(models.Model):
    TYPE_CHOICES = [('post', 'Post')]
    
    VISIBILITY_CHOICES = [
      ('FRIENDS', 'Friends'),
      ('PUBLIC', 'Public'),
      ('UNLISTED', 'Unlisted'),
      ('DELETED', 'Deleted')
    ]
    
    CONTENT_TYPE_CHOICES = [
      ('text/plain', 'Plain'),
      ('text/markdown', 'Markdown'),
      ('image', 'Image'),
    ]
    
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='post')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author_id = models.ForeignKey('users.Author', on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=200, blank=True, null=True, default='No Title')
    description = models.TextField(blank=True, null=True)
    content_type = models.CharField(max_length=50, choices=CONTENT_TYPE_CHOICES, default='text/plain')
    text_content = models.TextField(blank=True, null=True)
    image_content = models.ImageField(upload_to='images/', blank=True, null=True)
    published = models.DateTimeField(auto_now_add=True)
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='PUBLIC')

    def __str__(self):
        return self.title
      
    class Meta:
        ordering = ['-published']
      

class Like(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author_id = models.ForeignKey('users.Author', on_delete=models.CASCADE, related_name='likes') 
    published = models.DateTimeField(auto_now_add=True)  # auto_now_add sets the time of creation automatically
    object_url = models.URLField(null=True, blank=True)  # can be a URL to a post or comment
<<<<<<< Updated upstream
    
    def __str__(self):
      return f'{self.author_id} liked {self.object_url}'
    
=======

    # generic foreign key to attach like to Post or Comment
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()  # No need for max_length
    content_object = GenericForeignKey('content_type', 'object_id')  # foreign key to a Comment or Post

    def __str__(self):
        return f'{self.author_id} like'
>>>>>>> Stashed changes
class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author_id = models.ForeignKey('users.Author', on_delete=models.CASCADE, related_name='comments') 
    published = models.DateTimeField(auto_now_add=True)
    comment = models.TextField()
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content_type = models.CharField(max_length=50, blank=True, null=True)
    page = models.URLField(blank=True, null=True)
    
    def __str__(self):
      return f'{self.author_id} commented on {self.post_id}'
    
    class Meta:
        ordering = ['-published']
    