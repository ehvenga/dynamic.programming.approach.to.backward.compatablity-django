from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from django.http import JsonResponse
from django.forms.models import model_to_dict
from rest_framework import status
from .models import Webservicelist, Inputparameter, Outputparameter, Parameterlist
from .serializers import WebservicelistSerializer, WebserviceslistSerializer, InputparameterSerializer, OutputparameterSerializer, ParameterlistSerializer

# Create your views here.

class WebserviceDetailView(APIView):
    def get(self, request, servicenumber):
        webservice = Webservicelist.objects.filter(webserviceid='wss'+servicenumber).first()
        if webservice:
            serializer = WebservicelistSerializer(webservice)
            return Response(serializer.data)
        else:
            return Response({'error': 'Webservice not found'}, status=status.HTTP_404_NOT_FOUND)
        
class WebserviceListView(ListAPIView):
    queryset = Webservicelist.objects.all()
    serializer_class = WebserviceslistSerializer

class InputparameterDetailView(ListAPIView):
    serializer_class = InputparameterSerializer

    def get_queryset(self):
        webservice_id = self.kwargs['webserviceId']
        return Inputparameter.objects.filter(webserviceid='wss'+webservice_id)

class OutputparameterDetailView(ListAPIView):
    serializer_class = OutputparameterSerializer

    def get_queryset(self):
        webservice_id = self.kwargs['webserviceId']
        return Outputparameter.objects.filter(webserviceid='wss'+webservice_id)

class ParameterlistDetailView(ListAPIView):
    serializer_class = ParameterlistSerializer

    def get_queryset(self):
        parameter_id = self.kwargs['parameterId']
        return Parameterlist.objects.filter(parameterid='p'+parameter_id)
    
class WebserviceDetailAPI(APIView):
    def get(self, request, servicenumber):
        webservice = Webservicelist.objects.filter(webserviceid='wss' + servicenumber).first()
        if webservice:
            data = model_to_dict(webservice)
            return JsonResponse(data)
        else:
            return JsonResponse({'error': 'Webservice not found'}, status=404)

class WebserviceListAPI(APIView):
    def get(self, request):
        webservices = Webservicelist.objects.all()
        data = list(webservices.values())
        return JsonResponse(data, safe=False)

class InputparameterDetailAPI(APIView):
    def get(self, request, webserviceId):
        inputparameters = Inputparameter.objects.filter(webserviceid='wss' + webserviceId)
        data = list(inputparameters.values())
        return JsonResponse(data, safe=False)

class OutputparameterDetailAPI(APIView):
    def get(self, request, webserviceId):
        outputparameters = Outputparameter.objects.filter(webserviceid='wss' + webserviceId)
        data = list(outputparameters.values())
        return JsonResponse(data, safe=False)

class ParameterlistDetailAPI(APIView):
    def get(self, request, parameterId):
        parameterlists = Parameterlist.objects.filter(parameterid='p' + parameterId)
        data = list(parameterlists.values())
        return JsonResponse(data, safe=False)
