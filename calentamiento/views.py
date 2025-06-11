from django.shortcuts import render
from registro.models import Profile

# Create your views here.
def calentamientoPage(request):
    return render(request, 'calentamiento.html')

