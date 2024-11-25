from django.urls import path
from .views import CommentByFQIDView

"""
for post urls that start with comment/ or commented
"""
urlpatterns = [
    path('<path:comment_fqid>/', CommentByFQIDView.as_view(), name='comment_fqid'),
]
