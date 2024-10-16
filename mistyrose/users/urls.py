from django.urls import path
from . import views

urlpatterns = [
    path('api/profile/', views.get_profile, name='get_profile'),  # GET request for profile
    path('api/profile/update/', views.update_profile, name='update_profile'),  # POST request to update profile
]