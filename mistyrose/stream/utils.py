from urllib.parse import urlparse
import base64
import requests
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType

from users.models import Author, Follows
from node.models import Node
from posts.models import Post, Comment, Like
from .serializers import FollowSerializer
from posts.serializers import PostSerializer, CommentSerializer, LikeSerializer

def handle_follow_request(request, author):
  serializer = FollowSerializer(data=request.data)

  # Retrieve actor and object data, and handle None case
  actor_data = request.data.get('actor')
  object_data = request.data.get('object')
  print(object_data)
  # Check if actor_data and object_data exist
  if actor_data is None or 'id' not in actor_data:
      return Response({"error": "'actor' or 'actor.id' is missing from the request"}, status=status.HTTP_400_BAD_REQUEST)

  if object_data is None or 'id' not in object_data:
      return Response({"error": "'object' or 'object.id' is missing from the request"}, status=status.HTTP_400_BAD_REQUEST)

  # Extract actor_id and object_id safely
  actor_id = actor_data['id'].rstrip('/').split('/')[-1]
  object_id = object_data['id'].rstrip('/').split('/')[-1]
#   object_id = object_data['page'].rstrip('/').split('/')[-1]
  print(object_id)
  # Extract host information and normalize
  actor_host = urlparse(actor_data['host']).netloc  # Extracts only the netloc (e.g., "127.0.0.1:8000")
  object_host = urlparse(object_data['host'])
  object_hostn = urlparse(object_data['host']).netloc
  object_host_with_scheme = f"{object_host.scheme}://{object_host.netloc}"
  current_host = request.get_host()
  # Determine if actor is remote or local 
  print(f"actor_host: {actor_host} vs. current_host: {current_host}")
  is_remote_actor = actor_host != current_host

  if is_remote_actor:
      # Populate the `Author` table with remote `actor` details if it doesn't exist
      Author.objects.get_or_create(
          id=actor_id,
          defaults={
              "host": actor_data['host'],
              "display_name": actor_data.get('displayName'),
              "url": actor_data['id'],
              "github": actor_data.get('github', ""),
              "profile_image": actor_data.get('profileImage', ""),
              "page": actor_data.get('page', ""),
          }
      )

  # Determine if the `object` (followed author) is local or remote
  print(f"object_host: {object_hostn} vs. current_host: {current_host}")
  is_remote_object = object_hostn != current_host

  if is_remote_object:
      # node = Node.objects.get(host=str(object_host_with_scheme) + "/")
      node = Node.objects.filter(remote_node_url=object_host_with_scheme).first()
      if not node:
          return Response({"error": "Node not found"}, status=status.HTTP_404_NOT_FOUND)
      remote_inbox_url = f"{object_data['host'].rstrip('/')}/authors/{object_id}/inbox/"
      print(remote_inbox_url)
      parsed_url = urlparse(request.build_absolute_uri())
      host_with_scheme = f"{parsed_url.scheme}://{parsed_url.netloc}"
      credentials = f"{node.remote_username}:{node.remote_password}"
      base64_credentials = base64.b64encode(credentials.encode()).decode("utf-8")
      # 1. Send follow request to the remote node's inbox
      
      follow_request_payload = {
          "type": "follow",
          "summary": f"{actor_data['id']} wants to follow {object_data['id']}",  # Use ID for clarity
          "actor": actor_data,  # Send full actor data
          "object": object_data  # Send full object data
      }

      print(f"REQUEST remote_inbox_url: {remote_inbox_url} host_with_scheme: {host_with_scheme}")
      try:
          # Send POST request to the remote node
          response = requests.post(
              remote_inbox_url,
            #   params={"host": host_with_scheme},
              headers={"Authorization": f"Basic {base64_credentials}"},
              json=follow_request_payload,
          )
          if response.status_code not in [200, 201]:
              return Response({"error": f"Failed to send follow request to remote node {response}"}, status=status.HTTP_400_BAD_REQUEST)
      except requests.RequestException as e:
          return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

      # 2. Automatically accept the follow request locally
      local_follower = Author.objects.get(id=actor_id)  # Fetch local `actor`
      Follows.objects.create(
          local_follower_id=local_follower,  # Set local actor
          remote_follower_url=actor_data.get('id'),  # Store actor's full ID
          followed_id=author,
          status="ACCEPTED",
          is_remote=True  # Mark as a remote follow request
      )

      return Response({"message": "Follow request sent to remote node and accepted locally."}, status=status.HTTP_201_CREATED)

  else:
      # Local follow request handling
      serializer = FollowSerializer(data=request.data)
      existing_follow = Follows.objects.filter(
          local_follower_id=actor_id,
          followed_id=author,
      ).first()

      if existing_follow:
          return Response(FollowSerializer(existing_follow).data, status=status.HTTP_200_OK)

      if serializer.is_valid():
          serializer.validated_data['local_follower_id']['id'] = actor_id
          serializer.validated_data['followed_id']['id'] = object_id
          print("is_remote_actor:",is_remote_actor)
          if is_remote_actor:
            serializer.validated_data['is_remote'] = True
          serializer.save()
          return Response(serializer.data, status=status.HTTP_201_CREATED)
      else:
          print("error")
          return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def handle_post_inbox(request, post_author, author_id):
  # create post object type and user.
  author = get_object_or_404(Author, id=author_id) #author whose stream we want to add post to

  if request.data.get('visibility') == 'PUBLIC':
      # check if post's author in database, create author if not
      author_of_post = request.data["author"]["id"]
      author_of_post_id = author_of_post.rstrip('/').split("/authors/")[-1]

      author_data = request.data["author"]
      # get or create remote author who made the post
      post_author, created = Author.objects.get_or_create(
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
      author_of_post = request.data["author"]["id"]
      author_of_post_id = author_of_post.rstrip('/').split("/authors/")[-1]

      try:
          post_author = Author.objects.get(id=author_of_post_id)

          #check that they are actually friends
          are_friends = (
            Follows.objects.filter(local_follower_id=author, followed_id=post_author, status='ACCEPTED').exists() and #do you follow the poster's author?
            Follows.objects.filter(local_follower_id=post_author, followed_id=author, status='ACCEPTED').exists() #does poster follow you?
          )

          if not are_friends:
            return Response({"error": "Author is not a friend"}, status=status.HTTP_403_FORBIDDEN)
          
      except Author.DoesNotExist:
          return Response({"error": "Author is not a friend"}, status=status.HTTP_404_NOT_FOUND)
      
  elif request.data.get('visibility') == 'UNLISTED':
      #check if poster's author in database and actually friends (if friends, should already be in database)
      author_of_post = request.data["author"]["id"]
      author_of_post_id = author_of_post.rstrip('/').split("/authors/")[-1]

      try:
          post_author = Author.objects.get(id=author_of_post_id)

          is_follower = Follows.objects.filter(
                local_follower_id=author, followed_id=post_author, status='ACCEPTED'
            ).exists()
          if not is_follower:
                return Response(
                    {"error": "Current author is not following the post's author"},
                    status=status.HTTP_403_FORBIDDEN
                )
          
      except Author.DoesNotExist:
          return Response({"error": "Post author does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
      


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
      post.author_id = post_author
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
          author_id=post_author,
          title=request.data.get("title"),
          description=request.data.get("description"),
          content=request.data.get("content"),
          content_type=request.data.get("contentType"),
          visibility=request.data.get("visibility"),
      )
      serializer = PostSerializer(post)
      return Response(serializer.data, status=status.HTTP_201_CREATED)

def handle_comment_inbox(request, author, author_id):
    author = get_object_or_404(Author, id=author_id) #author is the one who made the comment
    # we already get the post its supposed to be added to from the request body
    # TODO: need to make author if they don't exist from another node. not get object or 404

    comment_data = request.data
    
    post_url = comment_data.get("post")
    if not post_url:
        return Response({"Error": "Post URL is required."}, status=status.HTTP_400_BAD_REQUEST)

    post_id = post_url.rstrip('/').split("/posts/")[-1]
    post = get_object_or_404(Post, id=post_id)

    # get author of commenter 
    author_of_comment = comment_data["author"]["id"]
    author_of_comment_id = author_of_comment.rstrip('/').split("/authors/")[-1]
    comment_id = comment_data["id"].rstrip('/').split('/commented/')[-1]

    author_data = request.data["author"]

    # get or create remote author who made the comment
    comment_author, created = Author.objects.get_or_create(
        id=author_of_comment_id,
        defaults={
            "host": author_data['host'],
            "display_name": author_data['displayName'],
            "github": author_data.get('github', ''),
            "profile_image": author_data.get('profileImage', ''),
            "page": author_data['page'],
        }
    )

    comment = Comment.objects.filter(id=comment_id).first()
    if not comment:
        #creating the comment object
        comment_serializer = CommentSerializer(data=request.data)
        if comment_serializer.is_valid():
            comment_serializer.save(
                id=comment_id,
                author_id=comment_author,
                post_id=post
            )
    
        return Response(comment_serializer.data, status=status.HTTP_201_CREATED) 
    else:
        comment_serializer = CommentSerializer(comment)
        return Response(comment_serializer.data, status=status.HTTP_200_OK)    
        
def handle_like_inbox(request, author, author_id):
    #author who created the like
    author = get_object_or_404(Author, id=author_id)

    like_data = request.data

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
    
    # get author of commenter 
    author_of_like = like_data["author"]["id"]
    author_of_like_id = author_of_like.rstrip('/').split("/authors/")[-1]

    author_data = request.data["author"]
    # get or create remote author who made the comment
    like_author, created = Author.objects.get_or_create(
        id=author_of_like_id,
        defaults={
            "host": author_data['host'],
            "display_name": author_data['displayName'],
            "github": author_data.get('github', ''),
            "profile_image": author_data.get('profileImage', ''),
            "page": author_data['page'],
        }
    )

    #check if user has already liked the object
    existing_like = Like.objects.filter(
        author_id=like_author,
        object_url=object_url
    ).first()

    if existing_like:
        return Response(LikeSerializer(existing_like).data, status=status.HTTP_200_OK) #if they've already liked, can't like again

    like_serializer = LikeSerializer(data=request.data) #asked chatGPT how to set the host in the serializer, need to add context 2024-11-02
    if like_serializer.is_valid():

        like_serializer.save(
            author_id=like_author,  
            object_id=liked_object.id,
            content_type=object_content_type,
            object_url=object_url
        )

        # #creating Inbox object to forward to correct inbox
        # post_host = object_url.split("//")[1].split("/")[0]
        # if post_host != request.get_host():
        #     # TODO: Part 3-5 post or comment not on our host, need to forward it to a remote inbox
        #     pass
        
        return Response(like_serializer.data, status=status.HTTP_201_CREATED)   
    else:
        return Response(like_serializer.errors, status=status.HTTP_400_BAD_REQUEST)