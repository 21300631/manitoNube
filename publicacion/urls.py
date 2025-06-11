from django.urls import path
from .views import pagina, nueva_publicacion

urlpatterns = [
    path('', pagina, name='publicacion'),
    path('new/', nueva_publicacion, name='nueva_publicacion'),
    ]