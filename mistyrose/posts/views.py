from django.shortcuts import render
from users.models import Author
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from .models import Post, Comment, Like
from stream.models import Inbox
from .serializers import PostSerializer, CommentSerializer, LikeSerializer
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType


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
    
    def get(self, request, fqid):
        try:
            post = Post.objects.get(id=fqid)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = PostSerializer(post)
        return Response(serializer.data)
      
class AuthorPostsView(APIView):
    """
    List all posts by an author, or create a new post for author.
    """
    # permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get(self, request, author_serial):
        posts = Post.objects.filter(author_id=author_serial)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
      
    def post(self, request, author_serial):
        try:
            print(f"AUTHOR SERIAL: {author_serial}")
            author = Author.objects.get(id=author_serial)
        except Author.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        
        request.data['author_id'] = author_serial
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
          
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
      
class PostImageView(APIView):
    """
    Retrieve the image of a post if available.
    """
    # permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, author_serial, post_serial):
        try:
            post = Post.objects.get(author__id=author_serial, id=post_serial)
        except Post.DoesNotExist:
            return Response({"detail": "Post not found."}, status=status.HTTP_404_NOT_FOUND)

        if post.image:
            image_url = post.image.url
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
        #author who created the comment
        author = get_object_or_404(Author, id=author_serial)
       
        comment_data = request.data
        request_type = comment_data.get('type')

        if request_type != 'comment':
            return Response({"detail: Must be 'comment' type"}, status=status.HTTP_400_BAD_REQUEST)
        
        post_url = comment_data.get("post")
        if not post_url:
            return Response({"Error": "Post URL is required."}, status=status.HTTP_400_BAD_REQUEST)

        post_id = post_url.rstrip('/').split("/posts/")[-1]
        post = get_object_or_404(Post, id=post_id)

        #creating the comment object
        request.data['author_id'] = author_serial
        request.data['post_id'] = post_id
        comment_serializer = CommentSerializer(data=request.data)
        if comment_serializer.is_valid():
            comment_instance = comment_serializer.save()

            #creating Inbox object to forward to correct inbox
            post_host = post_url.split("//")[1].split("/")[0]
            if post_host != request.get_host():
                # TODO: post not on our host, need to forward it to a remote inbox
                pass
            else:
                # create and add to Inbox of the post's author
                post_author = post.author_id
                content_type = ContentType.objects.get_for_model(Comment)

                Inbox.objects.create(
                    type="comment",
                    author=post_author,
                    content_type=content_type,
                    object_id=comment_instance.id,
                    content_object=comment_instance,
                )

            return Response(comment_serializer.data, status=status.HTTP_201_CREATED)   
        else:
            return Response(comment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)        

#endregion

#region Like Views