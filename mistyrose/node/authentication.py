
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from node.models import Node  # Import your Node model
import base64

class NodeAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth = request.headers.get('Authorization')

        if not auth:
            raise AuthenticationFailed('No authorization header provided.')

        if not auth.startswith('Basic '):
            raise AuthenticationFailed('Authorization header must be Basic.')
        try:
            auth_decoded = base64.b64decode(auth.split(' ')[1]).decode('utf-8')
            username, password = auth_decoded.split(':')
        except:
            raise AuthenticationFailed('Invalid authorization header format.')

        try:
            node = Node.objects.get(username=username, password=password)
        except Node.DoesNotExist:
            raise AuthenticationFailed('Invalid username or password.')

        # - usually, you would return (user, additional_data) here if it was user authentication
        return (node, None)