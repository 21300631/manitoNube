from django.urls import path
from inicio.views import inicioSesion
from .views import   generarLeccion, siguiente_ejercicio, mostrar_ejercicio, reiniciar_progreso, mostrar_finalizado, actualizar_progreso
from .views_ejercicios import ejercicio_emparejar, ejercicio_completar, ejercicio_escribir, ejercicio_gesto, ejercicio_seleccion, ejercicio_seleccion2
from .views_validar import verificar_seleccion, verificar_completar, verificar_seleccion2,  verificar_escribir, verificar_emparejar
# from .views_gesto import gesto_referencia

urlpatterns = [  
    # generar lecciones
    path('generar/', generarLeccion, name='generar_leccion'),  # Cambié la URL a 'generarLeccion' para evitar conflictos con la vista
    path('siguiente/', siguiente_ejercicio, name='siguiente_ejercicio'),  
    path('mostrar/', mostrar_ejercicio, name='mostrar_ejercicio'),
    # ejercicios
    path('emparejar/', ejercicio_emparejar, name='ejercicio_emparejar'),
    path('completar/', ejercicio_completar, name='ejercicio_completar'),
    path('escribir/', ejercicio_escribir, name='ejercicio_escribir'),
    path('gesto/', ejercicio_gesto, name='ejercicio_gesto'),
    path('seleccion/', ejercicio_seleccion, name='ejercicio_seleccion'),
    path('seleccion2/', ejercicio_seleccion2, name='ejercicio_seleccion2'),
    # validaciones
    path('verificar_seleccion/', verificar_seleccion, name='verificar_seleccion'),
    path('verificar_completar/', verificar_completar, name='verificar_completar'),
    path('verificar_seleccion2/', verificar_seleccion2, name='verificar_seleccion2'),
    path('verificar_emparejar/', verificar_emparejar, name='verificar_emparejar'),
    path('verificar_escribir/', verificar_escribir, name='verificar_escribir'),
    path('reiniciar-progreso/', reiniciar_progreso, name='reiniciar_progreso'),

    path('finalizado/', mostrar_finalizado, name='finalizado'),  # Cambié la URL a 'mostrar_ejercicio' para evitar conflictos con la vista
    # path('inicio/', inicioSesion, name='inicio'),  # Cambié la URL a 'inicio' para evitar conflictos con la vista
    # path('comparar_gesto/', comparar_gesto, name='comparar_gesto'),

    path('actualizar_progreso/', actualizar_progreso, name='actualizar_progreso'),
    

    # path('load_reference_gesto/', load_reference_gesto, name='load_reference_gesto'),

]