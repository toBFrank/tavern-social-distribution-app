from django.urls import path
from .views import 

"""
for post urls that start with api/comment/
"""
urlpatterns = [
    path('<path:comment_fqid>/', LikedFQIDView.as_view(), name='liked_fqid'),
]
