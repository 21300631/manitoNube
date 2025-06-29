from django.shortcuts import render, redirect
from .models import Publicacion
from django.views.decorators.csrf import csrf_exempt
from registro.models import Profile
from django.http import HttpResponse
from django.contrib import messages
MAX_IMAGE_SIZE = 500 * 1024  # 500 KB
MAX_VIDEO_SIZE = 10 * 1024 * 1024  # 10 MB
from perfil.models import Insignia, Logro

def pagina(request):
    edad = request.user.profile.edad
    return render(request, 'publicacionNueva.html', {'edad':edad})
@csrf_exempt  
def nueva_publicacion(request):
    if request.method == "POST":
        titulo = request.POST.get("titulo")
        contenido = request.POST.get("contenido")
        media = request.FILES.get("media")  # Puede ser imagen o video
        hashtags = request.POST.get("hashtags")

        usuario = request.user  
        profile = Profile.objects.get(user=usuario)  
        anios = profile.edad
        
        context = {
            'titulo': titulo,
            'contenido': contenido,
            'hashtags': hashtags,
            'edad': anios
        }

        # Validar campos obligatorios
        if not (titulo and contenido and hashtags):
            context['error'] = 'Faltan campos obligatorios'
            return render(request, 'publicacionNueva.html', context)

        if media:
            ALLOWED_TYPES = [
                'image/jpeg', 'image/png', 'image/gif',  # Imágenes
                'video/mp4', 'video/webm', 'video/ogg'   # Videos
            ]
            if media.content_type not in ALLOWED_TYPES:
                context['error'] = 'Tipo de archivo no permitido. Solo imágenes (JPEG, PNG, GIF) y videos (MP4, WebM, Ogg)'
                return render(request, 'publicacionNueva.html', context)
            
            # Validar tamaño máximo (ejemplo: 10MB)
            if media.size > 10 * 1024 * 1024:  # 10MB
                context['error'] = 'El archivo es demasiado grande (máximo 10MB)'
                return render(request, 'publicacionNueva.html', context)
            
        # Guardar la publicación
        try:
            nueva_publicacion = Publicacion.objects.create(
                titulo=titulo,
                contenido=contenido,
                archivo_media=media,
                hashtags=hashtags,
                usuario=profile
            )
            messages.success(request, '¡Publicación creada exitosamente!')

            # Asignar insignia "estudioso" si es la primera publicación
            publicaciones_count = Publicacion.objects.filter(usuario=profile).count()
            
            if publicaciones_count == 1:  # Si es la primera publicación
                try:
                    insignia_estudioso = Insignia.objects.get(imagen="insignias/estudioso.png")
                    # Verificar si el usuario no tiene ya esta insignia
                    if not Logro.objects.filter(usuario=profile, insignia=insignia_estudioso).exists():
                        Logro.objects.create(
                            usuario=profile,
                            insignia=insignia_estudioso
                        )
                        messages.success(request, '¡Felicidades! Has ganado la insignia Estudioso por crear tu primera publicación.')
                except Insignia.DoesNotExist:
                    print("Insignia estudioso.png no encontrada en la base de datos")

            return redirect('/publicacion/')
        
        except Exception as e:
            context['error'] = f'Error al crear la publicación: {str(e)}'
            return render(request, 'publicacionNueva.html', context)
    
    return HttpResponse("Método no permitido", status=405)


def vista_alguna(request):
    perfil = Profile.objects.get(user=request.user)
    return render(request, 'publicacion.html', {'theme': perfil.theme})