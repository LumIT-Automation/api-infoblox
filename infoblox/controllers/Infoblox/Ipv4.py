import json

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from infoblox.models.Infoblox.Ipv4 import Ipv4
from infoblox.models.Permission.Permission import Permission
from infoblox.models.History.History import History

from infoblox.serializers.Infoblox.Ipv4 import InfobloxIpv4Serializer as Serializer

from infoblox.controllers.CustomController import CustomController

from infoblox.helpers.Lock import Lock
from infoblox.helpers.Conditional import Conditional
from infoblox.helpers.Mail import Mail
from infoblox.helpers.Log import Log
from infoblox.helpers.decorators.ActionHistory import HistoryLog


class InfobloxIpv4Controller(CustomController):
    @staticmethod
    @HistoryLog
    def get(request: Request, assetId: int, ipv4address: str) -> Response:
        user = CustomController.loggedUser(request)
        data = dict()
        etagCondition = { "responseEtag": "" }
        userNetwork = "Unauthorized"
        networkCidr = "/"
        networkContainerCidr = "/" # container of userNetwork, if any.

        try:
            ipv4 = Ipv4(assetId, ipv4address)
            try:
                networkCidr = ipv4.network
                userNetwork, mask = networkCidr.split("/")
            except Exception:
                pass

            if Permission.hasUserPermission(groups=user["groups"], action="ipv4_get", assetId=assetId, network=networkCidr):
                Log.actionLog("Get ipv4s address information: "+ipv4address, user)

                lock = Lock("network", locals(), userNetwork=userNetwork, objectName=ipv4address) # must use an additional parameter for calculated network.
                if lock.isUnlocked():
                    lock.lock()

                    serializer = Serializer(data=ipv4.repr())
                    if serializer.is_valid():
                        data["data"] = serializer.validated_data
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
                            "infoblox": "Upstream data mismatch."
                        }

                        Log.log("Upstream data incorrect: "+str(serializer.errors))

                    lock.release()

                    # Run registered plugins.
                    CustomController.plugins("ipv4_get", data=data, ipv4Address=ipv4address, user=user)
                else:
                    data = None
                    httpStatus = status.HTTP_423_LOCKED
            else:
                data = None
                httpStatus = status.HTTP_403_FORBIDDEN

        except Exception as e:
            if "userNetwork" in locals():
                Lock("network", locals(), userNetwork=locals()["userNetwork"], objectName=locals()["ipv4address"]).release()

            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "ETag": etagCondition["responseEtag"],
            "Cache-Control": "must-revalidate"
        })



    @staticmethod
    def delete(request: Request, assetId: int, ipv4address: str) -> Response:
        user = CustomController.loggedUser(request)
        userNetwork = ""
        networkCidr = "/"
        networkContainerCidr = "/" # container of userNetwork, if any.

        try:
            ipv4 = Ipv4(assetId, ipv4address)
            try:
                networkCidr = ipv4.network
                userNetwork, mask = networkCidr.split("/")
            except Exception:
                pass

            if Permission.hasUserPermission(groups=user["groups"], action="ipv4_delete", assetId=assetId, network=networkCidr):
                Log.actionLog("Delete ipv4s address: "+ipv4address, user)

                lock = Lock("network", locals(), userNetwork=userNetwork, objectName=ipv4address)
                if lock.isUnlocked():
                    lock.lock()

                    ipv4.release(fixedaddressOnly=True)
                    httpStatus = status.HTTP_200_OK

                    lock.release()

                    historyId = InfobloxIpv4Controller.__historyLog(assetId, user["username"], "ipv4_delete", "deleted", ipv4address)
                    Mail.send(user, "ALERT_JSM", "IPv4 address "+ipv4address+" has been deleted by "+user["username"]+"."+"\r\nGroup: IT Network Management.") # @todo: move away.

                    # Run registered plugins.
                    CustomController.plugins("ipv4_delete", ipv4Address=ipv4address, user=user)
                else:
                    httpStatus = status.HTTP_423_LOCKED
                    Log.actionLog("Ipv4 locked: "+str(lock), user)
            else:
                httpStatus = status.HTTP_403_FORBIDDEN
        except Exception as e:
            if "userNetwork" in locals():
                Lock("network", locals(), userNetwork=locals()["userNetwork"], objectName=locals()["ipv4address"]).release()

            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(None, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })



    @staticmethod
    def patch(request: Request, assetId: int, ipv4address: str) -> Response:
        response = None
        user = CustomController.loggedUser(request)
        userNetwork = ""
        networkCidr = "/"
        networkContainerCidr = "/" # container of userNetwork, if any.

        try:
            ipv4 = Ipv4(assetId, ipv4address)
            try:
                networkCidr = ipv4.network
                userNetwork, mask = networkCidr.split("/")
            except Exception:
                pass

            if Permission.hasUserPermission(groups=user["groups"], action="ipv4_patch", assetId=assetId, network=networkCidr):
                Log.actionLog("Modify ipv4s address: "+ipv4address, user)
                Log.actionLog("User data: "+str(request.data), user)

                serializer = Serializer(data=request.data["data"], partial=True)
                if serializer.is_valid():
                    data = serializer.validated_data

                    lock = Lock("network", locals(), userNetwork=userNetwork, objectName=ipv4address)
                    if lock.isUnlocked():
                        lock.lock()

                        ipv4.modify(data) # address pass: data will be modified, using this for the logs.

                        httpStatus = status.HTTP_200_OK
                        lock.release()

                        historyId = InfobloxIpv4Controller.__historyLog(assetId, user["username"], "ipv4_patch: " + json.dumps(data), "modified", ipv4address)

                        # Run registered plugins.
                        CustomController.plugins("ipv4_patch", ipv4Address=ipv4address, user=user)
                    else:
                        httpStatus = status.HTTP_423_LOCKED
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
            if "userNetwork" in locals():
                Lock("network", locals(), userNetwork=locals()["userNetwork"], objectName=locals()["ipv4address"]).release()

            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(response, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })



    ####################################################################################################################
    # Helper methods
    ####################################################################################################################

    @staticmethod
    def __historyLog(assetId, user, action, status, ipv4, network: str = "", gateway: str = "", mask: str = "") -> int:
        data = {
            "log": {
                "username": user,
                "action": action,
                "asset_id": assetId,
                "status": status
            },
            "log_object": {
                "type": "ipv4",
                "address": ipv4,
                "network": network,
                "mask": mask,
                "gateway": gateway
            }
        }

        try:
            return History.add(data)
        except Exception:
            pass
