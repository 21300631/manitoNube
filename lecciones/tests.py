# from django.test import TestCase, RequestFactory
# from django.contrib.auth.models import User
# from registro.models import Profile
# from ejercicio.models import Leccion, PalabraUsuario, Instruccion
# from .views import generar_leccion_view

# class GenerarLeccionTestCase(TestCase):
#     def setUp(self):
#     # Configuración inicial para todos los tests
#     self.factory = RequestFactory()
    
#     # Crear usuario
#     self.user = User.objects.create_user(
#         username='testuser', 
#         password='testpass123'
#     )
    
#     # Crear perfil con TODOS los campos requeridos
#     self.profile = Profile.objects.create(
#         user=self.user,
#         leccion=1,  # Ahora que es IntegerField
#         edad=25,    # Proporciona un valor para edad
#         # Añade cualquier otro campo requerido que tenga tu modelo Profile
#         imagen='usuario/default.jpg',
#         # ... otros campos que tu modelo Profile requiera
#     )
    
#     # Resto de la configuración...
#     Instruccion.objects.create(
#         tipo='seleccion',
#         description='Selecciona el gesto correcto para {palabra}'
#     )
#     Instruccion.objects.create(
#         tipo='gesto',
#         description='Realiza el siguiente gesto para la palabra {palabra}'
#     )
    
#     # Crear palabras para lección
#     self.palabra1 = Leccion.objects.create(
#         leccion_id=1,
#         texto='palabra1'
#     )
#     self.palabra2 = Leccion.objects.create(
#         leccion_id=1,
#         texto='palabra2'
#     )
#     self.palabra3 = Leccion.objects.create(
#         leccion_id=1,
#         texto='palabra3'
#     )

#     def test_generar_leccion_usuario_autenticado(self):
#         """Test que verifica la generación de lección para usuario autenticado"""
#         request = self.factory.get('/generar-leccion/')
#         request.user = self.user
        
#         response = generar_leccion_view(request)
        
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('ejercicios', response.context)

#     def test_palabras_nuevas_con_instruccion_gesto(self):
#         """Verifica que palabras nuevas usen instrucción 'gesto'"""
#         request = self.factory.get('/generar-leccion/')
#         request.user = self.user
        
#         response = generar_leccion_view(request)
#         ejercicios = response.context['ejercicios']
        
#         # Las primeras 3 deberían ser de tipo 'gesto' (palabras nuevas)
#         for ejercicio in ejercicios[:3]:
#             self.assertEqual(ejercicio['instruccion'].tipo, 'gesto')

#     def test_cantidad_ejercicios(self):
#         """Verifica que se generen 10 ejercicios (3 nuevos + 7 repaso)"""
#         # Necesitas tener al menos 7 palabras de repaso para este test
#         for i in range(3, 10):
#             PalabraUsuario.objects.create(
#                 usuario=self.profile,
#                 texto=f'repaso_extra_{i}'
#             )
        
#         request = self.factory.get('/generar-leccion/')
#         request.user = self.user
        
#         response = generar_leccion_view(request)
#         ejercicios = response.context['ejercicios']
        
#         self.assertEqual(len(ejercicios), 10)

#     def test_usuario_no_autenticado(self):
#         """Test para usuario no autenticado"""
#         request = self.factory.get('/generar-leccion/')
#         request.user = AnonymousUser()
        
#         response = generar_leccion_view(request)
        
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('error', response.context)

#     def test_usuario_sin_perfil(self):
#         """Test para usuario sin perfil"""
#         new_user = User.objects.create_user(
#             username='noprofile', 
#             password='testpass123'
#         )
        
#         request = self.factory.get('/generar-leccion/')
#         request.user = new_user
        
#         response = generar_leccion_view(request)
        
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('error', response.context)