from django.urls import path
from . import views

urlpatterns = [
    path('api/authors/<str:author_id>/inbox', views.InboxView.as_view(), name="inbox"),
    path('api/authors/<str:author_id>/inbox/follow_requests', views.get_follow_requests, name="follow_requests") #TODO: might be temporary depending on when stream gets implemented
]