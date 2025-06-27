from manito.settings import MANITO_BUCKET_DOMAIN
from django.utils.safestring import mark_safe
from django.templatetags.static import static
from django.shortcuts import render, redirect
from registro.models import Profile
from .models import PalabraUsuario
from .models import Palabra
import random
import re

def ejercicio_emparejar(request):
    ejercicios = request.session.get('ejercicios', [])
    index = request.session.get('ejercicio_actual', 0)
    progreso = request.session.get('progreso', 0)
    print(f"Ejercicio Emparejar - Índice: {index + 1}, Total Ejercicios: {len(ejercicios)}, Progreso {progreso}")  # Debug
    
    if index >= len(ejercicios):
        return redirect('mostrar_ejercicio')

    ejercicio_actual = ejercicios[index]
    palabra_id = ejercicio_actual['palabra']
    palabra_obj = Palabra.objects.get(id=palabra_id)

    user = request.user
    perfil = Profile.objects.get(user=user)

    # Obtener palabras para el ejercicio
    if PalabraUsuario.objects.filter(usuario=perfil).count() < 2:
        palabras_usuario = list(
            Palabra.objects.filter(leccion=1).exclude(id=palabra_obj.id).order_by('?')[:2]
        )
    else:
        relaciones_usuario = PalabraUsuario.objects.filter(usuario=perfil).exclude(palabra=palabra_obj)
        palabras_usuario = [relacion.palabra for relacion in relaciones_usuario.order_by('?')[:2]]

    opciones = palabras_usuario + [palabra_obj]
    random.shuffle(opciones)  # Mezclar palabras

    # Crear lista de gestos mezclada (no en el mismo orden que las palabras)
    gestos_mezclados = opciones.copy()
    random.shuffle(gestos_mezclados)

    opciones_gestos_con_url = []
    for gesto_obj in gestos_mezclados:
        es_video = str(gesto_obj.gesto).lower().endswith('.mp4')
        opciones_gestos_con_url.append({
            'objeto': gesto_obj,
            'url': f"{MANITO_BUCKET_DOMAIN}/{gesto_obj.gesto}",
            'es_video': es_video
        })

    context = {
        'theme': request.session.get('theme', 'claro'),
        'texto_instruccion': "Empareja cada palabra con su gesto correspondiente",
        'palabras': opciones,
        'gestos': opciones_gestos_con_url,
    }
    return render(request, 'emparejar.html', context)

def ejercicio_seleccion(request):
    ejercicios = request.session.get('ejercicios', [])
    index = request.session.get('ejercicio_actual', 0)
    progreso = request.session.get('progreso', 0)
    print(f"Ejercicio seleccion - Índice: {index + 1}, Total Ejercicios: {len(ejercicios)}, Progreso {progreso}")  # Debug

    
    if index >= len(ejercicios):
        return redirect('mostrar_ejercicio')

    ejercicio_actual = ejercicios[index]
    palabra_id = ejercicio_actual['palabra']  # Obtener el ID de la palabra del ejercicio actual
    palabra_obj = Palabra.objects.get(id=palabra_id)

    # Distractores (otras palabras)
    gestos_distractores = list(
        Palabra.objects.exclude(id=palabra_obj.id).order_by('?')[:2]
    )

    # Opciones mezcladas
    opciones = gestos_distractores + [palabra_obj]
    random.shuffle(opciones)

    # Creamos una lista de opciones con URL completa y tipo (imagen o video)
    opciones_data = []
    for opcion in opciones:
        url = f"{MANITO_BUCKET_DOMAIN}/{opcion.gesto}"
        es_video = opcion.gesto.lower().endswith('.mp4')
        opciones_data.append({
            'id': opcion.id,
            'palabra': opcion.palabra,
            'url': url,
            'es_video': es_video,
        })

    context = {
        'theme': 'claro',  # o 'oscuro'
        'texto_instruccion': f"Selecciona el gesto correcto para: {palabra_obj.palabra}",
        'opciones': opciones_data,
        'palabra_correcta_id': palabra_obj.id,
    }
    print("Opciones:", opciones_data)
    return render(request, 'seleccion.html', context)

def ejercicio_seleccion2(request):
    print("Ejercicio Selección 2")
    ejercicios = request.session.get('ejercicios', [])
    index = request.session.get('ejercicio_actual', 0)
    progreso = request.session.get('progreso', 0)
    print(f"Ejercicio seleccion2 - Índice: {index + 1}, Total Ejercicios: {len(ejercicios)}, Progreso {progreso}")  # Debug

    
    if index >= len(ejercicios):
        return redirect('mostrar_ejercicio')

    ejercicio_actual = ejercicios[index]
    palabra_id = ejercicio_actual['palabra']  # Obtener el ID de la palabra del ejercicio actual
    palabra_obj = Palabra.objects.get(id=palabra_id)

    # Obtener ejemplos como lista
    ejemplos_raw = palabra_obj.ejemplos.split(" - ")

    # Resaltar la palabra objetivo en los ejemplos
    palabra_resaltada = palabra_obj.palabra
    ejemplos_resaltados = []
    for ejemplo in ejemplos_raw:
        resaltado = re.sub(
            fr'({re.escape(palabra_resaltada)})',
            r'<span class="resaltado">\1</span>',
            ejemplo,
            flags=re.IGNORECASE
        )
        ejemplos_resaltados.append(mark_safe(resaltado))  # Mark safe para permitir HTML

    # Distractores
    distractores = list(Palabra.objects.exclude(id=palabra_obj.id).order_by('?')[:2])

    # Opciones mezcladas
    opciones = distractores + [palabra_obj]
    random.shuffle(opciones)

    # Preparar URLs y tipo de archivo
    opciones_data = []
    for opcion in opciones:
        url = f"{MANITO_BUCKET_DOMAIN}/{opcion.gesto}"
        es_video = opcion.gesto.lower().endswith('.mp4')
        opciones_data.append({
            'id': opcion.id,
            'palabra': opcion.palabra,
            'url': url,
            'es_video': es_video,
        })

    context = {
        'theme': 'claro',
        'texto_instruccion': "Selecciona el gesto correcto a la palabra resaltada",
        'ejemplos': ejemplos_resaltados,
        'opciones': opciones_data,
        'palabra_correcta_id': palabra_obj.id,
    }

    return render(request, 'seleccion2.html', context)


