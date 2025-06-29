from django.shortcuts import render
from django.views.generic import ListView
from publicacion.models import Publicacion, Comentario
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from registro.models import Profile
from django.http import JsonResponse
from inicio.models import Notificacion
from django.contrib import messages
from perfil.models import Insignia, Logro


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
            if profile != publicacion.usuario.user:  
                Notificacion.objects.create(
                    emisor=request.user,
                    receptor=publicacion.usuario.user,
                    tipo='like',
                    publicacion=publicacion
                )

            if publicacion.likes.count() > 3:
                try:
                    insignia_popular = Insignia.objects.get(imagen="insignias/popular.png")
                    creador_publicacion = publicacion.usuario
                    
                    if not Logro.objects.filter(usuario=creador_publicacion, insignia=insignia_popular).exists():
                        Logro.objects.create(
                            usuario=creador_publicacion,
                            insignia=insignia_popular
                        )
                except Insignia.DoesNotExist:
                    print("Insignia popular.png no encontrada en la base de datos")

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


    if publicacion.reportes.count() >= 2:
        publicacion.delete()
        eliminada = True

    return JsonResponse({
        'total_reportes': publicacion.reportes.count() if not eliminada else 0,
        'eliminada': eliminada
    })

@login_required
def agregar_comentario(request, publicacion_id):
    publicacion = get_object_or_404(Publicacion, id=publicacion_id)
    perfil_comentarista = request.user.profile

    if request.method == "POST":
        contenido = request.POST.get("contenido")
        archivo = request.FILES.get("archivo")

        if archivo:
            ALLOWED_TYPES = [
                'image/jpeg', 'image/png', 'image/gif',
                'video/mp4', 'video/webm', 'video/ogg'
            ]
            
            if archivo.content_type not in ALLOWED_TYPES:
                messages.error(request, 'Tipo de archivo no permitido')
                return redirect("foro")

        if contenido:  
            Comentario.objects.create(
                publicacion=publicacion,
                usuario=perfil_comentarista,
                contenido=contenido,
                archivo=archivo
            )
            
            if request.user != publicacion.usuario.user:
                Notificacion.objects.create(
                    emisor=request.user,
                    receptor=publicacion.usuario.user,
                    tipo='comentario',
                    publicacion=publicacion
                )
                
                try:
                    insignia = Insignia.objects.get(imagen="insignias/caridad.png")
                    
                    if not Logro.objects.filter(usuario=perfil_comentarista, insignia=insignia).exists():
                        comentarios_a_otros = Comentario.objects.filter(
                            usuario=perfil_comentarista
                        ).exclude(
                            publicacion__usuario=perfil_comentarista
                        ).count()
                        
                        if comentarios_a_otros == 1:
                            Logro.objects.create(
                                usuario=perfil_comentarista,
                                insignia=insignia
                            )
                            messages.success(request, '¡Has ganado la insignia "Alma Caritativa" por ayudar a otros usuarios!', extra_tags='swal_subtitle')
                except Insignia.DoesNotExist:
                    print("Error: Insignia no encontrada")

    return redirect("foro")

def vista_alguna(request):
    perfil = Profile.objects.get(user=request.user)
    return render(request, 'foro.html', {'theme': perfil.theme})