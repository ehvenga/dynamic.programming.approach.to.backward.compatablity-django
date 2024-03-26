from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from django.http import JsonResponse
from django.forms.models import model_to_dict
from rest_framework import status
from django.core import serializers
from .models import Webservicelist, Inputparameter, Outputparameter, Parameterlist, Initialgoalparameter, Parameterhierarchy
from .serializers import WebservicelistSerializer, WebserviceslistSerializer, InputparameterSerializer, OutputparameterSerializer, ParameterlistSerializer, GenerateParametersSerializer

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
    
class ParametersListAPI(APIView):
    def get(self, request):
        # Fetch all Parameterlist objects
        parameters = Parameterlist.objects.all()

        # Serialize the queryset
        serializer = ParameterlistSerializer(parameters, many=True)

        # Return the serialized data as a JSON response
        return Response(serializer.data)
    


def parameters_dropdown_view(request):
    input_parameters = Inputparameter.objects.all()
    initial_goal_parameters = Initialgoalparameter.objects.all()
    context = {
        'input_parameters': input_parameters,
        'initial_goal_parameters': initial_goal_parameters,
    }
    return render(request, 's_agent_8/parameters_dropdown.html', context)

def find_parameter_chain(current_parameter, goal_parameter, visited=set()):
    if current_parameter == goal_parameter:
        return [current_parameter]
    
    visited.add(current_parameter)

    children = Parameterhierarchy.objects.filter(parentparameterid=current_parameter).exclude(childparameterid__in=visited)
    
    for child in children:
        path = find_parameter_chain(child.childparameterid, goal_parameter, visited)
        if path:
            return [current_parameter] + path

    return []

class GenerateParametersAPI(APIView):
    def post(self, request):
        serializer = GenerateParametersSerializer(data=request.data)

        if serializer.is_valid():
            initial_parameter = serializer.validated_data['initialParameter']
            goal_parameter = serializer.validated_data['goalParameter']

            parameter_chain = find_parameter_chain(initial_parameter, goal_parameter)

            if parameter_chain:
                return Response({'parameterChain': parameter_chain})
            else:
                return Response({'error': 'No path found from initial to goal parameter.'}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
