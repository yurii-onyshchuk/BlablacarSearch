from django.shortcuts import redirect


class RedirectAuthenticatedUserMixin:
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.redirect_authenticated_user_url)
        return super().get(request, *args, **kwargs)
