from django.shortcuts import render, redirect
from registro.models import Profile 
from .models import Leccion, Instruccion, PalabraUsuario, Palabra
import random
from django.http import HttpResponseForbidden, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from django.utils import timezone
from .models import LeccionUsuario

@login_required
def generarLeccion(request):
    usuario = request.user
    perfil = Profile.objects.get(user=usuario)
    leccion_id = int(request.GET.get('leccion_id', 0))

    if leccion_id > perfil.leccion:
        return HttpResponseForbidden("No tienes acceso a esta lección todavía.")
    
    # Reiniciar completamente el estado de la lección
    request.session.update({
        'leccion_actual': leccion_id,
        'progreso': 0,
        'ejercicio_actual': 0,
        'ejercicios': [],
        'ejercicios_originales': [],
        'ejercicios_errores': [],
        'repeticiones': 0,
        'en_repeticion': False
    })
    
    leccion_obj = Leccion.objects.get(id=leccion_id)
    
    # 1. Obtener palabras nuevas (3 primeras de la lección)
    palabras_nuevas = list(leccion_obj.palabras.all()[:3])
    
    # 2. Obtener palabras de repaso (7 en total)
    relaciones_repaso = PalabraUsuario.objects.filter(usuario=perfil)
    palabras_repaso = []
    
    # Si hay suficientes palabras aprendidas, seleccionar 7 al azar
    if relaciones_repaso.count() >= 7:
        palabras_repaso = random.sample([rel.palabra for rel in relaciones_repaso], 7)
    else:
        # Si no hay suficientes, completar con palabras nuevas
        palabras_repaso = [rel.palabra for rel in relaciones_repaso]
        faltantes = 7 - len(palabras_repaso)
        palabras_repaso.extend(random.choices(palabras_nuevas, k=faltantes))
    
    # 3. Preparar ejercicios
    instrucciones_repaso = list(Instruccion.objects.exclude(tipo='gesto'))
    instruccion_gesto = Instruccion.objects.get(tipo='gesto')
    
    ejercicios = []
    
    # 3.1 Ejercicios de gesto con palabras nuevas (siempre primeros 3)
    for palabra in palabras_nuevas:
        ejercicios.append({
            'palabra': palabra.id,
            'instruccion': 'gesto',
            'texto': instruccion_gesto.generar_texto(palabra.palabra),
            'es_repeticion': False  # Para identificar ejercicios de repetición
        })
    
    # 3.2 Ejercicios de repaso con instrucciones aleatorias
    for palabra in palabras_repaso:
        instruccion = random.choice(instrucciones_repaso)
        ejercicios.append({
            'palabra': palabra.id,
            'instruccion': instruccion.tipo,
            'texto': instruccion.generar_texto(palabra.palabra),
            'es_repeticion': False
        })
    
    # Mezclar los ejercicios (excepto los primeros 3 de gesto)
    ejercicios_repaso = ejercicios[3:]
    random.shuffle(ejercicios_repaso)
    ejercicios = ejercicios[:3] + ejercicios_repaso
    
    # Guardar en sesión
    request.session['ejercicios'] = ejercicios
    request.session['ejercicios_originales'] = list(ejercicios)  # Guardar copia de los originales
    request.session.modified = True


    return redirect('mostrar_ejercicio')

