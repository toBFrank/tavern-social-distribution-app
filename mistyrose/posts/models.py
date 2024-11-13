import uuid
from django.db import models
import uuid
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError # Remove this!

def get_upload_path(instance, filename):
    return f'posts/{instance.author_id}/{instance.id}/{filename}'

# Create your models here.
class Post(models.Model):
    TYPE_CHOICES = [('post', 'Post')]
    
    VISIBILITY_CHOICES = [
      ('FRIENDS', 'Friends'),
      ('PUBLIC', 'Public'),
      ('UNLISTED', 'Unlisted'),
      ('DELETED', 'Deleted'),
      ('SHARED', 'Shared')
    ]
    
    CONTENT_TYPE_CHOICES = [
      ('text/plain', 'Plain'),
      ('text/markdown', 'Markdown'),
      ('image/png', 'PNG Image'),
      ('image/jpeg', 'JPEG Image'),
      ('image/gif', 'GIF Image'),  # teehee this one is a bonus
      
    ]
    
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='post')
    title = models.CharField(max_length=200, blank=True, null=True, default='No Title')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author_id = models.ForeignKey('users.Author', on_delete=models.CASCADE, related_name='posts')
    description = models.TextField(blank=True, null=True, editable=True)
    content_type = models.CharField(max_length=50, choices=CONTENT_TYPE_CHOICES, default='text/plain')
    content = models.TextField(blank=True, null=True)
    # text_content = models.TextField(blank=True, null=True)
    # # put image content to user's media folder media/posts/author_id/post_id/image_content_name
    # image_content = models.ImageField(upload_to=get_upload_path, blank=True, null=True)
    published = models.DateTimeField(auto_now=True)
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='PUBLIC')
    original_url = models.JSONField(blank=True, null=True)

    # generic relation for reverse lookup for 'Like' objects on the post - because we are using generic foreign key in the like
    likes = GenericRelation('Like')

    def __str__(self):
        return self.title
    
    # Remove this
    def clean(self):
        # Custom validation to ensure original_url is set for shared posts
        if self.visibility == 'SHARED' and not self.original_url:
            raise ValidationError("Original URL must be provided for shared posts.")
        super().clean()
      
    class Meta:
        ordering = ['-published']
      
class Like(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author_id = models.ForeignKey('users.Author', on_delete=models.CASCADE, related_name='likes') 
    published = models.DateTimeField(null=True, auto_now_add=True)
    object_url = models.URLField(null=True, blank=True)  # can be a URL to a post or comment

    # generic foreign key to attach like to Post or Comment
    # set default value to post content type
    # content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, default=ContentType.objects.get_for_model(Post).id)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.UUIDField(max_length=200, null=True, blank=True) # for storing primary key value of the model itll be relating to
    content_object = GenericForeignKey('content_type', 'object_id') # foreign key to a Comment or Post

    def __str__(self):
      return f'{self.author_id} like'
    
class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author_id = models.ForeignKey('users.Author', on_delete=models.CASCADE, related_name='comments') 
    published = models.DateTimeField(auto_now_add=True)
    comment = models.TextField()
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content_type = models.CharField(max_length=50, blank=True, null=True)
    page = models.URLField(blank=True, null=True)

    # generic relation for reverse lookup for 'Like' objects on the post - because we are using generic foreign key in the like
    likes = GenericRelation('Like')
    
    def __str__(self):
      return f'{self.author_id} commented on {self.post_id}'
    
    class Meta:
        ordering = ['-published']
    