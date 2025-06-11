from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
from perfil.models import  Logro, Insignia
import re
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from registro.models import Profile
from inicio.models import Medalla

def formulario(request):
    return render(request, 'registro.html')


@csrf_exempt  # Solo para pruebas, recuerda quitarlo después
def registro_usuario(request):
    if request.method == "POST":
        print(request.POST)  # Muestra los datos en la consola
        
        nombre = request.POST.get("nombre-personal")
        username = request.POST.get("usuario-nombre")
        edad = request.POST.get("usuario-edad")
        email = request.POST.get("usuario-correo")  
        password = request.POST.get("usuario-pass")
        password2 = request.POST.get("usuario-pass2")

        context = {  # Para que los datos no se borren si hay un error
            'nombre': nombre,
            'username': username,
            'edad': edad,
            'email': email,
        }

        # Validaciones
        if not (nombre and username and edad and email and password):
            context['error'] = 'Faltan campos obligatorios'
            return render(request, 'registro.html', context)
        
        if User.objects.filter(username=username).exists():
            context['error'] = 'El usuario ya existe'
            return render(request, 'registro.html', context)
        
        if User.objects.filter(email=email).exists():
            context['error'] = 'El correo ya está registrado'
            return render(request, 'registro.html', context)

        if len(password) < 8:
            context['error'] = 'La contraseña debe tener al menos 8 caracteres'
            return render(request, 'registro.html', context)
        if not re.search("[a-z]", password):
            context['error'] = 'La contraseña debe tener al menos una letra minúscula'
            return render(request, 'registro.html', context)
        if not re.search("[A-Z]", password):
            context['error'] = 'La contraseña debe tener al menos una letra mayúscula'
            return render(request, 'registro.html', context)
        if not re.search("[0-9]", password):
            context['error'] = 'La contraseña debe tener al menos un número'
            return render(request, 'registro.html', context)

        if password != password2:
            context['error'] = 'Las contraseñas no coinciden'
            return render(request, 'registro.html', context)

        # Crear usuario en la tabla `User` de Django
        nuevo_usuario = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=nombre
        )
        nuevo_usuario.save()


        # Creamos nuevo perfil de usuario 
        medalla = Medalla.objects.get(imagen='medallas/circulo.png')
        nuevo_perfil = Profile(user=nuevo_usuario, edad=edad, racha=0, imagen='usuario/default.jpg', puntos=0, medalla=medalla)
        nuevo_perfil.save()

        # profile = Profile.objects.create(
        #     user=nuevo_usuario,
        #     edad=int(edad),
        #     racha=0,          
        #     imagen='usuarios/default.jpg',
        #     puntos=0,
        #     medalla = 'medalla/default.jpg'
            
        # )

        # Asignar insignia de bienvenida
        insignia_bienvenido = Insignia.objects.get(imagen='insignias/bienvenidos.png')
        nuevo_logro = Logro(usuario=nuevo_perfil, insignia=insignia_bienvenido)
        nuevo_logro.save()
       
        # Iniciar sesión automáticamente después del registro
        login(request, nuevo_usuario)

        return redirect('/inicio/')

    return HttpResponse("Método no permitido", status=405)
