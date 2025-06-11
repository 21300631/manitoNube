from django.urls import path
from .views import formulario, registro_usuario

urlpatterns = [
    path('', formulario),
    path('new/', registro_usuario, name='registro') 
]