@login_required
def mostrar_ejercicio(request):
    # Verificar e inicializar progreso si no existe
    if 'progreso' not in request.session:
        request.session['progreso'] = 0
    
    # Si no hay ejercicios, generar una nueva lección
    if 'ejercicios' not in request.session:
        return redirect('generarLeccion')
    
    ejercicios = request.session['ejercicios']
    index = request.session.get('ejercicio_actual', 0)
    
    # Si hemos completado todos los ejercicios
    if index >= len(ejercicios):
        return redirect('finalizado')
    
    try:
        ejercicio_actual = ejercicios[index]
        
        # Mapeo de tipos de ejercicio a sus vistas
        redirecciones = {
            'emparejar': 'ejercicio_emparejar',
            'seleccion': 'ejercicio_seleccion',
            'escribir': 'ejercicio_escribir',
            'gesto': 'ejercicio_gesto',
            'seleccion2': 'ejercicio_seleccion2',
            'completar': 'ejercicio_completar'
        }
        
        tipo_instruccion = ejercicio_actual['instruccion']
        if tipo_instruccion not in redirecciones:
            return HttpResponse("Tipo de ejercicio no reconocido", status=400)
            
        return redirect(redirecciones[tipo_instruccion])
        
    except Exception as e:
        print(f"Error al mostrar ejercicio: {str(e)}")
        return redirect('generarLeccion')


@login_required
def siguiente_ejercicio(request):
    if 'ejercicios' not in request.session:
        return redirect('generarLeccion')
    
    # Obtener el índice actual antes de incrementarlo
    ejercicio_actual = request.session.get('ejercicio_actual', 0)
    
    # Incrementar el contador de ejercicios
    request.session['ejercicio_actual'] = ejercicio_actual + 1
    
    # Sumar 10 al progreso solo si es uno de los primeros 3 ejercicios
    if not request.session.get('en_repeticion', False) and ejercicio_actual < 3:
    # Solo sumar progreso si no es repetición y son los primeros 3
        if 'progreso' not in request.session:
            request.session['progreso'] = 0
        
        nuevo_progreso = min(request.session['progreso'] + 10, 100)
        request.session['progreso'] = nuevo_progreso
        request.session.modified = True
    
    ejercicios = request.session['ejercicios']
    
    # Verificar si hemos completado todos los ejercicios actuales
    if request.session['ejercicio_actual'] >= len(ejercicios):
        # Si estamos en modo normal (no repetición) y hay errores
        if not request.session.get('en_repeticion', False) and \
           'ejercicios_errores' in request.session and \
           request.session['ejercicios_errores']:
            
            # Preparar repetición
            return preparar_repeticion_ejercicios(request)
        
        # Si estamos en modo repetición o no hay errores
        return redirect('finalizado')
    
    request.session.modified = True
    return redirect('mostrar_ejercicio')


@login_required
def preparar_repeticion_ejercicios(request):
    # Solo permitir una ronda de repetición
    if request.session.get('repeticiones', 0) >= 1:
        return redirect('finalizado')
    
    errores = request.session.get('ejercicios_errores', [])
    if not errores:
        return redirect('finalizado')
    
    # Crear nuevos ejercicios solo con los que tuvieron errores
    ejercicios_repeticion = []
    for i in errores:
        if i < len(request.session['ejercicios_originales']):
            ejercicio = request.session['ejercicios_originales'][i]
            ejercicio['es_repeticion'] = True
            ejercicios_repeticion.append(ejercicio)
    
    # Actualizar la sesión
    request.session.update({
        'ejercicios': ejercicios_repeticion,
        'ejercicio_actual': 0,
        'ejercicios_errores': [],
        'en_repeticion': True,
        'repeticiones': request.session.get('repeticiones', 0) + 1
    })
    request.session.modified = True
    
    return redirect('mostrar_ejercicio')

@login_required
@csrf_exempt
def reiniciar_progreso(request):
    if request.method == "POST":
        # 1. Preservar datos críticos de autenticación
        auth_data = {
            '_auth_user_id': request.session.get('_auth_user_id'),
            '_auth_user_backend': request.session.get('_auth_user_backend'),
            '_auth_user_hash': request.session.get('_auth_user_hash')
        }
        
        # 2. Limpiar solo datos de progreso
        request.session.pop('progreso', None)
        request.session.pop('ejercicios', None)
        # ... (eliminar solo las claves específicas necesarias)
        
        # 3. Restaurar auth data
        for key, value in auth_data.items():
            if value is not None:
                request.session[key] = value
        
        request.session.modified = True
    return redirect('/inicio/')


