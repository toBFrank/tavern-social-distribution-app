from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Author, Follows
from stream.models import Inbox  
import uuid
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from rest_framework_simplejwt.tokens import RefreshToken

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

        # Create test user
        self.user = User.objects.create_user(username='testuser', password='testpass')

        # Generate JWT token for the user
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        # Initialize API client
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)  # Use JWT authentication

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

    def test_approve_follow_request(self):
        # Send a PUT request to approve the follow request
        response = self.client.put(self.url, format='json')

        # Confirm that the status code is 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify that the Inbox entry has been deleted, using object_id instead of id
        self.assertFalse(Inbox.objects.filter(object_id=self.follow_request.id).exists())

    def test_deny_follow_request(self):
        # Send a DELETE request to deny the follow request
        response = self.client.delete(self.url)

        # Confirm that the status code is 204
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify that the follow_request has been deleted
        self.assertFalse(Follows.objects.filter(id=self.follow_request.id).exists())


class UnfollowTestCase(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(username='testuser', password='testpass')

        # Generate JWT token for the user
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        # Initialize API client
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)  # Use JWT authentication

        # Create test authors and follow relationship
        self.author1 = Author.objects.create(
            id=uuid.uuid4(), 
            display_name='Author 1', 
            host='http://localhost/', 
            page='http://localhost/author1',
            user=self.user  # Associate the created user with Author
        )
        self.author2 = Author.objects.create(
            id=uuid.uuid4(), 
            display_name='Author 2', 
            host='http://localhost/', 
            page='http://localhost/author2'
        )
        
        self.follow = Follows.objects.create(
            local_follower_id=self.author1, 
            followed_id=self.author2,
            status='ACCEPTED'
        )

        self.unfollow_url = f'/authors/{self.author2.id}/followers/{self.author1.id}/unfollow/'

    def test_unfollow_success(self):
        # Test successful unfollow
        response = self.client.delete(self.unfollow_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Successfully unfollowed the author.')

        # Ensure the follow relationship is deleted from the database
        follow_exists = Follows.objects.filter(
            followed_id=self.author2, 
            local_follower_id=self.author1
        ).exists()
        self.assertFalse(follow_exists)

    def test_unfollow_not_found(self):
        # Test unfollow when the follow relationship does not exist
        invalid_url = f'/authors/{self.author2.id}/followers/{uuid.uuid4()}/unfollow/'  # Use a non-existing follower_id
        response = self.client.delete(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Follow relationship does not exist.')

    def test_unfollow_invalid_uuid(self):
        # Test when UUID format is invalid
        invalid_url = f'/authors/{self.author2.id}/followers/invalid-uuid/unfollow/'
        response = self.client.delete(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid author or follower ID format.')
