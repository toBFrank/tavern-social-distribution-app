from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import FollowSerializer


# Create your views here.
class Inbox(APIView):
    def post(self, request, author_id):
        object_type = request.POST['type']

        if object_type == "post":
            serializer = PostSerializer(data=request.data) #TODO: import the Serializer after its created

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=201)

        elif object_type == "comment":
            serializer = CommentSerializer(data=request.data) #TODO:import the Serializer after its created 

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=201)

        elif object_type == "like":
            serializer = LikeSerializer(data=request.data) #TODO: import the Serializer after its created

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=201)

        #follow request 
        elif object_type == "follow":
            serializer = FollowSerializer(data=request.data) #TODO: after users app is created, import the FollowSerializer, for now its in this folder

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=201)

        else:
            return Response({"Error":"Object type does not exist"}, status=400)