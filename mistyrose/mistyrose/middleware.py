from django.http import HttpResponsePermanentRedirect
from django.utils.deprecation import MiddlewareMixin

class TrailingSlashMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Check if the URL doesn't end with a slash and is not an admin page
        if not request.path.endswith('/') and not request.path.startswith('/inbox'):
            # Always redirect to the URL with a trailing slash
            # Use 308 to preserve the original HTTP method (POST, PUT, etc.)
            return HttpResponsePermanentRedirect(request.path + '/', status=308)
        return None
