from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import AllowAny
from rest_framework import status
from .models import Node
from .serializers import NodeSerializer
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from base64 import b64decode

# Create your views here.
