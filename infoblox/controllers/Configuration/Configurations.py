from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from infoblox.models.Configuration.Configuration import Configuration
from infoblox.models.Permission.Permission import Permission

from infoblox.controllers.CustomController import CustomController

from infoblox.serializers.Configuration.Configurations import ConfigurationsSerializer
from infoblox.serializers.Configuration.Configuration import ConfigurationSerializer

from infoblox.helpers.Conditional import Conditional
from infoblox.helpers.Log import Log


class ConfigurationsController(CustomController):
    @staticmethod
    def get(request: Request) -> Response:
        data = dict()
        etagCondition = {"responseEtag": ""}

        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="configurations_get") or user["authDisabled"]:
                Log.actionLog("Configurations list", user)

                serializer = ConfigurationsSerializer(data={"items": Configuration.list()})  # serializer needs an "items" key.
                if serializer.is_valid():
                    data["data"] = serializer.validated_data["items"]
                    data["href"] = request.get_full_path()

                    # Check the response's ETag validity (against client request).
                    conditional = Conditional(request)
                    etagCondition = conditional.responseEtagFreshnessAgainstRequest(data["data"])
                    if etagCondition["state"] == "fresh":
                        data = None
                        httpStatus = status.HTTP_304_NOT_MODIFIED
                    else:
                        httpStatus = status.HTTP_200_OK
                else:
                    httpStatus = status.HTTP_500_INTERNAL_SERVER_ERROR
                    data = {
                        "Infoblox": "upstream data mismatch."
                    }

                    Log.log("Upstream data incorrect: "+str(serializer.errors))
            else:
                data = None
                httpStatus = status.HTTP_403_FORBIDDEN

        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "ETag": etagCondition["responseEtag"],
            "Cache-Control": "must-revalidate"
        })



    @staticmethod
    def post(request: Request) -> Response:
        response = None
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="configurations_post") or user["authDisabled"]:
                Log.actionLog("Configuration addition", user)
                Log.actionLog("User data: "+str(request.data), user)

                serializer = ConfigurationSerializer(data=request.data["data"])
                if serializer.is_valid():
                    data = serializer.validated_data
                    response = {"data": Configuration.add(data)}

                    httpStatus = status.HTTP_201_CREATED
                else:
                    httpStatus = status.HTTP_400_BAD_REQUEST
                    response = {
                        "Infoblox": {
                            "error": str(serializer.errors)
                        }
                    }

                    Log.actionLog("User data incorrect: "+str(response), user)
            else:
                httpStatus = status.HTTP_403_FORBIDDEN
        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(response, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })