# from django.db.models import F
# from .models import Medalla
# from registro.models import Profile

# def calcular_precision(perfil, ultimos_n=10):
#     """
#     Calcula la precisión basada en los últimos N ejercicios
#     Implementación de ejemplo - ajusta con tu lógica real
#     """
#     from ejercicio.models import ProgresoUsuario  # Asegúrate de importar tu modelo real
    
#     ejercicios_recientes = ProgresoUsuario.objects.filter(
#         perfil=perfil
#     ).order_by('-fecha')[:ultimos_n]
    
#     if not ejercicios_recientes:
#         return 0.0
    
#     total_correctos = sum(1 for e in ejercicios_recientes if e.correcto)
#     precision = (total_correctos / ultimos_n) * 100
    
#     return precision

# def actualizar_medalla_usuario(perfil):
#     """
#     Asigna la medalla correspondiente basada en el rendimiento actual
#     Devuelve True si se actualizó la medalla, False si no hubo cambios
#     """
#     # Obtener todas las medallas disponibles (de menor a mayor rango)
#     try:
#         medallas = {
#             'bronce': Medalla.objects.get(nombre__icontains='bronce'),
#             'plata': Medalla.objects.get(nombre__icontains='plata'),
#             'oro': Medalla.objects.get(nombre__icontains='oro')
#         }
#     except Medalla.DoesNotExist:
#         return False  # Si no existen medallas en la BD

#     # Calcular métricas de rendimiento
#     precision = calcular_precision(perfil)
#     puntos = perfil.puntos
    
#     # Lógica de asignación (ajusta estos valores según tus necesidades)
#     nueva_medalla = None
    
#     if puntos >= 1000 and precision >= 90:
#         nueva_medalla = medallas['oro']
#     elif puntos >= 500 and precision >= 80:
#         nueva_medalla = medallas['plata']
#     elif puntos >= 100 and precision >= 70:
#         nueva_medalla = medallas['bronce']
    
#     # Actualizar solo si hay un cambio
#     if nueva_medalla and (not perfil.medalla or nueva_medalla.id != perfil.medalla.id):
#         perfil.medalla = nueva_medalla
#         perfil.save(update_fields=['medalla'])
#         return True
    
#     return False

# def verificar_y_actualizar_medalla(usuario):
#     """
#     Función principal para ser llamada desde vistas o señales
#     """
#     try:
#         perfil = Profile.objects.get(user=usuario)
#         return actualizar_medalla_usuario(perfil)
#     except Profile.DoesNotExist:
#         return False