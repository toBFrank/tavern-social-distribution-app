import base64
import re
import uuid
from django.shortcuts import render
import requests
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
from .pagination import LikesPagination
import urllib.parse  # asked chatGPT how to decode the URL-encoded FQID 2024-11-02
from django.http import FileResponse
import requests
from requests.auth import HTTPBasicAuth #basic auth
from django.db import transaction #transaction requests so that if something happens in the middle, it'll be rolled back
from urllib.parse import unquote, urlparse
from node.authentication import NodeAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication  


#region Post Views
class PostDetailsView(APIView):
    """
    Retrieve, update or delete a post instance by author ID & post ID.
    """
    # permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get(self, request, author_serial, post_serial):
        try:
            post = Post.objects.get(id=post_serial, author_id=author_serial)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = PostSerializer(post)
        return Response(serializer.data)
      
    def put(self, request, author_serial, post_serial):
        try:
            post = Post.objects.get(id=post_serial, author_id=author_serial)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = PostSerializer(post, data=request.data)
        print("HELLO IM IN PUT")

        if serializer.is_valid():
            updated_post = serializer.save()
            try:
                remote_authors = get_remote_authors(request)  # Fetch remote authors
                if updated_post.visibility == 'PUBLIC':
                    for remote_author in remote_authors:
                        node = Node.objects.filter(host=remote_author.host.rstrip('/')).first()
                        print(f"HI IM UNDER THE NODENode: {node}")
                        if node:
                            author_inbox_url = f"{remote_author.host.rstrip('/')}/api/authors/{remote_author.id}/inbox/"
                            post_data = PostSerializer(updated_post).data
                            post_data['id'] = f"{remote_author.host.rstrip('/')}/api/authors/{remote_author.id}/posts/{updated_post.id}/"
                            
                            credentials = f"{node.username}:{node.password}"
                            base64_credentials = base64.b64encode(credentials.encode()).decode("utf-8")
                            headers = {"Authorization": f"Basic {base64_credentials}"}
                            
                            print(f"Authorization header in put: {headers}")
                            
                            # Send the updated post
                            response = requests.post(
                                author_inbox_url,
                                headers=headers,
                                json=post_data
                            )
                            
                            if response.status_code < 200 or response.status_code >= 300:
                                print(f"Failed to send post to {remote_author.host}: {response.status_code} - {response.text}")
                        return Response(serializer.data)
                
                elif updated_post.visibility == 'FRIENDS':
                    # Handle sending to remote friends (if applicable)
                    # TODO: Implement logic for fetching and sending to remote friends
                    pass
            
            except Exception as e:
                return Response(
                    {"error": f"Failed to re-send updated post: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

      
    def delete(self, request, author_serial, post_serial):
        try:
            # Fetch the post
            post = Post.objects.get(id=post_serial, author_id=author_serial)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Update the visibility to 'DELETED' using the serializer
        serializer = PostSerializer(post, data={'visibility': 'DELETED'}, partial=True)  # 'partial=True' means only updating visibility

        print("HELLO IM IN DELETE")

        if serializer.is_valid():
            updated_post = serializer.save()

            try:
                # Notify remote authors about the post deletion
                remote_authors = get_remote_authors(request)  # Fetch remote authors
                if updated_post.visibility == 'DELETED':
                    for remote_author in remote_authors:
                        node = Node.objects.filter(host=remote_author.host.rstrip('/')).first()
                        if node:
                            author_inbox_url = f"{remote_author.host.rstrip('/')}/api/authors/{remote_author.id}/inbox/"
                            
                            # Prepare the data to update the post visibility to 'DELETED'
                            update_data = {
                                'visibility': 'DELETED'
                            }

                            # Basic Auth for authentication
                            credentials = f"{node.username}:{node.password}"
                            base64_credentials = base64.b64encode(credentials.encode()).decode("utf-8")
                            headers = {"Authorization": f"Basic {base64_credentials}"}

                            # Send the update to notify about the deletion
                            response = requests.patch(
                                author_inbox_url,
                                headers=headers,
                                json=update_data
                            )

                            if not (200 <= response.status_code < 300):
                                # Log the failure to notify the remote author
                                print(f"Failed to notify {remote_author.host} about post deletion: {response.status_code} - {response.text}")

            except Exception as e:
                # Catch errors during remote notifications
                return Response(
                    {"error": f"Failed to notify remote authors about post deletion: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Return 204 No Content after successfully marking the post as deleted
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
      
class PostDetailsByFqidView(APIView):
    """
    Retrieve post by Fully Qualified ID (URL + ID).
    """
    # permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get(self, request, post_fqid):
        try:
            post = Post.objects.get(id=post_fqid)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = PostSerializer(post)
        return Response(serializer.data)

def get_remote_authors(request):
    remote_authors = []
    for node in Node.objects.filter(is_whitelisted=True):
        # get authors for each remote node connection
        #get authors 
        get_authors_url = f"{node.host.rstrip('/')}/api/authors/"
        parsed_url = urlparse(request.build_absolute_uri())
        host_with_scheme = f"{parsed_url.scheme}://{parsed_url.netloc}"
        credentials = f"{node.username}:{node.password}"
        base64_credentials = base64.b64encode(credentials.encode()).decode("utf-8")
        print(f"REQUEST \nget_authors_url: {get_authors_url}\nhost_with_scheme: {host_with_scheme}\nAuthorization: Basic {node.username}:{node.password}")
        response = requests.get(
                get_authors_url,
                params={"host": host_with_scheme},
                # auth=HTTPBasicAuth(local_node_of_remote.username, local_node_of_remote.password),
                headers={"Authorization": f"Basic {base64_credentials}"},
            )
        
        print(f"RESPONSE BRUH {response} WITH STATUS CODE {response.status_code}")
        
        # response = requests.get(get_authors_url, auth=HTTPBasicAuth(node.username, node.password)) #make http requests to remote node
        if response.status_code == 200:
            authors_data = response.json()["authors"]
            print(f"IS IT THIS ITERABLE? {authors_data}")
            for author_data in authors_data:
                author_id = author_data['id'].rstrip('/').split("/authors/")[-1]
                
                # Get remote author or create
                author, created = Author.objects.get_or_create(id=author_id)
                if created:
                    author.host = author_data['host']
                    author.display_name = author_data['displayName']
                    author.github = author_data.get('github', '')
                    author.profile_image = author_data.get('profileImage', '')
                    author.page = author_data['page']
                    author.save()

                remote_authors.append(author)
                print(f"AN AUTHOR: {author}")
        # else:  # But what if this node is down? Or no authors in this node?
        #     raise ValueError(f"Failed to fetch authors from {get_authors_url} with status code {response.status_code}.")
        
    return remote_authors

def send_to_inbox(remote_author, post_data, host_with_scheme):
    """
    Helper function to send post data to a remote author's inbox.
    """
    # Prepare URL and credentials for the remote author's inbox
    node = Node.objects.filter(host=remote_author.host.rstrip('/')).first()
    if node:
        author_inbox_url = f"{remote_author.host.rstrip('/')}/api/authors/{remote_author.id}/inbox/"
        credentials = f"{node.username}:{node.password}"
        base64_credentials = base64.b64encode(credentials.encode()).decode("utf-8")
        
        # Make the request
        response = requests.post(
            author_inbox_url,
            params={"host": host_with_scheme},
            headers={"Authorization": f"Basic {base64_credentials}"},
            json=post_data,
        )

        # Check for errors
        if response.status_code == 401:
            print(f"Authorization failed with status code 401. Response details:")
            print(f"Response Headers: {response.headers}")
            print(f"Response Content: {response.text}")
        
        if response.status_code >= 200 and response.status_code < 300:
            print(f"Successfully sent post to {remote_author.url}")
        else:
            print(f"Failed to send post to {remote_author.url}, {response.status_code} - {response.reason}")

class AuthorPostsView(APIView):
    """
    List all posts by an author, or create a new post for the author.
    """

    def get(self, request, author_serial):
        posts = Post.objects.filter(author_id=author_serial)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request, author_serial):
        '''
        create post locally and send to all remote inboxes if public, and remote friends if friends only post
        '''
        with transaction.atomic(): #a lot of datbase operations, better to do transaction so that if something fails, we can rollback instead of half updates
            # create post locally first 
            try:
                author = Author.objects.get(id=author_serial)
            except Author.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)

            serializer = PostSerializer(data=request.data)
            if serializer.is_valid():
                post = serializer.save(author_id=author)  # Associate the post with the author
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            # get remote authors and send post to remote inboxes 
            try:
                remote_authors = get_remote_authors(request)
                print(f" REMOTE AUTHORS YUHH {remote_authors}")

                # Prepare post data 
                post_data = PostSerializer(post).data
                post_data['id'] = f"{author.host.rstrip('/')}/api/authors/{author.id}/posts/{post.id}/"
                print(f"ERM THIS IS POST DATAAAA {post_data}")

                
                parsed_url = urlparse(request.build_absolute_uri())
                host_with_scheme = f"{parsed_url.scheme}://{parsed_url.netloc}"
                if post.visibility == 'PUBLIC':
                    #send to all remote inboxes if public post
                    for remote_author in remote_authors:
                        send_to_inbox(remote_author, post_data, host_with_scheme)
                        
                elif post.visibility == 'FRIENDS':
                    #send only to remote friends if friends post
                    #TODO: see how remote friends is being handled i.e. is it using remote_id?
                        # Get remote friends of the author
                    outgoing_follows = Follows.objects.filter(
                        local_follower_id=author, status='ACCEPTED'
                    ).values_list('followed_id', flat=True)

                    remote_friends = [
                        remote_author for remote_author in remote_authors
                        if Follows.objects.filter(
                            followed_id=author,
                            remote_follower_url=remote_author.url,
                            status='ACCEPTED'
                        ).exists() and remote_author.id in outgoing_follows
                    ]

                    # Send only to remote friends' inboxes
                    for remote_friend in remote_friends:
                        send_to_inbox(remote_friend, post_data, host_with_scheme)

            except Exception as e:
                #return an error if fetching remote authors fails
                return Response(
                    {"error": f"Failed to fetch remote authors: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)

      
class PostImageView(APIView):
    """
    Retrieve the image of a post if available.
    """
    # permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, author_serial, post_serial):
        author = get_object_or_404(Author, id=author_serial)
        post = get_object_or_404(Post, author_id=author, id=post_serial)

        if not post.content_type.startswith('image/'):
            return Response({'detail': 'No image available for this post'}, status=status.HTTP_404_NOT_FOUND)

        try:
            if ';base64,' in post.content:
                header, encoded_image = post.content.split(';base64,')
            else:
                encoded_image = post.content

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

        #creating the comment object

        comment_serializer = CommentSerializer(data=request.data)
        if comment_serializer.is_valid():
            comment_serializer.save(
                author_id=author,
                post_id=post
            )

            #creating Inbox object to forward to correct inbox
            post_host = post_url.split("//")[1].split("/")[0]
            if post_host != request.get_host():
                # TODO: post not on our host, need to forward it to a remote inbox
                pass
        
            return Response(comment_serializer.data, status=status.HTTP_201_CREATED)   
        else:
            return Response(comment_serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
        
    def get(self, request, author_serial):
        """ 
        Get the list of comments author has made on any post [local]
        """
        #TODO: get comments author has made for [remote]
        author = get_object_or_404(Author, id=author_serial)

        comments = author.comments.all().order_by('-published')

        serializer = CommentSerializer(comments, many=True) # many=True specifies that input is not just a single comment
        #host is the host of commenter
        host = author.host.rstrip('/')

        response_data = {
            "type": "comments",
            "page": f"{host}/api/authors/{author_serial}",
            "id": f"{host}/api/authors/{author_serial}",
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
            "page": f"{host}/api/authors/{author_serial}",
            "id": f"{host}/api/authors/{author_serial}",
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
        post = get_object_or_404(Post, id=post_serial)

        comments = post.comments.all().order_by('-published')

        serializer = CommentSerializer(comments, many=True) # many=True specifies that input is not just a single comment
        #host is the host from the post
        host = post.author_id.host.rstrip('/')
        post_author_id = post.author_id

        # "page":"http://nodebbbb/authors/222/posts/249",
        # "id":"http://nodebbbb/api/authors/222/posts/249/comments"
        response_data = {
            "type": "comments",
            "page": f"{host}/api/authors/{post_author_id}/posts/{post_serial}",
            "id": f"{host}/api/authors/{post_author_id}/posts/{post_serial}/comments",
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
            "page": f"{host}/api/authors/{post_author_id}/posts/{post_serial}",
            "id": f"{host}/api/authors/{post_author_id}/posts/{post_serial}/comments",
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
        elif "/commented/" in object_url:
            # object is a comment
            object_id = object_url.rstrip('/').split("/commented/")[-1]
            liked_object = get_object_or_404(Comment, id=object_id)
            object_content_type = ContentType.objects.get_for_model(Comment)
        else:
            return Response({"detail": "Invalid object URL format."}, status=status.HTTP_400_BAD_REQUEST)
        
        #check if user has already liked the object
        existing_like = Like.objects.filter(
            author_id=author,
            object_url=object_url
        ).first()

        if existing_like:
            return Response(LikeSerializer(existing_like).data, status=status.HTTP_200_OK) #if they've already liked, can't like again

        like_serializer = LikeSerializer(data=request.data) #asked chatGPT how to set the host in the serializer, need to add context 2024-11-02
        if like_serializer.is_valid():

            like_serializer.save(
                author_id=author,  
                object_id=liked_object.id,
                content_type=object_content_type,
                object_url=object_url
            )

            #creating Inbox object to forward to correct inbox
            post_host = object_url.split("//")[1].split("/")[0]
            if post_host != request.get_host():
                # TODO: Part 3-5 post or comment not on our host, need to forward it to a remote inbox
                pass
            
            return Response(like_serializer.data, status=status.HTTP_201_CREATED)   
        else:
            return Response(like_serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
        
    def get(self, request, author_serial):
        """
        get list of likes by author_id
        """
        author = get_object_or_404(Author, id=author_serial)
        likes = author.likes.all()

        # Pagination setup
        paginator = LikesPagination()
        paginated_likes = paginator.paginate_queryset(likes, request)

        serializer = LikeSerializer(paginated_likes, many=True)  # many=True specifies that input is not just a single like

        host = request.get_host()
        response_data = {
            "type": "likes",
            "page": f"http://{host}/api/authors/{author_serial}",
            "id": f"http://{host}/api/authors/{author_serial}/liked",
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
        post = get_object_or_404(Post, id=post_id)

        likes = post.likes.all().order_by('-published')

        # Pagination setup
        paginator = LikesPagination()
        paginated_likes = paginator.paginate_queryset(likes, request)

        serializer = LikeSerializer(paginated_likes, many=True)  # many=True specifies that input is not just a single like

        host = request.get_host()
        response_data = {
            "type": "likes",
            "page": f"http://{host}/api/authors/{author_serial}/posts/{post_id}",
            "id": f"http://{host}/api/authors/{author_serial}/posts/{post_id}/likes",
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
        post = get_object_or_404(Post, id=post_id)
        comment = get_object_or_404(Comment, id=comment_id, post_id=post)

        likes = comment.likes.all().order_by('-published')

        # Pagination setup
        paginator = LikesPagination()
        paginated_likes = paginator.paginate_queryset(likes, request)

        serializer = LikeSerializer(paginated_likes, many=True)  # many=True specifies that input is not just a single like

        host = request.get_host()
        response_data = {
            "type": "likes",
            "page": f"http://{host}/api/authors/{author_id}/commented/{comment_id}",
            "id": f"http://{host}/api/authors/{author_id}/commented/{comment_id}/likes",
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

        host = request.get_host()
        response_data = {
            "type": "likes",
            "page": f"http://{host}/api/authors/{author_id}/posts/{post_id}",
            "id": f"http://{host}/api/authors/{author_id}/posts/{post_id}/likes",
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

        host = request.get_host()
        response_data = {
            "type": "likes",
            "page": f"http://{host}/api/authors/{author_serial}",
            "id": f"http://{host}/api/authors/{author_serial}/liked",
            "page_number": paginator.page.number,
            "size": paginator.get_page_size(request),
            "count": author.likes.count(),
            "src": serializer.data  # List of serialized like data
        }

        return Response(response_data, status=status.HTTP_200_OK)
#endview
   
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

        for post_data in serializer.data:
            post_visibility = post_data.get('visibility')
            post_author_id = uuid.UUID(post_data.get('author').get('id').split('/')[-2])
            authorized_authors = set()

            if post_visibility == 'PUBLIC':
                authorized_authors.update(all_authors)
            
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
            authorized_authors_per_post.append({
                'post_id': post_data['id'], 
                'authorized_authors': list(authorized_authors),
                'visibility_type': post_visibility  # Add visibility_type here
            })

        # Create response data with posts and their respective authorized authors
        print(f"authorized_authors_per_post: {authorized_authors_per_post}")
        response_data = {
            'posts': serializer.data,  
            'authorized_authors_per_post': authorized_authors_per_post
        }        
        return Response(response_data, status=status.HTTP_200_OK)
    
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