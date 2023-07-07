from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from infoblox.models.Permission.Permission import Permission

from infoblox.usecases.CloudExtAttrFactory import CloudExtAttrFactory

from infoblox.controllers.CustomController import CustomController
from infoblox.helpers.Lock import Lock
from infoblox.helpers.Log import Log


class InfobloxCloudNetworkExtAttrsController(CustomController):
    @staticmethod
    def get(request: Request, assetId: int, extattr: str) -> Response:
        data = {"data": {}}
        etagCondition = { "responseEtag": "" }
        user = CustomController.loggedUser(request)

        fk = list()
        fv = list()
        filters = dict()

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="extattrs_get", assetId=assetId) or user["authDisabled"]:
                Log.actionLog("Get networks list", user)

                if 'fby' in request.GET and 'fval' in request.GET:
                    for f in dict(request.GET)["fby"]:
                        fk.append(f)
                    for v in dict(request.GET)["fval"]:
                        fv.append(v)
                    filters = dict(zip(fk, fv))

                lock = Lock("extattr", locals())
                if lock.isUnlocked():
                    lock.lock()

                    if extattr:
                        if extattr == "provider":
                            data["data"]["items"] = CloudExtAttrFactory(assetId, user)().listProviders(filters)
                        elif extattr == "account+provider":
                            data["data"]["items"] = CloudExtAttrFactory(assetId, user)().listAccountsProviders(filters)

                    httpStatus = status.HTTP_200_OK
                    lock.release()
                else:
                    data = None
                    httpStatus = status.HTTP_423_LOCKED
            else:
                data = None
                httpStatus = status.HTTP_403_FORBIDDEN
        except Exception as e:
            Lock("network", locals()).release()

            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "ETag": etagCondition["responseEtag"],
            "Cache-Control": "must-revalidate"
        })
