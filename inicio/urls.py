from django.urls import path
from .views import inicioSesion, puntosUsuario

urlpatterns = [
    path('', inicioSesion),
    path('puntosUsuario/', puntosUsuario, name='puntos_usuario'),
]