from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from infoblox.models.Infoblox.NetworkContainer import NetworkContainer
from infoblox.models.Permission.Permission import Permission

from infoblox.serializers.Infoblox.NetworkContainer import InfobloxNetworkContainerNetworksSerializer as Serializer
from infoblox.serializers.Infoblox.NetworkContainers import InfobloxNetworkContainerAddNetworkSerializer as AddNetworkSerializer

from infoblox.controllers.CustomController import CustomController

from infoblox.helpers.Lock import Lock
from infoblox.helpers.Conditional import Conditional
from infoblox.helpers.Log import Log


class InfobloxNetworkContainerNetworksController(CustomController):
    @staticmethod
    def get(request: Request, assetId: int, networkAddress: str, mask: str) -> Response:
        data = dict()
        itemData = dict()
        etagCondition = { "responseEtag": "" }
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="network_container_get", assetId=assetId, networkName=networkAddress+"/"+mask) or user["authDisabled"]: # @todo: check also for permissions in father container or container of upper levels.
                Log.actionLog("Network container information", user)

                lock = Lock("networkContainer", locals(), networkAddress)
                if lock.isUnlocked():
                    lock.lock()

                    itemData["items"] = NetworkContainer(assetId, networkAddress+"/"+mask).networks()

                    serializer = Serializer(data=itemData)
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
                            "infoblox": "Upstream data mismatch."
                        }

                        Log.log("Upstream data incorrect: "+str(serializer.errors))

                    lock.release()

                    CustomController.plugins("network_container_get", locals())
                else:
                    data = None
                    httpStatus = status.HTTP_423_LOCKED
            else:
                data = None
                httpStatus = status.HTTP_403_FORBIDDEN
        except Exception as e:
            if "networkAddress" in locals():
                Lock("networkContainer", locals(), locals()["networkAddress"]).release()

            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "ETag": etagCondition["responseEtag"],
            "Cache-Control": "must-revalidate"
        })



    @staticmethod
    def post(request: Request,  assetId: int, networkAddress: str, mask: str) -> Response:
        response = dict()
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="network_container_post", assetId=assetId) or user["authDisabled"]:
                Log.actionLog("Network addition in container", user)
                Log.actionLog("User data: "+str(request.data), user)

                serializer = AddNetworkSerializer(data=request.data["data"])
                if serializer.is_valid():
                    data = serializer.validated_data

                    lock = Lock("networkContainer", locals(), networkAddress)
                    if lock.isUnlocked():
                        lock.lock()

                        response["data"] = NetworkContainer(assetId, networkAddress + "/" + mask).addNextAvailableNetwork(
                            subnetMaskCidr=data["subnet_mask_cidr"],
                            data=data["network_data"]
                        )

                        httpStatus = status.HTTP_201_CREATED
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
            else:
                httpStatus = status.HTTP_403_FORBIDDEN
        except Exception as e:
            if "serializer" in locals():
                Lock("networkContainer", locals(), networkAddress).release()

            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(response, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })
