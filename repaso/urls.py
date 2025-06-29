from django.urls import path
from .views import iniciar_repaso, mostrar_ejercicio_repaso, siguiente_ejercicio_repaso, finalizar_repaso, no_hay_palabras, noRecuerdo

urlpatterns = [
    path('', iniciar_repaso, name='iniciar_repaso'),
    path('ejercicio/', mostrar_ejercicio_repaso, name='mostrar_ejercicio_repaso'),
    path('siguiente/', siguiente_ejercicio_repaso, name='siguiente_ejercicio_repaso'),
    path('finalizar/', finalizar_repaso, name='finalizar_repaso'),
    path('no-hay-palabras/', no_hay_palabras, name='no_hay_palabras'),
    path('no-recuerdo/', noRecuerdo, name='no_recuerdo'),
]