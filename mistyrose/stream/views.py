import requests
from requests.exceptions import RequestException
from urllib.parse import urljoin
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import FollowSerializer
from posts.serializers import CommentSerializer, LikeSerializer
from users.models import Author, Follows
from posts.models import Post, Like, Comment
from node.models import Node
from django.contrib.contenttypes.models import ContentType


class InboxView(APIView):
    def post(self, request, author_id):
        object_type = request.data.get('type')
        author = get_object_or_404(Author, id=author_id)

        # Ensure we are dealing with a follow request
        if object_type == "follow":
            serializer = FollowSerializer(data=request.data)
            actor_data = request.data.get('actor')
            object_data = request.data.get('object')

            # Check if actor_data and object_data exist
            if actor_data is None or 'id' not in actor_data:
                return Response({"error": "'actor' or 'actor.id' is missing from the request"}, status=status.HTTP_400_BAD_REQUEST)

            if object_data is None or 'id' not in object_data:
                return Response({"error": "'object' or 'object.id' is missing from the request"}, status=status.HTTP_400_BAD_REQUEST)

            # Extract actor_id and object_id safely
            actor_id = actor_data['id'].rstrip('/').split('/')[-1]
            object_id = object_data['id'].rstrip('/').split('/')[-1]
            
            existing_follow = Follows.objects.filter(
                local_follower_id=actor_id,
                followed_id=object_id
            ).first()

            if existing_follow:
                return Response(FollowSerializer(existing_follow).data, status=status.HTTP_200_OK)

            # If no follow request exists, validate and create a new one
            # If no follow request exists, validate and create a new one
            if serializer.is_valid():
                serializer.validated_data['local_follower_id']['id'] = actor_id
                serializer.validated_data['followed_id']['id'] = object_id
                serializer.save()

                # After creating locally, forward the request if the recipient is remote
                object_host = object_data.get("host")
                if object_host:
                    node = Node.objects.filter(host=object_host).first()
                    remote_inbox_url = urljoin(object_host, "inbox")  # Correct full URL
                    try:
                        response = requests.post(
                            remote_inbox_url,
                            json=serializer.data,
                            headers={"Authorization": f"Basic {node.username}:{node.password}"}
                        )
                        if response.status_code in [200, 201]:
                            return Response({"message": "Follow request forwarded successfully"}, status=status.HTTP_202_ACCEPTED)
                        else:
                            return Response(
                                {"error": "Failed to forward follow request", "details": response.text},
                                status=response.status_code
                            )
                    except RequestException as e:
                        return Response({"error": "Error forwarding follow request", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    return Response({"error": "Host is missing in the request"}, status=status.HTTP_400_BAD_REQUEST)

            return Response(serializer.data, status=status.HTTP_201_CREATED)


        # Comment Inbox
        elif object_type == "comment":
            author = get_object_or_404(Author, id=author_id)
            comment_data = request.data
            request_type = comment_data.get('type')

            if request_type != 'comment':
                return Response({"detail": "Must be 'comment' type"}, status=status.HTTP_400_BAD_REQUEST)

            post_url = comment_data.get("post")
            if not post_url:
                return Response({"Error": "Post URL is required."}, status=status.HTTP_400_BAD_REQUEST)

            post_id = post_url.rstrip('/').split("/posts/")[-1]
            post = get_object_or_404(Post, id=post_id)

            # Creating the comment object
            comment_serializer = CommentSerializer(data=request.data)
            if comment_serializer.is_valid():
                comment_serializer.save(
                    author_id=author,
                    post_id=post
                )

                return Response(comment_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(comment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Like Inbox
        elif object_type == "like":
            author = get_object_or_404(Author, id=author_id)
            like_data = request.data
            request_type = like_data.get('type')

            if request_type != 'like':
                return Response({"detail": "Must be 'like' type"}, status=status.HTTP_400_BAD_REQUEST)

            object_url = like_data.get("object")
            if not object_url:
                return Response({"Error": "object URL is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Determine if the like is for a post or comment
            if "/posts/" in object_url:
                object_id = object_url.rstrip('/').split("/posts/")[-1]
                liked_object = get_object_or_404(Post, id=object_id)
                object_content_type = ContentType.objects.get_for_model(Post)
            elif "/commented/" in object_url:
                object_id = object_url.rstrip('/').split("/commented/")[-1]
                liked_object = get_object_or_404(Comment, id=object_id)
                object_content_type = ContentType.objects.get_for_model(Comment)
            else:
                return Response({"detail": "Invalid object URL format."}, status=status.HTTP_400_BAD_REQUEST)

            # Check if user has already liked the object
            existing_like = Like.objects.filter(
                author_id=author,
                object_url=object_url
            ).first()

            if existing_like:
                return Response(LikeSerializer(existing_like).data, status=status.HTTP_200_OK)

            like_serializer = LikeSerializer(data=request.data)
            if like_serializer.is_valid():
                like_serializer.save(
                    author_id=author,
                    object_id=liked_object.id,
                    content_type=object_content_type,
                    object_url=object_url
                )

                # Forward like request if the post or comment is from a remote host
                post_host = object_url.split("//")[1].split("/")[0]
                if post_host != request.get_host():
                    # TODO: Forward to the remote inbox
                    pass

                return Response(like_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(like_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({"Error": "Object type does not exist"}, status=status.HTTP_400_BAD_REQUEST)


class FollowRequests(APIView):
    """
    Get follow requests for a user
    """
    def get(self, request, author_id):
        author = get_object_or_404(Author, id=author_id)
        pending_follow_requests = Follows.objects.filter(followed_id=author, status='PENDING')

        serialized_data = FollowSerializer(pending_follow_requests, many=True).data
        for follow_data in serialized_data:
            follow_data['type'] = 'follow'
        return Response(serialized_data, status=200)
