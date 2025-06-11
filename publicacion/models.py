from django.db import models
from django.contrib.auth.models import User
from registro.models import Profile
from .storages import ImageStorage

class Publicacion(models.Model):
    titulo = models.CharField(max_length=255)
    usuario = models.ForeignKey(Profile, on_delete=models.SET_DEFAULT, default=1)  # Usa Profile en lugar de User
    contenido = models.TextField()
    hashtags = models.CharField(max_length=100, blank=True, null=True)  # Añadido max_length
    archivo_media = models.FileField(
        storage=ImageStorage(), 
        upload_to='posts/', 
        blank=True, 
        null=True
    )
    likes = models.ManyToManyField(
        Profile, 
        related_name='likes_publicaciones', 
        blank=True
    )
    reportes = models.ManyToManyField(
        Profile, 
        related_name='reportes_publicaciones', 
        blank=True
    )
    fecha = models.DateTimeField(auto_now_add=True)

    def total_likes(self):
        return self.likes.count()

    def total_reportes(self):
        return self.reportes.count()

    def __str__(self):
        return self.titulo

class Comentario(models.Model):
    publicacion = models.ForeignKey(
        Publicacion, 
        on_delete=models.CASCADE, 
        related_name="comentarios"
    )
    usuario = models.ForeignKey(Profile, on_delete=models.CASCADE)  # Usa Profile
    contenido = models.TextField()
    archivo = models.FileField(
        storage=ImageStorage(), 
        upload_to='posts/', 
        blank=True, 
        null=True
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comentario de {self.usuario.user.username} en {self.publicacion.titulo}'