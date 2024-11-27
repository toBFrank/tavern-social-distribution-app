import base64
import re
import uuid
from django.shortcuts import render
import requests

from users.utils import is_fqid
from .utils import get_remote_friends, post_to_remote_inboxes, get_remote_followers_you
from users.models import Author
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from .models import Post, Comment, Like
from .serializers import PostSerializer, CommentSerializer, LikeSerializer
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from .models import Post
from users.models import Author, Follows  
from node.models import Node
from .pagination import LikesPagination, CustomPostsPagination
import urllib.parse  # asked chatGPT how to decode the URL-encoded FQID 2024-11-02
from django.http import FileResponse
import requests
from requests.auth import HTTPBasicAuth #basic auth
from django.db import transaction #transaction requests so that if something happens in the middle, it'll be rolled back
from urllib.parse import unquote, urlparse
from node.authentication import NodeAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication  
from rest_framework.generics import ListAPIView  
from rest_framework.pagination import PageNumberPagination



def handle_remote_inboxes(post, request, object_data, author):
    '''
    post - the post model object that is being posted, commented, or liked
    request - the api request 
    object_data - the post, comment, data to send to the remote inbox
    author - the author who is sending the post
    ''' 
    #author is the one sending the request out
    #remote_authors = get_remote_authors(request) 

    if object_data['type'] == 'post':
        #format id
        object_data['id'] = f"{author.host.rstrip('/')}/authors/{author.id}/posts/{post.id}/"

    print(f"WE ARE SENDING THIS {object_data}")

                
    if post.visibility == 'PUBLIC' or post.visibility == 'DELETED':
        # send to remote follower inboxes if public post
        remote_followers = get_remote_followers_you(author)
        post_to_remote_inboxes(request, remote_followers, object_data)
        
    elif post.visibility == 'FRIENDS':
        # send only to remote friends inboxes if friends post
        remote_friends = get_remote_friends(author)
        post_to_remote_inboxes(request, remote_friends, object_data)

    elif post.visibility == 'UNLISTED':
        # Send to remote followers
        remote_followers = get_remote_followers_you(author)
        post_to_remote_inboxes(request, remote_followers, object_data)


#region Post Views

