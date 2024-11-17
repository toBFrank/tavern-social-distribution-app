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
    authentication_classes = [NodeAuthentication]
    # permission_classes = [IsAuthenticated]
    
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
    # permission_classes = [IsAuthenticated]
    
    # get an is_connected response
    def get(self, request, pk):
        # gets the node from remote node (used for testing)
        
        local_node = get_object_or_404(Node, pk=pk)
        
        if not local_node.is_whitelisted:
            local_node.is_authenticated = False
            local_node.save()
            return Response(
                {"is_connected": False, "error": "Node is not whitelisted locally"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            response = requests.get(
                f"{local_node.host}/api/node/{pk}/",
                auth=HTTPBasicAuth(local_node.username, local_node.password),
            )
            response.raise_for_status()  # Raise exception if >= 400                
            response_data = response.json()
            remote_node_data = response_data["item"]
            print(f"Remote node data: {remote_node_data}")
            if remote_node_data is None:
                local_node.is_authenticated = False
                local_node.save()
                return Response(
                    {"is_connected": False, "error": "Node does not exist"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            if remote_node_data["is_whitelisted"]:
                local_node.is_authenticated = True
                local_node.save()
                return Response(
                    {"is_connected": True},
                    status=status.HTTP_200_OK,
                )
            else:
                local_node.is_authenticated = False
                local_node.save()
                return Response(
                    {"is_connected": False, "error": "Node is not whitelisted remotely"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except requests.exceptions.RequestException as e:
            local_node.is_authenticated = False
            local_node.save()
            return Response(
                {"is_connected": False, "error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )