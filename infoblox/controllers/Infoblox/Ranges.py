from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from infoblox.models.Infoblox.Range import Range
from infoblox.models.Infoblox.NetworkContainer import NetworkContainer

from infoblox.models.Permission.Permission import Permission

from infoblox.serializers.Infoblox.Ranges import InfobloxRangesSerializer as Serializer

from infoblox.controllers.CustomController import CustomController

from infoblox.helpers.Lock import Lock
from infoblox.helpers.Conditional import Conditional
from infoblox.helpers.Log import Log


class InfobloxRangesController(CustomController):
    @staticmethod
    def get(request: Request, assetId: int) -> Response:
        data = dict()
        allowedData = {
            "data": []
        }
        etagCondition = { "responseEtag": "" }
        user = CustomController.loggedUser(request)

        fk = list()
        fv = list()
        filters = dict()

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="ranges_get", assetId=assetId) or user["authDisabled"]:
                Log.actionLog("Get ranges list", user)

                if 'fby' in request.GET and 'fval' in request.GET:
                    for f in dict(request.GET)["fby"]:
                        fk.append(f)
                    for v in dict(request.GET)["fval"]:
                        fv.append(v)
                    filters = dict(zip(fk, fv))

                lock = Lock("range", locals())
                if lock.isUnlocked():
                    lock.lock()

                    ranges = Range.listData(assetId, filters)
                    networkContainers = NetworkContainer.listData(assetId)
                    # Filter networks' list basing on permissions.
                    # Todo: check performances.
                    for r in ranges:
                        if Permission.hasUserPermission(groups=user["groups"], action="ranges_get", assetId=assetId, network=str(r["network"]), containers=networkContainers):
                            allowedData["data"].append(r)

                    serializer = Serializer(data=allowedData)
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

                    lock.release()

                    # Run registered plugins.
                    CustomController.plugins("ranges_get", locals())
                else:
                    data = None
                    httpStatus = status.HTTP_423_LOCKED
            else:
                data = None
                httpStatus = status.HTTP_403_FORBIDDEN
        except Exception as e:
            Lock("range", locals()).release()

            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "ETag": etagCondition["responseEtag"],
            "Cache-Control": "must-revalidate"
        })
