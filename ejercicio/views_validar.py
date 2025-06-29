from django.http import JsonResponse    
from django.views.decorators.csrf import csrf_exempt
import json
from django.views.decorators.http import require_POST
from .models import Palabra, PalabraUsuario
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required



def check_auth(user):
    return user.is_authenticated


@user_passes_test(check_auth)
@require_POST
@csrf_exempt
def verificar_seleccion(request):
    try:
        opcion_id = int(request.POST.get("opcion_id"))
        index = request.session.get('ejercicio_actual', 0)
        ejercicios = request.session.get('ejercicios', [])
        
        if index >= len(ejercicios):
            return JsonResponse({'completado': True})
            
        ejercicio_actual = ejercicios[index]
        es_correcto = opcion_id == ejercicio_actual['palabra']
        
        if es_correcto:
            if not request.session.get('en_repeticion', False):
                request.session['progreso'] = min(
                    request.session.get('progreso', 0) + 10, 
                    100
                )
        else:
            # Agregar ejercicio actual a la lista de errores si no está ya
            if 'ejercicios_errores' not in request.session:
                request.session['ejercicios_errores'] = []
            
            if index not in request.session['ejercicios_errores']:
                request.session['ejercicios_errores'].append(index)

            request.session['progreso'] = min(
                    request.session.get('progreso', 0) + 10, 
                    100
                )
        
        # Siempre avanzar al siguiente ejercicio
        request.session.modified = True
        
        
        return JsonResponse({
            'correcto': es_correcto,
            'redirect_url': '/ejercicio/siguiente/',
            'mensaje': '¡Correcto!' if es_correcto else 'Incorrecto - Continuando...'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    

@user_passes_test(check_auth)
@require_POST
@csrf_exempt
def verificar_seleccion2(request):
    try:
        opcion_id = int(request.POST.get("opcion_id"))
        index = request.session.get('ejercicio_actual', 0)
        ejercicios = request.session.get('ejercicios', [])
        
        if index >= len(ejercicios):
            return JsonResponse({'completado': True})
            
        ejercicio_actual = ejercicios[index]
        es_correcto = opcion_id == ejercicio_actual['palabra']
        
        if es_correcto:
            if not request.session.get('en_repeticion', False):
                request.session['progreso'] = min(
                    request.session.get('progreso', 0) + 10, 
                    100
                )
        else:
            # Agregar ejercicio actual a la lista de errores si no está ya
            if 'ejercicios_errores' not in request.session:
                request.session['ejercicios_errores'] = []
            
            if index not in request.session['ejercicios_errores']:
                request.session['ejercicios_errores'].append(index)

            request.session['progreso'] = min(
                    request.session.get('progreso', 0) + 10, 
                    100
                )
        
        # Siempre avanzar al siguiente ejercicio
        request.session.modified = True
        
        
        return JsonResponse({
            'correcto': es_correcto,
            'redirect_url': '/ejercicio/siguiente/',
            'mensaje': '¡Correcto!' if es_correcto else 'Incorrecto - Continuando...'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@user_passes_test(check_auth)
@require_POST
@csrf_exempt
def verificar_completar(request):
    try:
        opcion_id = int(request.POST.get("opcion_id"))
        index = request.session.get('ejercicio_actual', 0)
        ejercicios = request.session.get('ejercicios', [])
        
        if index >= len(ejercicios):
            return JsonResponse({'completado': True})
            
        ejercicio_actual = ejercicios[index]
        palabra_correcta_id = ejercicio_actual['palabra']
        es_correcto = opcion_id == palabra_correcta_id
        
        if es_correcto:
            if not request.session.get('en_repeticion', False):
                request.session['progreso'] = min(
                    request.session.get('progreso', 0) + 10, 
                    100
                )
        else:
            # Agregar ejercicio actual a la lista de errores si no está ya
            if 'ejercicios_errores' not in request.session:
                request.session['ejercicios_errores'] = []
            
            if index not in request.session['ejercicios_errores']:
                request.session['ejercicios_errores'].append(index)

            request.session['progreso'] = min(
                    request.session.get('progreso', 0) + 10, 
                    100
                )
        
        # Siempre avanzar al siguiente ejercicio
        request.session.modified = True
        
        # Obtener la palabra correcta para el mensaje
        palabra_correcta = Palabra.objects.get(id=palabra_correcta_id)
        
        
        return JsonResponse({
            'correcto': es_correcto,
            'redirect_url': '/ejercicio/siguiente/',
            'mensaje': '¡Correcto!' if es_correcto else f'Incorrecto. La opción correcta era: "{palabra_correcta.palabra}" - Continuando...'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    


@csrf_exempt
@require_POST
def verificar_escribir(request):
    try:
        respuesta = request.POST.get('respuesta_usuario', '').strip().lower()
        index = request.session.get('ejercicio_actual', 0)
        ejercicios = request.session.get('ejercicios', [])
        
        if index >= len(ejercicios):
            return JsonResponse({'completado': True})
            
        ejercicio_actual = ejercicios[index]
        palabra = Palabra.objects.get(id=ejercicio_actual['palabra'])
        es_correcto = respuesta == palabra.palabra.lower()
        
        if es_correcto:
            if not request.session.get('en_repeticion', False):
                request.session['progreso'] = min(
                    request.session.get('progreso', 0) + 10, 
                    100
                )
        else:
            # Agregar ejercicio actual a la lista de errores si no está ya
            if 'ejercicios_errores' not in request.session:
                request.session['ejercicios_errores'] = []
            
            if index not in request.session['ejercicios_errores']:
                request.session['ejercicios_errores'].append(index)
            
            request.session['progreso'] = min(
                    request.session.get('progreso', 0) + 10, 
                    100
                )
        
        # Siempre avanzar al siguiente ejercicio
        request.session.modified = True
        
        
        return JsonResponse({
            'correcto': es_correcto,
            'redirect_url': '/ejercicio/siguiente/',
            'mensaje': '¡Correcto!' if es_correcto else f'Incorrecto" - Continuando...'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    
    
@user_passes_test(check_auth)
@require_POST
@csrf_exempt
def verificar_emparejar(request):
    try:
        data = json.loads(request.body)
        pares = data.get('pares', [])
        index = request.session.get('ejercicio_actual', 0)
        ejercicios = request.session.get('ejercicios', [])
        
        if index >= len(ejercicios):
            return JsonResponse({'completado': True})
            
        ejercicio_actual = ejercicios[index]
        palabras_db = Palabra.objects.in_bulk()
        todos_correctos = True
        
        # Verificar todos los pares
        for par in pares:
            palabra_id = int(par.get('palabra_id'))
            gesto_id = int(par.get('gesto_id'))
            palabra_db = palabras_db.get(palabra_id)
            
            if not (palabra_db and palabra_db.id == gesto_id):
                todos_correctos = False
                break
        
        if todos_correctos:
            if not request.session.get('en_repeticion', False):
                request.session['progreso'] = min(
                    request.session.get('progreso', 0) + 10, 
                    100
                )
        else:
            # Agregar ejercicio actual a la lista de errores si no está ya
            if 'ejercicios_errores' not in request.session:
                request.session['ejercicios_errores'] = []
            
            if index not in request.session['ejercicios_errores']:
                request.session['ejercicios_errores'].append(index)

            request.session['progreso'] = min(
                request.session.get('progreso', 0) + 10, 
                100
            )
        
        # Siempre avanzar al siguiente ejercicio
        request.session.modified = True
        
        
        
        return JsonResponse({
            'todos_correctos': todos_correctos,
            'redirect_url': '/ejercicio/siguiente/',
            'mensaje': '¡Todos los emparejamientos correctos!' if todos_correctos else 'Algunos emparejamientos incorrectos - Continuando...'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    
from django.utils import timezone
@csrf_exempt  
@login_required
def guardar_precision(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        precision = data.get('precision')
        palabra_id = data.get('palabra_id')

        perfil = request.user.profile

        try:
            palabra = Palabra.objects.get(id=palabra_id)
            palabra_usuario, created = PalabraUsuario.objects.get_or_create(
                usuario=perfil, 
                palabra=palabra,
                defaults={'fecha_completada': timezone.now()} 
            )
            palabra_usuario.precision = precision
            if not created:
                palabra_usuario.fecha_completada = timezone.now()  
            palabra_usuario.save()
            return JsonResponse({
                'status': 'ok',
                'precision': precision,
                'palabra': palabra.palabra,
                'nueva': created
            })
        except Palabra.DoesNotExist:
            return JsonResponse({'error': 'Palabra no encontrada'}, status=404)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)
