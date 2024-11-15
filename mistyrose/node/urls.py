from django.urls import path

from .views import NodeListCreateView, NodeDetailView, NodeConnectView, NodeDisconnectView

urlpatterns = [
  path("", NodeListCreateView.as_view(), name="node-list-create"),
  path("<str:pk>/", NodeDetailView.as_view(), name="node-detail"),
  path("<str:pk>/connect/", NodeConnectView.as_view(), name="node-connect"),
  path("<str:pk>/disconnect/", NodeDisconnectView.as_view(), name="node-disconnect"),
]
