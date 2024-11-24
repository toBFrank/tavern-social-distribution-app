from django.http import HttpResponsePermanentRedirect
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect

class TrailingSlashMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Check if the URL doesn't end with a slash and is not an admin page
        if not request.path.endswith('/') and not request.path.startswith('/admin'):
            # Always redirect to the URL with a trailing slash
            return HttpResponsePermanentRedirect(request.path + '/')
        return None

    def process_response(self, request, response):
        # If the response is a redirect (301 Permanent Redirect)
        if isinstance(response, HttpResponsePermanentRedirect):
            # If the original method was POST, PUT, DELETE, PATCH, etc., preserve the method after the redirect
            if request.method != 'GET':
                # Re-issue the redirect to the new URL with the original HTTP method
                return redirect(request.path + '/', permanent=True, method=request.method)
        return response