class PostDetailsView(APIView):
    """
    Retrieve, update or delete a post instance by author ID & post ID.
    """
    
    def get(self, request, author_serial, post_serial):
        """
        Retrieve a post instance by author ID & post ID.
        """
        try:
            # check if author_serial is a URL (FQID) or a uuid (SERIAL)
            # check if post_serial is a URL (FQID) or a uuid (SERIAL)
            if is_fqid(author_serial):
                author_serial = urllib.parse.unquote(author_serial)
                if not author_serial.endswith("/"):
                    author_serial += "/"
                author_serial = Author.objects.get(url=author_serial).id
            if is_fqid(post_serial):
                post_serial = urllib.parse.unquote(post_serial)
                if not post_serial.endswith("/"):
                    post_serial += "/"
                post_serial = Post.objects.get(url=post_serial).id
            post = Post.objects.get(id=post_serial, author_id=author_serial)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = PostSerializer(post)
        return Response(serializer.data)
      
    def put(self, request, author_serial, post_serial):
        """
        Update a post instance by author ID & post ID.
        """
        with transaction.atomic():
            print("In PostDetailsView - PUT")
            try:
                # check if author_serial is a URL (FQID) or a uuid (SERIAL)
                # check if post_serial is a URL (FQID) or a uuid (SERIAL)
                if is_fqid(author_serial):
                    author_serial = urllib.parse.unquote(author_serial)
                    if not author_serial.endswith("/"):
                        author_serial += "/"
                    author_serial = Author.objects.get(url=author_serial).id
                if is_fqid(post_serial):
                    post_serial = urllib.parse.unquote(post_serial)
                    if not post_serial.endswith("/"):
                        post_serial += "/"
                    post_serial = Post.objects.get(url=post_serial).id
            except:
                print("In PostDetailsView - PUT - You didn't give me a valid FQID or SERIAL, babe.")
                return Response({"error": "PostDetailsView - PUT - You didn't give me a valid FQID or SERIAL, babe."}, status=status.HTTP_400_BAD_REQUEST)
            
            # get the post instance
            try:
                print(f"author_serial: {author_serial}, post_serial: {post_serial}")
                old_post = Post.objects.get(id=post_serial, author_id=author_serial)
            except Post.DoesNotExist:
                return Response({"error": f"What post? {post_serial} not found, babe."}, status=status.HTTP_404_NOT_FOUND)
            
            # get the author instance
            try:
                author = Author.objects.get(id=author_serial)
            except Author.DoesNotExist:
                return Response({"error": f"Who dat? {author_serial} not found, babe."}, status=status.HTTP_404_NOT_FOUND)
            
            # serialize the updated post
            serializer = PostSerializer(old_post, data=request.data)
            # update post locally
            if serializer.is_valid():
                updated_post = serializer.save(author_id=author)
                updated_post_data = PostSerializer(updated_post).data
            else:
                return Response({"error": f"Couldn't update the post locally or remotely, babe. Your request was messed up: {serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)
            
            # get remote authors and send post to remote inboxes
            try:
                handle_remote_inboxes(updated_post, request, updated_post_data, author)

                # remote_authors = get_remote_authors(request)
                
                # if updated_post.visibility == 'PUBLIC' or updated_post.visibility == 'DELETED':
                #     # send to all remote inboxes if public post
                #     post_to_remote_inboxes(request, remote_authors, updated_post_data)
                    
                # elif updated_post.visibility == 'FRIENDS':
                #     # send only to remote friends if friends post
                #     remote_friends = get_remote_friends(author)
                #     post_to_remote_inboxes(request, remote_friends, updated_post_data)   
                         
            except Exception as e:
                return Response(
                    {"error": f"Couldn't send the updated post to remote inboxes, babe. {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        

class PostDetailsByFqidView(APIView):
    """
    Retrieve post by Fully Qualified ID (URL + ID).
    """
    # permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get(self, request, post_fqid):
        try:
            post = Post.objects.get(url=post_fqid)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = PostSerializer(post)
        return Response(serializer.data)
    

class AuthorPostsView(APIView):
    """
    List all posts by an author, or create a new post for the author.
    """
    pagination_class = CustomPostsPagination

    def get(self, request, author_serial):
        paginator = self.pagination_class()

        try:
            # check if author_serial is a URL (FQID) or a uuid (SERIAL)
            if is_fqid(author_serial):
                author_serial = urllib.parse.unquote(author_serial)
                if not author_serial.endswith("/"):
                    author_serial += "/"
                author_serial = Author.objects.get(url=author_serial).id
        except:
            return Response({"error": "AuthorPostsView - GET - You didn't give me a valid FQID or SERIAL, babe."}, status=status.HTTP_400_BAD_REQUEST)
        
        posts = Post.objects.filter(author_id=author_serial)

        # paginate request
        paginated_posts = paginator.paginate_queryset(posts, request, view=self)
        serializer = PostSerializer(paginated_posts, many=True)

        return Response(paginator.get_paginated_response(serializer.data), status=status.HTTP_200_OK)


    def post(self, request, author_serial):
        '''
        create post locally and send to remote followers inboxes if public, and remote friends if friends only post
        '''
        with transaction.atomic(): #a lot of datbase operations, better to do transaction so that if something fails, we can rollback instead of half updates
            try:
                # check if author_serial is a URL (FQID) or a uuid (SERIAL)
                if is_fqid(author_serial):
                    author_serial = urllib.parse.unquote(author_serial)
                    if not author_serial.endswith("/"):
                        author_serial += "/"
                    author_serial = Author.objects.get(url=author_serial).id
            except:
                return Response({"error": "AuthorPostsView - POST - You didn't give me a valid FQID or SERIAL, babe."}, status=status.HTTP_400_BAD_REQUEST)
            
            # create post locally first 
            try:
                author = Author.objects.get(id=author_serial)
            except Author.DoesNotExist:
                return Response({"error": f"Who dat? {author_serial} not found, babe."}, status=status.HTTP_404_NOT_FOUND)

            serializer = PostSerializer(data=request.data)
            # create post locally
            if serializer.is_valid():
                post = serializer.save(author_id=author)  # Associate the post with the author
            else:
                return Response({"error": f"Couldn't create the post locally or remotely, babe. Your request was messed up: {serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)
            
            # get remote authors and send post to remote inboxes 
            try:
                # Prepare post data 
                post_data = PostSerializer(post).data
                
                # if post.visibility == 'PUBLIC':
                #     # send to all remote inboxes if public post
                #     post_to_remote_inboxes(request, remote_authors, post_data)
                    
                # elif post.visibility == 'FRIENDS':
                #     remote_friends = get_remote_friends(author)
                    
                #     # Send only to remote friends' inboxes
                #     post_to_remote_inboxes(request, remote_friends, post_data)

                # elif post.visibility == 'UNLISTED':
                #     # Send to remote followers
                #     remote_followers = get_remote_followers_you(author)
                #     post_to_remote_inboxes(request, remote_followers, post_data)
                handle_remote_inboxes(post, request, post_data, author)

            except Exception as e:
                return Response(
                    {"error": f"Couldn't send the post to remote inboxes, babe. {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
      
class PostImageView(APIView):
    """
    Retrieve the image of a post if available.
    """
    # permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, author_serial, post_serial):
        try:
            # check if author_serial is a URL (FQID) or a uuid (SERIAL)
            # check if post_serial is a URL (FQID) or a uuid (SERIAL)
            if is_fqid(author_serial):
                author_serial = urllib.parse.unquote(author_serial)
                if not author_serial.endswith("/"):
                    author_serial += "/"
                author_serial = Author.objects.get(url=author_serial).id
            if is_fqid(post_serial):
                post_serial = urllib.parse.unquote(post_serial)
                if not post_serial.endswith("/"):
                    post_serial += "/"
                post_serial = Post.objects.get(url=post_serial).id
        except:
            return Response({"error": "PostImageView - GET - You didn't give me a valid FQID or SERIAL, babe."}, status=status.HTTP_400_BAD_REQUEST)
        
        author = get_object_or_404(Author, id=author_serial)
        post = get_object_or_404(Post, author_id=author, id=post_serial)

        if not post.content_type.startswith('image/'):
            return Response({'detail': 'No image available for this post'}, status=status.HTTP_404_NOT_FOUND)

        try:
            encoded_image = post.content
            # if ';base64,' in post.content:
            #     header, encoded_image = post.content.split(';base64,')
            # else:
            #     encoded_image = post.content

            missing_padding = len(encoded_image) % 4
            if missing_padding:
                encoded_image += '=' * (4 - missing_padding)
            encoded_image = re.sub(r"\s+", "", encoded_image)
            binary_image = base64.b64decode(encoded_image)

            # return Response(binary_image, content_type=post.content_type)
            return FileResponse(binary_image, content_type=post.content_type)
        except Exception as e:
            print(f"Error decoding image: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PublicPostsView(APIView):
    # To view all of the public posts in the home page
    permission_classes = [IsAuthenticatedOrReadOnly] 

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided to get public posts."}, status=status.HTTP_403_FORBIDDEN)

        current_author = get_object_or_404(Author, user=request.user)

        # posts = Post.objects.exclude(author_id=current_author.id)
        posts = Post.objects.all()

        serializer = PostSerializer(posts, many=True)

        # all_authors = list(Author.objects.exclude(id=current_author.id).values_list('id', flat=True))
        all_authors = list(Author.objects.all().values_list('id', flat=True))

        authorized_authors_per_post = []

        # - following_ids: set of IDs of authors that the current author follows
        # - followers_ids: set of IDs of authors that follow the current author
        following_ids = set(Follows.objects.filter(local_follower_id=current_author, status='ACCEPTED').values_list('followed_id', flat=True))
        followers_ids = set(Follows.objects.filter(followed_id=current_author, status='ACCEPTED').values_list('local_follower_id', flat=True))  
        mutual_friend_ids = following_ids.intersection(followers_ids)

        posts_to_remove = []
        filtered_posts = []
        for post_data in serializer.data:
            post_visibility = post_data.get('visibility')
            post_author_id = uuid.UUID(post_data.get('author').get('id').split('/')[-2])
            authorized_authors = set()

            if post_visibility == 'PUBLIC':
                post_author_url = post_data.get('author').get('id')
                parsed_url = urlparse(post_author_url)
                author_host = f"{parsed_url.scheme}://{parsed_url.hostname}"

                current_host = request.get_host().rstrip('/')
                current_host_full = f"{request.scheme}://{current_host}"

                print(f"PUBLIC POSTS AUTHOR_HOST {author_host} AND CURRENT HOST {current_host_full}")
                if author_host == current_host_full: #its a local author
                    authorized_authors.add(current_author.id)
                else:  
                    print(f"REMOTE THEREFORE FOLLOWING IDS {following_ids} WITH {post_author_id}")
                    if post_author_id in following_ids:
                        authorized_authors.add(current_author.id)
                    
            elif post_visibility == 'UNLISTED':
                accepted_following_ids = Follows.objects.filter(
                local_follower_id=current_author, 
                status='ACCEPTED'
                ).values_list('followed_id', flat=True)
                # Show the unlisted post if the post's author is someone the current author follows
                if post_author_id in accepted_following_ids or post_author_id == current_author.id:
                    authorized_authors.add(current_author.id)

            elif post_visibility == 'FRIENDS':
                # Only show FRIENDS posts if the post's author is a mutual friend
                if post_author_id in mutual_friend_ids or post_author_id == current_author.id:
                    authorized_authors.add(current_author.id)

            elif post_visibility == 'SHARED':
                #original_url = post_data.get('original_url')  
                #if original_url:
                #    original_author_id = original_url[0]  
                 #   authorized_authors.add(original_author_id) 
                #post_author_id = post_data.get('author_id')  # Get the author_id from post data
                #authorized_authors.add(post_author_id)
                if post_author_id in following_ids or post_author_id == current_author.id:
                  authorized_authors.add(current_author.id) 


            # Include visibility_type in the authorized_authors_per_post dictionary
            print(f"AUTHORIZED AUTHORS FOR STREAM {authorized_authors}")
            if authorized_authors: #if list is not empty
                authorized_authors_per_post.append({
                    'post_id': post_data['id'], 
                    'authorized_authors': list(authorized_authors),
                    'visibility_type': post_visibility  # Add visibility_type here
                })
            else:
                posts_to_remove.append(post_data['id'])

            filtered_posts = [post for post in serializer.data if post['id'] not in posts_to_remove]

        print(f"BIG DICTIONARY {authorized_authors_per_post}")

        # Create response data with posts and their respective authorized authors
        response_data = {
            'posts': filtered_posts,  
            'authorized_authors_per_post': authorized_authors_per_post
        }        
        return Response(response_data, status=status.HTTP_200_OK)
    
#endregion

#region Comment Views
class CommentedView(APIView):
    """
    get, comment on post
    """
    def post(self, request, author_serial):
        """
        Comment on a post
        """
        try:
            # check if author_serial is a URL (FQID) or a uuid (SERIAL)
            if is_fqid(author_serial):
                author_serial = urllib.parse.unquote(author_serial)
                if not author_serial.endswith("/"):
                    author_serial += "/"
                author_serial = Author.objects.get(url=author_serial).id
        except:
            return Response({"error": "CommentedView - POST - You didn't give me a valid FQID or SERIAL, babe."}, status=status.HTTP_400_BAD_REQUEST)
        
        #author who created the comment
        author = get_object_or_404(Author, id=author_serial)
       
        comment_data = request.data
        request_type = comment_data.get('type')

        if request_type != 'comment':
            return Response({"detail": "Must be 'comment' type"}, status=status.HTTP_400_BAD_REQUEST)
        
        post_url = comment_data.get("post")
        if not post_url:
            return Response({"Error": "Post URL is required."}, status=status.HTTP_400_BAD_REQUEST)

        post_id = post_url.rstrip('/').split("/posts/")[-1]
        post = get_object_or_404(Post, id=post_id)

        #creating the comment object locally
        comment_serializer = CommentSerializer(data=request.data)
        if comment_serializer.is_valid():
            comment = comment_serializer.save(
                author_id=author,
                post_id=post
            )
        else:
            return Response(comment_serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

        try:
            comment_data = CommentSerializer(comment).data
            print(f"COMMENT_DATA {comment_data}")
            handle_remote_inboxes(post, request, comment_data, author)
            # forward to correct remote inboxes
            # remote_authors = get_remote_authors(request)

            # #prepare comment data
            
            # print(f"COMMENT DATA REQUEST BODY {comment_data}")

            # if post.visibility == 'PUBLIC':
            #     post_to_remote_inboxes(request, remote_authors, comment_data)

            # elif post.visibility == 'FRIENDS':
            #     remote_friends = get_remote_friends(author)

            #     post_to_remote_inboxes(request, remote_friends, comment_data)

        except Exception as e:
            return Response(
                {"error": f"Couldn't send the comment to remote inboxes, babe. {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )  
    
        return Response(comment_serializer.data, status=status.HTTP_201_CREATED)   
        
        
    def get(self, request, author_serial):
        """ 
        Get the list of comments author has made on any post [local]
        """
        try:
            # check if author_serial is a URL (FQID) or a uuid (SERIAL)
            if is_fqid(author_serial):
                author_serial = urllib.parse.unquote(author_serial)
                if not author_serial.endswith("/"):
                    author_serial += "/"
                author_serial = Author.objects.get(url=author_serial).id
        except:
            return Response({"error": "CommentedView - GET - You didn't give me a valid FQID or SERIAL, babe."}, status=status.HTTP_400_BAD_REQUEST)
        
        author = get_object_or_404(Author, id=author_serial)

        comments = author.comments.all().order_by('-published')

        serializer = CommentSerializer(comments, many=True) # many=True specifies that input is not just a single comment
        #host is the host of commenter
        host = author.host.rstrip('/')

        response_data = {
            "type": "comments",
            "page": f"{host}/authors/{author_serial}",
            "id": f"{host}/authors/{author_serial}",
            "page_number": 1,
            "size": author.comments.count(),
            "count": author.comments.count(),
            "src": serializer.data  
        }

        return Response(response_data, status=status.HTTP_200_OK)
    
class CommentsByAuthorFQIDView(APIView):
    """
    Get the list of comments author has made on any post
    """
    def get(self, request, author_fqid):
        decoded_fqid = urllib.parse.unquote(author_fqid)

        # example author fqid: http://localhost/api/authors/1d6dfebf-63a6-47a9-8e88-5cda73675db5/
        try:
            parts = decoded_fqid.split('/')
            author_serial = parts[parts.index('authors') + 1] 
        except (ValueError, IndexError):
            return Response({"error": "Invalid FQID format"}, status=status.HTTP_400_BAD_REQUEST)
        
        author = get_object_or_404(Author, id=author_serial)

        comments = author.comments.all().order_by('-published')

        serializer = CommentSerializer(comments, many=True) # many=True specifies that input is not just a single comment
        #host is the host of commenter
        host = author.host.rstrip('/')

        response_data = {
            "type": "comments",
            "page": f"{host}/authors/{author_serial}",
            "id": f"{host}/authors/{author_serial}",
            "page_number": 1,
            "size": author.comments.count(),
            "count": author.comments.count(),
            "src": serializer.data  
        }

        return Response(response_data, status=status.HTTP_200_OK)
    
class CommentView(APIView):
    """
    Get a single comment
    """
    def get(self, request, author_serial, comment_serial):
        """
        Get a single comment
        """
        try:
            # check if comment_serial is a URL (FQID) or a uuid (SERIAL)
            if is_fqid(comment_serial):
                comment_serial = urllib.parse.unquote(comment_serial)
                if not comment_serial.endswith("/"):
                    comment_serial += "/"
                comment_serial = Comment.objects.get(url=comment_serial).id
        except:
            return Response({"error": "CommentView - GET - You didn't give me a valid FQID or SERIAL, babe."}, status=status.HTTP_400_BAD_REQUEST)
        
        comment = get_object_or_404(Comment, id=comment_serial)
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class CommentsView(APIView):
    """
    get comments on a post
    """
    def get(self, request, author_serial, post_serial):
        """
        get comments on a post 
        """
        try:
            # check if post_serial is a URL (FQID) or a uuid (SERIAL)
            if is_fqid(post_serial):
                post_serial = urllib.parse.unquote(post_serial)
                if not post_serial.endswith("/"):
                    post_serial += "/"
                post_serial = Post.objects.get(url=post_serial).id
        except:
            return Response({"error": "CommentsView - GET - You didn't give me a valid FQID or SERIAL, babe."}, status=status.HTTP_400_BAD_REQUEST)
        
        post = get_object_or_404(Post, id=post_serial)

        comments = post.comments.all().order_by('-published')

        serializer = CommentSerializer(comments, many=True) # many=True specifies that input is not just a single comment
        #host is the host from the post
        host = post.author_id.host.rstrip('/')
        post_author_id = post.author_id

        # "page":"http://nodebbbb/authors/222/posts/249",
        # "id":"http://nodebbbb/authors/222/posts/249/comments"
        response_data = {
            "type": "comments",
            "page": f"{host}/authors/{post_author_id}/posts/{post_serial}",
            "id": f"{host}/authors/{post_author_id}/posts/{post_serial}/comments",
            "page_number": 1,
            "size": post.comments.count(),
            "count": post.comments.count(),
            "src": serializer.data  
        }

        return Response(response_data, status=status.HTTP_200_OK)

class CommentsByFQIDView(APIView):
    """
    Get comments on a post by post FQID
    """
    def get(self, request, post_fqid):
        # example post url: http://nodebbbb/authors/222/posts/249
        #decoding fqid from chatGPT: asked chatGPT how to decode the FQID 2024-11-02
        decoded_fqid = urllib.parse.unquote(post_fqid)

        try:
            parts = decoded_fqid.split('/')
            author_id = parts[parts.index('authors') + 1] 
            post_serial = parts[parts.index('posts') + 1]      
        except (ValueError, IndexError):
            return Response({"error": "Invalid FQID format"}, status=status.HTTP_400_BAD_REQUEST)
        
        post = get_object_or_404(Post, id=post_serial) 

        comments = post.comments.all().order_by('-published')

        serializer = CommentSerializer(comments, many=True) # many=True specifies that input is not just a single comment
        #host is the host from the post
        host = post.author_id.host.rstrip('/')
        post_author_id = post.author_id.id

        # "page":"http://nodebbbb/authors/222/posts/249",
        # "id":"http://nodebbbb/api/authors/222/posts/249/comments"
        response_data = {
            "type": "comments",
            "page": f"{host}/authors/{post_author_id}/posts/{post_serial}",
            "id": f"{host}/authors/{post_author_id}/posts/{post_serial}/comments",
            "page_number": 1,
            "size": post.comments.count(),
            "count": post.comments.count(),
            "src": serializer.data  
        }

        return Response(response_data, status=status.HTTP_200_OK)
    
class CommentRemoteByFQIDView(APIView):
    """
    Get a comment by its FQID [local, remote]
    """
    def get(self, request, author_serial, post_serial, comment_fqid):
        """
        Get a comment by its FQID [local, remote]
        """
        #example comment url: http://nodeaaaa/api/authors/111/commented/130
        #decode comment fqid
        decoded_fqid = urllib.parse.unquote(comment_fqid)

        try:
            parts = decoded_fqid.split('/')
            author_id = parts[parts.index('authors') + 1] 
            comment_serial = parts[parts.index('commented') + 1]      
        except (ValueError, IndexError):
            return Response({"error": "Invalid FQID format"}, status=status.HTTP_400_BAD_REQUEST)
        
        comment = get_object_or_404(Comment, id=comment_serial)
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CommentByFQIDView(APIView):
    """
    get comment by comment fqid
    """
    def get(self, request, comment_fqid):
        """
        get comment by comment fqid
        """
        #example comment url: http://nodeaaaa/api/authors/111/commented/130
        #decode comment fqid
        decoded_fqid = urllib.parse.unquote(comment_fqid)

        try:
            parts = decoded_fqid.split('/')
            author_id = parts[parts.index('authors') + 1] 
            comment_serial = parts[parts.index('commented') + 1]      
        except (ValueError, IndexError):
            return Response({"error": "Invalid FQID format"}, status=status.HTTP_400_BAD_REQUEST)
        
        comment = get_object_or_404(Comment, id=comment_serial)
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
#endregion
    
#region Like views   
class LikedView(APIView):
    """
    get or like a post
    """
    def post(self, request, author_serial):
        try:
            # check if author_serial is a URL (FQID) or a uuid (SERIAL)
            if is_fqid(author_serial):
                author_serial = urllib.parse.unquote(author_serial)
                if not author_serial.endswith("/"):
                    author_serial += "/"
                author_serial = Author.objects.get(url=author_serial).id
        except:
            return Response({"error": "LikedView - POST - You didn't give me a valid FQID or SERIAL, babe."}, status=status.HTTP_400_BAD_REQUEST)
        
        #author who created the like
        author = get_object_or_404(Author, id=author_serial)
       
        like_data = request.data
        request_type = like_data.get('type')

        if request_type != 'like':
            return Response({"detail: Must be 'like' type"}, status=status.HTTP_400_BAD_REQUEST)
        
        object_url = like_data.get("object") #object can be either a comment or post
        if not object_url:
            return Response({"Error": "object URL is required."}, status=status.HTTP_400_BAD_REQUEST)

        # determine like was for post or comment
        if "/posts/" in object_url:
            # object is a post
            object_id = object_url.rstrip('/').split("/posts/")[-1]
            liked_object = get_object_or_404(Post, id=object_id)
            object_content_type = ContentType.objects.get_for_model(Post)
            object_url_remote = object_url
            # object_url_remote = f"{liked_object.author_id.host.rstrip('/')}/authors/{author.id}/posts/{object_id}/"
        elif "/commented/" in object_url:
            # object is a comment
            object_id = object_url.rstrip('/').split("/commented/")[-1]
            liked_object = get_object_or_404(Comment, id=object_id)
            object_content_type = ContentType.objects.get_for_model(Comment)
            object_url_remote = object_url
            # object_url_remote = f"{liked_object.author_id.host.rstrip('/')}/authors/{author.id}/commented/{object_id}/"
        else:
            return Response({"detail": "Invalid object URL format."}, status=status.HTTP_400_BAD_REQUEST)
        
        
        #check if user has already liked the object
        existing_like = Like.objects.filter(
            author_id=author,
            object_url=object_url_remote
        ).first()

        if existing_like:
            return Response(LikeSerializer(existing_like).data, status=status.HTTP_200_OK) #if they've already liked, can't like again

        # create like object locally
        like_serializer = LikeSerializer(data=request.data) #asked chatGPT how to set the host in the serializer, need to add context 2024-11-02
        if like_serializer.is_valid():

            like = like_serializer.save(
                author_id=author,  
                object_id=liked_object.id,
                content_type=object_content_type,
                object_url=object_url_remote
            )

            # #creating Inbox object to forward to correct inbox
            # post_host = object_url.split("//")[1].split("/")[0]
            # if post_host != request.get_host():
            #     # TODO: Part 3-5 post or comment not on our host, need to forward it to a remote inbox
            #     pass
            
            
        else:
            return Response(like_serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
        
        try:
            like_data = LikeSerializer(like).data
            print(f"LIKE DATA {like_data}")
            handle_remote_inboxes(liked_object, request, like_data, author)
        except Exception as e:
            return Response(
                {"error": f"Couldn't send the like to remote inboxes, babe. {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )  
        return Response(like_serializer.data, status=status.HTTP_201_CREATED)   
        
    def get(self, request, author_serial):
        """
        get list of likes by author_id
        """
        try:
            # check if author_serial is a URL (FQID) or a uuid (SERIAL)
            if is_fqid(author_serial):
                author_serial = urllib.parse.unquote(author_serial)
                if not author_serial.endswith("/"):
                    author_serial += "/"
                author_serial = Author.objects.get(url=author_serial).id
        except:
            return Response({"error": "LikedView - GET - You didn't give me a valid FQID or SERIAL, babe."}, status=status.HTTP_400_BAD_REQUEST)
        
        author = get_object_or_404(Author, id=author_serial)
        likes = author.likes.all()

        # Pagination setup
        paginator = LikesPagination()
        paginated_likes = paginator.paginate_queryset(likes, request)

        serializer = LikeSerializer(paginated_likes, many=True)  # many=True specifies that input is not just a single like

        host = request.get_host()
        response_data = {
            "type": "likes",
            "page": f"http://{host}/authors/{author_serial}",
            "id": f"http://{host}/authors/{author_serial}/liked",
            "page_number": paginator.page.number,
            "size": paginator.get_page_size(request),
            "count": author.likes.count(),
            "src": serializer.data  # List of serialized like data
        }

        return Response(response_data, status=status.HTTP_200_OK)

class LikeView(APIView):
    """
    Get a single like by author and like serial
    """
    def get(self, request, author_serial, like_serial):
        """
        Get a single like by author serial and like serial
        """
        try:
            # check if like_serial is a URL (FQID) or a uuid (SERIAL)
            if is_fqid(like_serial):
                like_serial = urllib.parse.unquote(like_serial)
                if not like_serial.endswith("/"):
                    like_serial += "/"
                like_serial = Like.objects.get(url=like_serial).id
        except:
            return Response({"error": "LikeView - GET - You didn't give me a valid FQID or SERIAL, babe."}, status=status.HTTP_400_BAD_REQUEST)
        
        like = get_object_or_404(Like, id=like_serial)
        serializer = LikeSerializer(like)
        return Response(serializer.data, status=status.HTTP_200_OK)

class LikesView(APIView):
    """
    get likes on a post
    """
    def get(self, request, author_serial, post_id):
        """
        Get likes on a post
        """
        try:
            # check if post_id is a URL (FQID) or a uuid (SERIAL)
            # check if author_serial is a URL (FQID) or a uuid (SERIAL)
            if is_fqid(author_serial):
                author_serial = urllib.parse.unquote(author_serial)
                if not author_serial.endswith("/"):
                    author_serial += "/"
                author_serial = Author.objects.get(url=author_serial).id
            if is_fqid(post_id):
                post_id = urllib.parse.unquote(post_id)
                if not post_id.endswith("/"):
                    post_id += "/"
                post_id = Post.objects.get(url=post_id).id
        except:
            return Response({"error": "LikesView - GET - You didn't give me a valid FQID or SERIAL, babe."}, status=status.HTTP_400_BAD_REQUEST)
        
        post = get_object_or_404(Post, id=post_id)

        likes = post.likes.all().order_by('-published')

        # Pagination setup
        paginator = LikesPagination()
        paginated_likes = paginator.paginate_queryset(likes, request)

        serializer = LikeSerializer(paginated_likes, many=True)  # many=True specifies that input is not just a single like

        host = request.get_host().rstrip('/')
        response_data = {
            "type": "likes",
            "page": f"http://{host}/authors/{author_serial}/posts/{post_id}",
            "id": f"http://{host}/authors/{author_serial}/posts/{post_id}/likes",
            "page_number": paginator.page.number,
            "size": paginator.get_page_size(request),
            "count": post.likes.count(),
            "src": serializer.data  # List of serialized like data
        }

        return Response(response_data, status=status.HTTP_200_OK)
    
class LikedCommentsView(APIView):
    """
    Get likes for a comment
    """
    def get(self, request, author_id, post_id, comment_id):
        """
        get likes for a comment
        """
        try:
            # check if author_id is a URL (FQID) or a uuid (SERIAL)
            # check if post_id is a URL (FQID) or a uuid (SERIAL)
            # check if comment_id is a URL (FQID) or a uuid (SERIAL)
            if is_fqid(author_id):
                author_id = urllib.parse.unquote(author_id)
                if not author_id.endswith("/"):
                    author_id += "/"
                author_id = Author.objects.get(url=author_id).id
            if is_fqid(post_id):
                post_id = urllib.parse.unquote(post_id)
                if not post_id.endswith("/"):
                    post_id += "/"
                post_id = Post.objects.get(url=post_id).id
            if is_fqid(comment_id):
                comment_id = urllib.parse.unquote(comment_id)
                if not comment_id.endswith("/"):
                    comment_id += "/"
                comment_id = Comment.objects.get(url=comment_id).id
        except:
            return Response({"error": "LikedCommentsView - GET - You didn't give me a valid FQID or SERIAL, babe."}, status=status.HTTP_400_BAD_REQUEST)
        
        post = get_object_or_404(Post, id=post_id)
        comment = get_object_or_404(Comment, id=comment_id, post_id=post)

        likes = comment.likes.all().order_by('-published')

        # Pagination setup
        paginator = LikesPagination()
        paginated_likes = paginator.paginate_queryset(likes, request)

        serializer = LikeSerializer(paginated_likes, many=True)  # many=True specifies that input is not just a single like

        host = request.get_host().rstrip('/')
        response_data = {
            "type": "likes",
            "page": f"http://{host}/authors/{author_id}/commented/{comment_id}",
            "id": f"http://{host}/authors/{author_id}/commented/{comment_id}/likes",
            "page_number": paginator.page.number,
            "size": paginator.get_page_size(request),
            "count": comment.likes.count(),
            "src": serializer.data  
        }

        return Response(response_data, status=status.HTTP_200_OK)

class LikesViewByFQIDView(APIView):
    """
    Get likes by FQID
    """
    def get(self, request, post_fqid):
        """
        get likes for post with fqid
        """
        # example post url: http://nodebbbb/authors/222/posts/249
        #decoding fqid from chatGPT: asked chatGPT how to decode the FQID 2024-11-02
        # Decode the FQID
        decoded_fqid = urllib.parse.unquote(post_fqid)

        # Split the decoded FQID to extract author_id and post_id
        try:
            parts = decoded_fqid.split('/')
            author_id = parts[parts.index('authors') + 1] 
            post_id = parts[parts.index('posts') + 1]      
        except (ValueError, IndexError):
            return Response({"error": "Invalid FQID format"}, status=status.HTTP_400_BAD_REQUEST)
        
        post = get_object_or_404(Post, id=post_id)

        likes = post.likes.all().order_by('-published')

        # Pagination setup
        paginator = LikesPagination()
        paginated_likes = paginator.paginate_queryset(likes, request)

        serializer = LikeSerializer(paginated_likes, many=True)  # many=True specifies that input is not just a single like

        host = request.get_host().rstrip('/')
        response_data = {
            "type": "likes",
            "page": f"http://{host}/authors/{author_id}/posts/{post_id}",
            "id": f"http://{host}/authors/{author_id}/posts/{post_id}/likes",
            "page_number": paginator.page.number,
            "size": paginator.get_page_size(request),
            "count": post.likes.count(),
            "src": serializer.data  # List of serialized like data
        }

        return Response(response_data, status=status.HTTP_200_OK)
    
class LikeViewByFQIDView(APIView):
    """
    Get a single like
    """
    def get(self, request, like_fqid):
        """
        Get a single like 
        """
        # example like url http://nodeaaaa/api/authors/222/liked/255
        # Decode the FQID
        decoded_fqid = urllib.parse.unquote(like_fqid)

        # Split the decoded FQID to extract author_id and like_id
        try:
            parts = decoded_fqid.split('/')
            #author_id = parts[parts.index('authors') + 1] 
            like_id = parts[parts.index('liked') + 1]      
        except (ValueError, IndexError):
            return Response({"error": "Invalid FQID format"}, status=status.HTTP_400_BAD_REQUEST)
        
        like = get_object_or_404(Like, id=like_id)
        serializer = LikeSerializer(like)
        return Response(serializer.data, status=status.HTTP_200_OK)

class LikedFQIDView(APIView):
    """
    get list of likes from author with FQID
    """
    def get(self, request, author_fqid):
        """
        get list of likes from author with FQID
        """
        # example author url: http://nodeaaaa/api/authors/111
        decoded_fqid = urllib.parse.unquote(author_fqid)

        try:
            parts = decoded_fqid.split('/')
            author_serial = parts[parts.index('authors') + 1] 
        except (ValueError, IndexError):
            return Response({"error": "Invalid FQID format"}, status=status.HTTP_400_BAD_REQUEST)
        
        author = get_object_or_404(Author, id=author_serial)
        likes = author.likes.all()

        # Pagination setup
        paginator = LikesPagination()
        paginated_likes = paginator.paginate_queryset(likes, request)

        serializer = LikeSerializer(paginated_likes, many=True)  # many=True specifies that input is not just a single like

        host = request.get_host().rstrip('/')
        response_data = {
            "type": "likes",
            "page": f"http://{host}/authors/{author_serial}",
            "id": f"http://{host}/authors/{author_serial}/liked",
            "page_number": paginator.page.number,
            "size": paginator.get_page_size(request),
            "count": author.likes.count(),
            "src": serializer.data  # List of serialized like data
        }

        return Response(response_data, status=status.HTTP_200_OK)
#endregion

#region Github Vews
class GitHubEventsView(APIView):
    """
    Get public GitHub events for a username.
    """

    def get(self, request, username):
        github_api_url = f'https://api.github.com/users/{username}/events/public'
        headers = {
            'Accept': 'application/vnd.github+json',
        }

        try:
            response = requests.get(github_api_url, headers=headers)
            response.raise_for_status()  # Raise an error for bad responses
            return Response(response.json(), status=status.HTTP_200_OK)
        except requests.exceptions.RequestException as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#endregion