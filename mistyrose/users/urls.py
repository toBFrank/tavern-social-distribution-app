from django.urls import path
from .views import LoginView, SignUpView, AuthorDetailView, LogoutView ,FollowerView
from .views import AuthorProfileView, AuthorEditProfileView, AuthorsView


urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('authors/<uuid:pk>/', AuthorDetailView.as_view(), name='author-detail'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('service/api/authors/<str:author_id>/followers/<str:follower_id>/', FollowerView.as_view(), name='manage_follow_request'),
    path('authors/<uuid:pk>/profile/', AuthorProfileView.as_view(), name='author-profile'),
    path('authors/<uuid:pk>/profile/edit/', AuthorEditProfileView.as_view(), name='author-edit-profile'),
    path('api/authors/', AuthorsView.as_view(), name='authors-list'),
]
