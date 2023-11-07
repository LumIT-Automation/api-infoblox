from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from infoblox.models.Permission.Permission import Permission

from infoblox.usecases.DeleteCloudNetworkFactory import DeleteCloudNetworksFactory

from infoblox.controllers.CustomController import CustomController

from infoblox.helpers.Lock import Lock
from infoblox.helpers.Log import Log


class InfobloxDeleteCloudNetworksController(CustomController):
    @staticmethod
    def delete(request: Request, assetId: int, networkAddress: str) -> Response:
        response = None
        auth = False
        data = dict()
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="cloud_network_delete", assetId=assetId, network=networkAddress) or user["authDisabled"]:
                Log.actionLog("Network deletion", user)

                lock = Lock("network", locals(), networkAddress)
                if lock.isUnlocked():
                    lock.lock()

                    DeleteCloudNetworksFactory(assetId, networkAddress, user)().delete()
                    httpStatus = status.HTTP_200_OK
                    lock.release()

                    # Run registered plugins.
                    CustomController.plugins("delete_cloud_network")
                else:
                    httpStatus = status.HTTP_423_LOCKED
            else:
                httpStatus = status.HTTP_403_FORBIDDEN
        except Exception as e:
            if "networkAddress" in locals():
                Lock("network", locals(), locals()["networkAddress"]).release()

            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(None, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })
