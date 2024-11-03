from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    LoginView,
    SignUpView,
    AuthorDetailView,
    LogoutView,
    AuthorProfileView,
    AuthorEditProfileView,
    VerifyTokenView,
    ProfileImageUploadView
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),  # Use JWT for login
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),  # Refresh JWT token endpoint
    path('verify/', VerifyTokenView.as_view(), name='verify-token'),  # Verify JWT token endpoint
    path('signup/', SignUpView.as_view(), name='signup'),  # User signup endpoint
    path('api/authors/<uuid:pk>/', AuthorDetailView.as_view(), name='author-detail'),  # Author detail view
    path('logout/', LogoutView.as_view(), name='logout'),  # User logout endpoint
    path('api/authors/<uuid:pk>/profile/', AuthorProfileView.as_view(), name='author-profile'),  # Author profile view
    path('api/authors/<uuid:pk>/profile/edit/', AuthorEditProfileView.as_view(), name='author-edit-profile'),  # Edit author profile
    path('authors/<str:username>/upload_image/', ProfileImageUploadView.as_view(), name='upload-profile-image'),
]