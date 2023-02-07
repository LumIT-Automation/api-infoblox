from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from infoblox.models.Infoblox.NetworkContainer import NetworkContainer
from infoblox.models.Permission.Permission import Permission

from infoblox.serializers.Infoblox.wrappers.AssignNetwork import InfobloxAssignNetworkSerializer as Serializer

from infoblox.controllers.CustomController import CustomController

from infoblox.helpers.Lock import Lock
from infoblox.helpers.Log import Log


class InfobloxAssignNetworkController(CustomController):
    @staticmethod
    def put(request: Request, assetId: int) -> Response:
        response = dict()
        httpStatus = status.HTTP_500_INTERNAL_SERVER_ERROR

        user = CustomController.loggedUser(request)

        try:
            Log.actionLog("assign network in container use case", user)
            Log.actionLog("User data: "+str(request.data), user)

            serializer = Serializer(data=request.data["data"])
            if serializer.is_valid():
                data = serializer.validated_data

                lock = Lock("networkContainer", locals())
                if lock.isUnlocked():
                    lock.lock()

                    # Eligible container networks.
                    containers = NetworkContainer.listData(assetId, {
                        "*CloudEnvironment": "cloud",
                        "*CloudCountry": data["provider"],
                        "*CloudCity": data["region"]
                    })

                    if containers:
                        for container in containers:
                            try:
                                if Permission.hasUserPermission(groups=user["groups"], action="assign_network", assetId=assetId, networkName=container) or user["authDisabled"]:
                                    response["data"] = NetworkContainer(assetId, container["network"]).addNextAvailableNetwork(
                                        subnetMaskCidr=24,
                                        data=data["network_data"]
                                    )

                                    httpStatus = status.HTTP_201_CREATED
                                    break
                                else:
                                    httpStatus = status.HTTP_403_FORBIDDEN
                            except Exception: # @todo: only no network available.
                                httpStatus = status.HTTP_400_BAD_REQUEST
                                response = {
                                    "Infoblox": {
                                        "error": "No network available"
                                    }
                                }
                    else:
                        httpStatus = status.HTTP_400_BAD_REQUEST
                        response = {
                            "Infoblox": {
                                "error": "No container available"
                            }
                        }

                    lock.release()
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
        except Exception as e:
            Lock("networkContainer", locals()).release()

            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(response, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })
