from django.shortcuts import render
from django.views.generic import ListView
from publicacion.models import Publicacion, Comentario
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from registro.models import Profile
from django.http import JsonResponse
from inicio.models import Notificacion
from django.contrib import messages


# Create your views here.
def foro(request):
    publicaciones = Publicacion.objects.all().order_by("-fecha")  # Ordenar por fecha
    
    return render(request, "foro.html", {"publicaciones": publicaciones})


@login_required
def dar_like(request, publicacion_id):
    if request.method == "POST":
        publicacion = get_object_or_404(Publicacion, id=publicacion_id)
        profile = request.user.profile
        liked = False

        if profile in publicacion.likes.all():
            publicacion.likes.remove(profile)
        else:
            publicacion.likes.add(profile)
            liked = True
            if profile != publicacion.usuario.user:  # para no notificar si se da like a sí mismo
                Notificacion.objects.create(
                    emisor=request.user,
                    receptor=publicacion.usuario.user,
                    tipo='like',
                    publicacion=publicacion
                )

        return JsonResponse({
            'total_likes': publicacion.likes.count(),
            'liked': liked
        })


@login_required
def reportar(request, publicacion_id):
    publicacion = get_object_or_404(Publicacion, id=publicacion_id)
    user_profile = request.user.profile

    eliminada = False
    if user_profile not in publicacion.reportes.all():
        publicacion.reportes.add(user_profile)
        if user_profile != publicacion.usuario.user:
            Notificacion.objects.create(
                emisor=request.user,
                receptor=publicacion.usuario.user,
                tipo='reporte',
                publicacion=publicacion
            )


    if publicacion.reportes.count() >= 15:
        publicacion.delete()
        eliminada = True

    return JsonResponse({
        'total_reportes': publicacion.reportes.count() if not eliminada else 0,
        'eliminada': eliminada
    })

@login_required
def agregar_comentario(request, publicacion_id):
    publicacion = get_object_or_404(Publicacion, id=publicacion_id)

    if request.method == "POST":
        contenido = request.POST.get("contenido")
        archivo = request.FILES.get("archivo")

        # Validar tipos de archivo permitidos
        if archivo:
            ALLOWED_TYPES = [
                'image/jpeg', 'image/png', 'image/gif',
                'video/mp4', 'video/webm', 'video/ogg'
            ]
            
            if archivo.content_type not in ALLOWED_TYPES:
                messages.error(request, 'Tipo de archivo no permitido')
                return redirect("foro")

        if contenido:  # Asegurar que no se envíe un comentario vacío
            Comentario.objects.create(
                publicacion=publicacion,
                usuario=request.user.profile,  # Asumiendo que tienes un `Profile` relacionado con `User`
                contenido=contenido,
                archivo=archivo
            )
            if request.user.profile != publicacion.usuario.user:
                Notificacion.objects.create(
                    emisor=request.user,
                    receptor=publicacion.usuario.user,
                    tipo='comentario',
                    publicacion=publicacion
                )


    return redirect("foro")  # Redirigir al foro después de comentar

def vista_alguna(request):
    perfil = Profile.objects.get(user=request.user)
    return render(request, 'foro.html', {'theme': perfil.theme})