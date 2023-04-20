from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from infoblox.models.Trigger.Trigger import Trigger
from infoblox.models.Permission.Permission import Permission

from infoblox.controllers.CustomController import CustomController
from infoblox.helpers.Log import Log


class InfobloxTriggerConditionController(CustomController):
    @staticmethod
    def delete(request: Request, triggerId: int, conditionId: int) -> Response:
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="trigger_delete") or user["authDisabled"]:
                Log.actionLog("Trigger's condition deletion", user)

                Trigger(triggerId).deleteCondition(conditionId)

                httpStatus = status.HTTP_200_OK
            else:
                httpStatus = status.HTTP_403_FORBIDDEN

        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(None, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })
