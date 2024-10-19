from django.urls import path
from .views import (
    CustomTokenRefreshView,
    LoginView,
    SignUpView,
    AuthorDetailView,
    LogoutView,
    AuthorProfileView,
    AuthorEditProfileView,
    VerifyTokenView,
    FollowerView, 
    AuthorsView
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),  # Use JWT for login
    path('refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),  # Token refresh endpoint
    path('verify/', VerifyTokenView.as_view(), name='verify-token'),  # Verify JWT token endpoint
    path('signup/', SignUpView.as_view(), name='signup'),  # User signup endpoint
    path('authors/<uuid:pk>/', AuthorDetailView.as_view(), name='author-detail'),  # Author detail view
    path('logout/', LogoutView.as_view(), name='logout'),  # User logout endpoint
    path('authors/<uuid:pk>/profile/', AuthorProfileView.as_view(), name='author-profile'),  # Author profile view
    path('authors/<uuid:pk>/profile/edit/', AuthorEditProfileView.as_view(), name='author-edit-profile'),  # Edit author profile
    path('service/api/authors/<str:author_id>/followers/<str:follower_id>/', FollowerView.as_view(), name='manage_follow_request'), 
    path('api/authors/', AuthorsView.as_view(), name='authors-list'),
]