from rest_framework import serializers
from .models import Webservicelist

class WebservicelistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Webservicelist
        fields = '__all__'  # Or specify the fields you want to include

class WebserviceslistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Webservicelist
        exclude = ('provider', 'url')  # Excluding provider and url fields