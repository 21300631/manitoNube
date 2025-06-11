from django.urls import path
from .views import  foro, dar_like, reportar, agregar_comentario
urlpatterns = [
    path("", foro, name="foro"),
    path('foro/dar_like/<int:publicacion_id>/', dar_like, name='dar_like'),
    path('foro/reportar/<int:publicacion_id>/', reportar, name='reportar'),

    # path('reportar/<int:publicacion_id>/', reportar, name='reportar'),
     path('agregar_comentario/<int:publicacion_id>/', agregar_comentario, name='agregar_comentario'),

]