from django.shortcuts import render
from models import Parameterhierarchy

def view_parameter_hierarchy(request):
    data = Parameterhierarchy.objects.all()
    return render(request, 'parameter_hierarchy.html', {'data': data})
