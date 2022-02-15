from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from infoblox.models.Infoblox.Network import Network
from infoblox.models.Permission.Permission import Permission

from infoblox.serializers.Infoblox.Networks import InfobloxNetworksSerializer as Serializer

from infoblox.controllers.CustomController import CustomController

from infoblox.helpers.Lock import Lock
from infoblox.helpers.Conditional import Conditional
from infoblox.helpers.Log import Log


class InfobloxNetworksController(CustomController):
    @staticmethod
    def get(request: Request, assetId: int) -> Response:
        data = dict()
        allowedData = {
            "data": []
        }
        etagCondition = { "responseEtag": "" }
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="networks_get", assetId=assetId) or user["authDisabled"]:
                Log.actionLog("Get networks list", user)

                lock = Lock("network", locals())
                if lock.isUnlocked():
                    lock.lock()

                    itemData = Network.list(assetId)

                    # Filter networks' list basing on permissions.
                    for p in itemData:
                        if Permission.hasUserPermission(groups=user["groups"], action="networks_get", assetId=assetId, networkName=str(p["network"])) or user["authDisabled"]:
                            allowedData["data"].append(p)

                    serializer = Serializer(data=allowedData)
                    if serializer.is_valid():
                        data["data"] = serializer.validated_data["data"]
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
                            "Infoblox": {
                                "error": "Infoblox upstream data mismatch."
                            }
                        }

                        Log.log("Upstream data incorrect: "+str(serializer.errors))

                    lock.release()

                    CustomController.plugins("networks_get", locals())
                else:
                    data = None
                    httpStatus = status.HTTP_423_LOCKED
            else:
                data = None
                httpStatus = status.HTTP_403_FORBIDDEN
        except Exception as e:
            Lock("network", locals()).release()

            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "ETag": etagCondition["responseEtag"],
            "Cache-Control": "must-revalidate"
        })
