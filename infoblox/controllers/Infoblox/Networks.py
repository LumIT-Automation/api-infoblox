from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from infoblox.models.Infoblox.Network import Network
from infoblox.models.Infoblox.NetworkContainer import NetworkContainer

from infoblox.models.Permission.Permission import Permission

from infoblox.serializers.Infoblox.Networks import InfobloxNetworksSerializer as Serializer
from infoblox.serializers.Infoblox.Network import InfobloxNetworkSerializer as NetworkAddSerializer

from infoblox.controllers.CustomController import CustomController

from infoblox.helpers.Lock import Lock
from infoblox.helpers.Conditional import Conditional
from infoblox.helpers.Log import Log


class InfobloxNetworksController(CustomController):
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
            if Permission.hasUserPermission(groups=user["groups"], action="networks_get", assetId=assetId) or user["authDisabled"]:
                Log.actionLog("Get networks list", user)

                if 'fby' in request.GET and 'fval' in request.GET:
                    for f in dict(request.GET)["fby"]:
                        fk.append(f)
                    for v in dict(request.GET)["fval"]:
                        fv.append(v)
                    filters = dict(zip(fk, fv))

                lock = Lock("network", locals())
                if lock.isUnlocked():
                    lock.lock()

                    networks = Network.listData(assetId, filters)
                    networkContainers = NetworkContainer.listData(assetId)
                    # Filter networks' list basing on permissions.
                    for n in networks:
                        if Permission.hasUserPermission(groups=user["groups"], action="networks_get", assetId=assetId, networkName=str(n["network"]), netContainerList=networkContainers, netList=networks):
                            allowedData["data"].append(n)

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

                    CustomController.plugins("networks_get", locals())
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



    @staticmethod
    def post(request: Request, assetId: int) -> Response:
        response = None
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="networks_post", assetId=assetId) or user["authDisabled"]:
                Log.actionLog("Network addition", user)
                Log.actionLog("User data: "+str(request.data), user)

                serializer = NetworkAddSerializer(data=request.data["data"])
                if serializer.is_valid():
                    data = serializer.validated_data

                    lock = Lock("network", locals(), data["network"])
                    if lock.isUnlocked():
                        lock.lock()

                        Network.add(assetId, data)

                        httpStatus = status.HTTP_201_CREATED
                        lock.release()
                    else:
                        httpStatus = status.HTTP_423_LOCKED
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
            if "serializer" in locals():
                Lock("network", locals(), locals()["serializer"].data["network"]).release()

            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(response, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })
