from django.db import models
from registro.models import Profile

# Create your models here.

class Etapa(models.Model): #ya en SQL
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre
    
class EtapaUsuario(models.Model):
    usuario = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='etapas_usuario')
    etapa = models.ForeignKey(Etapa, on_delete=models.CASCADE, related_name='etapas_usuario')

class Categoria(models.Model): #ya en SQL
    nombre = models.CharField(max_length=50)
    etapa = models.ForeignKey(Etapa, on_delete=models.CASCADE, related_name='categorias', null=True, blank=True)

    def __str__(self):
        return self.nombre

class Leccion(models.Model): # ya en SQL
    etapa = models.ForeignKey(Etapa, on_delete=models.CASCADE, related_name='lecciones', null=True, blank=True)

class LeccionUsuario(models.Model):
    usuario = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='lecciones_usuario')
    leccion = models.ForeignKey(Leccion, on_delete=models.CASCADE, related_name='lecciones_usuario')
    completada = models.BooleanField(default=False)  # Para saber si la lección ha sido completada
    fecha_completada = models.DateTimeField(null=True, blank=True)  # Fecha de finalización de la lección


class Palabra(models.Model): 
    palabra = models.CharField(max_length=50)
    leccion = models.ForeignKey('Leccion', on_delete=models.CASCADE, related_name='palabras')
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='palabras', null=True, blank=True)
    ejemplos = models.TextField(default='')
    gesto = models.URLField(default='', blank=True)  # URL de la imagen o video en S3
    frase = models.TextField(default='')  # Frase de ejemplo con la palabra


    def __str__(self):
        return self.palabra

class PalabraUsuario(models.Model):
    usuario = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='palabras_usuario')
    palabra = models.ForeignKey(Palabra, on_delete=models.CASCADE, related_name='palabras_usuario')
    fecha_completada = models.DateTimeField(null=True, blank=True)  # Fecha de finalización de la palabra
    precision = models.FloatField(default=0.0)  # Precisión del usuario al realizar el gesto


class Instruccion(models.Model): #ya en SQL
    TIPOS_INSTRUCCION = [
        ('seleccion', 'Selecciona el gesto correcto para {palabra}'),
        ('seleccion2', 'Selecciona el gesto correcto a la palabra resaltada'), #Este ejercicio muestran los ejemplos
        ('emparejar', 'Empareja las palabras con su respectivo texto'),
        ('completar', 'Selecciona el gesto que completa la frase'),
        ('escribir', 'Escribe la palabra que corresponde al gesto'),
        ('gesto', 'Realiza el siguiente gesto para la palabra {palabra}'),
    ]
    tipo = models.CharField(max_length=20, choices=TIPOS_INSTRUCCION)
    
    def generar_texto(self, palabra):
        return self.get_tipo_display().format(palabra=palabra)
    
    def __str__(self):
        return self.get_tipo_display()
    