@login_required
def mostrar_finalizado(request):
    print("Puntos anteriores:", request.user.profile.puntos)

    total = len(request.session.get('ejercicios_originales', []))
    errores = len(request.session.get('ejercicios_errores', []))
    aciertos = total - errores if total > 0 else 0

    puntosAciertos = aciertos * 10
    puntosErrores = errores * 5
    puntosTotales = puntosAciertos + puntosErrores

    perfil = request.user.profile

    try:
        # 1. Actualizar puntos
        perfil.puntos += puntosTotales
        
        # 2. Manejo de lecciones
        leccion_actual_id = request.session.get('leccion_actual')
        print(f"ID lección actual desde sesión: {leccion_actual_id}")
        
        if leccion_actual_id:
            try:
                leccion_actual = Leccion.objects.get(id=leccion_actual_id)
                print(f"Lección encontrada: {leccion_actual.id}")
                
                # Verificar si ya está registrada en LeccionUsuario
                leccion_registrada = LeccionUsuario.objects.filter(
                    usuario=perfil,
                    leccion=leccion_actual
                ).exists()
                print(f"¿Lección ya registrada? {leccion_registrada}")
                
                if not leccion_registrada:
                    # Buscar siguiente lección
                    siguiente_leccion = Leccion.objects.filter(
                        id__gt=leccion_actual_id
                    ).order_by('id').first()
                    
                    if siguiente_leccion:
                        perfil.leccion = siguiente_leccion.id
                        print(f"Actualizando lección en perfil a: {siguiente_leccion.id}")
                    
                    # Registrar lección completada
                    LeccionUsuario.objects.create(
                        usuario=perfil,
                        leccion=leccion_actual,
                        completada=True,
                        fecha_completada=timezone.now()
                    )
                    print(f"Lección {leccion_actual_id} registrada en LeccionUsuario")
                    
                    # 3. Agregar palabras aprendidas (versión optimizada)
                    palabras_leccion = Palabra.objects.filter(leccion__id=leccion_actual_id)
                    
                    # Obtener todas las palabras que el usuario ya tiene registradas
                    palabras_existentes = set(PalabraUsuario.objects.filter(
                        usuario=perfil
                    ).values_list('palabra_id', flat=True))
                    
                    # Filtrar solo las palabras nuevas
                    palabras_nuevas = [p for p in palabras_leccion if p.id not in palabras_existentes]
                    
                    # Crear todas las relaciones nuevas en una sola operación
                    if palabras_nuevas:
                        PalabraUsuario.objects.bulk_create([
                            PalabraUsuario(
                                usuario=perfil,
                                palabra=palabra,
                                fecha_completada=timezone.now()
                            ) for palabra in palabras_nuevas
                        ])
                        print(f"Palabras agregadas: {len(palabras_nuevas)}")
                    else:
                        print("Todas las palabras ya estaban registradas")
                
            except Leccion.DoesNotExist:
                print(f"Error: Lección con ID {leccion_actual_id} no encontrada")

        # Actualizar racha
        perfil.actualizar_racha()
        perfil.save()
        print(f"Puntos totales actualizados: {perfil.puntos}")
        print(f"Lección actual en perfil: {perfil.leccion}")

    except Exception as e:
        print(f"Error inesperado: {str(e)}")

    # Limpiar sesión
    keys_to_keep = [
        '_auth_user_id', '_auth_user_backend', '_auth_user_hash',
        'usuario', 'foto_perfil'
    ]
    session_keys = list(request.session.keys())
    for key in session_keys:
        if key not in keys_to_keep:
            del request.session[key]

    request.session.modified = True
    return render(request, 'finalizado.html', {
        'total_ejercicios': total,
        'ejercicios_correctos': aciertos,
        'racha_actual': perfil.racha
    })

@csrf_exempt
def actualizar_progreso(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            progreso = int(data.get('progreso', 0))
            request.session['progreso'] = progreso
            request.session.modified = True
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=405)