import jwt
from importlib import import_module

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication

from infoblox.helpers.Log import Log


class CustomController(APIView):
    if not settings.DISABLE_AUTHENTICATION:
        permission_classes = [IsAuthenticated]
        authentication_classes = [JWTTokenUserAuthentication]



    @staticmethod
    def loggedUser(request: Request) -> dict:
        if settings.DISABLE_AUTHENTICATION:
            user = {
                "authDisabled": True,
                "groups": []
            }
        else:
            # Retrieve user from the JWT token.
            authenticator = request.successful_authenticator
            user = jwt.decode(
                authenticator.get_raw_token(authenticator.get_header(request)),
                settings.SIMPLE_JWT['VERIFYING_KEY'],
                settings.SIMPLE_JWT['ALGORITHM'],
                do_time_check=True
            )
            user["authDisabled"] = False

        return user



    @staticmethod
    def plugins(what: str, o: dict) -> None:
        for plugin in settings.PLUGINS:
            try:
                p = import_module(plugin)
                p.run(what, o)
            except Exception:
                pass



    @staticmethod
    def exceptionHandler(e: Exception) -> tuple:
        Log.logException(e)

        data = dict()
        headers = { "Cache-Control": "no-cache" }

        if e.__class__.__name__ in ("ConnectionError", "Timeout", "ConnectTimeout", "TooManyRedirects", "SSLError", "HTTPError"):
            httpStatus = status.HTTP_503_SERVICE_UNAVAILABLE
            data["error"] = {
                "network": e.__str__()
            }
        elif e.__class__.__name__ == "CustomException":
            httpStatus = e.status
            data["error"] = e.payload
        elif e.__class__.__name__ == "ParseError":
            data = None
            httpStatus = status.HTTP_400_BAD_REQUEST # json parse.
        elif e.__class__.__name__ == "NotImplementedError":
            data = None
            httpStatus = status.HTTP_422_UNPROCESSABLE_ENTITY
        else:
            data = None
            httpStatus = status.HTTP_500_INTERNAL_SERVER_ERROR # generic.

        return data, httpStatus, headers
