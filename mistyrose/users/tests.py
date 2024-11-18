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
        self.url = reverse('login')  

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

# User Story #4 Test: As an author, I want a public page with my profile information.
class AuthorProfileViewTest(APITestCase):
    def setUp(self):
        # Creating a user and associated author
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.author = Author.objects.create(user=self.user, display_name='Test Author', github='https://github.com/testauthor')
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Creating posts with various visibility statuses
        Post.objects.create(
            author_id=self.author,
            title="Public Post",
            content="This is a public post.",
            content_type='text/plain',
            visibility='PUBLIC'
        )
        Post.objects.create(
            author_id=self.author,
            title="Friends Post",
            content="This is a friends-only post.",
            content_type='text/plain',
            visibility='FRIENDS'
        )
        Post.objects.create(
            author_id=self.author,
            title="Unlisted Post",
            content="This is an unlisted post.",
            content_type='text/plain',
            visibility='UNLISTED'
        )
        
        # Creating a follower relationship
        self.follower = Author.objects.create(display_name="Follower Author", github="https://github.com/followerauthor")
        Follows.objects.create(local_follower_id=self.follower, followed_id=self.author, status='ACCEPTED')

        # Defining the URL for the author profile
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

    # def test_get_authors_list(self):
    #     response = self.client.get(self.url)

    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    #     self.assertEqual(response.data['type'], 'authors')
    #     self.assertEqual(len(response.data['authors']), 3)
    #     self.assertEqual(response.data['authors'][0]['displayName'], 'Authenticated Author')
    #     self.assertEqual(response.data['authors'][1]['displayName'], 'Author 1')
    #     self.assertEqual(response.data['authors'][2]['displayName'], 'Author 2')

    # def test_empty_authors_list(self):
    #     Author.objects.all().delete()

    #     response = self.client.get(self.url)

    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data['authors'], [])

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
        
        # print(f"Generated URL: {self.url}")

    def test_approve_follow_request(self):
        # Send a PUT request to approve the follow request
        response = self.client.put(self.url, format='json')

        # Confirm that the status code is 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)

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

        self.unfollow_url = reverse('unfollow', kwargs={
            'author_id': str(self.author2.id),
            'follower_id': str(self.author1.id)
        })

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

        self.url = reverse('friends', kwargs={'author_id': str(self.author.id)})

    def test_get_friends_list(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data['friends']), 1)  # Should find 1 mutual friend
        self.assertEqual(response.data['friends'][0]['displayName'], 'Author One')  # Should return Author One

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

        self.url = reverse('followers', kwargs={'author_id': str(self.author.id)})

    def test_get_followers_list(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data['followers']), 2)
        self.assertEqual(response.data['followers'][0]['displayName'], 'Follower One')
        self.assertEqual(response.data['followers'][1]['displayName'], 'Follower Two')

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

