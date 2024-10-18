from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, generics
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework.reverse import reverse
from .models import Author,Follows
from .serializers import AuthorSerializer
from django.utils import timezone
from django.conf import settings
import uuid
from stream.models import Inbox
from django.contrib.contenttypes.models import ContentType
from urllib.parse import unquote

DEFAULT_PROFILE_PIC = "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png"

def create_author(author_data, request, user):
    """
    Creates an Author instance linked to the given user.
    """
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
        user=user  # Link to the User
    )
    return author

class LoginView(APIView):
    http_method_names = ["post"]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            return Response(
                {"message": "Username and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(username=username)
            if user.is_active:
                if user.check_password(password):
                    # Update last_login timestamp
                    user.last_login = timezone.now()
                    user.save()

                    token, created = Token.objects.get_or_create(user=user)
                    
                    author = user.author  
                    serializer = AuthorSerializer(author, context={"request": request})
                    data = {
                        "token": token.key,
                        "author": serializer.data
                    }
                    return Response(data, status=status.HTTP_200_OK)
                else:
                    return Response(
                        {"message": "Wrong password."},
                        status=status.HTTP_401_UNAUTHORIZED
                    )
            else:
                return Response(
                    {"message": "User is not activated yet."},
                    status=status.HTTP_403_FORBIDDEN
                )
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
                    is_active=False  # Set to False to require activation
                )
                
                # Set date_joined when the user is created
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
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def post(self, request):
        try:
            # Get the token associated with the request
            token = Token.objects.get(user=request.user)
            token.delete()  # Delete the token
            
            return Response(
                {"message": "Logged out successfully."},
                status=status.HTTP_200_OK
            )
        except Token.DoesNotExist:
            return Response(
                {"message": "User is already logged out."},
                status=status.HTTP_400_BAD_REQUEST
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

@api_view(['POST'])
def send_follow_request(request, AUTHOR_SERIAL):
    #Obtain the author who receives the follow request (AuthOR_SERIAL)
    object_author = get_object_or_404(Author, id=AUTHOR_SERIAL)

    #Retrieve the author (actor) who initiated the follow request
    actor_data = request.data.get('actor')
    actor_id = actor_data.get('id')
    actor_author = get_object_or_404(Author, id=actor_id)

    #Create a new follow request (Pending status)
    follow_request = Follows.objects.create(
        local_follower_id=actor_author,
        followed_id=object_author,
        status='PENDING'
    )

    #Create an Inbox entry
    Inbox.objects.create(
        type='follow',
        author=object_author,
        content_type=ContentType.objects.get_for_model(Follows),
        object_id=follow_request.id,
        content_object=follow_request
    )
    #print(f"Inbox entry created with object_id: {follow_request.id}")

    #Construct response
    response_data = {
        "type": "follow",
        "summary": f"{actor_author.display_name} wants to follow {object_author.display_name}",
        "actor": {
            "type": "author",
            "id": str(actor_author.id),
            "host": actor_author.host,
            "displayName": actor_author.display_name,
            "github": actor_author.github,
            "profileImage": actor_author.profile_image,
        },
        "object": {
            "type": "author",
            "id": str(object_author.id),
            "host": object_author.host,
            "displayName": object_author.display_name,
            "github": object_author.github,
            "profileImage": object_author.profile_image,
        }
    }

    return Response(response_data, status=201)

@api_view(['PUT', 'DELETE'])
def manage_follow_request(request, AUTHOR_SERIAL, FOREIGN_AUTHOR_FQID):
    # 解码 FOREIGN_AUTHOR_FQID
    foreign_author_fqid_decoded = unquote(FOREIGN_AUTHOR_FQID)
    #print(f"Decoded FOREIGN_AUTHOR_FQID: {foreign_author_fqid_decoded}")

    #Get followed authors
    author = get_object_or_404(Author, id=AUTHOR_SERIAL)

    #Get the current ContentType
    content_type = ContentType.objects.get_for_model(Follows)
    #print(f"ContentType for Follows: {content_type}")

    # #Print all Inbox entries
    # inbox_entries = Inbox.objects.all()
    # print(f"All Inbox entries: {[{'object_id': entry.object_id, 'content_type': entry.content_type} for entry in inbox_entries]}")

    #Search for Inbox entries
    inbox_entry = Inbox.objects.filter(author=author, object_id=foreign_author_fqid_decoded, content_type=content_type).first()
    #print(f"Inbox entry found: {inbox_entry}")

    if not inbox_entry:
        return Response({"error": "Follow request not found"}, status=404)

    #Get the corresponding follow_dequest object
    follow_request = inbox_entry.content_object
    #print(f"Follow request found: {follow_request}")

    #Processing PUT requests: approving requests
    if request.method == 'PUT':
        follow_request.status = 'ACCEPTED'
        follow_request.save()
        return Response({"status": "Follow request accepted"}, status=200)

    #Processing DELETE request: Reject request
    elif request.method == 'DELETE':
        follow_request.delete()  #Delete follow request
        inbox_entry.delete()  #Remove from Inbox
        return Response({"status": "Follow request denied"}, status=204)




