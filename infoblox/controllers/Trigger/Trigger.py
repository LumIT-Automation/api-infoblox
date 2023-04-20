from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from infoblox.models.Trigger.Trigger import Trigger
from infoblox.models.Permission.Permission import Permission

from infoblox.serializers.Trigger.Trigger import InfobloxTriggerSerializer as Serializer

from infoblox.controllers.CustomController import CustomController
from infoblox.helpers.Conditional import Conditional
from infoblox.helpers.Log import Log


class InfobloxTriggerController(CustomController):
    @staticmethod
    def get(request: Request, triggerId: int) -> Response:
        data = dict()
        etagCondition = { "responseEtag": "" }
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="trigger_get") or user["authDisabled"]:
                Log.actionLog("Trigger information", user)

                serializer = Serializer(
                    data=Trigger(triggerId, loadConditions=True).repr()
                )

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
    def delete(request: Request, triggerId: int) -> Response:
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="trigger_delete") or user["authDisabled"]:
                Log.actionLog("Trigger deletion", user)

                Trigger(triggerId).delete()

                httpStatus = status.HTTP_200_OK
            else:
                httpStatus = status.HTTP_403_FORBIDDEN

        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(None, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })



    @staticmethod
    def patch(request: Request, triggerId: int) -> Response:
        response = None
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="trigger_patch") or user["authDisabled"]:
                Log.actionLog("Trigger modification", user)
                Log.actionLog("User data: "+str(request.data), user)

                serializer = Serializer(data=request.data["data"], partial=True)
                if serializer.is_valid():
                    data = serializer.validated_data

                    Trigger(triggerId).modify(data)

                    httpStatus = status.HTTP_200_OK
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

        return Response(response, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })
