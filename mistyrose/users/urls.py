from django.urls import path
from .views import LoginView, SignUpView, AuthorDetailView, LogoutView,send_follow_request,manage_follow_request

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('authors/<uuid:pk>/', AuthorDetailView.as_view(), name='author-detail'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('service/api/authors/<uuid:AUTHOR_SERIAL>/inbox/', send_follow_request, name='send_follow_request'),
    path('service/api/authors/<uuid:AUTHOR_SERIAL>/followers/<path:FOREIGN_AUTHOR_FQID>/', manage_follow_request, name='manage_follow_request'),
]