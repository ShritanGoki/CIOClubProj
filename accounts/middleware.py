from django.shortcuts import redirect
from django.urls import reverse


class AdminLockdownMiddleware:
    """Restrict User Administrator accounts to admin-only paths.

    The admin role is dashboard-only and must not access app features.
    This middleware redirects authenticated admin users away from any
    non-allowlisted path to the admin panel.
    """

    ALLOWED_PREFIXES = (
        '/accounts/admin-panel/',
        '/accounts/logout/',
        '/accounts/login/',
        '/accounts/google/',
        '/accounts/social/',
        '/admin/',
        '/static/',
        '/media/',
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            profile = getattr(user, 'profile', None)
            if profile and profile.is_admin:
                path = request.path
                if not path.startswith(self.ALLOWED_PREFIXES):
                    return redirect(reverse('accounts:user_admin'))
        return self.get_response(request)
