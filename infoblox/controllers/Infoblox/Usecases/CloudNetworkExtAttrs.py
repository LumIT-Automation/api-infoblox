from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from infoblox.models.Permission.CheckPermissionFacade import CheckPermissionFacade

from infoblox.usecases.CloudExtAttrFactory import CloudExtAttrFactory

from infoblox.serializers.Infoblox.wrappers.CloudExtattr import InfobloxCloudExtAttrSerializer as Serializer

from infoblox.controllers.CustomController import CustomController
from infoblox.helpers.Lock import Lock
from infoblox.helpers.Exception import CustomException
from infoblox.helpers.Conditional import Conditional
from infoblox.helpers.Log import Log


class InfobloxCloudNetworkExtAttrsController(CustomController):
    @staticmethod
    def get(request: Request, assetId: int, extattr: str) -> Response:
        data = {"data": ""}
        etagCondition = { "responseEtag": "" }
        httpStatus = None
        user = CustomController.loggedUser(request)
        workflowId = request.headers.get("workflowId", "")  # a correlation id.
        checkWorkflowPermission = request.headers.get("checkWorkflowPermission", "")
        fk = list()
        fv = list()
        filters = dict()

        try:
            if CheckPermissionFacade.hasUserPermission(groups=user["groups"], action="cloud_extattrs_get", assetId=assetId, isWorkflow=bool(workflowId)) or user["authDisabled"]:
                if workflowId and checkWorkflowPermission:
                    httpStatus = status.HTTP_204_NO_CONTENT
                else:
                    Log.actionLog("Get networks list", user)

                    if 'fby' in request.GET and 'fval' in request.GET:
                        for f in dict(request.GET)["fby"]:
                            fk.append(f)
                        for v in dict(request.GET)["fval"]:
                            fv.append(v)
                        filters = dict(zip(fk, fv))

                    lock = Lock("extattr", locals(), workflowId=workflowId)
                    if lock.isUnlocked():
                        lock.lock()

                        if extattr:
                            if extattr == "provider":
                                data["data"] = CloudExtAttrFactory(assetId, user)().listProviders(filters)
                            elif extattr == "account+provider":
                                data["data"] = CloudExtAttrFactory(assetId, user)().listAccountsProviders(filters)
                            else:
                                raise CustomException(status=403, payload={"Infoblox": "Wrong extattr param."})

                            serializer = Serializer(data=data)
                            if serializer.is_valid():
                                data["data"] = serializer.validated_data["data"]
                                data["href"] = request.get_full_path()
                            else:
                                httpStatus, data = status.HTTP_500_INTERNAL_SERVER_ERROR, {"Infoblox": {"error": "Infoblox upstream data mismatch."}}
                                Log.log("Upstream data incorrect: " + str(serializer.errors))
                            
                            # Check the response's ETag validity (against client request).
                            if httpStatus != status.HTTP_500_INTERNAL_SERVER_ERROR:
                                conditional = Conditional(request)
                                etagCondition = conditional.responseEtagFreshnessAgainstRequest(data["data"])
                                Log.log(etagCondition, '_')
                                if etagCondition["state"] == "fresh":
                                    data = None
                                    httpStatus = status.HTTP_304_NOT_MODIFIED
                                else:
                                    httpStatus = status.HTTP_200_OK
                        if not workflowId:
                            lock.release()
                    else:
                        data = None
                        httpStatus = status.HTTP_423_LOCKED
            else:
                data = None
                httpStatus = status.HTTP_403_FORBIDDEN
        except Exception as e:
            if not workflowId:
                Lock("network", locals()).release()

            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "ETag": etagCondition["responseEtag"],
            "Cache-Control": "must-revalidate"
        })
