from django.urls import path
from . import views

urlpatterns = [
    path('api/authors/<str:author_id>/inbox', views.InboxView.as_view(), name="inbox")
]