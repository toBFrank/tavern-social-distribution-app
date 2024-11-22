from urllib.parse import urlparse, unquote
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from node.models import Node  # Import your Node model
import base64

class NodeAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        
        # no credentials given
        if not auth_header:
            return None
        
        # credentials given, but not Basic
        if not auth_header.startswith('Basic '):
            return None
        
        try:
            # decode the base64 encoded string
            # - for example:
            #     auth_header = "Basic YWRtaW46YWR" -> base64_decoded = "username:password"
            # - username & password should match local_username & local_password of a Node object
            base64_decoded = base64.b64decode(auth_header.split(' ')[1]).decode('utf-8')
            username, password = base64_decoded.split(':')
        except:
            raise AuthenticationFailed('You did not write the auth header properly; fix and try again, cutie.')
        
        try:
            # get the Node object that matches the username and password
            node = Node.objects.get(
                local_username=username, 
                local_password=password, 
                is_whitelisted=True,
                )
        except Node.DoesNotExist:
            raise AuthenticationFailed('I could not find a live node that matches. Wrong username/password? Or maybe I just blocked you. Who knows?')

        return (node, None)
    
    def authenticate_header(self, request):
        return 'Basic realm="Node Authentication"'