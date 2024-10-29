from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from infoblox.models.Permission.PermissionWorkflow import PermissionWorkflow
from infoblox.models.Permission.Permission import Permission

from infoblox.serializers.Permission.PermissionsWorkflow import PermissionsWorkflowSerializer as PermissionsSerializer
from infoblox.serializers.Permission.PermissionWorkflow import PermissionWorkflowSerializer as PermissionSerializer

from infoblox.controllers.CustomController import CustomController

from infoblox.helpers.Conditional import Conditional
from infoblox.helpers.Log import Log


class PermissionsWorkflowController(CustomController):
    @staticmethod
    def get(request: Request) -> Response:
        etagCondition = {"responseEtag": ""}
        user = CustomController.loggedUser(request)

        fk = list()
        fv = list()
        filters = dict()

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="permission_identityGroups_get") or user["authDisabled"]:
                Log.actionLog("Workflow Permissions list", user)

                if 'fby' in request.GET and 'fval' in request.GET:
                    for f in dict(request.GET)["fby"]:
                        fk.append(f)
                    for v in dict(request.GET)["fval"]:
                        fv.append(v)
                    filters = dict(zip(fk, fv))

                data = {
                    "data": {
                        "items": CustomController.validate(
                            PermissionWorkflow.workflowPermissionsDataList(filters=filters),
                            PermissionsSerializer,
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



    @staticmethod
    def post(request: Request) -> Response:
        response = None
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="permission_identityGroups_post") or user["authDisabled"]:
                Log.actionLog("Workflow Permission addition", user)
                Log.actionLog("User data: "+str(request.data), user)

                serializer = PermissionSerializer(data=request.data["data"])
                if serializer.is_valid():
                    data = serializer.validated_data

                    PermissionWorkflow.addFacade(
                        identityGroupId=data["identity_group_identifier"],
                        workflow=data["workflow"],
                        networkInfo={
                            "assetId": data["network"]["id_asset"],
                            "name": data["network"]["name"]
                        }
                    )

                    httpStatus = status.HTTP_201_CREATED
                else:
                    httpStatus = status.HTTP_400_BAD_REQUEST
                    response = {
                        "infoblox": {
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
