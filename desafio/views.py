from django.shortcuts import render
from django.urls import reverse
from manito import settings
from registro.models import Profile
from ejercicio.models import PalabraUsuario, Palabra
import random
from manito.settings import MANITO_BUCKET_DOMAIN
import time
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
def generarMemorama(request):
    usuario = request.user
    perfil = Profile.objects.get(user=usuario)
    
    # Verificar si viene de completar el juego
    if request.GET.get('completado') == '1':
        puntaje = request.GET.get('puntaje', 0)
        puntines = int(request.GET.get('puntuacion', 0))

        perfil.puntos += puntines
        perfil.save()
        return render(request, 'final_memorama.html', {
            'puntaje': puntaje,
            'categoria': Palabra.objects.filter(
                palabras_usuario__usuario=perfil
            ).first().categoria if Palabra.objects.filter(
                palabras_usuario__usuario=perfil
            ).exists() else "General"
        })
    
    palabras_usuario = PalabraUsuario.objects.filter(usuario_id=perfil)[:6]
    
    pares = []
    for p in palabras_usuario:
        palabra = p.palabra
        gesto = palabra.gesto
        es_video = str(gesto).lower().endswith('.mp4')

        if not es_video:
            pares.append({
                'tipo': 'imagen',
                'contenido': f"{settings.MANITO_BUCKET_DOMAIN}/{gesto}",
                'es_video': False,
                'id': palabra.id,
                'texto': palabra.palabra,
                'palabra_texto': palabra.palabra  # Añadido para referencia
            })

            pares.append({
                'tipo': 'palabra',
                'contenido': palabra.palabra,
                'es_video': False,
                'id': palabra.id,
                'palabra_texto': palabra.palabra  # Añadido para referencia
            })

    random.shuffle(pares)
    
    return render(request, 'memorama.html', {
        'cartas': pares,
        'total_pares': len(pares) // 2,
        'request_path': request.path  # Pasamos la ruta actual al template
    })

def finalMemorama(request):
    usuario = request.user
    perfil = Profile.objects.get(user=usuario)
    puntaje = request.GET.get('puntaje', 0)
    categoria = Palabra.objects.filter(
        palabras_usuario__usuario=perfil
    ).first().categoria if Palabra.objects.filter(
        palabras_usuario__usuario=perfil
    ).exists() else "General"

    return render(request, 'final_memorama.html', {
        'puntaje': puntaje,
        'categoria': categoria
    })


def generarRelacion(request):
    usuario = request.user
    perfil = Profile.objects.get(user=usuario)
    
    # Verificar si viene de completar el juego
    if request.GET.get('completado') == '1':
        puntaje = request.GET.get('puntaje', 0)
        puntines = int(request.GET.get('puntuacion', 0))

        perfil.puntos += puntines
        perfil.save()
        return render(request, 'final_relacion.html', {
            'puntaje': puntaje
        })
    
    palabras_usuario_ids = PalabraUsuario.objects.filter(usuario_id=perfil).values_list('palabra_id', flat=True)
    palabras_originales = list(Palabra.objects.filter(id__in=palabras_usuario_ids))

    print(f"Palabras originales del usuario: {[p.palabra for p in palabras_originales]}")  # Debug
    
    random.shuffle(palabras_originales)
    
    # Filtrar palabras sin video y mezclar
    palabras_filtradas = [
        p for p in palabras_originales
        if not str(p.gesto).lower().endswith('.mp4')
    ][:20]
    random.shuffle(palabras_filtradas)
    
    print(f"Palabras filtradas (sin video): {[p.palabra for p in palabras_filtradas]}")  # Debug
    
    # Tomar 10 palabras (5 pares correctos)
    palabras_seleccionadas = palabras_filtradas[:10]
    
    print(f"Palabras seleccionadas para el juego: {[p.palabra for p in palabras_seleccionadas]}")  # Debug
    
    # Preparar datos
    pares_correctos = [{
        'palabra': {'id': p.id, 'palabra': p.palabra},
        'imagen': {'id': p.id, 'url': f"{settings.MANITO_BUCKET_DOMAIN}/{p.gesto}", 'palabra': p.palabra}
    } for p in palabras_seleccionadas]
    
    print(f"Todos los pares correctos generados: {[p['palabra']['palabra'] for p in pares_correctos]}")  # Debug
    
    # Mezclar los pares
    random.shuffle(pares_correctos)
    
    # El problema estaba aquí: estabas dividiendo en índices 15: cuando solo hay 10 elementos
    context = {
        'pares_correctos': pares_correctos[:5],  # Primeros 5 pares
        'pares_reserva': pares_correctos[5:],    # Resto de pares (otros 5)
        'total_pares': 5
    }
    
    print(f"Pares enviados al template (pares_correctos): {[p['palabra']['palabra'] for p in context['pares_correctos']]}")  # Debug
    print(f"Pares en reserva (pares_reserva): {[p['palabra']['palabra'] for p in context['pares_reserva']]}")  # Debug
    
    return render(request, 'relacion.html', context)

