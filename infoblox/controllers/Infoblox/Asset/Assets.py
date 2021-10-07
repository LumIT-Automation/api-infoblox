from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from infoblox.models.Infoblox.Asset.Asset import Asset
from infoblox.models.Permission.Permission import Permission

from infoblox.serializers.Infoblox.Asset.Assets import InfobloxAssetsSerializer as AssetsSerializer
from infoblox.serializers.Infoblox.Asset.Asset import InfobloxAssetSerializer as AssetSerializer

from infoblox.controllers.CustomController import CustomController
from infoblox.helpers.Log import Log


class InfobloxAssetsController(CustomController):
    @staticmethod
    def get(request: Request) -> Response:
        data = dict()
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="assets_get") or user["authDisabled"]:
                Log.actionLog("Asset list", user)

                itemData = Asset.list()
                serializer = AssetsSerializer(data=itemData)

                if serializer.is_valid():
                    data["data"] = serializer.validated_data["data"]
                    data["href"] = request.get_full_path()

                    httpStatus = status.HTTP_200_OK
                else:
                    httpStatus = status.HTTP_500_INTERNAL_SERVER_ERROR
                    data = {
                        "infoblox": "Upstream data mismatch."
                    }
                    response = {
                        "Infoblox": {
                            "error": str(serializer.errors)
                        }
                    }
                    Log.actionLog("User data incorrect: " + str(response), user)
            else:
                httpStatus = status.HTTP_403_FORBIDDEN

        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })



    @staticmethod
    def post(request: Request) -> Response:
        data = None
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="assets_post") or user["authDisabled"]:
                Log.actionLog("Asset addition", user)
                Log.actionLog("User data: "+str(request.data), user)

                serializer = AssetSerializer(data=request.data)
                if serializer.is_valid():
                    Asset.add(serializer.validated_data["data"])

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

        return Response(data, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })
