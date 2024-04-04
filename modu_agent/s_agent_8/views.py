from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from django.http import JsonResponse
from django.forms.models import model_to_dict
from rest_framework import status
from django.core import serializers
from collections import deque, defaultdict
from .models import Webservicelist, Inputparameter, Outputparameter, Parameterlist, Initialgoalparameter, Parameterhierarchy
from .serializers import WebservicelistSerializer, WebserviceslistSerializer, InputparameterSerializer, OutputparameterSerializer, ParameterlistSerializer, GenerateParametersSerializer,WebServiceChainSerializer
from .serializers import WebServiceChainV2Serializer, WebServicePathSerializer, WebServiceChainV2Serializer

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

def find_web_service_chains(initial_parameters, goal_parameters):
    chains = {}

    for initial_param in initial_parameters:
        for goal_param in goal_parameters:
            # Initialize the queue with the initial parameter and an empty path
            queue = deque([({'parameter': initial_param, 'path': []})])
            while queue:
                current = queue.popleft()
                current_parameter = current['parameter']
                current_path = current['path']

                # Termination condition: if the current parameter is the goal
                if current_parameter == goal_param:
                    chains[(initial_param, goal_param)] = current_path
                    break  # Move to the next parameter pair

                # Find all web services that take the current parameter as input
                services_as_input = Inputparameter.objects.filter(parameterid=current_parameter)
                for service in services_as_input:
                    service_id = service.webserviceid

                    # For each service, find its outputs
                    outputs = Outputparameter.objects.filter(webserviceid=service_id)
                    for output in outputs:
                        next_parameter = output.parameterid
                        next_path = current_path + [service_id]

                        # Add the next parameter and path to the queue
                        queue.append({'parameter': next_parameter, 'path': next_path})

    return chains

class FindWebServicesV2API(APIView):
    def post(self, request):
        serializer = WebServiceChainV2Serializer(data=request.data)

        if serializer.is_valid():
            initial_parameters = serializer.validated_data['initialParameters']
            goal_parameters = serializer.validated_data['goalParameters']

            web_service_chains = find_web_service_chains(initial_parameters, goal_parameters)
            response_data = {}

            for (initial_param, goal_param), chain in web_service_chains.items():
                # Optionally, retrieve the names of the web services in the chain
                web_services_names = [Webservicelist.objects.get(webserviceid=ws_id).webservicename for ws_id in chain]
                response_data[f'From {initial_param} to {goal_param}'] = web_services_names

            return Response(response_data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
def construct_graph():
    graph = {}
    # Construct edges from output parameters to input parameters through web services
    for output in Outputparameter.objects.all():
        if output.parameterid not in graph:
            graph[output.parameterid] = []
        inputs = Inputparameter.objects.filter(webserviceid=output.webserviceid)
        for input_param in inputs:
            graph[output.parameterid].append((input_param.parameterid, output.webserviceid))
    return graph

def find_paths(graph, start, goals, path=[], paths=[]):
    if start in goals:
        paths.append(path)
        return
    if start not in graph:
        return
    for node, webservice in graph[start]:
        if node not in path:  # Avoid cycles
            find_paths(graph, node, goals, path + [(webservice, node)], paths)

# class FindWebServicesPathsAPI(APIView):
#     def post(self, request):
#         serializer = WebServicePathSerializer(data=request.data)

#         if serializer.is_valid():
#             initial_parameters = set(serializer.validated_data['initialParameters'])
#             goal_parameters = set(serializer.validated_data['goalParameters'])

#             graph = construct_graph()
#             all_paths = []

#             for initial_param in initial_parameters:
#                 paths = []
#                 find_paths(graph, initial_param, goal_parameters, path=[initial_param], paths=paths)
#                 all_paths.extend(paths)

#             # Transform paths to include web service names
#             named_paths = [
#                 [{'webservice_id': webservice, 'webservice_name': Webservicelist.objects.get(webserviceid=webservice).webservicename, 'parameter': param} 
#                  for webservice, param in path] for path in all_paths
#             ]

#             return Response({'paths': named_paths})

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
def find_paths_bfs(graph, starts, goals, max_depth=5):
    queue = deque([([(None, start)], start) for start in starts])  # Initialize paths with (None, start) to indicate no preceding web service for the starting points
    paths = []

    while queue:
        path, current = queue.popleft()
        if len(path) > max_depth + 1:  # +1 accounts for the initial (None, start) in each path
            continue
        if current in goals:
            paths.append(path[1:])  # Skip the initial (None, start)
            continue
        for next_param, webservice in graph.get(current, []):
            if next_param not in [p for _, p in path]:  # Check path for cycles based on parameters only
                queue.append((path + [(webservice, next_param)], next_param))
    
    return paths


class FindWebServicesPathsAPI(APIView):
    def post(self, request):
        serializer = WebServicePathSerializer(data=request.data)

        if serializer.is_valid():
            initial_parameters = serializer.validated_data['initialParameters']
            goal_parameters = serializer.validated_data['goalParameters']

            graph = construct_graph()
            paths = find_paths_bfs(graph, initial_parameters, goal_parameters)

            # Now properly unpack webservice and param from each step in the paths
            named_paths = []
            for path in paths:
                named_path = []
                for webservice_id, param in path:
                    if webservice_id:  # Skip the initial step where webservice_id is None
                        webservice_name = Webservicelist.objects.get(webserviceid=webservice_id).webservicename
                        named_path.append({'webservice_id': webservice_id, 'webservice_name': webservice_name, 'parameter': param})
                named_paths.append(named_path)

            return Response({'paths': named_paths})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
def preprocess_webservices():
    input_to_services = defaultdict(list)
    output_to_services = defaultdict(list)
    service_outputs = defaultdict(list)

    for inp in Inputparameter.objects.all():
        input_to_services[inp.parameterid].append(inp.webserviceid)

    for outp in Outputparameter.objects.all():
        output_to_services[outp.parameterid].append(outp.webserviceid)
        service_outputs[outp.webserviceid].append(outp.parameterid)

    return input_to_services, output_to_services, service_outputs

def bfs_with_path_tracking(initial_parameters, goal_parameters, input_to_services, service_outputs):
    queue = deque(initial_parameters)
    paths = {param: [] for param in initial_parameters}  # Track paths
    visited = set(initial_parameters)

    while queue:
        current_param = queue.popleft()

        # If a goal parameter is reached, reconstruct and return the path
        if current_param in goal_parameters:
            return reconstruct_path(current_param, paths)

        for service_id in input_to_services[current_param]:
            for next_param in service_outputs[service_id]:
                if next_param not in visited:
                    queue.append(next_param)
                    visited.add(next_param)
                    paths[next_param] = paths[current_param] + [(service_id, next_param)]

    return []  # Return an empty list if no path is found

def reconstruct_path(param, paths):
    return [(service, param) for service, param in paths[param]]


def find_web_service_chains_v2(initial_parameters, goal_parameters):
    all_chains = []

    # Function to find a single chain, reused from the previous example
    def find_chain(current_parameter, goal_parameter, current_path, visited):
        if current_parameter in goal_parameters:
            all_chains.append(current_path)
            return True

        visited.add(current_parameter)

        services_as_input = Inputparameter.objects.filter(parameterid=current_parameter)
        for service in services_as_input:
            service_id = service.webserviceid
            if service_id in visited:
                continue

            outputs = Outputparameter.objects.filter(webserviceid=service_id)
            for output in outputs:
                next_parameter = output.parameterid
                if next_parameter not in visited:
                    find_chain(next_parameter, goal_parameters, current_path + [service_id], visited.copy())

    # Iterate over each initial parameter and attempt to find a chain to any goal parameter
    for initial_param in initial_parameters:
        find_chain(initial_param, goal_parameters, [], set())

    return 

class FindWebChainsV2API(APIView):
    def post(self, request):
        serializer = WebServiceChainV2Serializer(data=request.data)

        if serializer.is_valid():
            initial_parameters = set(serializer.validated_data['initialParameters'])
            goal_parameters = set(serializer.validated_data['goalParameters'])

            # Preprocess to create mappings
            input_to_services, output_to_services, service_outputs = preprocess_webservices()

            # Find web service chains for each initial parameter
            chains = []
            for initial_param in initial_parameters:
                chain = bfs_with_path_tracking([initial_param], goal_parameters, input_to_services, service_outputs)
                if chain:
                    chains.append(chain)

            return Response({'webServiceChains': chains})

        return Response(serializer.errors, status=400)