@login_required
def generarContrarreloj(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    usuario = request.user
    perfil = Profile.objects.get(user=usuario)
    
    # Obtener palabras del usuario excluyendo videos
    palabras_usuario_ids = PalabraUsuario.objects.filter(usuario_id=perfil).values_list('palabra_id', flat=True)
    palabras_filtradas = list(Palabra.objects.filter(id__in=palabras_usuario_ids).exclude(gesto__iendswith='.mp4'))
    
    if not palabras_filtradas:
        return render(request, 'error.html', {'message': 'No tienes palabras disponibles para el desafío'})
    
    random.shuffle(palabras_filtradas)

    print("Palabras filtradas para contrarreloj:")
    for palabra in palabras_filtradas:
        print(f"- {palabra.palabra}")  # Suponiendo que el campo de texto se llama 'texto'

    
    # Guardar la lista de palabras en la sesión
    request.session['palabras_contrarreloj'] = [p.id for p in palabras_filtradas]
    request.session['indice_palabra_actual'] = 0
    request.session['puntaje_contrarreloj'] = 0
    request.session['tiempo_inicio'] = time.time()
    
    # Redirigir al primer ejercicio
    return redirect('mostrar_ejercicio_contrarreloj')

def mostrar_ejercicio_contrarreloj(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    palabras_ids = request.session.get('palabras_contrarreloj', [])
    indice_actual = request.session.get('indice_palabra_actual', 0)
    
    if indice_actual >= len(palabras_ids):
        return redirect('resultado_contrarreloj')
    
    palabra_actual = Palabra.objects.get(id=palabras_ids[indice_actual])
    archivo_url = f"{MANITO_BUCKET_DOMAIN}/{palabra_actual.gesto}"
    
    context = {
        'archivo': archivo_url,
        'palabra_correcta': palabra_actual.palabra,
        'indice_actual': indice_actual,
        'total_palabras': len(palabras_ids),
        'puntaje_actual': request.session.get('puntaje_contrarreloj', 0),
    }
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Si es una petición AJAX, devuelve solo los datos necesarios
        return JsonResponse({
            'archivo_url': archivo_url,
            'palabra_correcta': palabra_actual.palabra,
            'indice_actual': indice_actual,
            'total_palabras': len(palabras_ids),
            'puntaje_actual': request.session.get('puntaje_contrarreloj', 0),
        })
    
    return render(request, 'contrarreloj.html', context)

@csrf_exempt
def siguiente_ejercicio_contrarreloj(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'No autenticado'}, status=401)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            es_correcto = data.get('es_correcto', False)
            
            if es_correcto:
                request.session['puntaje_contrarreloj'] = request.session.get('puntaje_contrarreloj', 0) + 10
            
            request.session['indice_palabra_actual'] = request.session.get('indice_palabra_actual', 0) + 1
            
            # Obtener los datos del siguiente ejercicio
            palabras_ids = request.session.get('palabras_contrarreloj', [])
            indice_actual = request.session.get('indice_palabra_actual', 0)
            
            if indice_actual >= len(palabras_ids):
                return JsonResponse({
                    'status': 'completed',
                    'redirect_url': reverse('resultado_contrarreloj'),
                })
            
            palabra_actual = Palabra.objects.get(id=palabras_ids[indice_actual])
            archivo_url = f"{MANITO_BUCKET_DOMAIN}/{palabra_actual.gesto}"
            
            return JsonResponse({
                'status': 'success',
                'archivo_url': archivo_url,
                'palabra_correcta': palabra_actual.palabra,
                'indice_actual': indice_actual,
                'total_palabras': len(palabras_ids),
                'puntaje_actual': request.session.get('puntaje_contrarreloj', 0),
            })
        
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)


def resultado_contrarreloj(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Calcular tiempo transcurrido
    tiempo_inicio = request.session.get('tiempo_inicio', time.time())
    tiempo_transcurrido = time.time() - tiempo_inicio
    
    # Obtener resultados
    puntaje = request.session.get('puntaje_contrarreloj', 0)
    total_palabras = len(request.session.get('palabras_contrarreloj', []))

    perfil = Profile.objects.get(user=request.user)
    perfil.puntos += puntaje
    perfil.save()
    
    # Limpiar la sesión
    for key in ['palabras_contrarreloj', 'indice_palabra_actual', 'puntaje_contrarreloj', 'tiempo_inicio']:
        if key in request.session:
            del request.session[key]
    
    context = {
        'puntaje': puntaje,
        'total_palabras': total_palabras,
        'tiempo_transcurrido': round(tiempo_transcurrido, 2),
        'porcentaje': round((puntaje / total_palabras) * 100, 2) if total_palabras > 0 else 0
    }
    
    return render(request, 'resultado.html', context)


@csrf_exempt
def tiempo_terminado(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'No autenticado'}, status=401)
    
    if request.method == 'POST':
        # Guardar el puntaje actual si es necesario
        return JsonResponse({
            'status': 'completed',
            'redirect_url': reverse('resultado_contrarreloj')
        })
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)