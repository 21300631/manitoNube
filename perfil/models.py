from django.db import models

class Insignia(models.Model):
    nombre = models.CharField(max_length=50)
    imagen = models.ImageField(upload_to='insignias/')
    
    def __str__(self):
        return self.nombre
    
class Logro(models.Model):
    usuario = models.ForeignKey('registro.Profile', on_delete=models.CASCADE)  # Usar referencia de cadena
    insignia = models.ForeignKey(Insignia, on_delete=models.CASCADE)

    def __str__(self):
        return f"Logro de {self.usuario.user.username}"