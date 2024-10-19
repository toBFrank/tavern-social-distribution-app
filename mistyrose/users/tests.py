from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Author, Follows
from stream.models import Inbox  
import uuid
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view


class FollowRequestTestCase(TestCase):
    def setUp(self):
        # Create two authors for testing purposes
        self.author1 = Author.objects.create(
            id=uuid.uuid4(),
            host='http://example.com/',
            display_name='Author 1',
            github='http://github.com/author1',
            profile_image='http://example.com/author1/image'
        )
        self.author2 = Author.objects.create(
            id=uuid.uuid4(),
            host='http://example.com/',
            display_name='Author 2',
            github='http://github.com/author2',
            profile_image='http://example.com/author2/image'
        )

        # Create test users and tokens
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.token = Token.objects.create(user=self.user)

        # Initialize API client
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)  # Use token authentication

        # Create Follows request
        self.follow_request = Follows.objects.create(
            local_follower_id=self.author1,
            followed_id=self.author2,
            status='PENDING'
        )

        # Create Inbox entry
        content_type = ContentType.objects.get_for_model(Follows)
        self.inbox_entry = Inbox.objects.create(
            author=self.author2,
            content_type=content_type,
            object_id=self.follow_request.id,
            content_object=self.follow_request
        )

        # Set the URL with author1.id as follower_id
        self.url = reverse('manage_follow_request', kwargs={
            'author_id': str(self.author2.id),  
            'follower_id': str(self.author1.id)  # Use author1 as the follower
        })
        
        print(f"Generated URL: {self.url}")




    # def test_get_follower_exists(self):
    #     # Set the follow request status to ACCEPTED
    #     self.follow_request.status = 'ACCEPTED'
    #     self.follow_request.remote_follower_url = str(self.follow_request.id)  # Ensure URL matches
    #     self.follow_request.save()  # Save to the database

    #     # Send GET request to check if the follower exists
    #     response = self.client.get(self.url)

    #     # Print debugging information
    #     print(f"Response status: {response.status_code}")
    #     print(f"Response content: {response.content}")

    #     # Confirm the status code is 200
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data["status"], "Follower exists")

    # def test_get_follower_not_found(self):
    #     # Delete the follow request
    #     self.follow_request.delete()

    #     # Send GET request
    #     response = self.client.get(self.url)
    #     self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    #     self.assertEqual(response.data["error"], "Follower not found")

    def test_approve_follow_request(self):
        # Send a PUT request to approve the follow request
        response = self.client.put(self.url, format='json')

        # Confirm that the status code is 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        #Verify that the Inbox entry has been deleted, using object_id instead of id
        self.assertFalse(Inbox.objects.filter(object_id=self.follow_request.id).exists())



    def test_deny_follow_request(self):
        # Send a DELETE request to deny the follow request
        response = self.client.delete(self.url)

        # Confirm that the status code is 204
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify that the follow_request has been deleted
        self.assertFalse(Follows.objects.filter(id=self.follow_request.id).exists())


