from django.urls import path
from .views import WebserviceDetailView, WebserviceListView, InputparameterDetailView, OutputparameterDetailView, ParameterlistDetailView
from .views import (WebserviceDetailAPI, WebserviceListAPI, InputparameterDetailAPI, OutputparameterDetailAPI, ParameterlistDetailAPI)


urlpatterns = [
    path('webservice/<str:servicenumber>/', WebserviceDetailView.as_view(), name='webservice-detail'),
    path('webservices/', WebserviceListView.as_view(), name='webservice-list'),
    path('inputparam/<str:webserviceId>/', InputparameterDetailView.as_view(), name='inputparameter-detail'),
    path('outputparam/<str:webserviceId>/', OutputparameterDetailView.as_view(), name='outputparameter-detail'),
    path('param/<str:parameterId>/', ParameterlistDetailView.as_view(), name='parameterlist-detail'),
    path('api/webservice/<str:servicenumber>/', WebserviceDetailAPI.as_view(), name='webservice-detail-api'),
    path('api/webservices/', WebserviceListAPI.as_view(), name='webservice-list-api'),
    path('api/inputparam/<str:webserviceId>/', InputparameterDetailAPI.as_view(), name='inputparameter-detail-api'),
    path('api/outputparam/<str:webserviceId>/', OutputparameterDetailAPI.as_view(), name='outputparameter-detail-api'),
    path('api/param/<str:parameterId>/', ParameterlistDetailAPI.as_view(), name='parameterlist-detail-api'),
]
