from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from infoblox.models.Asset.Asset import Asset
from infoblox.models.Permission.Permission import Permission
from infoblox.serializers.Asset.Asset import InfobloxAssetSerializer as Serializer

from infoblox.controllers.CustomController import CustomController
from infoblox.helpers.Log import Log


class InfobloxAssetController(CustomController):
    @staticmethod
    def delete(request: Request, assetId: int) -> Response:
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="asset_delete") or user["authDisabled"]:
                Log.actionLog("Asset deletion", user)

                infoblox = Asset(assetId)
                infoblox.delete()

                httpStatus = status.HTTP_200_OK
            else:
                httpStatus = status.HTTP_403_FORBIDDEN

        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(None, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })



    @staticmethod
    def patch(request: Request, assetId: int) -> Response:
        response = None
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="asset_patch") or user["authDisabled"]:
                Log.actionLog("Asset modification", user)
                Log.actionLog("User data: "+str(request.data), user)

                serializer = Serializer(data=request.data["data"], partial=True)
                if serializer.is_valid():
                    data = serializer.validated_data

                    infoblox = Asset(assetId)
                    infoblox.modify(data)

                    httpStatus = status.HTTP_200_OK
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
