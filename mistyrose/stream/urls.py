from django.urls import path
from . import views

urlpatterns = [
    path('api/authors/<str:author_id>/inbox', views.Inbox.as_view(), name="inbox")
]