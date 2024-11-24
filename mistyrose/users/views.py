from django.shortcuts import render
import os
from node.authentication import NodeAuthentication
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, generics
from .models import Author 
from .serializers import AuthorSerializer, AuthorEditProfileSerializer, LoginSerializer 
from django.shortcuts import get_object_or_404  
from rest_framework.views import APIView  
from rest_framework.generics import ListAPIView  
from rest_framework.permissions import IsAuthenticated, AllowAny  
from rest_framework_simplejwt.tokens import RefreshToken  
from rest_framework_simplejwt.authentication import JWTAuthentication  
from django.contrib.auth.models import User  
from django.db import transaction  
from rest_framework.reverse import reverse 
from .models import Author, Follows  
from django.utils import timezone  
from django.conf import settings  
import uuid  
from posts.models import Post  
from django.middleware.csrf import get_token  
from django.contrib.auth import authenticate  
from django.http import HttpRequest
from .pagination import AuthorsPagination  
from posts.serializers import PostSerializer  
from uuid import UUID 
from users.utils import get_remote_authors
from urllib.parse import urlparse

# Default profile picture URL to be used when no image is provided
DEFAULT_PROFILE_PIC = "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png"

# Function to create an Author instance
def create_author(author_data, request, user):
    author_id = author_data.get('id', uuid.uuid4())  # Generate or get the UUID for the author
    host = request.build_absolute_uri('/')[:-1]  # Build the host
    #page_url = reverse('author-detail', kwargs={'pk': author_id}, request=request)  # Generate the URL for the author's page
    page_url = f"{host}/profile/{author_id}"
    author = Author.objects.create(  # Create the Author object
        id=author_id,
        host=host,
        display_name=author_data['displayName'],  # Set display name
        profile_image=author_data.get('profileImage', DEFAULT_PROFILE_PIC),  # Set the profile image or default one
        page=page_url,
        github=author_data.get('github', ''),  # Optional GitHub URL
        user=user  # Associate the Author with the created user
    )
    return author  # Return the newly created Author object

# View for handling login functionality
class LoginView(APIView):
    permission_classes = [AllowAny]  # No authentication required to access this view
    
    def post(self, request):
        # Deserialize and validate input data
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Retrieve username and password from the validated data
        username = serializer.validated_data.get("username")
        password = serializer.validated_data.get("password")
        
        # Authenticate the user
        user = authenticate(username=username, password=password)
        if user is None:
            return Response({"error": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.is_active:  # Check if the user is active
            return Response({"error": "User account is not activated. Please contact an admin."}, status=status.HTTP_403_FORBIDDEN)
        
        author_id = Author.objects.get(user=user).id  # Fetch the associated Author ID
        refresh = RefreshToken.for_user(user)  # Generate JWT refresh token for the user
        access_token = str(refresh.access_token)  # Get the access token from the refresh token
        
        # Return tokens and author_id in the response
        response = Response({
            "author_id": author_id,
            "refresh_token": str(refresh),
            "access_token": access_token
        }, status=status.HTTP_200_OK)

        # Set tokens in cookies for client-side usage (set to secure=False in this case)
        response.set_cookie(
            'author_id', 
            author_id, 
            httponly=True, 
            secure=False,  # Should be True in production when using HTTPS
            samesite='None',
            path='/'
        )
        response.set_cookie(
            'access_token', 
            access_token, 
            httponly=True, 
            secure=False, 
            samesite='None',
            path='/'
        )
        response.set_cookie(
            'refresh_token', 
            str(refresh), 
            httponly=True, 
            secure=False, 
            samesite='None',
            path='/'
        )

        return response  # Return the final response containing the tokens

# Signup view for user registration
class SignUpView(APIView):
    http_method_names = ["post"]  # Only POST requests allowed
    permission_classes = [AllowAny]  # No authentication required for signup

    def post(self, request):
        # Get required data from the request body
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")
        display_name = request.data.get("displayName")
        github = request.data.get("github", "")
        profile_image = request.data.get("profileImage", DEFAULT_PROFILE_PIC)

        # Validate that required fields are present
        if not all([username, email, password, display_name]):
            return Response(
                {"message": "Username, email, password, and displayName are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if the username is already taken
        if User.objects.filter(username=username).exists():
            return Response(
                {"message": "Username already exists."},
                status=status.HTTP_409_CONFLICT
            )
        
        try:
            # Use a transaction to ensure both user and author are created or rolled back if any issue occurs
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    is_active=False  # Set inactive until admin activates
                )
                user.date_joined = timezone.now()  # Set account creation time
                user.save()  # Save the User object
                
                # Create the corresponding Author object
                author_data = {
                    "displayName": display_name,
                    "profileImage": profile_image,
                    "github": github,
                }
                author = create_author(author_data, request, user)  # Call create_author to create the author
                
                # Serialize the author data to return it in the response
                serializer = AuthorSerializer(author, context={"request": request})
                
                response = Response(serializer.data, status=status.HTTP_201_CREATED)  # Return the serialized author
                return response
        except Exception as e:
            return Response(
                {"message": f"An error occurred: {str(e)}"},  # Handle any errors that occur
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# View for verifying if a JWT token is still valid
class VerifyTokenView(APIView):
    authentication_classes = [JWTAuthentication]  # Use JWT for authentication
    permission_classes = [IsAuthenticated]  # User must be authenticated

    def get(self, request):
        try:
            # Get the Author object associated with the user
            author = Author.objects.get(user=request.user)
            return Response({'authorId': str(author.id)}, status=200)  # Return the author's ID if found
        except Author.DoesNotExist:  # Return error if the author does not exist
            return Response({'error': 'Author not found'}, status=404)

# View to retrieve a specific author's details using the author ID (primary key)
class AuthorDetailView(generics.RetrieveAPIView):
    queryset = Author.objects.all()  # Specify the queryset of authors
    serializer_class = AuthorSerializer  # Use the AuthorSerializer for serialization
    lookup_field = 'pk'  # The lookup field used for retrieving a specific author is the primary key

'''
class AuthorProfileView(APIView):
    def get(self, request, pk):
        # Retrieve the author instance by primary key (pk)
        author = get_object_or_404(Author, pk=pk)
        
        # Use FriendsView to get the author's friends
        friends_view = FriendsView()
        friends_response = friends_view.get(request, author_id=pk)
        friends_data = friends_response.data.get('friends', [])

        # Calculate the number of friends based on the retrieved friends data
        friends_count = len(friends_data)
        
        # Get the count of followers (accepted follow requests)
        followers_count = Follows.objects.filter(followed_id=author, status='ACCEPTED').count()
        
        # Get the count of people the author is following (accepted follow requests)
        following_count = Follows.objects.filter(local_follower_id=author, status='ACCEPTED').count()
        
        # Retrieve posts by the author, filtered by visibility
        public_posts = Post.objects.filter(author_id=author, visibility='PUBLIC').order_by('-published')
        friends_posts = Post.objects.filter(author_id=author, visibility='FRIENDS').order_by('-published')
        unlisted_posts = Post.objects.filter(author_id=author, visibility='UNLISTED').order_by('-published')
        shared_posts = Post.objects.filter(author_id=author, visibility='SHARED').order_by('-published')

        # Serialize the author data
        author_serializer = AuthorSerializer(author)
        
        # Serialize the posts data
        public_post_serializer = PostSerializer(public_posts, many=True)
        friends_post_serializer = PostSerializer(friends_posts, many=True)
        unlisted_post_serializer = PostSerializer(unlisted_posts, many=True)
        shared_post_serializer = PostSerializer(shared_posts, many=True)
        
        # Prepare the response data
        data = author_serializer.data
        data['friends_count'] = friends_count
        data['followers_count'] = followers_count
        data['following_count'] = following_count
        data['public_posts'] = public_post_serializer.data
        data['friends_posts'] = friends_post_serializer.data
        data['unlisted_posts'] = unlisted_post_serializer.data
        data['shared_posts'] = shared_post_serializer.data
        
        # Return the prepared response
        return Response(data)
'''

class AuthorProfileView(APIView):
    def get_friends_count(self, request, pk):
        """Retrieve the count of mutual friends using FriendsView."""
        friends_view = FriendsView()
        friends_response = friends_view.get(request, pk=pk)
        return len(friends_response.data.get('friends', []))

    def get_follower_count(self, author):
        """Retrieve the count of followers with accepted follow requests."""
        return Follows.objects.filter(followed_id=author, status='ACCEPTED').count()

    def get_following_count(self, author):
        """Retrieve the count of authors that the user is following with accepted follow requests."""
        return Follows.objects.filter(local_follower_id=author, status='ACCEPTED').count()

    def get_author_posts(self, author, visibility):
        """Retrieve posts by visibility and serialize them."""
        return PostSerializer(
            Post.objects.filter(author_id=author, visibility=visibility).order_by('-published'), many=True
        ).data

    def get(self, request, pk):
        # Retrieve the author instance by primary key (pk)
        author = get_object_or_404(Author, pk=pk)
        
        # Serialize author data
        author_data = AuthorSerializer(author).data
        
        # Gather counts and categorized posts
        friends_count = self.get_friends_count(request, pk=pk)
        followers_count = self.get_follower_count(author)
        following_count = self.get_following_count(author)
        public_posts = self.get_author_posts(author, 'PUBLIC')
        friends_posts = self.get_author_posts(author, 'FRIENDS')
        unlisted_posts = self.get_author_posts(author, 'UNLISTED')
        shared_posts = self.get_author_posts(author, 'SHARED')
        
        # Prepare the response data
        data = {
            **author_data,
            'friends_count': friends_count,
            'followers_count': followers_count,
            'following_count': following_count,
            'public_posts': public_posts,
            'friends_posts': friends_posts,
            'unlisted_posts': unlisted_posts,
            'shared_posts': shared_posts,
        }
        
        return Response(data)

class AuthorEditProfileView(APIView):
    def get(self, request, pk):
        # Retrieve the author by primary key (pk)
        author = get_object_or_404(Author, pk=pk)
        
        # Serialize the author for editing profile purposes
        serializer = AuthorEditProfileSerializer(author)
        
        # Return the serialized data
        return Response(serializer.data)

    def put(self, request, pk):
        # Retrieve the author instance by primary key (pk)
        author = get_object_or_404(Author, pk=pk)
        
        # Deserialize and validate the incoming data
        serializer = AuthorEditProfileSerializer(author, data=request.data)
        if serializer.is_valid():
            # Save the validated data
            serializer.save()
            return Response(serializer.data)
        
        # Return validation errors if the data is not valid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthorsView(ListAPIView): #used ListAPIView because this is used to handle a collection of model instances AND comes with pagination
    authentication_classes = [NodeAuthentication, JWTAuthentication]
    #asked chatGPT how to get the authors using ListAPIView 2024-10-18
    # variables that ListAPIView needs
    # only get authors on our own node
    serializer_class = AuthorSerializer
    pagination_class = AuthorsPagination
    def get_queryset(self):
        # only get authors who are on this node
        request_host = self.request.get_host().rstrip('/')

        authors = Author.objects.all()
        authors = [author for author in authors if urlparse(author.host).netloc.rstrip('/') == request_host]
        
        return authors
    
    def get(self, request, *args, **kwargs): #args and kwargs for the page and size 
        #retrieve all profiles on the node (paginated)
        response = super().get(request, *args, **kwargs) #get provided by ListAPIView that queries database, serializes, and handles pagination

        #customize structure of response
        response.data = {
        "type": "authors",  
        "authors": response.data['results']  
        }

        return response
    
class GetRemoteAuthorsView(APIView): 
    # getting a consolidated list of remote authors from all nodes as well as the authors on this node
    #authentication_classes = [NodeAuthentication, JWTAuthentication]
    def get(self, request): 
        try:
            # Retrieve all profiles on the node (paginated)
            get_remote_authors(request)  # This saves them to the database
            
            # Fetch all authors from the database
            all_authors = Author.objects.all()
            print(f"ALL AUTHORS {all_authors}")
            if not all_authors:
                return Response({"error": "Something went wrong", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            serializer = AuthorSerializer(all_authors, many=True)
            print(f"SERIALIZER AUTHORS DATA: {serializer} aND DATA: {serializer.data}")
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            print(f"Error: {str(e)}")  
            
            return Response({"error": "Something went wrong", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class FollowerView(APIView):
    
    def get(self, request, author_id, follower_id):
        """
        Check if follower_id is a follower of author_id
        return 200 if following (accepted)
        return 202 if follow request pending (202 to indicate request is still in progress)
        return 404 if not following or requested
        """
        author = get_object_or_404(Author, id=author_id)

        # Check if the follow request has been accepted
        is_accepted = Follows.objects.filter(
            local_follower_id=follower_id, followed_id=author, status='ACCEPTED'
        ).exists()

        # Check if there's a pending follow request
        is_pending = Follows.objects.filter(
            local_follower_id=follower_id, followed_id=author, status='PENDING'
        ).exists()

        # Return appropriate response based on follower status
        if is_accepted:
            return Response({"status": "Following"}, status=status.HTTP_200_OK)

        if is_pending:
            return Response({"status": "Follow request pending"}, status=status.HTTP_202_ACCEPTED)

        # TODO: Update documentation!
        # Return 404 if follower not found or follow request doesn't exist
        return Response({"status": "Follow request not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, author_id, follower_id):        
        # get follow_request
        follow_request = Follows.objects.filter(followed_id=author_id, local_follower_id=follower_id).first()
        
        if not follow_request:
            return Response({"error": "Follow request not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # update status to "ACCEPTED"
        follow_request.status = 'ACCEPTED'
        follow_request.save()
        
        return Response({"status": "Follow request accepted"}, status=status.HTTP_200_OK)



    def delete(self, request, author_id, follower_id):
        
        # get follow_request
        follow_request = Follows.objects.filter(followed_id=author_id, local_follower_id=follower_id).first()

        if not follow_request:
            return Response({"error": "Follow request not found"}, status=status.HTTP_404_NOT_FOUND)

        
        # delete follow_request
        follow_request.delete()

        # second confirm whether the request has been deleted
        if Follows.objects.filter(id=follow_request.id).exists():
            print("Error: Follow request was not deleted!")
        else:
            print("Follow request deleted successfully")

        return Response({"status": "Follow request denied"}, status=status.HTTP_204_NO_CONTENT)




class UnfollowView(APIView):
    def delete(self, request, author_id, follower_id):
        try:
            # Validate UUID format
            author_id = UUID(author_id)
            follower_id = UUID(follower_id)
        except ValueError:
            return Response({'error': 'Invalid author or follower ID format.'}, status=400)
        
        try:
            # find corresponding follow relationship
            follow = Follows.objects.get(followed_id=author_id, local_follower_id=follower_id)
            
            # delete follow relationship
            follow.delete()
            return Response({'message': 'Successfully unfollowed the author.'}, status=200)
        
        except Follows.DoesNotExist:
            return Response({'error': 'Follow relationship does not exist.'}, status=404)

class FollowersDetailView(APIView):
    def get(self, request, pk):  # Add 'pk' parameter
        # Get the author based on the provided pk
        author = get_object_or_404(Author, id=pk)
        
        # Retrieve all followers who have an accepted follow request for the author
        followers = Follows.objects.filter(followed_id=author, status='ACCEPTED').select_related('local_follower_id')
        
        followers_data = [
            {
                "type": "author",
                "id": request.build_absolute_uri(f'/api/authors/{follower.local_follower_id.id}/'),  # Full URL for ID 
                "host": request.build_absolute_uri('/'),  # Builds the host URL dynamically
                "displayName": follower.local_follower_id.display_name, 
                "page": request.build_absolute_uri(f'/api/authors/{follower.local_follower_id.id}/'),
                "github": follower.local_follower_id.github,  # Assuming github is a field on the Author model
                "profileImage": follower.local_follower_id.profile_image if follower.local_follower_id.profile_image else None
            } 
            for follower in followers
        ]

        # Return the list of followers with HTTP 200 status
        return Response({
            "type": "followers",
            "followers": followers_data
        }, status=status.HTTP_200_OK)

class FollowingDetailView(APIView):
    def get(self, request, pk):  # Add 'pk' parameter for the current user's ID
        # Get the author based on the provided pk (the current user)
        author = get_object_or_404(Author, id=pk)
        
        # Retrieve all users that the author is following with accepted follow requests
        following = Follows.objects.filter(local_follower_id=author, status='ACCEPTED').select_related('followed_id')
        
        # Create a list of following users' details with additional fields
        following_data = [
            {
                "type": "author",
                "id": request.build_absolute_uri(f'/api/authors/{follow.followed_id.id}/'),  # Full URL for ID
                "host": request.build_absolute_uri('/'),  # Builds the host URL dynamically
                "displayName": follow.followed_id.display_name,
                "page": request.build_absolute_uri(f'/api/authors/{follow.followed_id.id}/'),
                "github": follow.followed_id.github,  # Assuming github is a field on the Author model
                "profileImage": follow.followed_id.profile_image if follow.followed_id.profile_image else None
            }
            for follow in following
        ]

        # Return the list of following users with HTTP 200 status
        return Response({
            "type": "following",
            "following": following_data
        }, status=status.HTTP_200_OK)

class FriendsView(APIView):

    def get(self, request, pk=None):
        # Get the current logged-in user (Author instance)
        current_user = get_object_or_404(Author, user=request.user)

        # Check if an author_id is provided, else use the current logged-in user as the viewed author
        if pk:
            viewed_author = get_object_or_404(Author, id=pk)
        else:
            viewed_author = current_user

        # Get all authors that the viewed author is following and the follow status is ACCEPTED
        following_ids = Follows.objects.filter(local_follower_id=viewed_author, status='ACCEPTED').values_list('followed_id', flat=True)
        
        # Get all authors who follow the viewed author and the follow status is ACCEPTED
        followers_ids = Follows.objects.filter(followed_id=viewed_author, status='ACCEPTED').values_list('local_follower_id', flat=True)

        # Find mutual friends by intersecting the sets of followers and followings
        mutual_friend_ids = set(following_ids).intersection(set(followers_ids))

        # Retrieve all mutual friends (Authors)
        friends = Author.objects.filter(id__in=mutual_friend_ids)

        # Create a list of friends' details with additional fields
        friends_data = [
            {
                "type": "author",
                "id": request.build_absolute_uri(f'/api/authors/{friend.id}/'),  # Full URL for ID
                "host": request.build_absolute_uri('/'),  # Builds the host URL dynamically
                "displayName": friend.display_name,
                "page": request.build_absolute_uri(f'/api/authors/{friend.id}/'),
                "github": friend.github,  # Assuming github is a field on the Author model
                "profileImage": friend.profile_image if friend.profile_image else None
            }
            for friend in friends
        ]

        # Return the list of friends with HTTP 200 status
        return Response({
            "type": "friends",
            "friends": friends_data
        }, status=status.HTTP_200_OK)
    
class ProfileImageUploadView(APIView):
    permission_classes = [AllowAny]  # Allow access without authentication

    def post(self, request, username):
        try:
            # Ensure the username is provided
            if not username:
                return Response({"error": "Username not provided."}, status=status.HTTP_400_BAD_REQUEST)

            # Check if a file (profile image) was uploaded in the request
            file = request.FILES.get('profile_image')
            if not file:
                return Response({"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

            # Create a unique file path for saving the image based on the username
            file_path = f'profiles/{username}/{file.name}'
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)

            # Ensure the directory exists (create if necessary)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            # Save the file to the media folder in chunks
            with open(full_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            # Construct the media URL for accessing the profile image via HTTP
            base_url = self.get_base_url(request)
            media_url = f'{base_url}{settings.MEDIA_URL}{file_path}'

            # Return a success message along with the image URL
            return Response({"message": "Profile image uploaded successfully", "url": media_url}, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle any errors and return a server error response
            return Response({"error": f"Failed to upload profile image: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_base_url(self, request: HttpRequest):
        """
        Generate the base URL (protocol + host) based on the request.
        """
        protocol = 'https' if request.is_secure() else 'http'
        host = request.get_host()  # This gives the hostname and port (if not default)
        return f'{protocol}://{host}'