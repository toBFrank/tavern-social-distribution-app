from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APIClient
from users.models import Author
from posts.models import Post, Comment
import uuid
from django.urls import reverse
from rest_framework import status


# Create your tests here.
class CommentViewTests(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(username='testuser', password='testpass')

        # Generate JWT token for the user
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        # Initialize API client
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)  # Use JWT authentication

        self.commenter_author = Author.objects.create(
            id=uuid.uuid4(), 
            host='http://example.com/',
            display_name="Commenter",
            github='http://github.com/actor1',
            page='http://example.com/actor/page'
        )

        self.post_author = Author.objects.create(
            id=uuid.uuid4(), 
            host='http://example.com/',
            display_name="Poster",
            github='http://github.com/actor1',
            page='http://example.com/actor/page'
        )

        self.post = Post.objects.create(
            id=uuid.uuid4(),
            author_id=self.post_author,
            title='Post title idk',
            description='test Post hiiii',
            visibility='PUBLIC'
        )

    def test_create_local_comment_201(self):
        url = reverse('commented', kwargs={'author_serial': self.commenter_author.id})
        comment_request = {
            "type": "comment",
            "author": {
                "type": "author",
                "id": f"http://localhost/api/authors/{self.commenter_author.id}/",
                "host": self.commenter_author.host,
                "displayName": self.commenter_author.display_name,
                "page": self.commenter_author.page
            },
            "comment": "comment test creation heyy",
            "post": f"http://localhost/api/authors/{self.post_author.id}/posts/{self.post.id}",
        }
        response = self.client.post(url, comment_request, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_comments_200(self):
        url = reverse('post_comments', kwargs={'author_serial': self.commenter_author.id, 'post_id': self.post.id}) 

        Comment.objects.create(
            id=uuid.uuid4(),
            author_id=self.commenter_author,
            comment="testing get coments comment",
            post_id=self.post,
            page=self.commenter_author.page
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

class LikeViewTests(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(username='testuser', password='testpass')

        # Generate JWT token for the user
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        # Initialize API client
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)  # Use JWT authentication

        self.like_author = Author.objects.create(
            id=uuid.uuid4(), 
            host='http://example.com/',
            display_name="Liker",
            github='http://github.com/actor1',
            page='http://example.com/actor/page'
        )

        self.post_author = Author.objects.create(
            id=uuid.uuid4(), 
            host='http://example.com/',
            display_name="Poster",
            github='http://github.com/actor1',
            page='http://example.com/actor/page'
        )

        self.post = Post.objects.create(
            id=uuid.uuid4(),
            author_id=self.post_author,
            title='Post title idk',
            description='test Post hiiii',
            visibility='PUBLIC'
        )

    def test_like_post_201(self):
        url = reverse('liked', kwargs={'author_serial': self.like_author.id})  

        like_request = {
            "type": "like",
            "author": {
                "type": "author",
                "id": f"http://localhost/api/authors/{self.like_author.id}/",
                "host": self.like_author.host,
                "displayName": self.like_author.display_name,
                "page": self.like_author.page
            },
            "object": f"http://localhost/api/authors/{self.post_author.id}/posts/{self.post.id}",
        }

        response = self.client.post(url, like_request, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
