from django.test import TestCase
from users.models import Author, Follows
import uuid
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from posts.models import Post, Comment, Like
from django.contrib.contenttypes.models import ContentType

# Create your tests here.
class InboxViewTest(TestCase):
    def setUp(self):
        self.actor_id = uuid.uuid4()
        self.actor = Author.objects.create(
            id=self.actor_id, 
            host='http://example.com/',
            display_name="Actor",
            github='http://github.com/actor1',
            page=f'http://localhost/authors/{self.actor_id}'
        )

        self.object_id = uuid.uuid4()
        self.object = Author.objects.create(
            id=self.object_id,
            host='http://example.com/',
            display_name='Object',
            github='http://github.com/object',
            page=f'http://localhost/authors/{self.object_id}'
        )

        self.follow_request = {
            "type": "follow",
            "summary": f"{self.actor.display_name} wants to follow {self.object.display_name}",
            "actor": {
                "type": "author",
                "id": f"http://localhost/api/authors/{self.actor.id}/",
                "host": self.actor.host,
                "displayName": self.actor.display_name,
                "page": self.actor.page
            },
            "object": {
                "type": "follow",
                "id": f"http://localhost/api/authors/{self.object.id}/",
                "host": self.object.host,
                "displayName": self.object.display_name,
                "page": self.object.page
            }
        }

        # Create test user
        self.user = User.objects.create_user(username='testuser', password='testpass')

        # Generate JWT token for the user
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        # Initialize API client
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)  # Use JWT authentication

        #url
        self.url = reverse("inbox", kwargs={'author_id': self.object.id})

    def test_create_follow_request_201(self):
        # follow request to inbox test at URL: api/authors/<uuid:author_id>/inbox/
        response = self.client.post(self.url, self.follow_request, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_follow_request_200(self): 
        #make the same request twice -> returns success if requested twice, but wont be created 
        self.client.post(self.url, self.follow_request, format='json')
        response = self.client.post(self.url, self.follow_request, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class GetFollowRequestsTest(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(username='testuser', password='testpass')

        # Generate JWT token for the user
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        # Initialize API client
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)  # Use JWT authentication

        self.actor = Author.objects.create(
            id=uuid.uuid4(), 
            host='http://example.com/',
            display_name="Actor",
            github='http://github.com/actor1',
            page=f'http://localhost/authors/{uuid.uuid4()}'
        )
        
        self.object = Author.objects.create(
            id=uuid.uuid4(),
            host='http://example.com/',
            display_name='Object',
            github='http://github.com/object',
            page=f'http://example.com/authors/{uuid.uuid4()}'
        )

        self.follow_request = Follows.objects.create(
            local_follower_id=self.actor,
            followed_id=self.object,
            status='PENDING'
        )

       
        self.url = reverse('follow_requests', kwargs={'author_id': self.object.id})

    def test_get_follow_requests_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        #should be one follow request
        self.assertEqual(len(response.data), 1)

    def test_get_follow_requests_400(self):
        response = self.client.get(reverse('follow_requests', kwargs={'author_id': uuid.uuid4()})) #random author id that doesnt exist
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class LikedViewTest(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(username='testuser', password='testpass')

        # Generate JWT token for the user
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        # Initialize API client
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)  # Use JWT authentication

        self.author_id = uuid.uuid4()
        self.author = Author.objects.create(
            id=self.author_id, 
            host='http://example.com/',
            display_name="Actor",
            github='http://github.com/actor1',
            page=f'http://localhost/authors/{self.author_id}'
        )

        self.post = Post.objects.create(
            author_id=self.author,
            title='Public Post',
            content_type='text/plain',
            content='This is a public post.',
            visibility='PUBLIC'
        )

        self.comment = Comment.objects.create(
            author_id=self.author,
            post_id=self.post,
            comment="This is the first comment.",
            content_type="text/plain",
        )

        self.like_url = reverse('inbox', args=[self.author.id])  
        self.author.host = 'http://localhost'
        self.author.save()

    def test_like_post(self):
        like_data = {
            "type": "like",
            'author': {
                'type': 'author',
                'id': f'http://localhost/api/authors/{self.author.id}/',
                'host': 'http://localhost',
                'page': f'http://localhost/api/authors/{self.author.id}/',
                'displayName': 'Greg',
            },
            "object": f"http://{self.author.host}/authors/{self.author.id}/posts/{self.post.id}"
        }

        response = self.client.post(self.like_url, like_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['type'], 'like')

class CommentedViewTestCase(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(username='testuser', password='testpass')

        # Generate JWT token for the user
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        # Initialize API client
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)  # Use JWT authentication

        self.author_id = uuid.uuid4()
        self.author = Author.objects.create(
            id=self.author_id, 
            host='http://example.com/',
            display_name="Actor",
            github='http://github.com/actor1',
            page=f'http://localhost/authors/{self.author_id}'
        )

        self.post = Post.objects.create(
            author_id=self.author,
            title='Public Post',
            content_type='text/plain',
            content='This is a public post.',
            visibility='PUBLIC'
        )
        self.comment_url = reverse('inbox', args=[self.author.id])  
        self.author.host = 'http://localhost'
        self.author.save()

    def test_create_comment_success(self):
        data = {
            'type': 'comment',
            'author': {
                'type': 'author',
                'id': f'http://localhost/api/authors/{self.author.id}/',
                'host': 'http://localhost',
                'page': f'http://localhost/api/authors/{self.author.id}/',
                'displayName': 'Greg',
            },
            'post': f'http://localhost/authors/{self.author.id}/posts/{self.post.id}/',
            'comment': 'This is a test comment.',
            'contentType': 'text/plain'
        }
        response = self.client.post(self.comment_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['comment'], 'This is a test comment.')
        self.assertEqual(Comment.objects.count(), 1)
