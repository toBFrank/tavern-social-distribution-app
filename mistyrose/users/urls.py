from django.urls import path
from . import views
from .views import LoginView, signup, AuthorDetailView, LogoutView
from .views import AuthorProfileView,AuthorEditProfileView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('signup/', signup, name='signup'),
    path('authors/<uuid:pk>/', AuthorDetailView.as_view(), name='author-detail'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('authors/<uuid:pk>/profile/', AuthorProfileView.as_view(), name='author-profile'),
    path('authors/<uuid:pk>/profile/edit/', AuthorEditProfileView.as_view(), name='author-edit-profile'),
]