from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Author, Follows
from rest_framework.test import APITestCase
from stream.models import Inbox  
import uuid
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import Author, Follows
from posts.models import Post

class LoginViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.author = Author.objects.create(user=self.user, display_name='Test User')
        self.url = reverse('login')  # Ensure you have named the login URL as 'login'

    def test_login_success(self):
        data = {"username": "testuser", "password": "testpass"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)

    def test_login_invalid_credentials(self):
        data = {"username": "wronguser", "password": "wrongpass"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
        
class SignUpViewTest(APITestCase):
    def setUp(self):
        self.url = reverse('signup')  

    def test_signup_success(self):
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword",
            "displayName": "New User",
            "github": "https://github.com/newuser"
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['displayName'], 'New User')

    def test_signup_username_exists(self):
        User.objects.create_user(username='newuser', password='testpass')
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword",
            "displayName": "New User"
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertIn('message', response.data)

    def test_signup_missing_fields(self):
        data = {
            "username": "newuser",
            "password": "newpassword",
            "displayName": "New User"
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('message', response.data)


class LogoutViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        self.url = reverse('logout')

    def test_logout_success(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
class VerifyTokenViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.author = Author.objects.create(user=self.user, display_name='Test User')
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        self.url = reverse('verify-token')  
    def test_verify_token_valid(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['authorId'], str(self.author.id))

    def test_verify_token_invalid(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalidtoken')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
class AuthorDetailViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.author = Author.objects.create(user=self.user, display_name='Test User')
        self.url = reverse('author-detail', kwargs={'pk': self.author.id})
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_author_detail(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['displayName'], 'Test User')
    def test_author_detail_not_found(self):
        non_existing_uuid = uuid.uuid4()
        response = self.client.get(reverse('author-detail', kwargs={'pk': non_existing_uuid}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
class AuthorProfileViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.author = Author.objects.create(user=self.user, display_name='Test Author', github='https://github.com/testauthor')
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        Post.objects.create(author_id=self.author, title="Public Post", visibility='PUBLIC')
        Post.objects.create(author_id=self.author, title="Friends Post", visibility='FRIENDS')
        Post.objects.create(author_id=self.author, title="Unlisted Post", visibility='UNLISTED')
        
        self.follower = Author.objects.create(display_name="Follower Author", github="https://github.com/followerauthor")
        Follows.objects.create(local_follower_id=self.follower, followed_id=self.author, status='ACCEPTED')
        self.url = reverse('author-profile', kwargs={'pk': str(self.author.id)})

    def test_author_profile_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['displayName'], 'Test Author')
        self.assertEqual(response.data['followers_count'], 1)
        self.assertEqual(response.data['public_posts'][0]['title'], 'Public Post')
        self.assertEqual(len(response.data['friends_posts']), 1)
        self.assertEqual(len(response.data['unlisted_posts']), 1)

    def test_author_profile_not_found(self):
        
        non_existing_uuid = uuid.uuid4()
        url = reverse('author-profile', kwargs={'pk': non_existing_uuid})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class AuthorEditProfileViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.author = Author.objects.create(user=self.user, display_name="Test Author", github="https://github.com/testauthor")
        
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        self.url = reverse('author-edit-profile', kwargs={'pk': str(self.author.id)})

    def test_get_author_profile_for_editing(self):
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['display_name'], 'Test Author')

    def test_edit_author_profile_success(self):
        data = {
            "display_name": "Updated Test Author",
            "github": "https://github.com/updatedauthor"
        }
        
        response = self.client.put(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['display_name'], 'Updated Test Author')

    def test_edit_author_profile_invalid_data(self):
        data = {
            "display_name": "",  
        }
        
        
        response = self.client.put(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('display_name', response.data)

class AuthorsViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.author = Author.objects.create(user=self.user, display_name="Authenticated Author")

        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        self.author1 = Author.objects.create(
            id=uuid.uuid4(),
            display_name="Author 1",
            github="https://github.com/author1"
        )
        self.author2 = Author.objects.create(
            id=uuid.uuid4(),
            display_name="Author 2",
            github="https://github.com/author2"
        )

        self.url = reverse('authors-list')

    def test_get_authors_list(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertEqual(response.data['type'], 'authors')
        self.assertEqual(len(response.data['authors']), 3)
        self.assertEqual(response.data['authors'][0]['displayName'], 'Authenticated Author')
        self.assertEqual(response.data['authors'][1]['displayName'], 'Author 1')
        self.assertEqual(response.data['authors'][2]['displayName'], 'Author 2')

    def test_empty_authors_list(self):
        Author.objects.all().delete()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['authors'], [])

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

class FollowersDetailViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.author = Author.objects.create(user=self.user, display_name="Test Author")

        self.follower1 = Author.objects.create(user=User.objects.create_user(username='follower1', password='password1'), display_name='Follower One')
        self.follower2 = Author.objects.create(user=User.objects.create_user(username='follower2', password='password2'), display_name='Follower Two')

        Follows.objects.create(local_follower_id=self.follower1, followed_id=self.author, status='ACCEPTED')
        Follows.objects.create(local_follower_id=self.follower2, followed_id=self.author, status='ACCEPTED')

        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        self.url = reverse('followers')

    def test_get_followers_list(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data['followers']), 2)
        self.assertEqual(response.data['followers'][0]['displayName'], 'Follower One')
        self.assertEqual(response.data['followers'][1]['displayName'], 'Follower Two')
        
class FriendsViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.author = Author.objects.create(user=self.user, display_name="Authenticated Author")

        self.author1 = Author.objects.create(user=User.objects.create_user(username='author1', password='password1'), display_name='Author One')
        self.author2 = Author.objects.create(user=User.objects.create_user(username='author2', password='password2'), display_name='Author Two')

        # Create follow requests for mutual friendship
        Follows.objects.create(local_follower_id=self.author, followed_id=self.author1, status='ACCEPTED')  # self.author follows author1
        Follows.objects.create(local_follower_id=self.author1, followed_id=self.author, status='ACCEPTED')  # author1 follows self.author
        Follows.objects.create(local_follower_id=self.author2, followed_id=self.author, status='ACCEPTED')  # author2 follows self.author

        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        self.url = reverse('friends')

    def test_get_friends_list(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data['friends']), 1)  # Should find 1 mutual friend
        self.assertEqual(response.data['friends'][0]['displayName'], 'Author One')  # Should return Author One


class ProfileImageUploadViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.author = Author.objects.create(user=self.user, display_name="Test Author")

        self.url = reverse('upload-profile-image', kwargs={'username': self.user.username})
        
        self.image = SimpleUploadedFile(
            name='https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png',
            content=b'image',
            content_type='image/png'
        )
   
    def test_upload_profile_image_success(self):
        response = self.client.post(self.url, {'profile_image': self.image})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('url', response.data)
        self.assertIn('Profile image uploaded successfully', response.data['message'])

    def test_upload_profile_image_no_file(self):
        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'No file provided.')