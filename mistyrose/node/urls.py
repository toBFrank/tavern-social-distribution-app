from django.urls import path

from .views import NodeListCreateView, NodeDetailView

urlpatterns = [
  path("list/", NodeListCreateView.as_view(), name="node-list-create"),
  path("", NodeDetailView.as_view(), name="node-detail"), 
]
