from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework import status

from .models import KeyValueMapping

from django.core.cache import cache


class PingToPongView(View):
    def get(self, request, *args, **kwargs):
        try:
            return Response({"success": True, "message": "Pong"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"success": False, "message": e}, status=status.HTTP_400_BAD_REQUEST)

class AuthorizationView(View):
    def post(self, request, *args, **kwargs):
        try:
            secret_key = request.headers.get('Authorization')
            if secret_key == 'shared_secret_value':
                return Response({"success": True, "message": "Your are Authorized"}, status=status.HTTP_200_OK)
            else:
                return Response({"success": False, "message": "Your are not Authorized"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"success": False, "message": e}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class SaveView(View):
    def post(self, request, *args, **kwargs):
        try:
            key = request.data.get('key')
            value = request.data.get('value')
            if not key and value:
                 return Response({"success": False, "message": "Invalid kay and value"}, status=status.HTTP_200_OK)

            # Cache the data for future retrieval from cache
            cache.set(key, value)
            # Save to the database (optional)
            KeyValueMapping.objects.create(key=key, value=value)
            return Response({"success": True, "message": "Successfully Created"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"success": False, "message": e}, status=status.HTTP_400_BAD_REQUEST)


class GetView(View):
    def get(self, request, *args, **kwargs):
        try:
            # Try to get the data from the cache
            data = cache.get('key')

            if data is None:
                # If not in cache, fetch from the database
                data = list(KeyValueMapping.objects.values())
                # Cache the data for future requests
                cache.set('key', data)
            return Response({"success": True, "data": data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"success": False, "message": e}, status=status.HTTP_400_BAD_REQUEST)


class PurgeView(View):
    def delete(self, request, *args, **kwargs):
        try:
            key = request.data.get('key')
            KeyValueMapping.objects.filter(key=key).delete()
            return Response({"success": True, "message": "Record successfully purge"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"success": False, "message": e}, status=status.HTTP_400_BAD_REQUEST)

