from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from registro.models import Profile
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Logro, Insignia
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from login.views import login_usuario
from inicio.models import Notificacion
# Create your views here.
@login_required
def perfil(request):
    usuario = request.user
    perfil = Profile.objects.get(user=usuario)  # Obtiene el perfil del usuario
    logros = Logro.objects.filter(usuario=perfil)
    insignias = [logro.insignia for logro in logros]  # Extrae las insignias
    notificaciones = Notificacion.objects.filter(receptor=request.user).order_by('-fecha')[:10]

    try:
        medalla = perfil.medalla  # Obtiene la medalla del usuario
    except Profile.DoesNotExist:
        medalla = None  # Si el usuario no tiene perfil, medalla será None
    contexto = {
            'usuario': usuario,
            'imagen': perfil.imagen,
            'medalla': perfil.medalla,
            'insignias': insignias,
            'racha': perfil.racha,
            'puntos': perfil.puntos,
            'notificaciones': notificaciones,
    }
    print(perfil.imagen.url)

    return render(request, 'perfil.html', contexto)

@login_required

def cambiar_foto_perfil(request):
    if request.method == 'POST':
        nueva_imagen = request.FILES.get('nueva_imagen')
        if nueva_imagen:
            perfil = Profile.objects.get(user=request.user)
            primer_cambio = perfil.imagen.name.endswith('default.jpg') # Ajusta si tienes imagen por defecto
            perfil.imagen = nueva_imagen
            perfil.save()
            messages.success(request, 'Foto de perfil actualizada correctamente')
            print("Imagen subida:", perfil.imagen.url)

            if primer_cambio:
                print("Nombre actual de imagen:", perfil.imagen.name)

                try:
                    insignia_fotogenico = Insignia.objects.get(imagen="insignias/fotogenico.png")
                    logro_existente = Logro.objects.filter(usuario=perfil, insignia=insignia_fotogenico).exists()

                    if not logro_existente:
                        Logro.objects.create(usuario=perfil, insignia=insignia_fotogenico)
                        messages.success(request, '¡Has ganado la insignia Fotogénico! 🏅')
                except Insignia.DoesNotExist:
                    messages.error(request, 'La insignia "Fotogénico" no existe en la base de datos.')
        else:
            messages.error(request, 'No se seleccionó ninguna imagen')
    return redirect('perfil')


def cambiar_nombre(request):
    if not request.user.is_authenticated:
        return redirect('login')  

    usuario = request.user
    try:
        perfil = Profile.objects.get(user=usuario)
    except Profile.DoesNotExist:
        return redirect('login')

    if request.method == 'POST' and 'nuevo_username' in request.POST:
        nuevo_username = request.POST.get('nuevo_username').strip()
        
        if nuevo_username and nuevo_username != usuario.username:
            # Verifica si el nombre ya existe
            if not User.objects.filter(username=nuevo_username).exclude(pk=usuario.pk).exists():
                usuario.username = nuevo_username
                usuario.save()
                
                # Actualiza la instancia del usuario en la sesión
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, usuario)
                
                messages.success(request, 'Nombre de usuario actualizado correctamente')
            else:
                messages.error(request, 'Este nombre de usuario ya está en uso')
        else:
            messages.error(request, 'El nombre de usuario no puede estar vacío o ser igual al actual')
        
        return redirect('perfil')

    contexto = {
        'usuario': usuario,
        'imagen': perfil.imagen,
        'medalla': perfil.medalla, 
        'racha': perfil.racha,
        'puntos': perfil.puntos,
    }
    return render(request, 'perfil.html', contexto)


@csrf_exempt
def cambiar_tema(request):
    if request.method == 'POST' and request.user.is_authenticated:
        data = json.loads(request.body)
        tema = data.get('theme')

        profile = Profile.objects.get(user=request.user)
        profile.theme = tema
        profile.save()

        return JsonResponse({'status': 'ok', 'theme': tema})
    return JsonResponse({'status': 'error'}, status=400)



def obtener_tema(request):
    if request.user.is_authenticated:
        theme = request.user.profile.theme 
        return JsonResponse({'theme': theme})
    return JsonResponse({'theme': 'light'})  # Default para usuarios no autenticados

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login_usuario')  # Redirige a la página de inicio de sesión después de cerrar sesión
    return render(request, 'login.html')  