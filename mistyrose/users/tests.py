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
import urllib.parse

class FollowRequestTestCase(TestCase):
    def setUp(self):
        #Create two authors for testing purposes
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

        #Create test users and tokens
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.token = Token.objects.create(user=self.user)

        #Initialize API client
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)  # 通过token认证

    # def test_send_follow_request(self):
    #     #Test the API for sending follow requests
    #     url = reverse('send_follow_request', kwargs={'AUTHOR_SERIAL': self.author2.id})
    #     data = {
    #         "actor": {
    #             "id": str(self.author1.id),
    #             "type": "author",
    #             "host": "http://example.com/",
    #             "displayName": "Author 1",
    #             "github": "http://github.com/author1",
    #             "profileImage": "http://example.com/author1/image"
    #         }
    #     }
    #     response = self.client.post(url, data, format='json')

    #     #Confirm that the returned status code is 201 Created
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #     #Confirm that the request has been saved as' PENDING 'status
    #     follow_request = Follows.objects.get(local_follower_id=self.author1, followed_id=self.author2)
    #     self.assertEqual(follow_request.status, 'PENDING')
        
    def test_approve_follow_request(self):
        #Simulate sending follow requests
        follow_request = Follows.objects.create(local_follower_id=self.author1, followed_id=self.author2, status='PENDING')

        #Manually create an Inbox entry
        inbox_entry = Inbox.objects.create(
            author=self.author2,  #Authors who receive attention requests
            content_type=ContentType.objects.get_for_model(Follows),
            object_id=follow_request.id,
            content_object=follow_request
        )
        print(f"Inbox entry manually created with object_id: {follow_request.id}")

        #Encoding external author ID
        foreign_author_fqid_encoded = urllib.parse.quote(str(follow_request.id))

        #Approval request
        url = reverse('manage_follow_request', kwargs={'AUTHOR_SERIAL': self.author2.id, 'FOREIGN_AUTHOR_FQID': foreign_author_fqid_encoded})
        response = self.client.put(url, format='json')

        #Print the response returned
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.content}")

        #Confirm that the status code is 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_deny_follow_request(self):
        #Simulate sending follow requests
        follow_request = Follows.objects.create(local_follower_id=self.author1, followed_id=self.author2, status='PENDING')

        #Manually create an Inbox entry
        inbox_entry = Inbox.objects.create(
            author=self.author2,  #Authors who receive attention requests
            content_type=ContentType.objects.get_for_model(Follows),
            object_id=follow_request.id,
            content_object=follow_request
        )
        print(f"Inbox entry manually created with object_id: {follow_request.id}")

        #Encoding external author ID
        foreign_author_fqid_encoded = urllib.parse.quote(str(follow_request.id))

        #Reject request
        url = reverse('manage_follow_request', kwargs={'AUTHOR_SERIAL': self.author2.id, 'FOREIGN_AUTHOR_FQID': foreign_author_fqid_encoded})
        response = self.client.delete(url)

        #Print the response returned
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.content}")

        #The confirmation status code is 204
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        #Confirm that the request has been deleted
        self.assertFalse(Follows.objects.filter(id=follow_request.id).exists())




