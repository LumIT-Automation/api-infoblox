import re
import ipaddress
import functools
from typing import List

from django.urls import resolve
from rest_framework.request import Request
from rest_framework.response import Response

from infoblox.models.Infoblox.Asset.Trigger import Trigger

from infoblox.helpers.Log import Log


class RunTriggers:
    def __init__(self, wrappedMethod: callable, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.wrappedMethod = wrappedMethod
        self.triggerMethod = "GET"
        self.triggerAction = self.getTriggerAction()
        self.requestPrimary = None
        self.responsePrimary = None

        self.primaryAssetId: int = 0
        self.drAssetIds = set() # secondary/dr assetIds.



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def __call__(self, request: Request, **kwargs):
        @functools.wraps(request)
        def wrapped():
            try:
                self.primaryAssetId = int(kwargs["assetId"])
                self.requestPrimary = request
                self.responsePrimary = self.wrappedMethod(request, **kwargs)

                # Whatever a particular condition is met, perform found triggers.
                if self.triggerCondition():
                    Log.log(self.__triggers(), "_")



                    # self.drAssetIds = self.__triggerAssetList()
                    # try:
                    #     for req in self.triggerBuildRequests():
                    #         r = self.triggerAction(**req)
                    #         # Todo: history.
                    # except Exception:
                    #     # Todo: Log and continue
                    #     pass

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

                t = RunTriggers.list(filter=triggerFilter)
                networkCondition = [el["trigger_condition"] for el in RunTriggers.list(filter=triggerFilter)]
                for ip in ipAddressList:
                    if any(ipaddress.ip_address(ip) in ipaddress.ip_network(net) for net in networkCondition):
                        from infoblox.models.Infoblox.Ipv4 import Ipv4
                        outputList.append(Ipv4(assetId=assetId, address=ip).repr())
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

    def __triggers(self) -> List[dict]:
        triggers = list()

        try:
            # Find related triggers:
            # triggers named after the controller's decorated name (via urls.py) + method.
            l = Trigger.list(filter={
                "trigger_name": resolve(self.requestPrimary.path).url_name + '_' + self.requestPrimary.method.lower(),
                "src_asset_id": self.primaryAssetId,
                "enabled": True
            })

            # Return relevant information.
            for el in l:
                triggers.append({
                    "destinationAssetId": el["dst_asset_id"],
                    "action": el["trigger_action"],
                    "condition": el["trigger_condition"],
                })

            return triggers
        except Exception as e:
            raise e



    def __prResponseParser(self, response: Response) -> list:
        ipList = []

        try:
            for el in response.data["data"]:
                if "result" in el:
                    ipList.extend(
                        re.findall(
                            r'fixedaddress/[A-Za-z0-9]+:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})/[A-Za-z]+$', # example: "fixedaddress/ZG5zLmZpeGVkX2FkZHJlc3MkMTAuOC4wLjIzMS4wLi4:10.8.0.231/default"
                            el["result"]
                        )
                    )
        except KeyError:
            pass
        except Exception as e:
            raise e

        return ipList