def ejercicio_completar(request):
    ejercicios = request.session.get('ejercicios', [])
    index = request.session.get('ejercicio_actual', 0)
    progreso = request.session.get('progreso', 0)
    print(f"Ejercicio completar - Índice: {index + 1}, Total Ejercicios: {len(ejercicios)}, Progreso {progreso}")  # Debug

    
    if index >= len(ejercicios):
        return redirect('mostrar_ejercicio')

    ejercicio_actual = ejercicios[index]
    palabra_id = ejercicio_actual['palabra']  # Obtener el ID de la palabra del ejercicio actual
    palabra_obj = Palabra.objects.get(id=palabra_id)
    
    
    # Frase con espacio en blanco
    frase_completar = palabra_obj.frase

    # Gestos distractores
    gestos_distractores = list(
        Palabra.objects.exclude(id=palabra_obj.id).order_by('?')[:2]
    )

    # Opciones mezcladas
    opciones = gestos_distractores + [palabra_obj]
    random.shuffle(opciones)

    # Agregamos URLs y tipo (video o imagen)
    opciones_data = []
    for opcion in opciones:
        url = f"{MANITO_BUCKET_DOMAIN}/{opcion.gesto}"
        es_video = opcion.gesto.lower().endswith('.mp4')
        opciones_data.append({
            'id': opcion.id,
            'palabra': opcion.palabra,
            'url': url,
            'es_video': es_video,
        })

    context = {
        'theme': 'claro',
        'texto_instruccion': "Selecciona el gesto que completa la frase:",
        'frase_completar': frase_completar,
        'opciones': opciones_data,
        'palabra_correcta_id': palabra_obj.id,
    }

    return render(request, 'completar.html', context)


def ejercicio_escribir(request):
    ejercicios = request.session.get('ejercicios', [])
    index = request.session.get('ejercicio_actual', 0)
    progreso = request.session.get('progreso', 0)
    print(f"Ejercicio escribir - Índice: {index + 1}, Total Ejercicios: {len(ejercicios)}, Progreso {progreso}")  # Debug

    
    if index >= len(ejercicios):
        return redirect('mostrar_ejercicio')

    ejercicio_actual = ejercicios[index]
    palabra_id = ejercicio_actual['palabra']  # Obtener el ID de la palabra del ejercicio actual
    palabra_obj = Palabra.objects.get(id=palabra_id)

    

    archivo_url = f"{MANITO_BUCKET_DOMAIN}/{palabra_obj.gesto}"
    es_video = palabra_obj.gesto.lower().endswith('.mp4')

    context = {
        'theme': 'claro',
        'texto_instruccion': "Escribe la palabra que corresponde al gesto",
        'gesto_url': archivo_url,
        'es_video': es_video,
        'palabra_correcta': palabra_obj.palabra,  # por si lo necesitas validar
    }

    print("Gesto URL:", archivo_url)
    return render(request, 'escribir.html', context)
from django.core.exceptions import ObjectDoesNotExist

def ejercicio_gesto(request):
    ejercicios = request.session.get('ejercicios', [])
    index = request.session.get('ejercicio_actual', 0)
    progreso = request.session.get('progreso', 0)
    print(f"Ejercicio Gesto - Índice: {index + 1}, Total Ejercicios: {len(ejercicios)}, Progreso {progreso}")

    if index >= len(ejercicios):
        return redirect('mostrar_ejercicio')

    ejercicio_actual = ejercicios[index]
    palabra_id = ejercicio_actual.get('palabra')  

    try:
        palabra = Palabra.objects.get(id=palabra_id)
    except ObjectDoesNotExist:
        print(f"❌ Palabra con ID {palabra_id} no encontrada.")
        return render(request, 'error_generico.html', {'mensaje': f'Palabra con ID {palabra_id} no encontrada.'})

    # Proteger contra gesto vacío o None
    gesto = palabra.gesto if palabra.gesto else ''
    archivo_url = f"{MANITO_BUCKET_DOMAIN}/{gesto}"
    
    print("Gesto URL:", archivo_url)

    json_url = static(f'landmarks/{palabra.palabra}.json')


    contexto = {
        'texto_instruccion': f"Realiza el gesto correspondiente a la palabra: {palabra.palabra}",
        'archivo': archivo_url,
        'is_video': gesto.lower().endswith('.mp4') if gesto else False,
        'theme': request.session.get('theme', 'light'),
        'palabra_correcta': palabra.palabra,
        'json_url': json_url,
        'palabra_id': palabra_id,  # Pasar el ID de la palabra al template
    }

    try:
        return render(request, 'gesto.html', contexto)
    except Exception as e:
        import traceback
        print("❌ ERROR EN TEMPLATE GESTO:", e)
        traceback.print_exc()
    return render(request, 'error_generico.html', {'mensaje': f'Error en template gesto: {str(e)}'})