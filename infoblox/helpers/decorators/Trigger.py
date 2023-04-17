import ipaddress

import functools

from django.http import HttpRequest, QueryDict
from django.urls import resolve
from rest_framework.request import Request
from rest_framework.response import Response

from infoblox.models.Infoblox.Asset.Trigger import Trigger

from infoblox.helpers.Log import Log



# Trigger a GET ipv4 request for example and test.
class Trigger:
    def __init__(self, wrappedMethod: callable, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.wrappedMethod = wrappedMethod
        self.triggerMethod = "GET"
        self.triggerAction = self.getTriggerAction()
        self.requestPrimary = None
        self.responsePrimary = None
        self.primaryAssetId: int = 0
        self.drAssetIds = set() # secondary/dr assetIds.
        self.assets = list() # dr asset ids list.
        self.controllerName = ""




    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def __call__(self, request: Request, **kwargs):
        @functools.wraps(request)
        def wrapped():
            try:
                self.primaryAssetId = int(kwargs["assetId"])
                self.requestPrimary = request
                self.controllerName = resolve(self.requestPrimary.path).url_name + '_' + self.requestPrimary.method.lower()
                self.responsePrimary = self.wrappedMethod(request, **kwargs)

                # Whatever a particular condition is met, perform found triggers.
                if self.triggerCondition():
                    self.drAssetIds = self.__triggerAssetList()
                    try:
                        for req in self.triggerBuildRequests():
                            r = self.triggerAction(**req)
                            # Todo: history.
                    except Exception:
                        # Todo: Log and continue
                        pass

                return self.responsePrimary
            except Exception as e:
                raise e

        return wrapped()



    def triggerBuildRequests(self):
        outputList = list()

        try:
            ipAddressList = self.__prResponseParser(self.responsePrimary)

            for assetId in self.drAssetIds:
                triggerFilter = {
                    "trigger_name": self.controllerName,
                    "src_asset_id": self.primaryAssetId,
                    "dst_asset_id": assetId
                }

                Log.log(triggerFilter, 'GGGGGGGGGGGGGGGGGGGGGG')
                t = Trigger.list(filter=triggerFilter)
                Log.log(t, 'TTTTTTTTTTTTTTTTT')
                networkCondition = [el["trigger_condition"] for el in Trigger.list(filter=triggerFilter)]
                Log.log(networkCondition, 'NNNNNNNNNNNNNNN')
                for ip in ipAddressList:
                    if any(ipaddress.ip_address(ip) in ipaddress.ip_network(net) for net in networkCondition):
                        from infoblox.models.Infoblox.Ipv4 import Ipv4
                        outputList.append(Ipv4(assetId=assetId, address=ip).repr())

            Log.log(outputList, 'OOOOOOOOOOOOOOOOOOOOOOOOOOO')
            return outputList
        except Exception as e:
            raise e



    def getTriggerAction(self) -> callable:
        try:
            from infoblox.controllers.Infoblox.Ipv4 import InfobloxIpv4Controller as action

            m = self.triggerMethod.lower()
            if hasattr(action, m) and callable(getattr(action, m)):
                return getattr(action, m)
        except ImportError as e:
            raise e



    def triggerCondition(self):
        if self.responsePrimary.status_code in (200, 201, 202, 204): # trigger the action in dr only if it was successful.
            if "rep" in self.requestPrimary.query_params and self.requestPrimary.query_params["rep"]: # trigger action in dr only if rep=1 param was passed.
                return True

        return False



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __prResponseParser(self, response: Response) -> list:
        import re
        ipList = []

        try:
            """
            # responsePrimary example:
            {
                "data": [
                    {
                        "result": "fixedaddress/ZG5zLmZpeGVkX2FkZHJlc3MkMTAuOC4wLjIzMS4wLi4:10.8.0.231/default",
                        "mask": "255.255.128.0",
                        "gateway": "10.8.1.1"
                    }
                ]
            }
            """

            if hasattr(response, "data"):
                if "data" in response.data and response.data["data"]:
                    for el in response.data["data"]:
                        if "result" in el:
                            ipList.extend(
                                re.findall(
                                    r'fixedaddress/[A-Za-z0-9]+:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})/[A-Za-z]+$',
                                    el["result"]
                                )
                            )

            return ipList
        except Exception as e:
            raise e



    def __triggerAssetList(self) -> set:
        s = set()

        try:
            if self.primaryAssetId:
                from infoblox.models.Infoblox.Asset.Trigger import Trigger
                for el in Trigger.list({"trigger_name": self.controllerName, "src_asset_id": self.primaryAssetId}):
                    s.add( el["dst_asset_id"] )

            return s
        except Exception as e:
            raise e