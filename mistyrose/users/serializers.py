from rest_framework import serializers
from .models import Author 

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        # Adjusting fields based on your feedback
        fields = ['display_name', 'github', 'profile_image']  

    # Optional: Only include 'page' if it's a valid public profile link
    # Need to check if we need it or not
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.page:  # If 'page' field is populated, include it
            data['page'] = instance.page
        return data