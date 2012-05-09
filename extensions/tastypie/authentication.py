import logging

from tastypie.authentication import ApiKeyAuthentication
from django.contrib.auth.models import User

logger = logging.getLogger('apps')

class CustomApiKeyAuthentication(ApiKeyAuthentication):
    
    def extract_credentials(self, request):
        if request.META.get('HTTP_AUTHORIZATION') and request.META['HTTP_AUTHORIZATION'].lower().startswith('apikey '):
            (auth_type, data) = request.META['HTTP_AUTHORIZATION'].split()

            if auth_type.lower() != 'apikey':
                raise ValueError("Incorrect authorization header.")

            username, api_key = data.split(':', 1)
        else:
            username = request.GET.get('username') or request.POST.get('username')
            api_key = request.GET.get('api_key') or request.POST.get('api_key')

        return username, api_key
    
    def is_authenticated(self, request, **kwargs):
        try:
            username, api_key = self.extract_credentials(request)
        except ValueError:
            return self._unauthorized()

        if not username or not api_key:
            return self._unauthorized()

        try:
            user = User.objects.get(username=username)
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return self._unauthorized()

        request.user = user
        return self.get_key(user, api_key)