from django.urls import path
from .views import LikeViewByFQIDView

"""
for post urls that start with liked/
"""
urlpatterns = [
    path('<path:like_fqid>/', LikeViewByFQIDView.as_view(), name='get_like_fqid')
]
