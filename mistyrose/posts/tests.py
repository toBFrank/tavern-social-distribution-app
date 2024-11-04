from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from users.models import Author
from posts.models import Comment, Like, Post
import urllib.parse
import json
import uuid

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

#region Comments Tests
#asked chatGPT to assist with writing test cases for comments endpoints 2024-11-04
class CommentedViewTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.post = Post.objects.create(
            author_id=self.author,
            title='Public Post',
            content_type='text/plain',
            text_content='This is a public post.',
            visibility='PUBLIC'
        )
        self.comment_url = reverse('commented', args=[self.author.id])  
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

    def test_create_comment_invalid_type(self):
        data = {
            'type': 'like',  # Wrong type 
            'author': {
                'type': 'author',
                'id': f'http://localhost/api/authors/{self.author.id}/',
                'host': 'http://localhost',
                'page': f'http://localhost/api/authors/{self.author.id}/',
                'displayName': 'Greg',
            },
            'post': f'http://localhost:8000/authors/{self.author.id}/posts/{self.post.id}/',
            'comment': 'This is a test comment with wrong type.',
            'contentType': 'text/plain'
        }
        response = self.client.post(self.comment_url, data, format='json')
        
        # Check for 400 status 
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Must be 'comment' type", response.data['detail'])

    def test_get_comments_by_author(self):
        # Make a GET request for comments by the author
        response = self.client.get(self.comment_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response_data = response.json()
        self.assertEqual(response_data['type'], 'comments')
        self.assertEqual(response_data['page'], f'http://localhost/api/authors/{self.author.id}')
        self.assertEqual(response_data['id'], f'http://localhost/api/authors/{self.author.id}')

class CommentsByAuthorFQIDViewTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()  

        self.post = Post.objects.create(
            author_id=self.author,
            title="Test Post",
            content_type="text/plain",
            text_content="This is a test post.",
            visibility="PUBLIC"
        )

        self.comment1 = Comment.objects.create(
            author_id=self.author,
            post_id=self.post,
            comment="This is the first comment.",
            content_type="text/plain",
        )

        self.comment2 = Comment.objects.create(
            author_id=self.author,
            post_id=self.post,
            comment="This is the second comment.",
            content_type="text/plain",
        )

        self.fqid_url = f"http://localhost/api/authors/{self.author.id}/"

    def test_get_comments_by_author_success(self):
        # URL encode the FQID for the request
        url = reverse('comments_by_author_fqid', args=[urllib.parse.quote(self.fqid_url)])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["type"], "comments")
        self.assertEqual(response.data["page"], f"{self.author.host}/api/authors/{self.author.id}")
        self.assertEqual(response.data["id"], f"{self.author.host}/api/authors/{self.author.id}")

    def test_get_comments_by_author_invalid_fqid(self):
        # Test with an invalid FQID format - 400
        invalid_fqid = "invalid_fqid"
        url = reverse('comments_by_author_fqid', args=[invalid_fqid])
        response = self.client.get(url)

        # Ensure it returns 400 with appropriate error message
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Invalid FQID format")

    def test_get_comments_by_author_nonexistent_author(self):
        # non existent author - 404
        non_existent_fqid = f"http://localhost/api/authors/{uuid.uuid4()}/"
        url = reverse('comments_by_author_fqid', args=[urllib.parse.quote(non_existent_fqid)])
        response = self.client.get(url)

        # Ensure it returns 404 as author does not exist
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class CommentViewTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()  

        self.post = Post.objects.create(
            author_id=self.author,
            title="Test Post",
            content_type="text/plain",
            text_content="This is a test post.",
            visibility="PUBLIC"
        )

        self.comment = Comment.objects.create(
            author_id=self.author,
            post_id=self.post,
            comment="This is the first comment.",
            content_type="text/plain",
        )
    
    def test_get_comment_success(self):
        url = reverse('comment', args=[self.author.id, self.comment.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["type"], "comment")
        self.assertEqual(response.data["comment"], "This is the first comment.")

    def test_get_comment_not_found(self):
        # get non existent comment - 404
        non_existent_comment_id = f'{uuid.uuid4()}'
        url = reverse('comment', args=[self.author.id, non_existent_comment_id])
        response = self.client.get(url)

        #404 error
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class CommentsViewTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()  

        self.post = Post.objects.create(
            author_id=self.author,
            title="Test Post",
            content_type="text/plain",
            text_content="This is a test post.",
            visibility="PUBLIC"
        )

        self.comment1 = Comment.objects.create(
            author_id=self.author,
            post_id=self.post,
            comment="This is the first comment.",
            content_type="text/plain",
        )

        self.comment2 = Comment.objects.create(
            author_id=self.author,
            post_id=self.post,
            comment="This is the second comment.",
            content_type="text/plain",
        )

        self.url = reverse('get_post_comments', args=[self.author.id, self.post.id])  

    def test_get_comments_on_post_success(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)  
        self.assertEqual(len(response.data['src']), 2)  

    def test_get_comments_on_post_not_found(self):
        non_existent_post_id = f"{uuid.uuid4()}"  
        url = reverse('get_post_comments', args=[self.author.id, non_existent_post_id])  
        response = self.client.get(url)

        # 404 not found response
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class CommentsByFQIDView(BaseTestCase):
    def setUp(self):
        super().setUp()  

        self.post = Post.objects.create(
            author_id=self.author,
            title="Test Post",
            content_type="text/plain",
            text_content="This is a test post.",
            visibility="PUBLIC"
        )

        self.comments_fqid_url = f'http://localhost/api/authors/{self.author.id}/posts/{self.post.id}'

    def test_get_comments_by_fqid_success(self):
        Comment.objects.create(
            author_id=self.author,
            post_id=self.post,
            comment='This is a comment.'
        )

        response = self.client.get(reverse('get_comments_fqid', args=[self.comments_fqid_url]))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["type"], "comments")

class CommentRemoteByFQIDViewTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()  

        self.post = Post.objects.create(
            author_id=self.author,
            title="Test Post",
            content_type="text/plain",
            text_content="This is a test post.",
            visibility="PUBLIC"
        )

        self.comment = Comment.objects.create(
            author_id=self.author,
            post_id=self.post,
            comment="This is the first comment.",
            content_type="text/plain",
        )

        self.author.host = 'http://localhost'
        self.author.save()
        self.comment_fqid = f'http://localhost/api/authors/{self.author.id}/commented/{self.comment.id}'

    def test_get_comment_by_fqid_success(self):
        response = self.client.get(reverse('get_remote_comment_fqid', args=[self.author.id, self.post.id, self.comment_fqid]))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], f'http://localhost/api/authors/{self.author.id}/commented/{self.comment.id}')


class CommentByFQIDView(BaseTestCase):
    def setUp(self):
        super().setUp()  

        self.post = Post.objects.create(
            author_id=self.author,
            title="Test Post",
            content_type="text/plain",
            text_content="This is a test post.",
            visibility="PUBLIC"
        )

        self.comment = Comment.objects.create(
            author_id=self.author,
            post_id=self.post,
            comment="This is the first comment.",
            content_type="text/plain",
        )

        self.author.host = 'http://localhost'
        self.author.save()
        self.comment_fqid = f'http://localhost/api/authors/{self.author.id}/commented/{self.comment.id}'

    def test_get_comment_by_fqid_success(self):
        response = self.client.get(reverse('comment_fqid', args=[self.comment_fqid]))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], f'http://localhost/api/authors/{self.author.id}/commented/{self.comment.id}')

#endregion