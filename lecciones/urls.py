from django.urls import path
from .views import etapa1, etapa2, etapa3, etapa4

urlpatterns = [
    path('etapa1/', etapa1),
    path('etapa2/', etapa2),
    path('etapa3/', etapa3),
    path('etapa4/', etapa4),
]