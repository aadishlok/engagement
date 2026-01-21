from rest_framework import authentication, exceptions
from django.conf import settings
from drf_spectacular.extensions import OpenApiAuthenticationExtension


class APIKeyAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        api_key = request.META.get('HTTP_X_API_KEY')

        if api_key != settings.API_KEY:
            raise exceptions.AuthenticationFailed('Invalid API Key')
            
        return (None, None)


class APIKeyAuthenticationExtension(OpenApiAuthenticationExtension):
    target_class = APIKeyAuthentication
    name = 'APIKeyAuth'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'apiKey',
            'in': 'header',
            'name': 'X-API-Key',
            'description': 'API Key authentication. Include the API key in the X-API-Key header.'
        }