import json

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from infoblox.models.Infoblox.Range import Range
from infoblox.models.Permission.Permission import Permission
from infoblox.models.History.History import History

from infoblox.serializers.Infoblox.Range import InfobloxRangeSerializer

from infoblox.controllers.CustomController import CustomController

from infoblox.helpers.Lock import Lock
from infoblox.helpers.Conditional import Conditional
from infoblox.helpers.Log import Log


class InfobloxRangeController(CustomController):
    @staticmethod
    def get(request: Request, assetId: int, startAddr: str, endAddr: str) -> Response:
        auth = False
        data = dict()
        showIp = False
        ipv4Info = { "data": dict() }
        etagCondition = { "responseEtag": "" }

        user = CustomController.loggedUser(request)

        try:
            r = Range(assetId, startAddr, endAddr)
            if Permission.hasUserPermission(groups=user["groups"], action="range_get", assetId=assetId, network=r.network) or user["authDisabled"]:
                Log.actionLog("Range information", user)

                lock = Lock("range", locals(), startAddr)
                if lock.isUnlocked():
                    lock.lock()

                    serializer = InfobloxRangeSerializer(data=r.repr())
                    if serializer.is_valid():
                        data["data"] = serializer.validated_data
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

                    # Run registered plugins.
                    CustomController.plugins("range_get")
                else:
                    data = None
                    httpStatus = status.HTTP_423_LOCKED
            else:
                data = None
                httpStatus = status.HTTP_403_FORBIDDEN
        except Exception as e:
            if "startAddr" in locals():
                Lock("range", locals(), locals()["startAddr"]).release()

            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "ETag": etagCondition["responseEtag"],
            "Cache-Control": "must-revalidate"
        })
