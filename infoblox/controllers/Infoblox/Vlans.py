from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from infoblox.models.Infoblox.Vlan import Vlan
from infoblox.models.Permission.CheckPermissionFacade import CheckPermissionFacade

from infoblox.serializers.Infoblox.Vlans import InfobloxVlansSerializer as Serializer

from infoblox.controllers.CustomController import CustomController

from infoblox.helpers.Lock import Lock
from infoblox.helpers.Conditional import Conditional
from infoblox.helpers.Log import Log


class InfobloxVlansController(CustomController):
    @staticmethod
    def get(request: Request, assetId: int) -> Response:
        data = dict()
        itemData = dict()
        etagCondition = { "responseEtag": "" }
        user = CustomController.loggedUser(request)
        workflowId = request.headers.get("workflowId", "") # a correlation id.
        checkWorkflowPermission = request.headers.get("checkWorkflowPermission", "")

        fk = list()
        fv = list()
        filters = dict()

        try:
            if CheckPermissionFacade.hasUserPermission(groups=user["groups"], action="vlans_get", assetId=assetId, isWorkflow=bool(workflowId)) or user["authDisabled"]:
                if workflowId and checkWorkflowPermission:
                    httpStatus = status.HTTP_204_NO_CONTENT
                else:
                    Log.actionLog("Get vlans list", user)

                    if 'fby' in request.GET and 'fval' in request.GET:
                        for f in dict(request.GET)["fby"]:
                            fk.append(f)
                        for v in dict(request.GET)["fval"]:
                            fv.append(v)
                        filters = dict(zip(fk, fv))

                    lock = Lock("vlan", locals(), workflowId=workflowId)
                    if lock.isUnlocked():
                        lock.lock()

                        itemData["data"] = Vlan.listData(assetId, filters)
                        serializer = Serializer(data=itemData)
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

                        if not workflowId:
                            lock.release()

                        # Run registered plugins.
                        CustomController.plugins("vlans_get")
                    else:
                        data = None
                        httpStatus = status.HTTP_423_LOCKED
            else:
                data = None
                httpStatus = status.HTTP_403_FORBIDDEN
        except Exception as e:
            if not workflowId:
                Lock("vlan", locals()).release()

            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "ETag": etagCondition["responseEtag"],
            "Cache-Control": "must-revalidate"
        })
