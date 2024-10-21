from django.test import TestCase
from users.models import Author, Follows
import uuid
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from stream.models import Inbox
from django.contrib.contenttypes.models import ContentType

# Create your tests here.
class InboxViewTest(TestCase):
    def setUp(self):
        self.actor = Author.objects.create(
            id=uuid.uuid4(), 
            host='http://example.com/',
            display_name="Actor",
            github='http://github.com/actor1',
            page='http://example.com/actor/page'
        )

        self.object = Author.objects.create(
            id=uuid.uuid4(),
            host='http://example.com/',
            display_name='Object',
            github='http://github.com/object',
            page='http://example.com/object/page'
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
        self.actor = Author.objects.create(
            id=uuid.uuid4(), 
            host='http://example.com/',
            display_name="Actor",
            github='http://github.com/actor1',
            page='http://example.com/actor/page'
        )
        
        self.object = Author.objects.create(
            id=uuid.uuid4(),
            host='http://example.com/',
            display_name='Object',
            github='http://github.com/object',
            page='http://example.com/object/page'
        )

        self.follow_request = Follows.objects.create(
            local_follower_id=self.actor,
            followed_id=self.object,
            status='PENDING'
        )

        content_type = ContentType.objects.get_for_model(Follows)

        Inbox.objects.create(
            author=self.object,
            content_type=content_type,
            object_id=self.follow_request.id,
            content_object=self.follow_request
        )

        self.url = reverse('follow_requests', kwargs={'author_id': self.object.id})

    def test_get_follow_requests_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        #should be one follow request
        self.assertEqual(len(response.data), 1)

        #asked chatGPT how to check the response body for the follow requests endpoint tests 2024-10-21
        self.assertEqual(response.data[0]['actor']['id'], f"http://localhost/api/authors/{self.actor.id}/")
        self.assertEqual(response.data[0]['object']['id'], f"http://localhost/api/authors/{self.object.id}/")
