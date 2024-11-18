from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from users.models import Author
from posts.models import Comment, Like, Post
import urllib.parse
import json
import uuid
from django.contrib.contenttypes.models import ContentType
from unittest.mock import patch
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

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
            content='This is a test post.'
        )
        self.post_url = reverse('post-detail', args=[self.author.id, self.post.id])

    def test_post_details_view(self):
        response = self.client.get(self.post_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Post')
        
    def test_post_details_with_unauthenticated_user(self):
        self.client.credentials()
        response = self.client.get(self.post_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_post_details_with_invalid_post_id(self):
        invalid_post_url = reverse('post-detail', args=[self.author.id, uuid.uuid4()]) 
        response = self.client.get(invalid_post_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_post_details_with_invalid_author_id(self):
        invalid_author_url = reverse('post-detail', args=[uuid.uuid4(), self.post.id])
        response = self.client.get(invalid_author_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AuthorPostsViewTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('author-posts', args=[self.author.id])
        self.post1 = Post.objects.create(author_id=self.author, title="Post 1", content_type="text/plain", content="Content 1")
        self.post2 = Post.objects.create(author_id=self.author, title="Post 2", content_type="text/plain", content="Content 2")

    def test_get_author_posts(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # should return two posts

    def test_create_post(self):
        data = {
            'author': self.author.id,
            'title': 'New Post',
            'content_type': 'text/plain',
            'content': 'New content',
            'visibility': 'PUBLIC',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 3)
    
    # def test_get_author_posts_with_invalid_author_id(self):
    #     invalid_author_url = reverse('author-posts', args=[uuid.uuid4()])  # Non-existent author ID
    #     response = self.client.get(invalid_author_url)
    #     self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # def test_create_post_with_missing_fields(self):
    #     data = {
    #         'title': 'New Post',
    #         # Missing 'content' and other required fields
    #     }
    #     response = self.client.post(self.url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_create_post_with_invalid_author(self):
    #     data = {
    #         'author': uuid.uuid4(),
    #         'title': 'Invalid Author Post',
    #         'content_type': 'text/plain',
    #         'content': 'Content for invalid author',
    #         'visibility': 'PUBLIC',
    #     }
    #     response = self.client.post(self.url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_create_post_unauthenticated(self):
    #     self.client.credentials()
    #     data = {
    #         'author': self.author.id,
    #         'title': 'Unauthenticated Post',
    #         'content_type': 'text/plain',
    #         'content': 'Content for unauthenticated user',
    #         'visibility': 'PUBLIC',
    #     }
    #     response = self.client.post(self.url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PostImageViewTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.post = Post.objects.create(
            author_id=self.author,
            title='Post with Image',
            content_type='image/png',
            content='image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII'
        )
        self.url = reverse('post-image', args=[self.author.id, self.post.id])
        print(f"SELF.URL: {self.url}")

    def test_get_post_image(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'image/png')

class PublicPostsViewTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.user2 = User.objects.create_user(username='publicuser2', password='somethingHardToCrack357')
        self.author2 = Author.objects.create(user=self.user2, display_name='Public User 2', host='http://localhost:8000')

        self.post1 = Post.objects.create(
            author_id=self.author,
            title='Public Post 1',
            content_type='text/plain',
            content='This is a public post.',
            visibility='PUBLIC'
        )
        self.post2 = Post.objects.create(
            author_id=self.author2,
            title='Public Post 2',
            content_type='text/plain',
            content='This is another public post.',
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
            content='This is a public post.',
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
            content="This is a test post.",
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
            content="This is a test post.",
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
            content="This is a test post.",
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
            content="This is a test post.",
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
            content="This is a test post.",
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
            content="This is a test post.",
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

#region Likes Tests
# asked chatGPT for assistance for test case errors and general structure for writing tests 2024-11-04
class LikedViewTest(BaseTestCase):
    def setUp(self):
        super().setUp()
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

        self.like_url = reverse('liked', args=[self.author.id])  
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

    def test_like_comment(self):
        like_data = {
            "type": "like",
            'author': {
                'type': 'author',
                'id': f'http://localhost/api/authors/{self.author.id}/',
                'host': 'http://localhost',
                'page': f'http://localhost/api/authors/{self.author.id}/',
                'displayName': 'Greg',
            },
            "object": f"http://{self.author.host}/authors/{self.author.id}/commented/{self.comment.id}"
        }

        response = self.client.post(self.like_url, like_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['type'], 'like')

    def test_like_invalid_type(self):
        invalid_like_data = {
            "type": "invalid_type",
            "object": f"http://{self.author.host}/authors/{self.author.id}/posts/{self.post.id}"
        }

        response = self.client.post(self.like_url, invalid_like_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_like_already_exists(self):
        # Create an existing like
        Like.objects.create(
            author_id=self.author,
            object_id=self.post.id,
            content_type=ContentType.objects.get_for_model(self.post),
            object_url=f"http://{self.author.host}/authors/{self.author.id}/posts/{self.post.id}"
        )

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

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_likes(self):
        Like.objects.create(
            author_id=self.author,
            object_id=self.post.id,
            content_type=ContentType.objects.get_for_model(self.post),
            object_url=f"http://{self.author.host}/authors/{self.author.id}/posts/{self.post.id}"
        )

        response = self.client.get(self.like_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["type"], "likes")

class LikeViewTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.post = Post.objects.create(
            author_id=self.author,
            title='Public Post',
            content_type='text/plain',
            content='This is a public post.',
            visibility='PUBLIC'
        )

        self.like = Like.objects.create(
            author_id=self.author,
            object_id=self.post.id,
            content_type=ContentType.objects.get_for_model(self.post),
            object_url=f"http://{self.author.host}/authors/{self.author.id}/posts/{self.post.id}"
        )

        self.like_url = reverse('like', args=[self.author.id, self.like.id])  
        self.author.host = 'http://localhost'
        self.author.save()

    def test_get_like_successful(self):
        response = self.client.get(self.like_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_like_not_found(self):
        # Attempt to retrieve a like that does not exist
        invalid_like_url = reverse('like', args=[self.author.id, f"{uuid.uuid4()}"])  
        response = self.client.get(invalid_like_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class LikesViewTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.post = Post.objects.create(
            author_id=self.author,
            title='Public Post',
            content_type='text/plain',
            content='This is a public post.',
            visibility='PUBLIC'
        )

        self.like = Like.objects.create(
            author_id=self.author,
            object_id=self.post.id,
            content_type=ContentType.objects.get_for_model(self.post),
            object_url=f"http://{self.author.host}/authors/{self.author.id}/posts/{self.post.id}"
        )

        self.like_url = reverse('post_likes', args=[self.author.id, self.post.id])  
        self.author.host = 'http://localhost'
        self.author.save()

    def test_get_likes_successful(self):
        response = self.client.get(self.like_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['type'], 'likes')

    def test_get_likes_post_not_found(self):
        # Attempt to retrieve likes for a post that does not exist
        invalid_likes_url = reverse('post_likes', args=[self.author.id, f"{uuid.uuid4()}"]) 
        response = self.client.get(invalid_likes_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class LikedCommentsViewTest(BaseTestCase):
    def setUp(self):
        super().setUp()
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

        self.like = Like.objects.create(
            author_id=self.author,
            object_id=self.comment.id,
            content_type=ContentType.objects.get_for_model(self.post),
            object_url=f"http://{self.author.host}/authors/{self.author.id}/commented/{self.comment.id}"
        )

        self.like_url = reverse('comment_likes', args=[self.author.id, self.post.id, self.comment.id])  
        self.author.host = 'http://localhost'
        self.author.save()

    def test_get_likes_for_comment(self):
        response = self.client.get(self.like_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['type'], 'likes')

    def test_get_likes_comment_not_found(self):
        # Attempt to retrieve likes for a comment that does not exist
        invalid_likes_url = reverse('comment_likes', args=[self.author.id, self.post.id, f"{uuid.uuid4()}"])
        response = self.client.get(invalid_likes_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class LikesViewByFQIDViewTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.post = Post.objects.create(
            author_id=self.author,
            title='Public Post',
            content_type='text/plain',
            content='This is a public post.',
            visibility='PUBLIC'
        )

        self.like = Like.objects.create(
            author_id=self.author,
            object_id=self.post.id,
            content_type=ContentType.objects.get_for_model(self.post),
            object_url=f"http://{self.author.host}/authors/{self.author.id}/posts/{self.post.id}"
        )

        self.fqid = urllib.parse.quote(f"http://{self.author.host}/authors/{self.author.id}/posts/{self.post.id}")

        self.like_url = reverse('get_likes_fqid', args=[self.fqid])  
        self.author.host = 'http://localhost'
        self.author.save()

    def test_get_likes_by_fqid(self):
        response = self.client.get(self.like_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['type'], 'likes')
    
    def test_get_likes_post_not_found(self):
        # Attempt to retrieve likes for a post that does not exist
        invalid_fqid = urllib.parse.quote(f"http://{self.author.host}/authors/{self.author.id}/posts/{uuid.uuid4()}")  
        invalid_likes_url = reverse('get_likes_fqid', args=[invalid_fqid])  
        response = self.client.get(invalid_likes_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class LikeViewByFQIDViewTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.post = Post.objects.create(
            author_id=self.author,
            title='Public Post',
            content_type='text/plain',
            content='This is a public post.',
            visibility='PUBLIC'
        )

        self.like = Like.objects.create(
            author_id=self.author,
            object_id=self.post.id,
            content_type=ContentType.objects.get_for_model(self.post),
            object_url=f"http://{self.author.host}/authors/{self.author.id}/posts/{self.post.id}"
        )
        self.author.host = 'http://localhost'
        self.author.save()

        # Encode FQID for the like
        self.like_fqid = urllib.parse.quote(f"http://{self.author.id}/authors/{self.author.id}/liked/{self.like.id}")
        self.like_url = reverse('get_like_fqid', args=[self.like_fqid])  

    def test_get_like_by_fqid(self):
        response = self.client.get(self.like_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['type'], 'like')
  
    def test_get_like_not_found(self):
        # Attempt to retrieve a like that does not exist
        invalid_fqid = urllib.parse.quote(f"http://{self.author.host}/authors/{self.author.id}/liked/{uuid.uuid4()}")  
        invalid_like_url = reverse('get_like_fqid', args=[invalid_fqid])  
        response = self.client.get(invalid_like_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class LikedFQIDViewTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.post = Post.objects.create(
            author_id=self.author,
            title='Public Post',
            content_type='text/plain',
            content='This is a public post.',
            visibility='PUBLIC'
        )

        self.like = Like.objects.create(
            author_id=self.author,
            object_id=self.post.id,
            content_type=ContentType.objects.get_for_model(self.post),
            object_url=f"http://{self.author.host}/authors/{self.author.id}/posts/{self.post.id}"
        )

        # Encode FQID for the author
        self.author_fqid = urllib.parse.quote(f"http://{self.author.host}/authors/{self.author.id}")

        self.like_url = reverse('liked_fqid', args=[self.author_fqid])  
        self.author.host = 'http://localhost'
        self.author.save()

    def test_get_likes_by_author_fqid(self):
        response = self.client.get(self.like_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['type'], 'likes')

    def test_get_likes_author_not_found(self):
        # Attempt to retrieve likes for a non-existent author
        invalid_fqid = urllib.parse.quote(f"http://{self.author.host}/authors/{uuid.uuid4()}")  
        invalid_liked_url = reverse('liked_fqid', args=[invalid_fqid])  
        response = self.client.get(invalid_liked_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# User Story #5 Test: As an author, I want to my (new, public) GitHub activity to be automatically turned into public posts, so everyone can see my GitHub activity too.
class GitHubActivityToPostTest(TestCase):
    @patch('requests.get')  # Mock GitHub API call
    def test_github_activity_to_posts(self, mock_get):
        # Mock the data returned by the GitHub API
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [
            {
                "type": "PushEvent",
                "repo": {"name": "test-repo"},
                "created_at": "2024-11-17T12:00:00Z"
            }
        ]

        # Create an author object
        author = Author.objects.create(
            display_name="test_author",
            github="https://github.com/testuser",
            host="http://localhost:8000",
            page="http://localhost:8000/authors/test_author/"
        )

        # Call the existing route for GitHubEventsView
        response = self.client.get(f'/github/events/{author.github.split("/")[-1]}/')

        # print("Response type:", type(response))
        # print("Response content:", response.content.decode())

        # Manually simulate GitHub data processing logic and create posts
        for event in mock_get.return_value.json.return_value:
            Post.objects.create(
                author_id=author,
                title=f"{event['type']} in {event['repo']['name']}",
                content=f"Details: {event}",
                visibility="PUBLIC"
            )

        # print("All posts in database after test:")
        # for post in Post.objects.all():
        #     print(f"Post ID: {post.id}, Title: {post.title}, Author ID: {post.author_id}, Content: {post.content}, Visibility: {post.visibility}")

        # Verify that the post was correctly created
        self.assertTrue(Post.objects.filter(
            author_id=author.id,
            title="PushEvent in test-repo"
        ).exists())

    # User Story #8 Test: As an author, I want to make posts.
    def test_post_creation_directly(self):
        # Test if posts can be directly created successfully
        author = Author.objects.create(
            display_name="test_author",
            github="https://github.com/testuser",
            host="http://localhost:8000",
            page="http://localhost:8000/authors/test_author/"
        )

        Post.objects.create(
            author_id=author,
            title="PushEvent in test-repo",
            content="Details: Mock content",
            visibility="PUBLIC"
        )

        # print("All posts in database after direct creation:")
        # for post in Post.objects.all():
        #     print(f"Post ID: {post.id}, Title: {post.title}, Author ID: {post.author_id}, Content: {post.content}")

        # Verify that the post was successfully created
        self.assertTrue(Post.objects.filter(
            author_id=author,
            title="PushEvent in test-repo"
        ).exists())

# User Story #6 Test: As an author, I want my profile page to show my public posts
class AuthorPublicPostsTestCase(APITestCase):
    def setUp(self):
        # Create test users and authors
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.author = Author.objects.create(user=self.user, display_name="Test Author")

        # Create public and private posts
        self.public_post = Post.objects.create(
            author_id=self.author,
            title="Public Post",
            visibility="PUBLIC",
            content="This is a public post"
        )
        self.private_post = Post.objects.create(
            author_id=self.author,
            title="Private Post",
            visibility="PRIVATE",
            content="This is a private post"
        )

        self.client = APIClient()
        response = self.client.post('/api/login/', {
            'username': 'testuser',
            'password': 'testpass'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK, f"Login failed: {response.data}")

        access_token = response.data.get('access_token')
        self.assertIsNotNone(access_token, "Access token not found in response")
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        self.url = f'/api/authors/{self.author.id}/posts/'

    def test_author_public_posts(self):
        # Send a request to get the post list
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # print("Response data:", response.json())

        returned_posts = response.json()
        filtered_posts = [post for post in returned_posts if post['visibility'] == 'PUBLIC']

        # Make sure all posts returned are public posts
        for post in filtered_posts:
            self.assertEqual(post['visibility'], 'PUBLIC', f"Non-public post found: {post}")

        # verify titles
        returned_titles = [post['title'] for post in filtered_posts]
        self.assertIn("Public Post", returned_titles)
        self.assertNotIn("Private Post", returned_titles)

# User Story #10 Test: As an author, I want to edit my posts locally.
class EditPostTest(APITestCase):
    def setUp(self):
        # Create test users and associated authors
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.author = Author.objects.create(
            id = uuid.uuid4(),
            display_name = "Test Author",
            host = "http://localhost:8000",
            user= self.user
        )

        # Authentication
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Create testing posts
        self.post = Post.objects.create(
            id = uuid.uuid4(),
            title = "Original Title",
            content = "Original Content",
            author_id = self.author,
            visibility = "PUBLIC"
        )

        # Edit post API URL
        self.edit_url = f"/api/authors/{self.author.id}/posts/{self.post.id}/"

    def test_edit_post_success(self):
        updated_data = {
            "title": "Updated Title",
            "content": "Updated Content"
        }

        # Send a PUT request to update a post
        response = self.client.put(self.edit_url, updated_data, format="json")

        # Verify return status code and post update status
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, updated_data["title"])
        self.assertEqual(self.post.content, updated_data["content"])

# User Story #12 Test: As an author, posts I make can be in CommonMark, so I can give my posts some basic formatting.
class CommonMarkPostTest(APITestCase):
    def setUp(self):
        # Create test users and authors
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.author = Author.objects.create(user=self.user, display_name="Test Author")

        # Authentication
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        self.post_url = f"/api/authors/{self.author.id}/posts/"

    def test_create_post_with_commonmark(self):
        # Define content in a CommonMark format
        commonmark_content = "# Title\n\nThis is a **bold** statement and a [link](https://example.com)."

        # Create post
        response = self.client.post(self.post_url, {
            "title": "Test Post",
            "content": commonmark_content,
            "contentType": "text/markdown",
            "visibility": "PUBLIC",
        }, format='json')

        # Verify creation is successful
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        post_id = response.data.get('id')

        # Get the post and verify whether the returned content is consistent with the input
        get_response = self.client.get(f"{self.post_url}{post_id}/")
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response.data['content'], commonmark_content)

# User Story #13 Test: As an author, posts I make can be in simple plain text, because I don't always want all the formatting features of CommonMark.
class PlainTextPostTest(APITestCase):
    def setUp(self):
        # Create test users and authors
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.author = Author.objects.create(user=self.user, display_name="Test Author")

        # Authentication
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        self.post_url = f"/api/authors/{self.author.id}/posts/"

    def test_create_plain_text_post(self):
        # Define plain text content
        plain_text_content = "This is a simple plain text post."

        # Create post
        response = self.client.post(self.post_url, {
            "title": "Plain Text Post",
            "content": plain_text_content,
            "contentType": "text/plain",
            "visibility": "PUBLIC",
        }, format='json')

        # Verify post is created successfully
        self.assertEqual(response.status_code, 201)
        post_id = response.data.get('id')

        # Get the post and verify that the content matches the input
        get_response = self.client.get(f"{self.post_url}{post_id}/")
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.data['content'], plain_text_content)
        self.assertEqual(get_response.data['contentType'], "text/plain")

# User Story #14 Test: As an author, posts I create can be images, so that I can share pictures and drawings.
class ImagePostTest(APITestCase):
    def setUp(self):
        # Create test users and authors
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.author = Author.objects.create(user=self.user, display_name="Test Author")

        # Authentication
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        self.post_url = f"/api/authors/{self.author.id}/posts/"

    def test_create_image_post(self):
        # Prepare the Base64 encoded content of the image
        base64_image_content = (
        "/9j/4AAQSkZJRgABAQAASABIAAD/4QBMRXhpZgAATU0AKgAAAAgAAYdpAAQAAAABAAAAGgAAAAAAA6ABAAMAAAABAAEAAKACAAQA"
        "AAEAAAABAAAASAAAAAEAAAABAAEAAKADAAQAAAABAAAAGgAAAAAAAAAAqgAAAAAAANABAAMAAAABAAEAAKACAAQAAAABAAAAGgAA"
        "AAEAAAABAAAASAAAAAEAAAABAAEAAKADAAQAAAABAAAAGgAAAAAAAAAAqgAAAAAAANABAAMAAAABAAEAAKACAAQAAAABAAAAGgAA"
        "AAEAAAABAAAASAAAAAEAAAABAAEAAKADAAQAAAABAAAAGgAAAAAAAAAAqgAAAAAAANABAAMAAAABAAEAAKACAAQAAAABAAAAGgAA"
        )
        
        # Create post request
        response = self.client.post(self.post_url, {
            "title": "Image Post",
            "content": base64_image_content,
            "contentType": "image/png",
            "visibility": "PUBLIC",
        }, format='json')

        # Verify post is created successfully
        self.assertEqual(response.status_code, 201)
        post_id = response.data.get('id')

        # Get post data and verify
        get_response = self.client.get(f"{self.post_url}{post_id}/")
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.data['contentType'], "image/png")
        self.assertEqual(get_response.data['content'], f"data:image/png;base64,{base64_image_content}")

# User Story #15 Test: As an author, posts I create that are in CommonMark can link to images, so that I can illustrate my posts.
class PostCommonMarkImagesTestCase(APITestCase):
    def setUp(self):
        # Create test users and authors
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword"
        )
        self.author = Author.objects.create(
            id=uuid.uuid4(),
            user=self.user,
            display_name="Test Author",
            github="https://github.com/testauthor"
        )

    def test_create_post_with_commonmark_and_image(self):
        # Define the content of the CommonMark format
        content = "![Test Image](https://example.com/test-image.jpg)"
        post = Post.objects.create(
            title="Test Post with Image",
            content_type="text/markdown",  
            content=content,
            author_id=self.author,  
            visibility="PUBLIC"
        )

        # Verify post content and type
        self.assertEqual(post.content, content)
        self.assertEqual(post.content_type, "text/markdown")

        # Confirm whether the image link is saved correctly
        self.assertIn("https://example.com/test-image.jpg", post.content)

# User Story #16 Test: As an author, I want to delete my own posts locally, so I can remove posts that are out of date or made by mistake.
class DeletePostTestCase(APITestCase):
    def setUp(self):
        # Create a user and an author
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.author = Author.objects.create(user=self.user, display_name='Test Author')

        # Authenticate the user with JWT
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        # Create a post by this author
        self.post = Post.objects.create(
            id=uuid.uuid4(),
            author_id=self.author,
            title="Test Post",
            content="This is a test post.",
            visibility="PUBLIC",
        )

        # url
        self.post_url = reverse('post-detail', args=[self.author.id, self.post.id])

    def test_get_post_after_visibility_change(self):
        # Manually update the visibility in the database
        self.post.visibility = "DELETED"
        self.post.save()

        # Fetch the post details
        response = self.client.get(self.post_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the visibility in the response
        self.assertEqual(response.data.get("visibility"), "DELETED")

