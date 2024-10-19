from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, generics
from .models import Author
from .serializers import AuthorSerializer, AuthorEditProfileSerializer
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework.reverse import reverse
from .models import Author, Follows
from django.utils import timezone
from django.conf import settings
import uuid
from stream.models import Inbox
from django.contrib.contenttypes.models import ContentType
from posts.models import Post
from .serializers import PostSerializer

DEFAULT_PROFILE_PIC = "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png"

def create_author(author_data, request, user):
    author_id = author_data.get('id', uuid.uuid4())
    host = request.build_absolute_uri('/')[:-1]  
    page_url = reverse('author-detail', kwargs={'pk': author_id}, request=request)
    author = Author.objects.create(
        id=author_id,
        host=host,
        display_name=author_data['displayName'],
        profile_image=author_data.get('profileImage', DEFAULT_PROFILE_PIC),
        page=page_url,
        github=author_data.get('github', ''),
        user=user
    )
    return author

class LoginView(APIView):
    http_method_names = ["post"]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        
        if not username or not password:
            return Response({"message": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(username=username)
            if user.is_active:
                if user.check_password(password):
                    user.last_login = timezone.now()
                    user.save()
                    refresh = RefreshToken.for_user(user)
                    author = user.author  
                    serializer = AuthorSerializer(author, context={"request": request})
                    data = {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                        "author": serializer.data
                    }
                    return Response(data, status=status.HTTP_200_OK)
                else:
                    return Response({"message": "Wrong password."}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({"message": "User is not activated yet."}, status=status.HTTP_403_FORBIDDEN)
        except User.DoesNotExist:
            return Response(
                {"message": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )  

class SignUpView(APIView):
    http_method_names = ["post"]
    
    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")
        display_name = request.data.get("displayName")
        github = request.data.get("github", "")
        profile_image = request.data.get("profileImage", DEFAULT_PROFILE_PIC)

        if not all([username, email, password, display_name]):
            return Response(
                {"message": "Username, email, password, and displayName are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if User.objects.filter(username=username).exists():
            return Response(
                {"message": "Username already exists."},
                status=status.HTTP_409_CONFLICT
            )
        
        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    is_active=False  
                )
                user.date_joined = timezone.now()
                user.save()
                
                author_data = {
                    "displayName": display_name,
                    "profileImage": profile_image,
                    "github": github,
                }
                author = create_author(author_data, request, user)
                serializer = AuthorSerializer(author, context={"request": request})
                
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]  

    def post(self, request):
        try:
            request.user.tokens().blacklist()
            return Response(
                {"message": "Logged out successfully."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AuthorDetailView(generics.RetrieveAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    lookup_field = 'pk'

class AuthorProfileView(APIView):
    def get(self, request, pk):
        author = get_object_or_404(Author, pk=pk)
        friends_count = Follows.objects.filter(local_follower_id=author, status='ACCEPTED').count()
        followers_count = Follows.objects.filter(followed_id=author, status='ACCEPTED').count()
        following_count = Follows.objects.filter(local_follower_id=author, status='ACCEPTED').count()
        public_posts = Post.objects.filter(author_id=author, visibility='PUBLIC').order_by('-published')
        friends_posts = Post.objects.filter(author_id=author, visibility='FRIENDS').order_by('-published')
        unlisted_posts = Post.objects.filter(author_id=author, visibility='UNLISTED').order_by('-published')
        author_serializer = AuthorSerializer(author)
        # Serialize posts
        public_post_serializer = PostSerializer(public_posts, many=True)
        friends_post_serializer = PostSerializer(friends_posts, many=True)
        unlisted_post_serializer = PostSerializer(unlisted_posts, many=True)
        # Prepare the response data
        data = author_serializer.data
        data['friends_count'] = friends_count
        data['followers_count'] = followers_count
        data['following_count'] = following_count
        data['public_posts'] = public_post_serializer.data
        data['friends_posts'] = friends_post_serializer.data
        data['unlisted_posts'] = unlisted_post_serializer.data
        return Response(data)

class AuthorEditProfileView(APIView):
    def get(self, request, pk):
        author = get_object_or_404(Author, pk=pk)
        serializer = AuthorEditProfileSerializer(author)
        return Response(serializer.data)

    def put(self, request, pk):
        author = get_object_or_404(Author, pk=pk)
        serializer = AuthorEditProfileSerializer(author, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FollowerView(APIView):
    
    # def get(self, request, author_id, follower_id):
    #     """
    #     Check if follower_id is a follower of author_id
    #     """
    #     author = get_object_or_404(Author, id=author_id)

    #     # Check follow status using the remote URL
    #     follow_status = Follows.objects.filter(remote_follower_url=follower_id, followed_id=author, status='ACCEPTED').exists()

    #     if follow_status:
    #         print("Follower exists")
    #         return Response({"status": "Follower exists"}, status=status.HTTP_200_OK)
    #     print("Follower not found")
    #     return Response({"error": "Follower not found"}, status=status.HTTP_404_NOT_FOUND)


    def put(self, request, author_id, follower_id):
        print(f"Received Author ID: {author_id}, Received Follower ID: {follower_id}")
        
        # get follow_request
        follow_request = Follows.objects.filter(followed_id=author_id, local_follower_id=follower_id).first()
        
        if not follow_request:
            print("Follow request not found in database for PUT")
            return Response({"error": "Follow request not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # update status to "ACCEPTED"
        follow_request.status = 'ACCEPTED'
        follow_request.save()
        
        # delete corresponding inbox_entry
        content_type = ContentType.objects.get_for_model(Follows)
        inbox_entry = Inbox.objects.filter(author__id=author_id, object_id=follow_request.id, content_type=content_type).first()
        
        if inbox_entry:
            print(f"Deleting Inbox entry: {inbox_entry}")
            inbox_entry.delete()
        else:
            print("Inbox entry not found")
        
        return Response({"status": "Follow request accepted"}, status=status.HTTP_200_OK)



    def delete(self, request, author_id, follower_id):
        print(f"Received Author ID: {author_id}, Received Follower ID: {follower_id}")
        
        # get follow_request
        follow_request = Follows.objects.filter(followed_id=author_id, local_follower_id=follower_id).first()

        if not follow_request:
            print("Follow request not found in database")
            return Response({"error": "Follow request not found"}, status=status.HTTP_404_NOT_FOUND)

        # delete inbox_entry
        content_type = ContentType.objects.get_for_model(Follows)
        inbox_entry = Inbox.objects.filter(author__id=author_id, object_id=follow_request.id, content_type=content_type).first()

        if inbox_entry:
            print(f"Found Inbox entry: {inbox_entry}")
            inbox_entry.delete()

        print(f"Deleting Follow Request: {follow_request.id}")
        
        # delete follow_request
        follow_request.delete()

        # second confirm whether the request has been deleted
        if Follows.objects.filter(id=follow_request.id).exists():
            print("Error: Follow request was not deleted!")
        else:
            print("Follow request deleted successfully")

        return Response({"status": "Follow request denied"}, status=status.HTTP_204_NO_CONTENT)

