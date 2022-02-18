from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from infoblox.models.Infoblox.Network import Network
from infoblox.models.Permission.Permission import Permission

from infoblox.serializers.Infoblox.Network import InfobloxNetworkSerializer
from infoblox.serializers.Infoblox.Ipv4s import InfobloxIpv4sSerializer

from infoblox.controllers.CustomController import CustomController

from infoblox.helpers.Lock import Lock
from infoblox.helpers.Conditional import Conditional
from infoblox.helpers.Log import Log


class InfobloxNetworkController(CustomController):
    @staticmethod
    def get(request: Request, assetId: int, networkAddress: str) -> Response:
        auth = False
        data = dict()
        showIp = False
        ipv4Info = { "data": dict() }
        etagCondition = { "responseEtag": "" }
        permissionNetwork = list("none")

        user = CustomController.loggedUser(request)

        try:
            # Find the network and the father-network-container (if any)
            # in the form aaaa/m to check permissions against.
            netInfo = Network(assetId, networkAddress)

            permissionNetwork.append(netInfo.network)
            if netInfo.network_container != "/":
                permissionNetwork.append(netInfo.network_container)
        except Exception:
            pass

        try:
            for net in permissionNetwork:
                if Permission.hasUserPermission(groups=user["groups"], action="network_get", assetId=assetId, networkName=net) or user["authDisabled"]: # @todo: check also for permissions in containers of upper levels.
                    auth = True

            if auth:
                Log.actionLog("Network information", user)

                # If asked for, get related IPs.
                if "related" in request.GET:
                    rList = request.GET.getlist('related')
                    if "ip" in rList:
                        showIp = True

                lock = Lock("network", locals(), networkAddress)
                if lock.isUnlocked():
                    lock.lock()

                    n = Network(assetId, networkAddress)
                    serializer = InfobloxNetworkSerializer(data=n.repr())
                    if serializer.is_valid():
                        data["data"] = serializer.validated_data
                        data["href"] = request.get_full_path()

                        if showIp:
                            ipv4Info["data"]["items"] = n.ipv4Addresses()
                            serializerIpv4 = InfobloxIpv4sSerializer(data=ipv4Info, reqType="get")
                            if serializerIpv4.is_valid():
                                data["data"].update({
                                    "ipv4Info": serializerIpv4.validated_data["data"]["items"]
                                })

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

                                Log.log("Upstream data incorrect: " + str(serializer.errors))
                        else:
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

                    CustomController.plugins("network_get", locals())
                else:
                    data = None
                    httpStatus = status.HTTP_423_LOCKED
            else:
                data = None
                httpStatus = status.HTTP_403_FORBIDDEN
        except Exception as e:
            Lock("network", locals(), locals()["networkAddress"]).release()

            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "ETag": etagCondition["responseEtag"],
            "Cache-Control": "must-revalidate"
        })

