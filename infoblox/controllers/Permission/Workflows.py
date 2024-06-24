from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from infoblox.models.Permission.Workflow import Workflow
from infoblox.models.Permission.Permission import Permission

from infoblox.serializers.Permission.Workflows import WorkflowsSerializer as Serializer

from infoblox.controllers.CustomController import CustomController
from infoblox.helpers.Conditional import Conditional
from infoblox.helpers.Log import Log


class WorkflowsPrivilegesController(CustomController):
    @staticmethod
    def get(request: Request) -> Response:
        etagCondition = {"responseEtag": ""}

        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="workflows_privileges_get") or user["authDisabled"]:
                Log.actionLog("Workflow privileges list", user)

                # Filter by workflows.
                wList = []
                if "workflow" in request.GET:
                    wList = request.GET.getlist('workflow')

                data = {
                    "data": {
                        "items": CustomController.validate(
                            [r.repr() for r in Workflow.list(loadPrivilege=True, selectWorkflow=wList)],
                            Serializer,
                            "list"
                        )
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
                httpStatus = status.HTTP_403_FORBIDDEN
        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "ETag": etagCondition["responseEtag"],
            "Cache-Control": "must-revalidate"
        })
