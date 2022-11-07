from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from infoblox.models.Permission.IdentityGroup import IdentityGroup
from infoblox.models.Permission.Permission import Permission

from infoblox.serializers.Permission.Permission import PermissionSerializer as Serializer

from infoblox.controllers.CustomController import CustomController
from infoblox.helpers.Log import Log


class PermissionController(CustomController):
    @staticmethod
    def delete(request: Request, permissionId: int) -> Response:
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="permission_identityGroup_delete") or user["authDisabled"]:
                Log.actionLog("Permission deletion", user)

                p = Permission(permissionId)
                p.delete()

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
    def patch(request: Request, permissionId: int) -> Response:
        response = None
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="permission_identityGroup_patch") or user["authDisabled"]:
                Log.actionLog("Permission modification", user)
                Log.actionLog("User data: "+str(request.data), user)

                serializer = Serializer(data=request.data, partial=True)
                if serializer.is_valid():
                    data = serializer.validated_data["data"]

                    identityGroupId = IdentityGroup(identityGroupIdentifier=data["identity_group_identifier"]).id

                    p = Permission(permissionId)
                    p.modify(
                        identityGroupId,
                        data["role"],
                        data["network"]["id_asset"],
                        data["network"]["name"]
                    )

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
