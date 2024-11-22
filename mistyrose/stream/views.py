from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import FollowSerializer
from users.models import Author, Follows
from django.shortcuts import get_object_or_404
from rest_framework import status  
from .utils import handle_follow_request, handle_post_a_post, handle_comment_inbox, handle_like_inbox


class InboxView(APIView):
    """
    Handle incoming requests to the inbox.
    """
    
    def post(self, request, author_id):
        object_type = request.data.get('type')
        author = get_object_or_404(Author, id=author_id)

        if object_type == "follow":
            response = handle_follow_request(request, author)
            return response

        elif object_type == "post":
            # create post object type and user.
            author = get_object_or_404(Author, id=author_id) #author whose stream we want to add post to

            if request.data.get('visibility') == 'PUBLIC' or request.data.get('visibility') == 'DELETED':
                # check if post's author in database, create author if not
                author_of_post = request.data["author"]["id"]
                author_of_post_id = author_of_post.rstrip('/').split("/authors/")[-1]

                author_data = request.data["author"]
                # get or create remote author who made the post
                author, created = Author.objects.get_or_create(
                    id=author_of_post_id,
                    defaults={
                        "host": author_data['host'],
                        "display_name": author_data['displayName'],
                        "github": author_data.get('github', ''),
                        "profile_image": author_data.get('profileImage', ''),
                        "page": author_data['page'],
                    }
                )

            elif request.data.get('visibility') == 'FRIENDS':
                #check if poster's author in database and actually friends (if friends, should already be in database)
                try:
                    # Retrieve the author if they exist, otherwise return an error response
                    author = Author.objects.get(id=author_of_post_id)
                    
                    # Check if the author is actually a friend
                    # if not author.is_friend(author_id):  # assuming you have an `is_friend` method
                    #     return Response({"error": "Author is not a friend."}, status=status.HTTP_403_FORBIDDEN)
                    
                except Author.DoesNotExist:
                    return Response({"error": "Author not found in the database."}, status=status.HTTP_404_NOT_FOUND)


            # Extract post ID from the data
            post_id = request.data.get("id").rstrip('/').split("/posts/")[-1]

            # Check if the post already exists and create it if it doesn’t
            # post, created = Post.objects.get_or_create(
            #     id=post_id,
            #     defaults={
            #         "author_id": author,
            #         "title": request.data.get("title"),
            #         "description": request.data.get("description"),
            #         "content": request.data.get("content"),
            #         "content_type": request.data.get("contentType"),
            #         "visibility": request.data.get("visibility"),
            #     }
            # )
            # filter for post
            # if it exists, replace it with the new one
            post = Post.objects.filter(id=post_id).first()
            if post:
                post.author_id = author
                post.title = request.data.get("title")
                post.description = request.data.get("description")
                post.content = request.data.get("content")
                post.content_type = request.data.get("contentType")
                post.visibility = request.data.get("visibility")
                post.save()
                
                # Post already exists, return a message or existing post data
                return Response(
                    {"message": "Post already exists", "post": PostSerializer(post).data},
                    status=status.HTTP_200_OK
                )
            else:
                post = Post.objects.create(
                    id=post_id,
                    author_id=author,
                    title=request.data.get("title"),
                    description=request.data.get("description"),
                    content=request.data.get("content"),
                    content_type=request.data.get("contentType"),
                    visibility=request.data.get("visibility"),
                )
                serializer = PostSerializer(post)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            
        #endregion
        #region Comment Inbox
        elif object_type == "comment":
            response = handle_comment_inbox(request, author, author_id)
        
        elif object_type == "like":
            response = handle_like_inbox(request, author, author_id)
        
        else:
            return Response({"Error": f"What is a(n) {object_type}? I don't f with that, babe."}, status=status.HTTP_400_BAD_REQUEST)
        
        return response

class FollowRequests(APIView):
    """
    get follow requests for user
    """
    def get(self, request, author_id):
        author = get_object_or_404(Author, id=author_id)
        pending_follow_requests = Follows.objects.filter(followed_id=author, status='PENDING')

        serialized_data = FollowSerializer(pending_follow_requests, many=True).data
        for follow_data in serialized_data:
            follow_data['type'] = 'follow'
        return Response(serialized_data, status=200)