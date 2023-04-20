from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from infoblox.models.Trigger.Trigger import Trigger
from infoblox.models.Permission.Permission import Permission

from infoblox.serializers.Trigger.Triggers import InfobloxTriggersSerializer as TriggersSerializer
from infoblox.serializers.Trigger.Trigger import InfobloxTriggerSerializer as TriggerSerializer

from infoblox.controllers.CustomController import CustomController
from infoblox.helpers.Conditional import Conditional
from infoblox.helpers.Log import Log


class InfobloxTriggersController(CustomController):
    @staticmethod
    def get(request: Request) -> Response:
        data = dict()
        itemData = {"data": dict()}
        etagCondition = {"responseEtag": ""}

        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="triggers_get") or user["authDisabled"]: # @todo/db: superadmin only.
                Log.actionLog("Triggers list", user)

                itemData["items"] = Trigger.dataList(loadConditions=True)
                serializer = TriggersSerializer(data=itemData)
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
                        "Infoblox": "upstream data mismatch."
                    }

                    Log.log("Upstream data incorrect: "+str(serializer.errors))
            else:
                data = None
                httpStatus = status.HTTP_403_FORBIDDEN
        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "ETag": etagCondition["responseEtag"],
            "Cache-Control": "must-revalidate"
        })



    @staticmethod
    def post(request: Request) -> Response:
        data = None
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="triggers_post") or user["authDisabled"]: # @todo/db: superadmin only.
                Log.actionLog("Trigger addition", user)
                Log.actionLog("User data: "+str(request.data), user)

                serializer = TriggerSerializer(data=request.data["data"])
                if serializer.is_valid():
                    Trigger.add(serializer.validated_data)

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
