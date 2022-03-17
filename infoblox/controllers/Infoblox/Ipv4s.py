from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from infoblox.usecases.ReserveFactory import ReserveFactory

from infoblox.models.Permission.Permission import Permission

from infoblox.serializers.Infoblox.Ipv4s import InfobloxIpv4sSerializer as Serializer

from infoblox.controllers.CustomController import CustomController

from infoblox.helpers.Lock import Lock
from infoblox.helpers.Log import Log


class InfobloxIpv4sController(CustomController):
    @staticmethod
    def post(request: Request, assetId: int) -> Response:
        response = dict()
        user = CustomController.loggedUser(request)

        if "next-available" in request.GET:
            reqType = "post.next-available"
        else:
            reqType = "post.specified-ip"

        try:
            serializer = Serializer(data=request.data, reqType=reqType) # adaptive serializer.
            if serializer.is_valid():
                userValidatedData = serializer.validated_data["data"]
                ipv4CustomReserve = ReserveFactory(assetId, reqType, userValidatedData, user["username"])()

                permissionCheckNetwork = ipv4CustomReserve.permissionCheckNetwork
                if Permission.hasUserPermission(groups=user["groups"], action="ipv4s_post", assetId=assetId, networkName=permissionCheckNetwork) or user["authDisabled"]:
                    Log.actionLog("Ipv4 addition", user)
                    Log.actionLog("User data: "+str(request.data), user)

                    lock = Lock("network", locals(), userNetwork=permissionCheckNetwork) # lock permissionCheckNetwork.
                    if lock.isUnlocked():
                        lock.lock()

                        response["data"], actualNetwork, mask, gateway, historyId = ipv4CustomReserve.reserve()

                        httpStatus = status.HTTP_201_CREATED
                        lock.release()

                        # Run registered plugins.
                        CustomController.plugins("ipv4s_post", locals()) # @todo: do not rely on locals() for plugins.
                    else:
                        httpStatus = status.HTTP_423_LOCKED
                        Log.actionLog("Ipv4 locked: "+str(lock), user)
                else:
                    response = None
                    httpStatus = status.HTTP_403_FORBIDDEN
            else:
                httpStatus = status.HTTP_400_BAD_REQUEST
                response = {
                    "Infoblox": {
                        "error": str(serializer.errors)
                    }
                }

                Log.log("User data incorrect: "+str(response))
        except Exception as e:
            if "permissionCheckNetwork" in locals():
                Lock("network", locals(), userNetwork=locals()["permissionCheckNetwork"]).release()

            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(response, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })
