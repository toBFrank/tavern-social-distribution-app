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
    # after creating the necessary follow/like/comment/post object, Inbox object will also be created with a generic foreign key to keep track of whats in the inbox
    def post(self, request, author_id): #author id of the person's Inbox 
        object_type = request.data.get('type')
        author = get_object_or_404(Author, id=author_id) 

        #TODO: FILL IN FOR NECESSARY PARTS
        # if object_type == "post":
        #     serializer = PostSerializer(data=request.data) 
        #     content_type = ContentType.objects.get_for_model(Post)

        # elif object_type == "comment":
        #     serializer = CommentSerializer(data=request.data) 
        #     content_type = ContentType.objects.get_for_model(Follows)

        # elif object_type == "like":
        #     serializer = LikeSerializer(data=request.data) 
        #     content_type = ContentType.objects.get_for_model(Like) 

        #follow request 
        if object_type == "follow":
            #TODO: shouldn't allow creating the same follow request multiple times.
            serializer = FollowSerializer(data=request.data)
            content_type = ContentType.objects.get_for_model(Follows)

        else:
            return Response({"Error":"Object type does not exist"}, status=400)
        
        #want to return 200 if they already request, but don't create another follow request
        actor_data = request.data.get('actor')
        object_data = request.data.get('object')
        actor_id = actor_data['id'].rstrip('/').split('/')[-1] 
        object_id = object_data['id'].rstrip('/').split('/')[-1] 

        #asked chatGPT how to filter for a table 2024-10-19
        existing_follow = Follows.objects.filter(
            local_follower_id=actor_id,
            followed_id=object_id
        ).first()

        if existing_follow:
            return Response(FollowSerializer(existing_follow).data, status=200)
        
        #if no follow request created already, create entry
        if serializer.is_valid():
            object_instance = serializer.save()
            
            #create Inbox entry
            Inbox.objects.create(
                type=object_type,
                author=author,
                content_type=content_type,
                object_id=object_instance.id, # assumes Follow, Comment, Like, Post all have id
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
