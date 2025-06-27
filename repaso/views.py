from django.shortcuts import render, redirect
from registro.models import Profile
from django.contrib.auth.decorators import login_required
from ejercicio.models import PalabraUsuario, Palabra
from django.conf import settings
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.templatetags.static import static
from django.urls import reverse

@login_required
def iniciar_repaso(request):
    user = request.user
    perfil = Profile.objects.get(user=user)

    # Limpiar sesión previa
    keys = ['repaso_palabras', 'repaso_index', 'repaso_errores']
    for key in keys:
        if key in request.session:
            del request.session[key]

    # Obtener palabras para repaso
    palabras_repaso = PalabraUsuario.objects.filter(usuario=perfil)\
                          .select_related('palabra')\
                          .order_by('?')[:10]
    
    if not palabras_repaso.exists():
        return redirect('no_hay_palabras')
    
    palabras_ids = [rel.palabra.id for rel in palabras_repaso]
    
    # Debug
    print("Palabras seleccionadas para repaso:")
    for palabra in Palabra.objects.filter(id__in=palabras_ids):
        print(f"- {palabra.palabra} (ID: {palabra.id})")
    
    # Configurar sesión
    request.session.update({
        'repaso_palabras': palabras_ids,
        'repaso_index': 0,
        'repaso_errores': [],
        'repaso_iniciado': True
    })
    request.session.modified = True
    
    return redirect('mostrar_ejercicio_repaso')


@csrf_exempt
@login_required
def siguiente_ejercicio_repaso(request):
    if not request.session.get('repaso_iniciado', False):
        return JsonResponse({'status': 'error', 'message': 'Sesión no iniciada'}, status=400)
    
    palabras_ids = request.session.get('repaso_palabras', [])
    current_index = request.session.get('repaso_index', 0)
    
    # Verificar si ya hemos terminado antes de procesar
    if current_index >= len(palabras_ids):
        return JsonResponse({
            'status': 'completed',
            'redirect_url': reverse('finalizar_repaso')
        })
    
    if request.method == 'POST':
        # Procesar error si existe
        try:
            data = json.loads(request.body) if request.content_type == 'application/json' else request.POST.dict()
            
            if data.get('error', False):
                errores = request.session.get('repaso_errores', [])
                errores.append(current_index)
                request.session['repaso_errores'] = errores
            
            # Avanzar al siguiente ejercicio
            request.session['repaso_index'] = current_index + 1
            request.session.modified = True
            
            # Verificar si hemos terminado después de avanzar
            if request.session['repaso_index'] >= len(palabras_ids):
                return JsonResponse({
                    'status': 'completed',
                    'redirect_url': reverse('finalizar_repaso')
                })
            
            return JsonResponse({
                'status': 'success',
                'redirect_url': reverse('mostrar_ejercicio_repaso')
            })
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

@login_required
def mostrar_ejercicio_repaso(request):
    if not request.session.get('repaso_iniciado', False):
        return redirect('iniciar_repaso')
    
    palabras_ids = request.session.get('repaso_palabras', [])
    index = request.session.get('repaso_index', 0)
    
    # Verificar si hemos terminado antes de intentar mostrar un ejercicio
    if index >= len(palabras_ids):
        return redirect('finalizar_repaso')
    
    try:
        palabra_actual = Palabra.objects.get(id=palabras_ids[index])
    except Palabra.DoesNotExist:
        # Si la palabra no existe, avanzar y redirigir de nuevo
        request.session['repaso_index'] += 1
        request.session.modified = True
        return redirect('mostrar_ejercicio_repaso')
    
    # Construir URL del JSON usando static
    json_url = static(f'landmarks/{palabra_actual.palabra}.json')
    
    contexto = {
        'palabra': {
            'id': palabra_actual.id,
            'texto': palabra_actual.palabra,
            'gesto_url': f"{settings.MANITO_BUCKET_DOMAIN}/{palabra_actual.gesto}" if palabra_actual.gesto else None,
            'is_video': bool(palabra_actual.gesto and palabra_actual.gesto.lower().endswith('.mp4')),
            'json_url': json_url
        },
        'progreso': {
            'actual': index + 1,
            'total': len(palabras_ids)
        },
        'tipo_ejercicio': 'repaso',
        'es_ultimo_ejercicio': (index + 1) >= len(palabras_ids)
    }
    
    return render(request, 'repaso.html', contexto)

@csrf_exempt
@login_required
def noRecuerdo(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)
    
    if 'repaso_index' not in request.session or 'repaso_palabras' not in request.session:
        return JsonResponse({'status': 'error', 'message': 'Sesión no iniciada'}, status=400)
    
    try:
        # Registrar error
        index = request.session['repaso_index']
        errores = request.session.get('repaso_errores', [])
        errores.append(index)
        request.session['repaso_errores'] = errores
        
        # Avanzar al siguiente ejercicio
        request.session['repaso_index'] += 1
        request.session.modified = True
        
        # Verificar si hemos terminado
        palabras_ids = request.session.get('repaso_palabras', [])
        if request.session['repaso_index'] >= len(palabras_ids):
            return JsonResponse({
                'status': 'completed',
                'redirect_url': reverse('finalizar_repaso')
            })
        
        return JsonResponse({
            'status': 'success',
            'redirect_url': reverse('mostrar_ejercicio_repaso')
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def finalizar_repaso(request):
    if 'repaso_palabras' not in request.session:
        return redirect('iniciar_repaso')
    
    total = len(request.session['repaso_palabras'])
    errores = len(request.session.get('repaso_errores', []))
    aciertos = total - errores
    
    contexto = {
        'total_ejercicios': total,
        'ejercicios_correctos': aciertos,
        'ejercicios_incorrectos': errores,
        'porcentaje_acierto': (aciertos / total * 100) if total > 0 else 0,
        'tipo_repaso': 'general'
    }
    
    # Limpiar la sesión
    request.session.pop('repaso_palabras', None)
    request.session.pop('repaso_index', None)
    request.session.pop('repaso_errores', None)
    request.session.modified = True
    
    return render(request, 'estadisticas.html', contexto)

@login_required
def no_hay_palabras(request):
    return render(request, 'noPalabras.html')


@login_required
@csrf_exempt
def guardar_precision(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        precision = data.get('precision')
        palabra_id = data.get('palabra_id')

        perfil = request.user.profile

        try:
            palabra = Palabra.objects.get(id=palabra_id)
            palabra_usuario, created = PalabraUsuario.objects.get_or_create(usuario=perfil, palabra=palabra)
            palabra_usuario.precision = precision
            palabra_usuario.save()
            return JsonResponse({'status': 'ok'})
        except Palabra.DoesNotExist:
            return JsonResponse({'error': 'Palabra no encontrada'}, status=404)

    return JsonResponse({'error': 'Método no permitido'}, status=405)