from urllib.parse import unquote, urlparse
from .authentication import NodeAuthentication
from rest_framework.response import Response
from rest_framework.decorators import renderer_classes, permission_classes
from .models import Node
from .serializers import NodeSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from requests.auth import HTTPBasicAuth
import requests
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import AllowAny

class NodeListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get all nodes.
        """
        nodes = Node.objects.all()
        serializer = NodeSerializer(nodes, many=True)
        response = {
            "type": "nodes",
            "items": serializer.data,
        }
        return Response(response, status=status.HTTP_200_OK)

class NodeDetailView(APIView):
    authentication_classes = [NodeAuthentication]
    permission_classes = []
    
    def get(self, request):
        """
        Get a node.
        """
        node = get_object_or_404(Node, remote_node_url=request.data.get("host"))
        serializer = NodeSerializer(node)
        response = {
            "type": "node",
            "item": serializer.data,
        }
        return Response(response, status=status.HTTP_200_OK)
    
    def put(self, request):
        """
        Update a node.
        """
        node = get_object_or_404(Node, host=request.data.get("host"))
        serializer = NodeSerializer(node, data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = {
                "type": "node",
                "item": serializer.data,
            }
            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)