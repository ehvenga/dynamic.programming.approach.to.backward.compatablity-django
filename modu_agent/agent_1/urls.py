# agent_1/urls.py

from django.urls import path
from .views import WebserviceDetailView, WebserviceListView

urlpatterns = [
    path('webservice/<str:servicenumber>/', WebserviceDetailView.as_view(), name='webservice-detail'),
    path('webservices/', WebserviceListView.as_view(), name='webservice-list'),
]
