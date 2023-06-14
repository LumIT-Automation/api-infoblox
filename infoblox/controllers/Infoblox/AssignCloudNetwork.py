from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from infoblox.models.Permission.Permission import Permission

from infoblox.usecases.AssigncloudNetworkFactory import AssignCloudNetworkFactory

from infoblox.serializers.Infoblox.wrappers.AssignNetwork import InfobloxAssignNetworkSerializer as Serializer

from infoblox.controllers.CustomController import CustomController

from infoblox.helpers.Lock import Lock
from infoblox.helpers.Log import Log


class InfobloxAssignCloudNetworkController(CustomController):
    @staticmethod
    def put(request: Request, assetId: int) -> Response:
        response = dict()
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="assign_network", assetId=assetId) or user["authDisabled"]:
                Log.actionLog("assign network in container use case", user)
                Log.actionLog("User data: "+str(request.data), user)

                serializer = Serializer(data=request.data["data"])
                if serializer.is_valid():
                    data = serializer.validated_data

                    lock = Lock("networkContainer", locals())
                    if lock.isUnlocked():
                        lock.lock()

                        response["data"] = AssignCloudNetworkFactory(assetId, data["provider"], data["region"], user)().assignNetwork(data["network_data"])

                        httpStatus = status.HTTP_201_CREATED
                        lock.release()

                        # Run registered plugins.
                        CustomController.plugins("assign_network")
                    else:
                        httpStatus = status.HTTP_423_LOCKED
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
            Lock("networkContainer", locals()).release()

            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(response, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })
