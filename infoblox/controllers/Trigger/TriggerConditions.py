from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from infoblox.models.Trigger.Trigger import Trigger
from infoblox.models.Permission.Permission import Permission

from infoblox.serializers.Trigger.TriggerCondition import InfobloxTriggerConditionSerializer as Serializer

from infoblox.controllers.CustomController import CustomController
from infoblox.helpers.Log import Log


class InfobloxTriggersConditionsController(CustomController):
    @staticmethod
    def post(request: Request, triggerId) -> Response:
        data = None
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="triggers_post") or user["authDisabled"]:
                Log.actionLog("Trigger's condition addition", user)
                Log.actionLog("User data: "+str(request.data), user)

                serializer = Serializer(data=request.data["data"])
                if serializer.is_valid():
                    Trigger(triggerId).addCondition(serializer.validated_data)

                    httpStatus = status.HTTP_201_CREATED
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
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })
