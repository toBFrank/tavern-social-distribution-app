from rest_framework import serializers
from users.models import Author


class AuthorSerializer(serializers.Serializer):
    type = serializers.CharField(default='author', read_only=True)
    id = serializers.SerializerMethodField()  # Full API URL for the author
    host = serializers.URLField() # The full API URL for the author's node
    displayName = serializers.CharField(source='display_name')
    github = serializers.CharField(required=False, allow_null=True, allow_blank=True)  # URL of the user's GitHub
    profileImage = serializers.CharField(required=False, source='profile_image', allow_null=True, allow_blank=True)
    page = serializers.CharField(required=False, allow_null=True, allow_blank=True) 

    def get_id(self, author):
    # Constructs the URL based on the author's host and their UUID
       return f"{author.host.rstrip('/')}/api/authors/{author.id}/"
    
    # https://dev.to/amanbothra/understanding-the-torepresentation-and-tointernalvalue-methods-in-the-django-rest-framework-naa want 'type' to be in serialized output but not part of model
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['type'] = 'author'  # Add 'type' to the representation

         # Ensure fields match specification
        data['displayName'] = data.pop('displayName', None)
        data['profileImage'] = data.pop('profileImage', None)

        # Remove fields if they are empty or None to prevent error in follow requests with empty string fields
        if not data.get('github'):
            data.pop('github', None)
        if not data.get('profileImage'):
            data.pop('profileImage', None)
    
        return data
    
class AuthorEditProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['display_name', 'github', 'profile_image']  # Only fields you want to update
    
    def update(self, instance, validated_data):
        # Update the author instance with the provided validated data
        instance.display_name = validated_data.get('display_name', instance.display_name)
        instance.github = validated_data.get('github', instance.github)
        instance.profile_image = validated_data.get('profile_image', instance.profile_image)
        instance.save()  # Save the updated instance to the database
        return instance

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    