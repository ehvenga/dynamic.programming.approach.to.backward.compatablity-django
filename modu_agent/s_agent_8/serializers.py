from rest_framework import serializers
from .models import Webservicelist, Inputparameter, Outputparameter, Parameterlist


class WebservicelistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Webservicelist
        fields = '__all__'  # Or specify the fields you want to include

class WebserviceslistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Webservicelist
        exclude = ('provider', 'url')  # Excluding provider and url fields

class InputparameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inputparameter
        fields = '__all__'

class OutputparameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Outputparameter
        fields = '__all__'

class ParameterlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameterlist
        fields = '__all__'

class GenerateParametersSerializer(serializers.Serializer):
    initialParameter = serializers.CharField(max_length=10)
    goalParameter = serializers.CharField(max_length=10)

class WebServiceChainSerializer(serializers.Serializer):
    initialParameter = serializers.CharField(max_length=10)
    goalParameter = serializers.CharField(max_length=10)
