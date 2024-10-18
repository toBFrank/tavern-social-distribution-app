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
from urllib.parse import unquote
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
        author_serializer = AuthorSerializer(author)
        post_serializer = PostSerializer(public_posts, many=True)
        data = author_serializer.data
        data['friends_count'] = friends_count
        data['followers_count'] = followers_count
        data['following_count'] = following_count
        data['public_posts'] = post_serializer.data
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

@api_view(['POST'])
def send_follow_request(request, AUTHOR_SERIAL):
    object_author = get_object_or_404(Author, id=AUTHOR_SERIAL)
    actor_data = request.data.get('actor')
    actor_id = actor_data.get('id')
    actor_author = get_object_or_404(Author, id=actor_id)
    follow_request = Follows.objects.create(local_follower_id=actor_author, followed_id=object_author, status='PENDING')
    Inbox.objects.create(type='follow', author=object_author, content_type=ContentType.objects.get_for_model(Follows), object_id=follow_request.id, content_object=follow_request)
    response_data = {
        "type": "follow",
        "summary": f"{actor_author.display_name} wants to follow {object_author.display_name}",
        "actor": {"type": "author", "id": str(actor_author.id), "host": actor_author.host, "displayName": actor_author.display_name, "github": actor_author.github, "profileImage": actor_author.profile_image},
        "object": {"type": "author", "id": str(object_author.id), "host": object_author.host, "displayName": object_author.display_name, "github": object_author.github, "profileImage": object_author.profile_image}
    }
    return Response(response_data, status=201)

@api_view(['PUT', 'DELETE'])
def manage_follow_request(request, AUTHOR_SERIAL, FOREIGN_AUTHOR_FQID):
    foreign_author_fqid_decoded = unquote(FOREIGN_AUTHOR_FQID)
    author = get_object_or_404(Author, id=AUTHOR_SERIAL)
    content_type = ContentType.objects.get_for_model(Follows)
    inbox_entry = Inbox.objects.filter(author=author, object_id=foreign_author_fqid_decoded, content_type=content_type).first()
    if not inbox_entry:
        return Response({"error": "Follow request not found"}, status=404)
    follow_request = inbox_entry.content_object
    if request.method == 'PUT':
        follow_request.status = 'ACCEPTED'
        follow_request.save()
        return Response({"status": "Follow request accepted"}, status=200)
    elif request.method == 'DELETE':
        follow_request.delete()
        inbox_entry.delete()
        return Response({"status": "Follow request denied"}, status=204)