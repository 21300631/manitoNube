from django.urls import path
from .views import calentamientoPage

urlpatterns = [
    path('', calentamientoPage)
]