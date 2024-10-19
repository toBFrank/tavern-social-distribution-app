from django.urls import path
from .views import LoginView, SignUpView, AuthorDetailView, LogoutView, manage_follow_request
from .views import AuthorProfileView, AuthorEditProfileView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('authors/<uuid:pk>/', AuthorDetailView.as_view(), name='author-detail'),
    path('logout/', LogoutView.as_view(), name='logout'),
    #path('service/api/authors/<uuid:AUTHOR_SERIAL>/inbox/send_follow_request', send_follow_request, name='send_follow_request'),
    path('service/api/authors/<uuid:AUTHOR_SERIAL>/followers/<path:FOREIGN_AUTHOR_FQID>/', manage_follow_request, name='manage_follow_request'),
    path('authors/<uuid:pk>/profile/', AuthorProfileView.as_view(), name='author-profile'),
    path('authors/<uuid:pk>/profile/edit/', AuthorEditProfileView.as_view(), name='author-edit-profile'),
]
