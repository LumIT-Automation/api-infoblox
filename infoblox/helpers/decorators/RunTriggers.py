import re
import functools
from ipaddress import ip_address, ip_network
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
        self.request = None
        self.primaryAssetId: int = 0



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def __call__(self, request: Request, **kwargs):
        @functools.wraps(request)
        def wrapped():
            try:
                self.request = request
                self.primaryAssetId = int(kwargs["assetId"])

                # Run wrappedMethod with given parameters.
                primaryResponse = self.wrappedMethod(request, **kwargs)

            except Exception as e:
                raise e

            try:
                # Whatever a particular pre-condition is met, perform found triggers.
                if self.__triggerPreCondition(primaryResponse):
                    # Run found triggers if trigger-condition is met.
                    for t in self.__triggers():
                        # [
                        #     {"destinationAssetId": 1, "action": "ipv4_get", "conditions": [{"src_asset_id": "1", "condition": "10.9.0.0/17 "}, {"src_asset_id": " 1", "condition": "10.8.0.0/17"}]},
                        #     {"destinationAssetId": 1, "action": "ipv4_post", "conditions": [{"src_asset_id": "1", "condition": "10.9.0.0/17"}]}
                        # ]

                        Log.log("Trigger execution: " + str(self.__runTrigger(t, primaryResponse)), "_") # add list to list.

            except Exception as e:
                Log.log("Trigger Exception: " + str(e), '_')
                pass

            return primaryResponse

        return wrapped()



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __triggerPreCondition(self, primaryResponse: Response):
        if primaryResponse.status_code in (200, 201, 202, 204): # trigger the action in dr only if it was successful.
            if "rep" in self.request.query_params and self.request.query_params["rep"]: # trigger action in dr only if rep=1 param was passed.
                return True

        return False



    def __triggers(self) -> List[dict]:
        triggers = list()

        try:
            # Find related triggers:
            # triggers named after the decorated controller's name (via urls.py) + method (get/post/...).
            l = Trigger.list(filter={
                "name": resolve(self.request.path).url_name + '_' + self.request.method.lower(),
                "src_asset_id": self.primaryAssetId,
                "enabled": True
            })

            # Return relevant information.
            for el in l:
                triggers.append({
                    "destinationAssetId": el["dst_asset_id"],
                    "action": el["action"],
                    "conditions": el["conditions"],
                })

            return triggers
        except Exception as e:
            raise e



    # def __getTriggerAction(self) -> callable:
    #     try:
    #         from infoblox.controllers.Infoblox.Ipv4 import InfobloxIpv4Controller as action
    #
    #         m = self.triggerMethod.lower()
    #         if hasattr(action, m) and callable(getattr(action, m)):
    #             return getattr(action, m)
    #     except ImportError as e:
    #         raise e



    def __runTrigger(self, t: dict, primaryResponse: Response):
        outputList = list()

        # t example:
        # {"destinationAssetId": 1, "action": "ipv4_get", "conditions": [{"src_asset_id": "1", "condition": "10.9.0.0/17"}, {...}]

        try:
            # Run trigger t for all response IPv4 addresses.
            for ip in RunTriggers.__responseIpv4Addresses(primaryResponse):
                if any(ip_address(ip) in ip_network(condition["condition"]) and self.primaryAssetId == condition["src_asset_id"] for condition in t["conditions"]):

                    from infoblox.models.Infoblox.Ipv4 import Ipv4
                    data = {
                        "ipv4addr": ip,
                        "mac": "00:00:00:00:00:00",
                        "extattrs":  self.request.data.get("extattrs", [])
                    }
                    outputList.append(Ipv4.reserve(assetId=t["destinationAssetId"], data=data))

            return outputList
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private static methods
    ####################################################################################################################

    @staticmethod
    def __responseIpv4Addresses(response: Response) -> list:
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
