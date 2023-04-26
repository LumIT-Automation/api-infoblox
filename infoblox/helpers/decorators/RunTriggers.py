import re
import functools
from ipaddress import ip_address, ip_network
from typing import List

from django.urls import resolve
from rest_framework.request import Request
from rest_framework.response import Response

from infoblox.models.Trigger.Trigger import Trigger

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
                # Whatever pre-conditions are met, perform found triggers.
                if self.__triggerPreCondition(primaryResponse):
                    triggers = self.__triggers()
                    if triggers:
                        for t in triggers:
                            o = self.__runTrigger(t, primaryResponse)
                            if o:
                                Log.log("[Triggers] Trigger execution: " + str(o))
                    else:
                        Log.log("[Triggers] No trigger found")
            except Exception as e:
                Log.log("[Triggers] Trigger error: " + str(e))

            return primaryResponse
        return wrapped()



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __triggerPreCondition(self, primaryResponse: Response) -> bool:
        try:
            if primaryResponse.status_code in (200, 201): # trigger the action in dr only if it was successful.
                if "rep" in self.request.query_params and self.request.query_params["rep"]: # trigger action in dr only if rep=1/true param was passed.
                    return True

            return False
        except Exception as e:
            raise e



    def __triggers(self) -> List[dict]:
        triggers = list()

        try:
            # Find related triggers:
            # triggers named after the decorated controller's name (via urls.py) + method (get/post/...).
            l = Trigger.dataList(filter={
                "name": resolve(self.request.path).url_name + '_' + self.request.method.lower(),
                "src_asset_id": self.primaryAssetId,
                "enabled": True
            }, loadConditions=True)

            # Return relevant information.
            for el in l:
                try:
                    triggers.append({
                        "dst_asset_id": el["dst_asset_id"],
                        "action": el["action"],
                        "conditions": el["conditions"],
                    })
                except KeyError:
                    pass

            return triggers
        except Exception as e:
            raise e



    def __runTrigger(self, t: dict, primaryResponse: Response) -> list:
        outputList = list()

        # t example:
        # {"dst_asset_id": 1, "action": "dst:ipv4s-replica", "conditions": [{"src_asset_id": "1", "condition": "src-ip-in:10.9.0.0/17"}, {...}]

        try:
            # Run trigger t.
            if t["action"] == "dst:ipv4s-replica":
                # Replicate all IP addresses found in primaryResponse onto dst_asset_id.
                # @todo: locks.
                from infoblox.models.Infoblox.Ipv4 import Ipv4
                from infoblox.controllers.CustomController import CustomController

                for ipAddressInformation in RunTriggers.__responseInfo(primaryResponse):
                    try:
                        if any("src-ip-in" in condition["condition"] and ip_address(ipAddressInformation["ipAddress"]) in ip_network(condition["condition"].split(":")[1].strip()) and self.primaryAssetId == condition["src_asset_id"] for condition in t["conditions"]):
                            data = {
                                "ipv4addr": ipAddressInformation["ipAddress"],
                                "mac": ipAddressInformation["mac"],
                                "extattrs": ipAddressInformation["extattrs"]
                            }

                            try:
                                outputList.append(
                                    Ipv4.reserve(assetId=t["dst_asset_id"], data=data)
                                )

                                # Run registered plugins.
                                reqType = "replica.specified-ip"
                                reqStatus = "success"
                                CustomController.plugins("ipv4s_post", locals())
                            except Exception as e:
                                RunTriggers.__raiseFlag("[Triggers] Trigger Exception: " + str(e))

                                # Run registered plugins.
                                reqType = "replica.specified-ip"
                                reqStatus = "failure"
                                CustomController.plugins("ipv4s_post", locals())
                        else:
                            Log.log("[Triggers] No suitable trigger found")
                    except IndexError:
                        pass
        except Exception as e:
            raise e

        return outputList



    ####################################################################################################################
    # Private static methods
    ####################################################################################################################

    @staticmethod
    def __responseInfo(response: Response) -> list:
        ipMacList = []

        try:
            for el in response.data["data"]:
                ipMacList.append({
                    "ipAddress":
                        re.findall(
                            r'fixedaddress/[A-Za-z0-9]+:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})/[A-Za-z]+$', # example: "fixedaddress/ZG5zLmZpeGVkX2FkZHJlc3MkMTAuOC4wLjIzMS4wLi4:10.8.0.231/default"
                            el["result"]
                        )[0],
                    "mac": el["mac"],
                    "extattrs": el["extattrs"]
                })
        except KeyError:
            pass
        except IndexError:
            pass
        except Exception as e:
            raise e

        return ipMacList



    @staticmethod
    def __raiseFlag(message):
        Log.log(message)
