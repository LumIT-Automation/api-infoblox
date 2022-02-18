import re
from ipaddress import IPv4Network

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from infoblox.models.Infoblox.Ipv4 import Ipv4
from infoblox.models.Infoblox.Network import Network
from infoblox.models.Permission.Permission import Permission
from infoblox.models.History import History

from infoblox.serializers.Infoblox.Ipv4s import InfobloxIpv4sSerializer as Serializer

from infoblox.controllers.CustomController import CustomController

from infoblox.helpers.Lock import Lock
from infoblox.helpers.Log import Log


class InfobloxIpv4sController(CustomController):
    @staticmethod
    def post(request: Request, assetId: int) -> Response:
        address = ""
        ipNetwork = ""
        response = {"data": list()}

        user = CustomController.loggedUser(request)

        if "next-available" in request.GET:
            # Next-available IPv4 ("network" or "container" logic).
            reqType = "post.next-available"
        else:
            # Specified IPv4 address.
            reqType = "post.specified-ip"

        try:
            serializer = Serializer(data=request.data, reqType=reqType) # adaptive serializer.
            if serializer.is_valid():
                validatedData = serializer.validated_data["data"]

                if reqType == "next-available":
                    # Find the network to check permissions against (network or direct-father-container) and logic information.
                    # On "container" logic, targetNetwork is set; on "network" logic, networkContainer is set.
                    permissionCheckNetwork, networkLogic, targetNetwork, networkContainer, gateway, mask = InfobloxIpv4sController.__infoNextAvail(assetId, validatedData)
                else:
                    permissionCheckNetwork, targetNetwork, mask, gateway = InfobloxIpv4sController.__infoProvidedIP(assetId, validatedData)
                    
                if Permission.hasUserPermission(groups=user["groups"], action="ipv4s_post", assetId=assetId, networkName=permissionCheckNetwork) or user["authDisabled"]:
                    Log.actionLog("Ipv4 addition", user)
                    Log.actionLog("User data: "+str(request.data), user)

                    lock = Lock("network", locals(), userNetwork=permissionCheckNetwork) # must use an additional parameter for calculated network; locking the permissionCheckNetwork.
                    if lock.isUnlocked():
                        lock.lock()

                        if reqType == "next-available":
                            response["data"], actualNetwork = InfobloxIpv4sController.__reserveNextAvail(assetId, validatedData, networkLogic, targetNetwork, networkContainer)
                            historyId = InfobloxIpv4sController.__historyLog(assetId, user["username"], "next-available", response, network=actualNetwork, gateway=gateway, mask=mask)
                        else:
                            response["data"] = InfobloxIpv4sController.__reserveProvided(assetId, validatedData)
                            historyId = InfobloxIpv4sController.__historyLog(assetId, user["username"], "user-specified", response, network=targetNetwork, gateway=gateway, mask=mask)

                        httpStatus = status.HTTP_201_CREATED
                        lock.release()

                        CustomController.plugins("ipv4s_post", locals())
                    else:
                        httpStatus = status.HTTP_423_LOCKED
                        Log.actionLog("Ipv4 locked: "+str(lock), user)
                else:
                    response = None
                    httpStatus = status.HTTP_403_FORBIDDEN
            else:
                httpStatus = status.HTTP_400_BAD_REQUEST
                response = {
                    "Infoblox": {
                        "error": str(serializer.errors)
                    }
                }

                Log.log("User data incorrect: "+str(response))
        except Exception as e:
            if "permissionCheckNetwork" in locals():
                Lock("network", locals(), userNetwork=locals()["permissionCheckNetwork"]).release()

            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(response, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })



    ####################################################################################################################
    # Helper methods
    ####################################################################################################################

    @staticmethod
    def __reserveNextAvail(assetId, data, networkLogic, targetNetwork, networkContainer) -> tuple:
        j = 0
        response = list()

        objectType = ""
        number = 1
        if "object_type" in data:
            objectType = data["object_type"]
        if "number" in data:
            number = int(data["number"])
            if number > 10:
                number = 10 # limited to 10.

        actualNetwork, addresses = Network.getNextAvailableIpv4Addresses(assetId, networkLogic, targetNetwork, networkContainer, number, objectType)
        for address in addresses:
            try:
                mac = data["mac"][j]
            except Exception:
                mac = "00:00:00:00:00:00"

            try:
                extattrs = data["extattrs"][j]
            except Exception:
                extattrs = data["extattrs"][0]

            response.append(Ipv4.reserveNextAvailable(assetId, address, extattrs, mac))
            j += 1

        return response, actualNetwork



    @staticmethod
    def __reserveProvided(assetId, data) -> list:
        response = list()

        if "number" in data:
            del (data["number"])
        data["mac"] = "00:00:00:00:00:00"

        if "extattrs" in data:
            data["extattrs"] = data["extattrs"][0]

        response.append(Ipv4.reserve(assetId, data))

        return response



    @staticmethod
    def __infoNextAvail(assetId, userData) -> tuple:
        networkContainer = ""
        targetNetwork = ""

        # Find out network belonging to the IPv4 address(es) to be created.
        try:
            userNetworkObj = Network.discriminateUserNetwork(assetId, userData["network"])
            if "network_container" in userNetworkObj:
                # On container logic, networkContainer is the network for permissions' check.
                networkLogic = "container"
                permissionCheckNetwork = networkContainer = userNetworkObj["network_container"]
            else:
                # On network logic.
                networkLogic = "network"
                permissionCheckNetwork = targetNetwork = userNetworkObj["targetNetwork"]

            gateway = userNetworkObj["gateway"]
            mask = userNetworkObj["mask"]
        except Exception as e:
            raise e

        return permissionCheckNetwork, networkLogic, targetNetwork, networkContainer, gateway, mask
    
    
    
    @staticmethod
    def __infoProvidedIP(assetId, userData) -> tuple:
        # Find out network belonging to the IPv4 address provided be the user.
        g = ""

        try:
            ipv4 = Ipv4(assetId, userData["ipv4addr"])
            permissionCheckNetwork = targetNetwork = ipv4.network
            n, mn = targetNetwork.split("/")

            try:
                info = Network(assetId, targetNetwork)
                m = info.extattrs["Mask"]["value"]
                g = info.extattrs["Gateway"]["value"]
            except Exception:
                m = IPv4Network(targetNetwork).netmask
        except Exception as e:
            raise e

        return permissionCheckNetwork, n, m, g



    @staticmethod
    def __historyLog(assetId, user, action, response, network: str = "", gateway: str = "", mask: str = "") -> int:
        hId = 0

        try:
            for createdObject in response["data"]:
                ipv4 = re.findall(r'[0-9]+(?:\.[0-9]+){3}', createdObject["result"])[0]

                oId = History.addByType({
                    "type": "ipv4Addresses",
                    "address": ipv4,
                    "network": network,
                    "mask": mask,
                    "gateway": gateway
                }, "object")

                hId = History.addByType({
                    "username": user,
                    "action": action,
                    "asset_id": assetId,
                    "object_id": oId,
                    "status": "created"
                }, "log")

        except Exception:
            pass

        return hId
