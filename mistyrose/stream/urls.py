from django.urls import path
from . import views

urlpatterns = [
    path('', views.InboxView.as_view(), name="inbox"),
    path('follow_requests/', views.get_follow_requests, name="follow_requests") #TODO: might be temporary depending on when stream gets implemented
]