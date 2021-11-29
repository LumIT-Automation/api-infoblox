from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from infoblox.models.History import History
from infoblox.models.Permission.Permission import Permission

from infoblox.serializers.History import HistorySerializer as Serializer

from infoblox.controllers.CustomController import CustomController
from infoblox.helpers.Conditional import Conditional
from infoblox.helpers.Log import Log


class HistoryLogsController(CustomController):
    @staticmethod
    def get(request: Request) -> Response:
        allUsersHistory = False
        data = dict()
        itemData = {"data": dict()}
        etagCondition = { "responseEtag": "" }

        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="historyComplete_get") or user["authDisabled"]:
                allUsersHistory = True

            Log.actionLog("History log", user)

            itemData["data"]["items"] = History.list(user["username"], allUsersHistory)
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

        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "ETag": etagCondition["responseEtag"],
            "Cache-Control": "must-revalidate"
        })
