from django.db import models
from registro.models import Profile
from django.contrib.auth.models import User
from publicacion.models import Publicacion
# Create your models here.
class Medalla(models.Model):
    nombre = models.CharField(max_length=50)
    imagen = models.ImageField(upload_to='medallas/')
    
    class Meta:
        ordering = ['nombre']  # Orden: Bronce, Plata, Oro
    
    def __str__(self):
        return self.nombre


class Notificacion(models.Model):
    TIPOS = [
        ('like', 'Like'),
        ('comentario', 'Comentario'),
        ('reporte', 'Reporte'),
    ]

    emisor = models.ForeignKey(User, related_name='emisor', on_delete=models.CASCADE)
    receptor = models.ForeignKey(User, related_name='receptor', on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    leida = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.emisor.username} -> {self.receptor.username} ({self.tipo})'
