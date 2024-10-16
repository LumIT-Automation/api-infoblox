import json

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from infoblox.models.Infoblox.Network import Network
from infoblox.models.Permission.CheckPermissionFacade import CheckPermissionFacade
from infoblox.models.History.History import History

from infoblox.serializers.Infoblox.Network import InfobloxNetworkSerializer
from infoblox.serializers.Infoblox.Ipv4s import InfobloxIpv4sSerializer
from infoblox.serializers.Infoblox.Ranges import InfobloxRangesSerializer

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
        showRange = False
        ipv4Info = { "data": dict() }
        rangeInfo = { "data": dict() }
        etagCondition = { "responseEtag": "" }
        httpStatus = None
        user = CustomController.loggedUser(request)
        workflowId = request.headers.get("workflowId", "") # a correlation id.
        checkWorkflowPermission = request.headers.get("checkWorkflowPermission", "")

        try:
            n = Network(assetId, networkAddress)
            if CheckPermissionFacade.hasUserPermission(groups=user["groups"], action="network_get", assetId=assetId, network=n, isWorkflow=bool(workflowId)) or user["authDisabled"]:
                if workflowId and checkWorkflowPermission:
                    httpStatus = status.HTTP_204_NO_CONTENT
                else:
                    Log.actionLog("Network information", user)

                    # If asked for, get related IPs.
                    if "related" in request.GET:
                        rList = request.GET.getlist('related')
                        if "ip" in rList:
                            showIp = True
                        if "range" in rList:
                            showRange = True

                    lock = Lock("network", locals(), networkAddress, workflowId=workflowId)
                    if lock.isUnlocked():
                        lock.lock()

                        serializer = InfobloxNetworkSerializer(data=n.repr())
                        if serializer.is_valid():
                            data["data"] = serializer.validated_data
                            data["href"] = request.get_full_path()

                            if showIp:
                                Log.actionLog("Ask also ip data information", user)
                                ipv4Info["data"]["items"] = n.ipv4sData()
                                serializerIpv4 = InfobloxIpv4sSerializer(data=ipv4Info, reqType="get")
                                if serializerIpv4.is_valid():
                                    data["data"].update({
                                        "ipv4Info": serializerIpv4.validated_data["data"]["items"]
                                    })
                                else:
                                    httpStatus, data = status.HTTP_500_INTERNAL_SERVER_ERROR, {"Infoblox": {"error": "Infoblox upstream data mismatch."} }
                                    Log.log("Upstream data incorrect: " + str(serializer.errors))

                            if showRange and CheckPermissionFacade.hasUserPermission(groups=user["groups"], action="ranges_get", assetId=assetId, network=n, isWorkflow=bool(workflowId)) or user["authDisabled"]:
                                Log.actionLog("Ask also ranges information", user)
                                rangeInfo["data"] = n.rangesData()
                                serializerRange = InfobloxRangesSerializer(data=rangeInfo)
                                if serializerRange.is_valid():
                                    data["data"].update({
                                        "rangeInfo": serializerRange.validated_data["data"]
                                    })
                                else:
                                    httpStatus, data = status.HTTP_500_INTERNAL_SERVER_ERROR, {"Infoblox": {"error": "Infoblox upstream data mismatch."} }
                                    Log.log("Upstream data incorrect: " + str(serializer.errors))
                        else:
                            httpStatus, data = status.HTTP_500_INTERNAL_SERVER_ERROR, {"Infoblox": {"error": "Infoblox upstream data mismatch."} }
                            Log.log("Upstream data incorrect: "+str(serializer.errors))

                        # Check the response's ETag validity (against client request).
                        if httpStatus != status.HTTP_500_INTERNAL_SERVER_ERROR:
                            conditional = Conditional(request)
                            etagCondition = conditional.responseEtagFreshnessAgainstRequest(data["data"])
                            if etagCondition["state"] == "fresh":
                                data = None
                                httpStatus = status.HTTP_304_NOT_MODIFIED
                            else:
                                httpStatus = status.HTTP_200_OK

                        if not workflowId:
                            lock.release()

                        # Run registered plugins.
                        CustomController.plugins("network_get")
                    else:
                        data = None
                        httpStatus = status.HTTP_423_LOCKED
            else:
                data = None
                httpStatus = status.HTTP_403_FORBIDDEN
        except Exception as e:
            if "networkAddress" in locals() and not workflowId:
                Lock("network", locals(), locals()["networkAddress"]).release()

            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "ETag": etagCondition["responseEtag"],
            "Cache-Control": "must-revalidate"
        })



    @staticmethod
    def delete(request: Request, assetId: int, networkAddress: str) -> Response:
        response = None
        auth = False
        data = dict()

        user = CustomController.loggedUser(request)
        workflowId = request.headers.get("workflowId", "") # a correlation id.
        checkWorkflowPermission = request.headers.get("checkWorkflowPermission", "")

        try:
            if CheckPermissionFacade.hasUserPermission(groups=user["groups"], action="network_delete", assetId=assetId, network=networkAddress, isWorkflow=workflowId) or user["authDisabled"]:
                if workflowId and checkWorkflowPermission:
                    httpStatus = status.HTTP_204_NO_CONTENT
                else:
                    Log.actionLog("Network deletion", user)

                    lock = Lock("network", locals(), networkAddress, workflowId=workflowId)
                    if lock.isUnlocked():
                        lock.lock()

                        Network(assetId, networkAddress).delete()
                        httpStatus = status.HTTP_200_OK
                        if not workflowId:
                            lock.release()
                    else:
                        httpStatus = status.HTTP_423_LOCKED
            else:
                httpStatus = status.HTTP_403_FORBIDDEN
        except Exception as e:
            if "networkAddress" in locals() and not workflowId:
                Lock("network", locals(), locals()["networkAddress"]).release()

            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(None, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })



    @staticmethod
    def patch(request: Request, assetId: int, networkAddress: str) -> Response:
        response = None
        auth = False
        data = dict()

        user = CustomController.loggedUser(request)
        workflowId = request.headers.get("workflowId", "") # a correlation id.
        checkWorkflowPermission = request.headers.get("checkWorkflowPermission", "")

        try:
            if CheckPermissionFacade.hasUserPermission(groups=user["groups"], action="network_patch", assetId=assetId, network=networkAddress, isWorkflow=workflowId) or user["authDisabled"]:
                if workflowId and checkWorkflowPermission:
                    httpStatus = status.HTTP_204_NO_CONTENT
                else:
                    Log.actionLog("Modify network", user)
                    Log.actionLog("User data: "+str(request.data), user)

                    serializer = InfobloxNetworkSerializer(data=request.data["data"], partial=True)
                    if serializer.is_valid():
                        data = serializer.validated_data

                        lock = Lock("network", locals(), networkAddress, workflowId=workflowId)
                        if lock.isUnlocked():
                            lock.lock()

                            n = Network(assetId, networkAddress).modify(data)
                            httpStatus = status.HTTP_200_OK
                            if not workflowId:
                                lock.release()
                            InfobloxNetworkController.__historyLog(assetId, user["username"], "network_patch: " + json.dumps(data), "modified", networkAddress, n["network"])
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
            if "networkAddress" in locals() and not workflowId:
                Lock("network", locals(), locals()["networkAddress"]).release()

            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(response, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })



    ####################################################################################################################
    # Helper methods
    ####################################################################################################################

    @staticmethod
    def __historyLog(assetId, user, action, status, network: str = "", address: str = "") -> None:
        data = {
            "log": {
                "username": user,
                "action": action,
                "asset_id": assetId,
                "status": status
            },
            "log_object": {
                "type": "network",
                "address": address,
                "network": network,
                "mask": "",
                "gateway": ""
            }
        }

        try:
            History.add(data)
        except Exception:
            pass
