from django.urls import path
from .views import WebserviceDetailView, WebserviceListView, InputparameterDetailView, OutputparameterDetailView, ParameterlistDetailView, parameters_dropdown_view
from .views import (WebserviceDetailAPI, WebserviceListAPI, InputparameterDetailAPI, OutputparameterDetailAPI, ParameterlistDetailAPI, ParametersListAPI, GenerateParametersAPI, FindWebServicesAPI)
from .views import (FindWebServicesV2API, FindWebServicesPathsAPI, FindWebChainsV2API, FindWebChainsV3API)

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
    path('api/parameters/', ParametersListAPI.as_view(), name='parameters_api'),
    path('api/generate-parameters/', GenerateParametersAPI.as_view(), name='generate_parameters_api'),
    path('api/find-webservices/', FindWebServicesAPI.as_view(), name='find_web_services'),

    path('api/find-webservices-paths/', FindWebServicesPathsAPI.as_view(), name='find_web_services_paths'),
    path('api/find-webservices-v2/', FindWebServicesV2API.as_view(), name='find_web_services_v2'),
    path('api/find-webchains-v2/', FindWebChainsV2API.as_view(), name='find_web_chains_v2'),

    path('api/find-webchains-v3/', FindWebChainsV3API.as_view(), name='find_web_chains_v3'),



    path('s_agent_8/', parameters_dropdown_view, name='parameters-dropdown'),
]
