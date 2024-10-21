from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from users.models import Author
from posts.models import Comment, Like, Post
import uuid

# Create your tests here.

class PostDetailsTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='postuser', password='somethingHardToCrack357')
        self.author = Author.objects.create(user=self.user, display_name='Post User', host='http://localhost:8000')
        
        response = self.client.post('/api/users/login/', {'username': 'postuser', 'password': 'somethingHardToCrack357'}, format='json')
        self.token = response.data['access_token']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        
        self.post = Post.objects.create(
            author_id=self.author,
            title='Test Post',
            content_type='text/plain',
            text_content='This is a test post.'
        )
        self.post_url = reverse('post-detail', args=[self.author.id, self.post.id])

    def test_post_details_view(self):
        """
        Get existing post by author ID and post ID.
        """
        response = self.client.get(self.post_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Post')

    def test_post_not_found(self):
        """
        Get non-existing post by author ID and post ID.
        """
        random_uuid = uuid.uuid4()
        url = reverse('post-detail', args=[self.author.id, random_uuid])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_update(self):
        """
        Update existing post.
        """
        self.client.login(username='postuser', password='somethingHardToCrack357')
        data = {
          'author_id': self.author.id,
          'title': 'Updated Test Post', 
          'text_content': 'Updated content',
          'content_type': 'text/plain',
          'visibility': 'PUBLIC',
          }
        response = self.client.put(self.post_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Updated Test Post')

    def test_post_delete(self):
        """
        (HARD) delete existing post.
        (Removing post from the db)
        """
        self.client.login(username='postuser', password='somethingHardToCrack357')
        response = self.client.delete(self.post_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())
        
class AuthorPostsViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='authoruser', password='somethingHardToCrack357')
        self.author = Author.objects.create(user=self.user, display_name='Author User', host='http://localhost:8000')
        
        response = self.client.post('/api/users/login/', {'username': 'authoruser', 'password': 'somethingHardToCrack357'}, format='json')
        self.token = response.data['access_token']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        
        self.url = reverse('author-posts', args=[self.author.id])
        self.post1 = Post.objects.create(author_id=self.author, title="Post 1", content_type="text/plain", text_content="Content 1")
        self.post2 = Post.objects.create(author_id=self.author, title="Post 2", content_type="text/plain", text_content="Content 2")

    def test_get_author_posts(self):
        """
        Get all posts of author.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Should return 2 posts

    def test_create_post(self):
        """
        Create post for author.
        """
        self.client.login(username='authoruser', password='somethingHardToCrack357')
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

class PostImageViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='imageuser', password='somethingHardToCrack357')
        self.author = Author.objects.create(user=self.user, display_name='Image User', host='http://localhost:8000')
        
        response = self.client.post('/api/users/login/', {'username': 'imageuser', 'password': 'somethingHardToCrack357'}, format='json')
        self.token = response.data['access_token']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        
        self.post = Post.objects.create(
            author_id=self.author,
            title='Post with Image',
            content_type='image',
            text_content='Image content here',
            image_content='test_image.png'
        )
        self.url = reverse('post-image', args=[self.author.id, self.post.id])

    def test_get_post_image(self):
        """
        Get post image.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('image_url', response.data)

    def test_get_post_image_no_image(self):
        """
        Get post of non-existing image.
        """
        post = Post.objects.create(
            author_id=self.author,
            title='Post without Image',
            content_type='text/plain',
            text_content='This post has no image.'
        )
        url = reverse('post-image', args=[self.author.id, post.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
class CommentedViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='commentuser', password='somethingHardToCrack357')
        self.author = Author.objects.create(user=self.user, display_name='Comment User', host='http://localhost:8000')
        self.post = Post.objects.create(
            author_id=self.author,
            title='Test Post meow',
            content_type='text/plain',
            text_content='This is a test post uwu for comments meow.'
        )
        
        response = self.client.post('/api/users/login/', {'username': 'commentuser', 'password': 'somethingHardToCrack357'}, format='json')
        self.token = response.data['access_token']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        
        self.comment_url = reverse('commented', args=[self.author.id])
        self.comments_list_url = reverse('post_comments', args=[self.author.id, self.post.id])

    def test_create_comment_success(self):
        """
        Create comment on post.
        """
        self.client.login(username='commentuser', password='somethingHardToCrack357')
        data = {
            'type': 'comment',
            'post': f'http://localhost:8000/posts/{self.post.id}',
            'comment': 'This is a test comment (you know, for testing).',
        }
        response = self.client.post(self.comment_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.first().comment, 'This is a test comment (you know, for testing).')

    def test_create_comment_invalid_type(self):
        """
        Create comment with wrong type.
        """
        self.client.login(username='commentuser', password='somethingHardToCrack357')
        data = {
            'type': 'like',
            'post': f'http://localhost:8000/posts/{self.post.id}',
            'comment': 'This is a test comment.',
        }
        response = self.client.post(self.comment_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)

    def test_get_comments_success(self):
        """
        Get comments on post
        """
        Comment.objects.create(
            post_id=self.post,
            author_id=self.author,
            comment="MEOW comment"
        )
        response = self.client.get(self.comments_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['comment'], 'MEOW comment')

    def test_get_comments_no_post_found(self):
        """
        get comments on non-existing post.
        """
        random_uuid = uuid.uuid4()
        url = reverse('post_comments', args=[self.author.id, random_uuid])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class LikedViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='likeruser', password='somethingHardToCrack357')
        self.author = Author.objects.create(user=self.user, display_name='Liker User', host='http://localhost:8000')
        
        response = self.client.post('/api/users/login/', {'username': 'likeruser', 'password': 'somethingHardToCrack357'}, format='json')
        self.token = response.data['access_token']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        
        # Create a post to be liked
        self.post = Post.objects.create(
            author_id=self.author,
            title='Likeable Post',
            content_type='text/plain',
            text_content='This post is likeable.'
        )
        self.url = reverse('liked', args=[self.author.id])

    def test_like_post(self):
        """
        Like post.
        """
        self.client.login(username='likeruser', password='somethingHardToCrack357')
        data = {'type': 'like', 'object': f'http://localhost:8000/posts/{self.post.id}'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Like.objects.count(), 1)

    def test_like_invalid_object(self):
        """
        Like non-existing object.
        """
        self.client.login(username='likeruser', password='somethingHardToCrack357')
        data = {'type': 'like', 'object': 'invalid-url'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
class PublicPostsViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='publicuser', password='somethingHardToCrack357')
        self.author = Author.objects.create(user=self.user, display_name='Public User', host='http://localhost:8000')
        
        response = self.client.post('/api/users/login/', {'username': 'publicuser', 'password': 'somethingHardToCrack357'}, format='json')
        self.token = response.data['access_token']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        
        
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
        
        self.friends_post_3 = Post.objects.create(
            author_id=self.author,
            title='Friends Post',
            content_type='text/plain',
            text_content='This is a friends post.',
            visibility='FRIENDS'
        )
        
    def test_get_public_posts(self):
        """
        Get all public posts.
        """
        response = self.client.get('/api/posts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Should return 2 public posts (1 is friends only)