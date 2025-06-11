from django.contrib.auth.models import User
from django.db import models
from .storages import ImageStorage
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Conexión con User
    edad = models.IntegerField()
    racha = models.IntegerField(default=0)
    imagen = models.ImageField(
        storage=ImageStorage(), 
        upload_to='usuario/', 
        blank=True, 
        null=True,
        default='usuario/default.jpg'
        )
    puntos = models.IntegerField(default=0)
    medalla = models.ForeignKey('inicio.Medalla', on_delete=models.SET_NULL, null=True, blank=True)
    theme = models.CharField(max_length=10, default="light")  # 'light' o 'dark'
    leccion = models.IntegerField(default=1)  # ID de la lección actual
    last_login = models.DateTimeField(default=timezone.now)  # Fecha y hora del último inicio de sesión

    @property
    def medalla_actual(self):
        """Devuelve la medalla de mayor rango (para templates)"""
        return self.medalla
    
    
    def __str__(self):
        return self.user.username
    
    def actualizar_racha(self):
        ahora = timezone.now()
        diferencia = ahora - self.last_login
        
        # Si pasaron más de 10 minutos, reiniciar racha
        if diferencia > timezone.timedelta(minutes=15):
            print(f"Diferencia de teimpo: {diferencia}.")
            if self.racha > 0:
                print(f"Reiniciando racha para {self.user.username}")
            self.racha = 0
        else:
            # Incrementar racha y otorgar puntos
            self.racha += 1
            self.puntos += 10  # 10 puntos por mantener la racha
            print(f"Tiempo desde el último acceso: {diferencia}.")
            print(f"Racha incrementada: {self.racha} (10 puntos añadidos)")
        
        self.last_login = ahora  # Actualizamos el último acceso
        self.save()