# User Story #2 Test: As an author, I want a consistent identity per node.
class AuthorUrlTestCase(APITestCase):
    def setUp(self):
        # Create test users and authors
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.author = Author.objects.create(
            user=self.user,
            display_name="Test User",
            host="http://example.com",
            github="https://github.com/testuser"
        )

        # API URL for author detail
        self.url = reverse('author-detail', kwargs={'pk': self.author.id})

        # Set up authentication
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_author_url_generation(self):
        # Verify that the URL is generated correctly
        expected_url = f"http://example.com/api/authors/{self.author.id}/"
        self.assertEqual(self.author.url, expected_url)
    
    def test_author_url_consistency(self):
        # Modify other fields and verify that the URL is consistent
        original_url = self.author.url
        self.author.display_name = "Updated Author"
        self.author.save()
        self.assertEqual(self.author.url, original_url)
        
    def test_author_url_in_api_response(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_url = f"http://example.com/api/authors/{self.author.id}/"
        self.assertEqual(response.data['id'], expected_url)  
    
    def test_author_detail_not_found(self):
        # Test for non-existent author
        non_existing_uuid = uuid.uuid4()
        response = self.client.get(reverse('author-detail', kwargs={'pk': non_existing_uuid}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

# User Story #2 Test: As an author, I want a consistent identity per node.
class AuthorApiConsistencyTestCase(APITestCase):
    def setUp(self):
        # Create test users and multiple authors
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.authors = [
            Author.objects.create(
                id=uuid.uuid4(),
                host="http://example.com",
                display_name=f"Author {i}",
                github=f"http://github.com/author{i}"
            ) for i in range(3)
        ]

        # Set up authentication
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        
    def test_multiple_authors_url_uniqueness(self):
        # Verify URL uniqueness
        urls = [f"http://example.com/api/authors/{author.id}/" for author in self.authors]
        self.assertEqual(len(urls), len(set(urls)))  
        for author in self.authors:
            expected_url = f"http://example.com/api/authors/{author.id}/"
            self.assertEqual(f"http://example.com/api/authors/{author.id}/", expected_url)

    # def test_deleted_authors_not_in_api_list(self):
    #     # After removing an author, verify that it no longer appears in the API list
    #     deleted_author = self.authors[0]
    #     deleted_author.delete()
    #     response = self.client.get("/api/authors/")
    #     self.assertEqual(response.status_code, 200)
    #     # Check if the `id` field does not contain a deleted author
    #     self.assertNotIn(
    #         str(deleted_author.id), 
    #         [author["id"] for author in response.json()["authors"]]
    #     )

    # def test_api_author_list_url_format(self):
    #     # Verify that the `id` format in the author list is correct
    #     response = self.client.get("/api/authors/")
    #     self.assertEqual(response.status_code, 200)
    #     for author in response.json()["authors"]:
    #         self.assertTrue(
    #             author["id"].startswith("http://example.com/api/authors/")  
    #         )

# User Story #3 Test: As a node admin, I want to host multiple authors on my node, so I can have a friendly online community.
class AdminManagementTests(APITestCase):
    def setUp(self):
        # Create an admin user
        self.admin_user = User.objects.create_superuser(username="admin", password="password123")
        Author.objects.create(
            user=self.admin_user,
            display_name="Admin Author",
            github="https://github.com/admin"
        )

        # Create multiple users and their associated authors
        for i in range(15):
            user = User.objects.create_user(username=f"user{i}", password="password123")
            Author.objects.create(
                user=user,
                display_name=f"Author{i}",
                github=f"https://github.com/user{i}"
            )

        # Log in as administrator user and obtain JWT Token
        response = self.client.post('/api/login/', {
            'username': 'admin',
            'password': 'password123'
        })
        # print(f"Login Response: {response.status_code}, {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK, f"Unexpected response: {response.data}")

        # Dynamically extract access token
        access_token = response.data.get('access_token')
        self.assertIsNotNone(access_token, "Access token not found in response")
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    
    # def test_get_all_authors(self):
    #     # Test to get a list of all authors
    #     response = self.client.get("/api/authors/")

    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data["type"], "authors")
    #     self.assertTrue("authors" in response.data)
    #     self.assertTrue(len(response.data["authors"]) <= 10)  # Assuming pagination returns a maximum of 10 authors per page
    
    # def test_pagination_on_authors_list(self):
    #     # Test paging functionality
    #     response = self.client.get("/api/authors/?page=2")

    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data["type"], "authors")
    #     self.assertTrue(len(response.data["authors"]) > 0)  # The second page should have remaining authors
    
    def test_get_author_detail(self):
        # Test getting details of a single author
        author = Author.objects.first()
        response = self.client.get(f"/api/authors/{author.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], f"/api/authors/{author.id}/")  
        self.assertEqual(response.data["displayName"], author.display_name)
        self.assertEqual(response.data["github"], author.github)
    
    def test_author_not_found(self):
        # Test to get non-existent author
        response = self.client.get("/api/authors/00000000-0000-0000-0000-000000000000/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "No Author matches the given query.")
