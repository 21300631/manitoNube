from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from inicio.models import Notificacion
from django.shortcuts import render
from registro.models import Profile
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from ejercicio.views import PalabraUsuario
from perfil.views import Insignia, Logro
from inicio.models import Medalla

@login_required
def inicioSesion(request):
    usuario = request.user
    perfil = Profile.objects.get(user=usuario)  # Obtiene el perfil del usuario
    notificaciones = Notificacion.objects.filter(receptor=request.user).order_by('-fecha')[:10]
    racha = perfil.racha

    # Para el repaso
    hayPalabras = PalabraUsuario.objects.filter(usuario=perfil)
    cantidadPalabras = hayPalabras.count()
    print(f"# palabras: {cantidadPalabras}")
    now = timezone.now()
    if hayPalabras.exists():
        if perfil.last_login:
            minutes_since_last_login = (now - perfil.last_login).total_seconds() / 60
            # days_since_last_login = (now - perfil.last_login).days
            if minutes_since_last_login > 15:
                messages.success(request, "¡Que bueno que has vuelto! No te habíamos visto en más de 3 días.", extra_tags='welcome_back success')
            if minutes_since_last_login > 10:
                perfil.racha = 0
                perfil.save()
    else:
        print("No hay repaso porque no hay que repasar")

    # Actualizar la última fecha de login
    perfil.last_login = now
    perfil.save()

    medalla = getattr(perfil, "medalla", None)

    ultimas_senias = PalabraUsuario.objects.filter(usuario=perfil, precision__gte=80).order_by('-fecha_completada')[:4]

    cantidad_precisas = sum(1 for s in ultimas_senias if s.precision >= 80)

    if cantidad_precisas >= 4:
        nueva_medalla_img = "medallas/oro.png"
    elif cantidad_precisas == 3:
        nueva_medalla_img = "medallas/plata.png"
    elif cantidad_precisas == 2:
        nueva_medalla_img = "medallas/bronce.png"
    else:
        nueva_medalla_img = "medallas/circulo.png"

    try:
        nueva_medalla = Medalla.objects.get(imagen=nueva_medalla_img)
        if perfil.medalla != nueva_medalla:
            perfil.medalla = nueva_medalla
            perfil.save()
            print(f"Medalla actualizada a: {nueva_medalla.nombre}")
    except Medalla.DoesNotExist:
        print(f"⚠️ Medalla con imagen '{nueva_medalla_img}' no encontrada.")


    print(f'Racha Usuario {racha}')
    if racha == 7:
    
        try:
            insignia_7dias= Insignia.objects.get(imagen="insignias/semana.png")
            logro_existente = Logro.objects.filter(usuario=perfil, insignia=insignia_7dias).exists()

            if not logro_existente:
                Logro.objects.create(usuario=perfil, insignia=insignia_7dias)
                print("Insignia semana")
                messages.success(request, '¡Has ganado la insignia 7 días por completar una semana de racha! Sigue así 🏅')
        except Insignia.DoesNotExist:
            messages.error(request, 'La insignia no existe')
    if racha == 30:    
        try:
            insignia_30dias= Insignia.objects.get(imagen="insignias/mes.png")
            logro_existente = Logro.objects.filter(usuario=perfil, insignia=insignia_30dias).exists()

            if not logro_existente:
                Logro.objects.create(usuario=perfil, insignia=insignia_30dias)
                print("Insignia mes")
                messages.success(request, '¡Has ganado la insignia 30 días por completar una mes de racha! Sigue así 🏅')
        except Insignia.DoesNotExist:
            messages.error(request, 'La insignia no existe')
    if racha == 90:    
        try:
            insignia_90dias= Insignia.objects.get(imagen="insignias/trimestre.png")
            logro_existente = Logro.objects.filter(usuario=perfil, insignia=insignia_90dias).exists()

            if not logro_existente:
                Logro.objects.create(usuario=perfil, insignia=insignia_90dias)
                print("Insignia trimestre")
                messages.success(request, '¡Has ganado la insignia 90 días por completar una tres meses de racha! Sigue así 🏅')
        except Insignia.DoesNotExist:
            messages.error(request, 'La insignia no existe')
    if racha == 365:    
        try:
            insignia_anio= Insignia.objects.get(imagen="insignias/year.png")
            logro_existente = Logro.objects.filter(usuario=perfil, insignia=insignia_anio).exists()

            if not logro_existente:
                Logro.objects.create(usuario=perfil, insignia=insignia_anio)
                print("Insignia year")
                messages.success(request, '¡Has ganado la insignia un año por completar una año de racha! Sigue así 🏅')
        except Insignia.DoesNotExist:
            messages.error(request, 'La insignia no existe')
    
    if cantidadPalabras == 10:    
        try:
            insignia_10P= Insignia.objects.get(imagen="insignias/calmado10.png")
            logro_existente = Logro.objects.filter(usuario=perfil, insignia=insignia_10P).exists()

            if not logro_existente:
                Logro.objects.create(usuario=perfil, insignia=insignia_10P)
                print("Insignia 10")
                messages.success(request, '¡Has ganado la insignia 10 palabras por completar 10 palabras! Sigue así 🏅')
        except Insignia.DoesNotExist:
            messages.error(request, 'La insignia no existe')

    if cantidadPalabras == 50:    
        try:
            insignia_50P= Insignia.objects.get(imagen="insignias/calmado50.png")
            logro_existente = Logro.objects.filter(usuario=perfil, insignia=insignia_50P).exists()

            if not logro_existente:
                Logro.objects.create(usuario=perfil, insignia=insignia_50P)
                print("Insignia 50")
                messages.success(request, '¡Has ganado la insignia 50 palabras por completar 50 palabras! Sigue así 🏅')
        except Insignia.DoesNotExist:
            messages.error(request, 'La insignia no existe')

    if cantidadPalabras == 100:    
        try:
            insignia_100P= Insignia.objects.get(imagen="insignias/feliz100.png")
            logro_existente = Logro.objects.filter(usuario=perfil, insignia=insignia_100P).exists()

            if not logro_existente:
                Logro.objects.create(usuario=perfil, insignia=insignia_100P)
                print("Insignia 100")
                messages.success(request, '¡Has ganado la insignia 50 palabras por completar 50 palabras! Sigue así 🏅')
        except Insignia.DoesNotExist:
            messages.error(request, 'La insignia no existe')

    if cantidadPalabras == 250:    
        try:
            insignia_250P= Insignia.objects.get(imagen="insignias/emocionado250.png")
            logro_existente = Logro.objects.filter(usuario=perfil, insignia=insignia_250P).exists()

            if not logro_existente:
                Logro.objects.create(usuario=perfil, insignia=insignia_250P)
                print("Insignia 250")
                messages.success(request, '¡Has ganado la insignia 250 palabras por completar 250 palabras! Sigue así 🏅')
        except Insignia.DoesNotExist:
            messages.error(request, 'La insignia no existe')
    
    if cantidadPalabras == 510:    
        try:
            insignia_510P= Insignia.objects.get(imagen="insignias/todas.png")
            logro_existente = Logro.objects.filter(usuario=perfil, insignia=insignia_510P).exists()

            if not logro_existente:
                Logro.objects.create(usuario=perfil, insignia=insignia_510P)
                print("Insignia 510")
                messages.success(request, '¡Has ganado la insignia todas las palabras por completar 510 palabras! Sigue así 🏅')
        except Insignia.DoesNotExist:
            messages.error(request, 'La insignia no existe')

    contexto = {
            'usuario': usuario,
            'imagen': perfil.imagen,
            'medalla': perfil.medalla,
            'racha': perfil.racha,
            'puntos': perfil.puntos,
            'notificaciones': notificaciones
    }
    print(f"Medalla del usuario: {perfil.medalla}")

    try:
        return render(request, 'inicio.html', contexto)
    except Exception as e:
        import traceback
        print("Error en inicioSesion:", e)
        traceback.print_exc()
        return render(request, 'error_generico.html', {'mensaje': str(e)})
    

@login_required
def puntosUsuario(request):
    user = request.user
    usuario = get_object_or_404(Profile, user=user)
    
    # Definir el número máximo de lecciones por etapa
    etapas_lecciones = {
        'etapa1': 38,
        'etapa2': 22,
        'etapa3': 55,
        'etapa4': 55
    }
    
    # Verificar si ha completado las lecciones de la etapa anterior
    etapa2_completa = usuario.puntos >= 6800 and usuario.leccion >= etapas_lecciones['etapa1']
    etapa3_completa = usuario.puntos >= 10200 and usuario.leccion >= sum(etapas_lecciones[e] for e in ['etapa1', 'etapa2'])
    etapa4_completa = usuario.puntos >= 16200 and usuario.leccion >= sum(etapas_lecciones[e] for e in ['etapa1', 'etapa2', 'etapa3'])
    
    return JsonResponse({
        'puntos': usuario.puntos,
        'leccion_actual': usuario.leccion,
        'unlocked_stages': {
            'etapa1': True,  # Siempre disponible
            'etapa2': etapa2_completa,
            'etapa3': etapa3_completa,
            'etapa4': etapa4_completa,
        },
        'etapas_lecciones': etapas_lecciones
    })

