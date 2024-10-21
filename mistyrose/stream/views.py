from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import FollowSerializer
from .models import Inbox
from users.models import Author, Follows
from posts.models import Post, Like
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view


# Create your views here.
class InboxView(APIView):
    def post(self, request, author_id):
        object_type = request.data.get('type')
        author = get_object_or_404(Author, id=author_id)

        # Ensure we are dealing with a follow request
        if object_type == "follow":
            serializer = FollowSerializer(data=request.data)
            content_type = ContentType.objects.get_for_model(Follows)
        else:
            return Response({"Error": "Object type does not exist"}, status=400)

        # Retrieve actor and object data, and handle None case
        actor_data = request.data.get('actor')
        object_data = request.data.get('object')

        # Check if actor_data and object_data exist
        if actor_data is None or 'id' not in actor_data:
            return Response({"error": "'actor' or 'actor.id' is missing from the request"}, status=400)

        if object_data is None or 'id' not in object_data:
            return Response({"error": "'object' or 'object.id' is missing from the request"}, status=400)

        # Extract actor_id and object_id safely
        actor_id = actor_data['id'].rstrip('/').split('/')[-1]
        object_id = object_data['id'].rstrip('/').split('/')[-1]

        # Check if the follow request already exists
        existing_follow = Follows.objects.filter(
            local_follower_id=actor_id,
            followed_id=object_id
        ).first()

        if existing_follow:
            return Response(FollowSerializer(existing_follow).data, status=200)

        # If no follow request exists, validate and create a new one
        if serializer.is_valid():
            object_instance = serializer.save()

            # Create Inbox entry
            Inbox.objects.create(
                type=object_type,
                author=author,
                content_type=content_type,
                object_id=object_instance.id,
                content_object=object_instance
            )
            return Response(serializer.data, status=201)
        else:
            return Response(serializer.errors, status=400)

#local only TODO: need to document this is a new one for local use only
#TODO: only unique requests...
@api_view(['GET'])
def get_follow_requests(request, author_id):
    author = get_object_or_404(Author, id=author_id)
    follow_content_type = ContentType.objects.get_for_model(Follows)

    inbox_entries = Inbox.objects.filter(
        author=author, 
        content_type=follow_content_type,
        #asked chatGPT how to filter for PENDING status follow requests only 2024-10-19
        object_id__in=Follows.objects.filter(status='PENDING').values_list('id', flat=True))

    serialized_data = []
    for entry in inbox_entries:
        follow_data = FollowSerializer(entry.content_object).data
        follow_data['type'] = 'follow'
        serialized_data.append(follow_data)
    return Response(serialized_data, status=200)
