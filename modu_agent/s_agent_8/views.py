from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from django.http import JsonResponse
from django.forms.models import model_to_dict
from rest_framework import status
from django.core import serializers
from collections import deque
from .models import Webservicelist, Inputparameter, Outputparameter, Parameterlist, Initialgoalparameter, Parameterhierarchy
from .serializers import WebservicelistSerializer, WebserviceslistSerializer, InputparameterSerializer, OutputparameterSerializer, ParameterlistSerializer, GenerateParametersSerializer,WebServiceChainSerializer

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
    
def find_web_service_chain(initial_parameter, goal_parameter, path=[]):
    # Find web services that produce the initial parameter as an output
    initial_services = Outputparameter.objects.filter(parameterid=initial_parameter)
    
    for service in initial_services:
        # Avoid cycles
        if service.webserviceid in [p['id'] for p in path]:
            continue
        
        # If the current service's output is the goal, return the path
        if goal_parameter in Outputparameter.objects.filter(webserviceid=service.webserviceid).values_list('parameterid', flat=True):
            return path + [{'id': service.webserviceid, 'name': Webservicelist.objects.get(webserviceid=service.webserviceid).webservicename}]
        
        # Otherwise, continue searching through services that take the current service's output as their input
        next_services = Inputparameter.objects.filter(parameterid=service.parameterid).exclude(webserviceid=service.webserviceid)
        
        for next_service in next_services:
            new_path = find_web_service_chain(next_service.parameterid, goal_parameter, path + [{'id': service.webserviceid, 'name': Webservicelist.objects.get(webserviceid=service.webserviceid).webservicename}])
            if new_path:
                return new_path

    return []

# class FindWebServicesAPI(APIView):
#     def post(self, request):
#         serializer = WebServiceChainSerializer(data=request.data)

#         if serializer.is_valid():
#             initial_parameter = serializer.validated_data['initialParameter']
#             goal_parameter = serializer.validated_data['goalParameter']

#             web_service_chain = find_web_service_chain(initial_parameter, goal_parameter)

#             if web_service_chain:
#                 return Response({'webServiceChain': web_service_chain})
#             else:
#                 return Response({'error': 'No chain found connecting initial to goal parameter.'}, status=404)

#         return Response(serializer.errors, status=400)
    
def find_web_service_chain_bfs(initial_parameter, goal_parameter):
    # Queue for BFS, each element is a tuple (current_parameter, path)
    queue = deque([(initial_parameter, [])])
    
    # Set to keep track of visited parameters to avoid cycles
    visited = set()

    while queue:
        current_parameter, path = queue.popleft()

        # Check if we've already visited this parameter
        if current_parameter in visited:
            continue
        visited.add(current_parameter)

        # Find web services that produce the current parameter as an output
        producing_services = Outputparameter.objects.filter(parameterid=current_parameter)

        for service in producing_services:
            service_id = service.webserviceid
            service_name = Webservicelist.objects.get(webserviceid=service_id).webservicename

            # Construct the new path including the current web service
            new_path = path + [{'id': service_id, 'name': service_name}]

            # Check if any of the outputs of the current service is the goal parameter
            if goal_parameter in Outputparameter.objects.filter(webserviceid=service_id).values_list('parameterid', flat=True):
                return new_path

            # Otherwise, enqueue the next parameters to be processed
            next_parameters = Inputparameter.objects.filter(webserviceid=service_id).values_list('parameterid', flat=True)
            for next_param in next_parameters:
                if next_param not in visited:
                    queue.append((next_param, new_path))

    # Return an empty list if no path is found
    return []

def find_web_service_chain(initial_parameter, goal_parameter):
    # Initialize the queue with the initial parameter and an empty path
    queue = deque([({'parameter': initial_parameter, 'path': []})])

    while queue:
        current = queue.popleft()
        current_parameter = current['parameter']
        current_path = current['path']

        # Termination condition: if the current parameter is the goal
        if current_parameter == goal_parameter:
            return current_path

        # Find all web services that take the current parameter as input
        services_as_input = Inputparameter.objects.filter(parameterid=current_parameter)

        for service in services_as_input:
            service_id = service.webserviceid

            # For each service, find its outputs
            outputs = Outputparameter.objects.filter(webserviceid=service_id)

            for output in outputs:
                next_parameter = output.parameterid

                # Build the new path including the current web service
                next_path = current_path + [service_id]

                # Add the next parameter and path to the queue
                queue.append({'parameter': next_parameter, 'path': next_path})

    # Return an empty list if no path is found
    return []

# class FindWebServicesAPI(APIView):
#     def post(self, request):
#         serializer = WebServiceChainSerializer(data=request.data)

#         if serializer.is_valid():
#             initial_parameter = serializer.validated_data['initialParameter']
#             goal_parameter = serializer.validated_data['goalParameter']

#             web_service_chain = find_web_service_chain_bfs(initial_parameter, goal_parameter)

#             if web_service_chain:
#                 return Response({'webServiceChain': web_service_chain})
#             else:
#                 return Response({'error': 'No chain found connecting initial to goal parameter.'}, status=404)

#         return Response(serializer.errors, status=400)
    
class FindWebServicesAPI(APIView):
    def post(self, request):
        serializer = WebServiceChainSerializer(data=request.data)

        if serializer.is_valid():
            initial_parameter = serializer.validated_data['initialParameter']
            goal_parameter = serializer.validated_data['goalParameter']

            web_service_chain = find_web_service_chain(initial_parameter, goal_parameter)

            if web_service_chain:
                # Optionally, retrieve the names of the web services in the chain
                web_services_names = [Webservicelist.objects.get(webserviceid=ws_id).webservicename for ws_id in web_service_chain]
                return Response({'webServiceChain': web_services_names})
            else:
                return Response({'error': 'No chain found connecting initial to goal parameter.'}, status=404)

        return Response(serializer.errors, status=400)

