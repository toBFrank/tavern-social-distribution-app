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
        decoded_url = unquote(request.query_params.get("host"))
        print(f"Decoded URL: {decoded_url}")
        node = get_object_or_404(Node, host=decoded_url)
        serializer = NodeSerializer(node)
        response = {
            "type": "node",
            "item": serializer.data,
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
    
    def put(self, request):
        """
        Update a node.
        """
        remote_node_url = request.data.get("host")
        node = get_object_or_404(Node, host=remote_node_url)
        serializer = NodeSerializer(node, data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = {
                "type": "node",
                "item": serializer.data,
            }
            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        # likely won't use; just set is_whitelisted to False
        remote_node_url = request.data.get("host")
        node = get_object_or_404(Node, host=remote_node_url)
        node.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class NodeConnectView(APIView):
    """
    Connect to a node.
    """
    authentication_classes = []
    permission_classes = []
    
    # get an is_connected response
    def get(self, request):
        # gets the node from remote node (used for testing)
        
        # get local node by host in request url
        remote_node_url = request.data.get("host")
        local_node_of_remote = get_object_or_404(Node, host=remote_node_url)
        
        if not local_node_of_remote.is_whitelisted:
            local_node_of_remote.is_authenticated = False
            local_node_of_remote.save()
            return Response(
                {"is_connected": False, "error": "Node is not whitelisted locally"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            parsed_url = urlparse(request.build_absolute_uri())
            host_with_scheme = f"{parsed_url.scheme}://{parsed_url.netloc}"
            httpbasicauth = HTTPBasicAuth(local_node_of_remote.username, local_node_of_remote.password)
            print(f"host with scheme: {host_with_scheme}")
            print(f"local node of remote httpbasicauth: {httpbasicauth.username} {httpbasicauth.password}")
            response = requests.get(
                f"{remote_node_url}/api/node/",
                params={"host": host_with_scheme},
                auth=HTTPBasicAuth(local_node_of_remote.username, local_node_of_remote.password),
            )
            response.raise_for_status()  # Raise exception if >= 400                
            response_data = response.json()
            remote_node_data = response_data["item"]
            print(f"Remote node data: {remote_node_data}")
            if remote_node_data is None:
                local_node_of_remote.is_authenticated = False
                local_node_of_remote.save()
                return Response(
                    {"is_connected": False, "error": "Node does not exist"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            if remote_node_data["is_whitelisted"]:
                local_node_of_remote.is_authenticated = True
                local_node_of_remote.save()
                return Response(
                    {"is_connected": True},
                    status=status.HTTP_200_OK,
                )
            else:
                local_node_of_remote.is_authenticated = False
                local_node_of_remote.save()
                return Response(
                    {"is_connected": False, "error": "Node is not whitelisted remotely"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except requests.exceptions.RequestException as e:
            local_node_of_remote.is_authenticated = False
            local_node_of_remote.save()
            return Response(
                {"is_connected": False, "error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )