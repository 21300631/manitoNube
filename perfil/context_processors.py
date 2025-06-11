from registro.models import Profile

def theme_context(request):
    theme = "light"
    if request.user.is_authenticated:
        try:
            profile = Profile.objects.get(user=request.user)
            theme = profile.theme
        except Profile.DoesNotExist:
            pass
    return {"theme": theme}
