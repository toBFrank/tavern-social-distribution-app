from django.shortcuts import render
from users.models import Author
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from .models import Post, Comment, Like
from stream.models import Inbox
from .serializers import PostSerializer, CommentSerializer, LikeSerializer
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from .models import Post
from users.models import Author, Follows  
from .pagination import LikesPagination
from django.http import JsonResponse
import urllib.parse  # asked chatGPT how to decode the URL-encoded FQID 2024-11-02

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

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

      
    def delete(self, request, author_serial, post_serial):
        try:
            post = Post.objects.get(id=post_serial, author_id=author_serial)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
      
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

class AuthorPostsView(APIView):
    """
    List all posts by an author, or create a new post for the author.
    """

    def get(self, request, author_serial):
        posts = Post.objects.filter(author_id=author_serial)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request, author_serial):
        try:
            author = Author.objects.get(id=author_serial)
        except Author.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author_id=author)  # Associate the post with the author
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

      
class PostImageView(APIView):
    """
    Retrieve the image of a post if available.
    """
    # permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, author_serial, post_serial):
        try:
            
            author = Author.objects.get(id=author_serial)
            post = Post.objects.get(author_id=author, id=post_serial)
        except Author.DoesNotExist:
            return Response({"detail": f"Author {author_serial} not found."}, status=status.HTTP_404_NOT_FOUND)
        except Post.DoesNotExist:
            return Response({"detail": f"Post {post_serial} not found for {author}"}, status=status.HTTP_404_NOT_FOUND)

        if post.image_content:
            image_url = request.build_absolute_uri(post.image_content.url)
            return Response({'image_url': image_url})
        else:
            return Response({'detail': 'No image available for this post'}, status=status.HTTP_404_NOT_FOUND)
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
        
    def get(self, request, author_serial, post_id):
        """ 
        Get comments on a post
        """
        post = get_object_or_404(Post, id=post_id) 

        comments = post.comments.all().order_by('-published')

        serializer = CommentSerializer(comments, many=True) # many=True specifies that input is not just a single comment
        #host is the host from the post
        host = post.author_id.host.rstrip('/')
        post_author_id = post.author_id.id

        # "page":"http://nodebbbb/authors/222/posts/249",
        # "id":"http://nodebbbb/api/authors/222/posts/249/comments"
        response_data = {
            "type": "comments",
            "page": f"{host}/api/authors/{post_author_id}/posts/{post_id}",
            "id": f"{host}/api/authors/{post_author_id}/posts/{post_id}/comments",
            "page_number": 1,
            "size": post.comments.count(),
            "count": post.comments.count(),
            "src": serializer.data  
        }

        return Response(response_data, status=status.HTTP_200_OK)
    
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
            return Response(LikeSerializer(existing_like).data, status=200) #if they've already liked, can't like again

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
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_403_FORBIDDEN)

        current_author = get_object_or_404(Author, user=request.user)

        posts = Post.objects.exclude(author_id=current_author.id)

        serializer = PostSerializer(posts, many=True)

        all_authors = list(Author.objects.exclude(id=current_author.id).values_list('id', flat=True))

        authorized_authors_per_post = []

        # Get a list of authors that the current author follows
        following_ids = set(Follows.objects.filter(local_follower_id=current_author, status='ACCEPTED').values_list('followed_id', flat=True))
        followers_ids = set(Follows.objects.filter(followed_id=current_author, status='ACCEPTED').values_list('local_follower_id', flat=True))  
        mutual_friend_ids = following_ids.intersection(followers_ids)

        for post_data in serializer.data:
            post_visibility = post_data.get('visibility')
            post_author_id = post_data['author_id']
            authorized_authors = set()

            if post_visibility == 'PUBLIC':
                authorized_authors.update(all_authors)
            
            
            
            elif post_visibility == 'UNLISTED':
                accepted_following_ids = Follows.objects.filter(
                local_follower_id=current_author, 
                status='ACCEPTED'
                ).values_list('followed_id', flat=True)
                # Show the unlisted post if the post's author is someone the current author follows
                if post_author_id in accepted_following_ids:
                    authorized_authors.add(current_author.id)

            
            elif post_visibility == 'FRIENDS':
                # Only show FRIENDS posts if the post's author is a mutual friend
                if post_author_id in mutual_friend_ids:
                    authorized_authors.add(current_author.id)

            elif post_visibility == 'SHARED':
                original_url = post_data.get('original_url')  
                if original_url:
                    original_author_id = original_url[0]  
                    authorized_authors.add(original_author_id) 
                post_author_id = post_data.get('author_id')  # Get the author_id from post data
                authorized_authors.add(post_author_id) 


            # Include visibility_type in the authorized_authors_per_post dictionary
            authorized_authors_per_post.append({
                'post_id': post_data['id'], 
                'authorized_authors': list(authorized_authors),
                'visibility_type': post_visibility  # Add visibility_type here
            })

        # Create response data with posts and their respective authorized authors
        response_data = {
            'posts': serializer.data,  
            'authorized_authors_per_post': authorized_authors_per_post
        }
        return Response(response_data, status=status.HTTP_200_OK)
    



            