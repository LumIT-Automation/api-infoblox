from django.conf import settings

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from infoblox.models.Permission.Authorization import Authorization
from infoblox.controllers.CustomController import CustomController
from infoblox.helpers.Conditional import Conditional
from infoblox.helpers.Log import Log


class AuthorizationsController(CustomController):
    @staticmethod
    # Enlist caller's permissions (depending on groups user belongs to).
    def get(request: Request) -> Response:
        data = dict()
        etagCondition = {"responseEtag": ""}

        user = CustomController.loggedUser(request)

        try:
            if not user["authDisabled"]:
                Log.actionLog("Permissions' list", user)

                data["data"] = Authorization.list(user["groups"])
                data["href"] = request.get_full_path()

                # Superadmin's permissions override.
                for gr in user["groups"]:
                    if gr.lower() == "automation.local":
                        data["data"] = {
                            "items": {
                                "any": [
                                    {
                                        "assetId": 0,
                                        "network": "any"
                                    }
                                ]
                            }
                        }

                # Check the response's ETag validity (against client request).
                conditional = Conditional(request)
                etagCondition = conditional.responseEtagFreshnessAgainstRequest(data["data"])
                if etagCondition["state"] == "fresh":
                    data = None
                    httpStatus = status.HTTP_304_NOT_MODIFIED
                else:
                    httpStatus = status.HTTP_200_OK
            else:
                data = None
                httpStatus = status.HTTP_200_OK

        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "ETag": etagCondition["responseEtag"],
            "Cache-Control": "must-revalidate"
        })
