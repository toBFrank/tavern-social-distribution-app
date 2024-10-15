from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response


# Create your views here.
class Inbox(APIView):
    def post(self, request, author_id):
        object_type = request.POST['type']

        if object_type == "post":
            pass

        elif object_type == "comment":
            pass

        elif object_type == "like":
            pass

        elif object_type == "follow":
            pass

        else:
            return Response({"Error":"Object type does not exist"}, status=400)