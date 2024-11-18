from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import FollowSerializer
from posts.serializers import CommentSerializer, LikeSerializer
from users.models import Author, Follows
from posts.models import Post, Like, Comment
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import renderer_classes, permission_classes
import requests
from django.conf import settings
from urllib.parse import urlparse
import logging

from node.models import Node

logger = logging.getLogger(__name__)
LOCAL_HOST_NAMES = ["http://127.0.0.1/",
                    "http://127.0.0.1:8000/"]

from requests.auth import HTTPBasicAuth
from urllib.parse import urlparse
import requests
import logging

logger = logging.getLogger(__name__)

def send_follow_request_to_remote_author(follow_request_data, author):
    """
    Send a follow request to a remote author's inbox, verifying the connection and whitelisting.

    Args:
        follow_request_data (dict): Serialized follow request data.
        author (Author): The remote Author object.

    Returns:
        dict: A response dictionary with the connection status and any errors.
    """
    try:
        # Get the node associated with the author's host
        node = Node.objects.get(host=author.host)
    except Node.DoesNotExist:
        logger.error(f"[ERROR]: Node for host {author.host} does not exist")
        return {"is_connected": False, "error": "Node does not exist locally"}

    # Ensure the node is whitelisted
    if not node.is_whitelisted:
        logger.error(f"[ERROR]: Node {node.host} is not whitelisted locally")
        node.is_authenticated = False
        node.save()
        return {"is_connected": False, "error": "Node is not whitelisted locally"}

    # Construct the remote API URL for connectivity check
    remote_node_url = f"{author.host}/api/node/"
    parsed_url = urlparse(node.host)
    local_host = f"{parsed_url.scheme}://{parsed_url.netloc}"

    try:
        # Verify connectivity with the remote node
        logger.info(f"[INFO]: Verifying connection to remote node at {remote_node_url}")
        response = requests.get(
            remote_node_url,
            params={"host": local_host},
            auth=HTTPBasicAuth(node.username, node.password),
        )
        response.raise_for_status()  # Raise an exception if the status code >= 400

        # Parse the response from the remote node
        remote_node_data = response.json().get("item")
        if not remote_node_data:
            logger.error(f"[ERROR]: Remote node {node.host} returned invalid data")
            node.is_authenticated = False
            node.save()
            return {"is_connected": False, "error": "Invalid response from remote node"}

        if not remote_node_data.get("is_whitelisted", False):
            logger.error(f"[ERROR]: Node {node.host} is not whitelisted remotely")
            node.is_authenticated = False
            node.save()
            return {"is_connected": False, "error": "Node is not whitelisted remotely"}

        # Update node's authentication status
        node.is_authenticated = True
        node.save()
        logger.info(f"[INFO]: Remote node {node.host} is connected and authenticated")

        # Send the follow request to the remote author's inbox
        follow_request_url = f"{author.url}/inbox/"
        logger.info(f"[INFO]: Sending follow request to {follow_request_url}")
        follow_response = requests.post(
            follow_request_url,
            json=follow_request_data,
            auth=HTTPBasicAuth(node.username, node.password),
        )
        if follow_response.status_code >= 400:
            logger.error(
                f"[ERROR]: Failed to send follow request to {author.url}, "
                f"Status: {follow_response.status_code}, Reason: {follow_response.reason}"
            )
            return {
                "is_connected": True,
                "error": f"Failed to send follow request: {follow_response.reason}",
            }
        else:
            logger.info(f"[SUCCESS]: Follow request sent to {author.url}")
            return {"is_connected": True}

    except requests.RequestException as e:
        logger.error(f"[ERROR]: Failed to verify/connect to remote node {node.host} - {str(e)}")
        node.is_authenticated = False
        node.save()
        return {"is_connected": False, "error": str(e)}

def is_local_author(author: Author):

    return author.host in LOCAL_HOST_NAMES


class InboxView(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self, request, author_id):
        object_type = request.data.get('type')
        author = get_object_or_404(Author, id=author_id)

        # Ensure we are dealing with a follow request
        #region Follow Inbox
        if object_type == "follow":
            serializer = FollowSerializer(data=request.data)

            # Retrieve actor and object data, and handle None case
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

            # Check if the follow request already exists
            existing_follow = Follows.objects.filter(
                local_follower_id=actor_id,
                followed_id=object_id
            ).first()

            if existing_follow:
                return Response(FollowSerializer(existing_follow).data, status=status.HTTP_200_OK)
            
            if not is_local_author:
                follow_request_data = serializer.validated_data
                send_follow_request_to_remote_author(follow_request_data, author)

            # If no follow request exists, validate and create a new one
            if serializer.is_valid():
                serializer.validated_data['local_follower_id']['id'] = actor_id
                serializer.validated_data['followed_id']['id'] = object_id
                serializer.save()

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        #endregion
        #region Comment Inbox
        elif object_type == "comment":
            author = get_object_or_404(Author, id=author_id) #author is the one who made the comment
            # we already get the post its supposed to be added to from the request body
            # TODO: need to make author if they don't exist from another node. not get object or 404

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
            
                return Response(comment_serializer.data, status=status.HTTP_201_CREATED)   
            else:
                return Response(comment_serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
        #endregion
        #region Like Inbox
        elif object_type == "like":
            #author who created the like
            author = get_object_or_404(Author, id=author_id)
        
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
        #endregion
        else:
            return Response({"Error": "Object type does not exist"}, status=status.HTTP_400_BAD_REQUEST)

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

