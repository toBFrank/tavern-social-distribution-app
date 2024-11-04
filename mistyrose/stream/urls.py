from django.urls import path
from .views import FollowRequests, InboxView

urlpatterns = [
    path('', InboxView.as_view(), name="inbox"),
    path('follow_requests/', FollowRequests.as_view(), name="follow_requests") 
]