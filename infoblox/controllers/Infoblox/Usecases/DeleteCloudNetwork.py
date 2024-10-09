from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from infoblox.models.Permission.CheckPermissionFacade import CheckPermissionFacade

from infoblox.usecases.DeleteCloudNetworkFactory import DeleteCloudNetworkFactory

from infoblox.controllers.CustomController import CustomController

from infoblox.helpers.Lock import Lock
from infoblox.helpers.Log import Log


class InfobloxDeleteCloudNetworkController(CustomController):
    @staticmethod
    def delete(request: Request, assetId: int, networkAddress: str) -> Response:
        response = None
        auth = False
        data = dict()
        user = CustomController.loggedUser(request)
        workflowId = request.headers.get("workflowId", "")  # a correlation id.
        checkWorkflowPermission = request.headers.get("checkWorkflowPermission", "")

        try:
            if CheckPermissionFacade.hasUserPermission(groups=user["groups"], action="cloud_network_delete", assetId=assetId, network=networkAddress, isWorkflow=bool(workflowId))  or user["authDisabled"]:
                if workflowId and checkWorkflowPermission:
                    httpStatus = status.HTTP_204_NO_CONTENT
                else:
                    Log.actionLog("Cloud network deletion use case", user)

                    lock = Lock("network", locals(), networkAddress, workflowId=workflowId)
                    if lock.isUnlocked():
                        lock.lock()

                        DeleteCloudNetworkFactory(assetId, networkAddress, user, isWorkflow=bool(workflowId))().delete()
                        httpStatus = status.HTTP_200_OK
                        if not workflowId:
                            lock.release()

                        # Run registered plugins.
                        CustomController.plugins("delete_cloud_network")
                    else:
                        httpStatus = status.HTTP_423_LOCKED
            else:
                httpStatus = status.HTTP_403_FORBIDDEN
        except Exception as e:
            if "networkAddress" in locals() and not workflowId:
                Lock("network", locals(), locals()["networkAddress"]).release()

            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(None, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })
