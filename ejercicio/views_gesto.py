# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from inicio.models import RegistroGesto


@csrf_exempt
@require_POST
def evaluar_gesto(request, palabra_id):
    try:
        from django.utils import timezone
        import json
        
        data = json.loads(request.body)
        correcto = data.get('correcto', False)
        
        # Registrar el gesto (usando tu modelo RegistroGesto)
        RegistroGesto.objects.create(
            usuario=request.user.profile,
            palabra_id=palabra_id,
            correcto=correcto,
            fecha=timezone.now()
        )
        
        return JsonResponse({'status': 'success'})
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)