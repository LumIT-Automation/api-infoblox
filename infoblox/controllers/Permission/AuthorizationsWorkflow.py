from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from infoblox.models.Permission.PermissionWorkflow import PermissionWorkflow
from infoblox.controllers.CustomController import CustomController
from infoblox.helpers.Conditional import Conditional
from infoblox.helpers.Log import Log


class AuthorizationsWorkflowController(CustomController):
    @staticmethod
    # Enlist caller's permissions (depending on groups user belongs to).
    def get(request: Request) -> Response:
        etagCondition = {"responseEtag": ""}
        user = CustomController.loggedUser(request)
        workflow = ""

        try:
            if not user["authDisabled"]:
                Log.actionLog("Workflow permissions' list", user)

                data = {
                    "data": {
                        "items": PermissionWorkflow.workflowAuthorizationsList(user["groups"], workflow)
                    },
                    "href": request.get_full_path()
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
