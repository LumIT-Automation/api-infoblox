from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from infoblox.models.Permission.Permission import Permission
from infoblox.models.Permission.CheckPermissionFacade import CheckPermissionFacade

from infoblox.usecases.AssignCloudNetworkFactory import AssignCloudNetworkFactory

from infoblox.serializers.Infoblox.wrappers.AssignCloudNetwork import InfobloxAssignCloudNetworkSerializer as Serializer

from infoblox.controllers.CustomController import CustomController

from infoblox.helpers.Lock import Lock
from infoblox.helpers.Log import Log


class InfobloxAssignCloudNetworkController(CustomController):
    @staticmethod
    def put(request: Request, assetId: int) -> Response:
        response = dict()
        user = CustomController.loggedUser(request)
        workflowId = request.headers.get("workflowId", "")  # a correlation id.
        checkWorkflowPermission = request.headers.get("checkWorkflowPermission", "")

        try:
            if CheckPermissionFacade.hasUserPermission(groups=user["groups"], action="cloud_network_assign_put", assetId=assetId, isWorkflow=bool(workflowId)) or user["authDisabled"]:
                if workflowId and checkWorkflowPermission:
                    httpStatus = status.HTTP_204_NO_CONTENT
                else:
                    Log.actionLog("assign network in container use case", user)
                    Log.actionLog("User data: "+str(request.data), user)

                    serializer = Serializer(data=request.data["data"])
                    if serializer.is_valid():
                        data = serializer.validated_data

                        lock = Lock("networkContainer", locals())
                        if lock.isUnlocked():
                            lock.lock()

                            response["data"] = AssignCloudNetworkFactory(assetId, data["provider"], data.get("region", ""), user)().assignNetwork(
                                data["network_data"]
                            )

                            httpStatus = status.HTTP_201_CREATED
                            if not workflowId:
                                lock.release()

                            # Run registered plugins.
                            CustomController.plugins("assign_network")
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
                Lock("networkContainer", locals()).release()

            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(response, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })
