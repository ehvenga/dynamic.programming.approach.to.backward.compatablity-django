from django.shortcuts import render
from models import Parameterhierarchy  # Import your model (adjust the name as necessary)

def view_parameter_hierarchy(request):
    data = Parameterhierarchy.objects.all()  # Query all records from the table
    return render(request, 'parameter_hierarchy.html', {'data': data})
