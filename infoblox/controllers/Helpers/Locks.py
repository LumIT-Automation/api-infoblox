from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from infoblox.helpers.Lock import Lock
from infoblox.models.Permission.CheckPermissionFacade import CheckPermissionFacade

from infoblox.controllers.CustomController import CustomController

from infoblox.helpers.Log import Log


class InfobloxWorkflowLocksController(CustomController):
    @staticmethod
    def delete(request: Request) -> Response:
        user = CustomController.loggedUser(request)
        workflowId = request.headers.get("workflowId", "") # a correlation id.
        checkWorkflowPermission = request.headers.get("checkWorkflowPermission", "")
        httpStatus = status.HTTP_500_INTERNAL_SERVER_ERROR

        try:
            if not workflowId:
                httpStatus = status.HTTP_400_BAD_REQUEST
            else:
                if CheckPermissionFacade.hasUserPermission(groups=user["groups"], action="locks_delete", isWorkflow=bool(workflowId)) or user["authDisabled"]:
                    if workflowId and checkWorkflowPermission:
                        httpStatus = status.HTTP_204_NO_CONTENT
                    elif workflowId:
                        Log.actionLog("Unlock workflow objects: "+workflowId, user)
                        Lock.releaseWorkflow(workflowId)
                        httpStatus = status.HTTP_200_OK
                else:
                    httpStatus = status.HTTP_403_FORBIDDEN
        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(None, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })

