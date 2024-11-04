from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from users.models import Author
from posts.models import Comment, Like, Post
import json

#Basic test class, used for login settings
class BaseTestCase(APITestCase):
    def setUp(self):
        self.test_username = 'testuser'
        self.test_password = 'testpassword'
        self.user = User.objects.create_user(username=self.test_username, password=self.test_password)
        self.author = Author.objects.create(user=self.user)

        # Log in and get token
        login_url = '/api/login/'
        response = self.client.post(
            login_url,
            data=json.dumps({
                'username': self.test_username,
                'password': self.test_password
            }),
            content_type='application/json'
        )

        # Check and extract token
        if response.status_code == 200 and 'access_token' in response.json():
            self.token = response.json()['access_token']
            self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        else:
            print("Login failed. Status:", response.status_code, "Content:", response.content)
            self.token = None


class PostDetailsTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.post = Post.objects.create(
            author_id=self.author,
            title='Test Post',
            content_type='text/plain',
            text_content='This is a test post.'
        )
        self.post_url = reverse('post-detail', args=[self.author.id, self.post.id])

    def test_post_details_view(self):
        response = self.client.get(self.post_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Post')


class AuthorPostsViewTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('author-posts', args=[self.author.id])
        self.post1 = Post.objects.create(author_id=self.author, title="Post 1", content_type="text/plain", text_content="Content 1")
        self.post2 = Post.objects.create(author_id=self.author, title="Post 2", content_type="text/plain", text_content="Content 2")

    def test_get_author_posts(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # should return two posts

    def test_create_post(self):
        data = {
            'author_id': self.author.id,
            'title': 'New Post',
            'content_type': 'text/plain',
            'text_content': 'New content',
            'visibility': 'PUBLIC',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 3)


class PostImageViewTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.post = Post.objects.create(
            author_id=self.author,
            title='Post with Image',
            content_type='image',
            text_content='Image content here',
            image_content='test_image.png'
        )
        self.url = reverse('post-image', args=[self.author.id, self.post.id])

    def test_get_post_image(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('image_url', response.data)

class PublicPostsViewTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.user2 = User.objects.create_user(username='publicuser2', password='somethingHardToCrack357')
        self.author2 = Author.objects.create(user=self.user2, display_name='Public User 2', host='http://localhost:8000')

        self.post1 = Post.objects.create(
            author_id=self.author,
            title='Public Post 1',
            content_type='text/plain',
            text_content='This is a public post.',
            visibility='PUBLIC'
        )
        self.post2 = Post.objects.create(
            author_id=self.author2,
            title='Public Post 2',
            content_type='text/plain',
            text_content='This is another public post.',
            visibility='PUBLIC'
        )

    def test_get_public_posts(self):
        response = self.client.get('/api/posts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # should return two posts
