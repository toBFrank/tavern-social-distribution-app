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
            response = handle_post_a_post(request, author, author_id)
            return response
            
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