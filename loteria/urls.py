from .views import loteria
from django.urls import path

urlpatterns = [
    path('', loteria, name='loteria'),
]