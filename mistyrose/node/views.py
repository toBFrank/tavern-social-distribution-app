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
    
    def post(self, request):
        """
        Create a new node.
        """
        serializer = NodeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = {
                "type": "node",
                "item": serializer.data,
            }
            return Response(response, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NodeDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        """
        Get a node.
        """
        node = get_object_or_404(Node, pk=pk)
        serializer = NodeSerializer(node)
        response = {
            "type": "node",
            "item": serializer.data,
        }
        return Response(response, status=status.HTTP_200_OK)
    
    def put(self, request, pk):
        """
        Update a node.
        """
        node = get_object_or_404(Node, pk=pk)
        serializer = NodeSerializer(node, data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = {
                "type": "node",
                "item": serializer.data,
            }
            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        # likely won't use; just use node disconnect?
        node = get_object_or_404(Node, pk=pk)
        node.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class NodeConnectView(APIView):
    """
    Connect to a node.
    """
    authentication_classes = [NodeAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        node = get_object_or_404(Node, pk=pk)
        if node.is_whitelisted:
            try:
                response = requests.get(
                    f"{node.host}/api/node/connect",
                    auth=HTTPBasicAuth(node.username, node.password)
                )
                response.raise_for_status()  # raises exception if >= 400
                node.is_authenticated = True
                node.save()
                # in body, should have is connected or not
                return Response({"is_connected": True}, status=status.HTTP_200_OK)
            except requests.exceptions.RequestException as e:
                node.is_authenticated = False
                node.save()
                return Response({"is_connected": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        node.is_authenticated = False
        node.save()
        return Response({"is_connected": False, "error": "Node is not whitelisted"}, status=status.HTTP_400_BAD_REQUEST)
                
class NodeDisconnectView(APIView):
    """
    Disconnect from a node.
    """
    authentication_classes = [NodeAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request, pk):
        node = get_object_or_404(Node, pk=pk)
        node.is_whitelisted = False
        node.save()
        return Response({"is_disconnected": True}, status=status.HTTP_200_OK)