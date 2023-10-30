from django.shortcuts import redirect


class RedirectAuthenticatedUserMixin:
    """Redirect authenticated users to a specified URL.

    This mixin checks if the user is authenticated. If they are, it redirects them to the specified URL
    defined in 'redirect_authenticated_user_url'. If the user is not authenticated, it continues with the
    standard GET request handling.
    """

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.redirect_authenticated_user_url)
        return super().get(request, *args, **kwargs)
