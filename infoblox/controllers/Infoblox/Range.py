import json

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from infoblox.models.Infoblox.Range import Range
from infoblox.models.Permission.CheckPermissionFacade import CheckPermissionFacade

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
        workflowId = request.headers.get("workflowId", "") # a correlation id.
        checkWorkflowPermission = request.headers.get("checkWorkflowPermission", "")

        try:
            r = Range(assetId, startAddr, endAddr)
            if CheckPermissionFacade.hasUserPermission(groups=user["groups"], action="range_get", assetId=assetId, network=r.network, isWorkflow=bool(workflowId)) or user["authDisabled"]:
                if workflowId and checkWorkflowPermission:
                    httpStatus = status.HTTP_204_NO_CONTENT
                else:
                    Log.actionLog("Range information", user)

                    lock = Lock("range", locals(), startAddr, workflowId=workflowId)
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

                        if not workflowId:
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
            if "startAddr" in locals() and not workflowId:
                Lock("range", locals(), locals()["startAddr"]).release()

            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "ETag": etagCondition["responseEtag"],
            "Cache-Control": "must-revalidate"
        })
