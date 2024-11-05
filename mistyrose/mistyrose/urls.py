"""
URL configuration for mistyrose project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path ,include, re_path
from django.urls import include, path
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.conf import settings
from posts.views import CommentedView, LikedView, LikesView
from django.views.generic import TemplateView


schema_view = get_schema_view(
    openapi.Info(
        title="MistyRose API Docs",
        default_version='v1',
        description="MistyRose Swagger style api",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/posts/', include('posts.urls')),
    path('api/authors/<uuid:author_id>/inbox/', include('stream.urls')),
    path('swagger', schema_view.with_ui('swagger', cache_timeout=0), name="swagger"),
    path('api/', include('users.urls')),
    path('api/authors/', include('posts.authors_urls')), #api/authors/ urls for posts, likes, comments
    path('api/authors/', include('users.authors_urls')), #api/authors/ for urls like following and authors
    path('api/liked/', include('posts.liked_urls')), #api/liked urls
    path('api/comment/', include('posts.comment_urls')), #api/comment urls
    path('api/commented/', include('posts.comment_urls')), #TODO: asked if there is an error in the project description, is this supposed to be the same one as the comments/comment_fqid?  
    re_path(r"^(?:.*)?$", TemplateView.as_view(template_name="index.html"))
]

if settings.DEBUG:  # Only serve media files in development mode
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)