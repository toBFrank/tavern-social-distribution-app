from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Author
from .serializers import AuthorSerializer

@api_view(['GET'])
def get_profile(request):
    try:
        author = Author.objects.get(id=request.user.id)
        serializer = AuthorSerializer(author)
        return Response(serializer.data)
    except Author.DoesNotExist:
        return Response({"detail": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
    

@api_view(['POST'])
def update_profile(request):
    try:
        author = Author.objects.get(id=request.user.id)
        serializer = AuthorSerializer(author, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Author.DoesNotExist:
        return Response({"detail": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
