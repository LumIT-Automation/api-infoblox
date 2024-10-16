from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from infoblox.models.Permission.CheckPermissionFacade import CheckPermissionFacade

from infoblox.usecases.DeleteAccountCloudNetworksFactory import DeleteAccountCloudNetworksFactory

from infoblox.serializers.Infoblox.wrappers.DeleteAccountCloudNetworks import InfobloxDeleteAccountCloudNetworksSerializer as Serializer

from infoblox.controllers.CustomController import CustomController

from infoblox.helpers.Lock import Lock
from infoblox.helpers.Log import Log


class InfobloxDeleteAccountCloudNetworksController(CustomController):
    @staticmethod
    def put(request: Request, assetId: int) -> Response:
        response = dict()
        user = CustomController.loggedUser(request)
        workflowId = request.headers.get("workflowId", "")  # a correlation id.
        checkWorkflowPermission = request.headers.get("checkWorkflowPermission", "")

        try:
            if CheckPermissionFacade.hasUserPermission(groups=user["groups"], action="delete_account_cloud_network_put", assetId=assetId, isWorkflow=bool(workflowId)) or user["authDisabled"]:
                if workflowId and checkWorkflowPermission:
                    httpStatus = status.HTTP_204_NO_CONTENT
                else:
                    Log.actionLog("delete account cloud networks", user)
                    Log.actionLog("User data: "+str(request.data), user)

                    serializer = Serializer(data=request.data["data"])
                    if serializer.is_valid():
                        data = serializer.validated_data

                        lock = Lock("network", locals(), workflowId=workflowId)
                        if lock.isUnlocked():
                            lock.lock()

                            response["data"] = DeleteAccountCloudNetworksFactory(assetId, data["provider"], user)().deleteNetworks(data["network_data"])

                            httpStatus = status.HTTP_200_OK
                            if not workflowId:
                                lock.release()

                            # Run registered plugins.
                            CustomController.plugins("delete_account_cloud_network")
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
            if not workflowId:
                Lock("network", locals()).release()

            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(response, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })
