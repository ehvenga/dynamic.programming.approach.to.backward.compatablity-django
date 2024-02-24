from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from .models import Webservicelist
from .serializers import WebservicelistSerializer, WebserviceslistSerializer

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