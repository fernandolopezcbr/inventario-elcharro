from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from functools import wraps

def grupo_requerido(*grupos):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            if request.user.is_authenticated and request.user.groups.filter(name__in=grupos).exists():
                return view_func(request, *args, **kwargs)
            if not grupos and request.user.is_authenticated:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied('No tienes permiso para acceder a esta sección')
        return wrapper
    return decorator

def administrador_requerido(view_func):
    return grupo_requerido('Administrador')(view_func)