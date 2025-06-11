from django.shortcuts import render, redirect
from registro.models import Profile
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from ejercicio.models import PalabraUsuario, Palabra

# Create your views here.
#Estas partes son para que se vea el progreso de las lecciones y se desbloqueen las siguientes
@login_required
def etapa1(request):
    usuario = request.user
    profile = Profile.objects.get(user=usuario)
    leccion_actual = profile.leccion  # Suponiendo que guardas la última lección alcanzada

    lecciones_etapa1 = list(range(1, 39)) + [501, 502, 503, 504]
    
    # Inicializa todas las lecciones como bloqueadas
    lecciones_estado = {i: 'bloqueada' for i in lecciones_etapa1 } # Ajusta el rango según tus lecciones
    
    # Marcar lecciones completadas (todas las anteriores a la actual)
    for i in range(1, leccion_actual):
        lecciones_estado[i] = 'completada'

    # Para las loterias de repaso
    if leccion_actual == 9:
        lecciones_estado[501] = 'completada'
    elif leccion_actual == 21:
        lecciones_estado[502] = 'completada'
    elif leccion_actual == 28:
        lecciones_estado[503] = 'completada'
    elif leccion_actual == 38:
        lecciones_estado[504] = 'completada'
    
    # Marcar lección actual
    if leccion_actual <= max(lecciones_estado.keys()):
        lecciones_estado[leccion_actual] = 'en-progreso'
    
    # Opcional: forzar desbloqueo de la primera si todas están bloqueadas
    if all(status == 'bloqueada' for status in lecciones_estado.values()):
        lecciones_estado[1] = 'en-progreso'

    palabras_por_leccion = {}
    for leccion_id in lecciones_etapa1:
        palabras = Palabra.objects.filter(leccion_id=leccion_id).values_list('palabra', flat=True)
        palabras_por_leccion[leccion_id] = list(palabras)
    
    return render(request, 'etapa1.html', {
        'lecciones_estado': lecciones_estado,
        'palabras_por_leccion': palabras_por_leccion,
        'theme': profile.theme if hasattr(profile, 'theme') else 'light'
    })       

@login_required
def etapa2(request):
    usuario = request.user
    profile = Profile.objects.get(user=usuario)
    leccion_actual = profile.leccion
    
    # Lecciones de la etapa 2 (IDs del 39 al 60 y repasos 201-202)
    lecciones_etapa2 = list(range(39, 61)) + [201, 202]
    
    # Inicializa todas como bloqueadas
    lecciones_estado = {i: 'bloqueada' for i in lecciones_etapa2}
    
    # Marcar completadas (las anteriores a la actual en esta etapa)
    for i in range(34, leccion_actual):
        if i in lecciones_estado:
            lecciones_estado[i] = 'completada'

    if leccion_actual == 45:
        lecciones_estado[201] = 'completada'
    elif leccion_actual == 60:
        lecciones_estado[202] = 'completada'
    
    # Marcar lección actual
    if leccion_actual in lecciones_estado:
        lecciones_estado[leccion_actual] = 'en-progreso'
    
    # Forzar primera lección si todas están bloqueadas
    if all(status == 'bloqueada' for status in lecciones_estado.values()):
        lecciones_estado[34] = 'en-progreso'
    
    return render(request, 'etapa2.html', {
        'lecciones_estado': lecciones_estado,
        'theme': profile.theme if hasattr(profile, 'theme') else 'light'
    })

@login_required
def etapa3(request):
    usuario = request.user
    profile = Profile.objects.get(user=usuario)
    leccion_actual = profile.leccion
    
    # Lecciones de la etapa 3 (IDs del 54 al 107 y repasos 301-304)
    lecciones_etapa3 = list(range(61, 116)) + [301, 302, 303, 304]
    
    # Inicializa todas como bloqueadas
    lecciones_estado = {i: 'bloqueada' for i in lecciones_etapa3}
    
    # Marcar completadas (las anteriores a la actual en esta etapa)
    for i in range(56, leccion_actual):
        if i in lecciones_estado:
            lecciones_estado[i] = 'completada'
    
    # Marcar lección actual
    if leccion_actual in lecciones_estado:
        lecciones_estado[leccion_actual] = 'en-progreso'
    
    if leccion_actual == 74:
        lecciones_estado[301] = 'completada'
    elif leccion_actual == 88:
        lecciones_estado[302] = 'completada'
    elif leccion_actual == 102:
        lecciones_estado[303] = 'completada'
    elif leccion_actual == 115:
        lecciones_estado[304] = 'completada'
    
    # Forzar primera lección si todas están bloqueadas
    if all(status == 'bloqueada' for status in lecciones_estado.values()):
        lecciones_estado[54] = 'en-progreso'
    
    return render(request, 'etapa3.html', {
        'lecciones_estado': lecciones_estado,
        'theme': profile.theme if hasattr(profile, 'theme') else 'light'
    })


@login_required
def etapa4(request):
    usuario = request.user
    profile = Profile.objects.get(user=usuario)
    leccion_actual = profile.leccion
    
    # Rango de lecciones (116-164) y repasos (401-405)
    rango_lecciones = list(range(116, 165))
    repasos = [401, 402, 403, 404, 405]
    
    # Inicializar todas como bloqueadas
    lecciones_estado = {leccion: 'bloqueada' for leccion in rango_lecciones + repasos}
    
    # Si viene de etapa anterior, comenzar en 110
    if leccion_actual < 110:
        leccion_actual = 110
        profile.leccion = 110
        profile.save()
    
    # Marcar completadas
    for leccion in rango_lecciones:
        if leccion < leccion_actual:
            lecciones_estado[leccion] = 'completada'

    # Marcar repasos completados
    if leccion_actual == 129:
        lecciones_estado[401] = 'completada'
    elif leccion_actual == 143:
        lecciones_estado[402] = 'completada'
    elif leccion_actual == 152:
        lecciones_estado[403] = 'completada'
    elif leccion_actual == 161:
        lecciones_estado[404] = 'completada'
    elif leccion_actual == 170:
        lecciones_estado[405] = 'completada'

    
    # Marcar actual
    if leccion_actual in lecciones_estado:
        lecciones_estado[leccion_actual] = 'en-progreso'
    
    return render(request, 'etapa4.html', {
        'lecciones_estado': lecciones_estado,
        'theme': profile.theme if hasattr(profile, 'theme') else 'light'
    })
