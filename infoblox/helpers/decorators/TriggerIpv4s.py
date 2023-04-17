import ipaddress
from rest_framework.response import Response
from rest_framework.request import Request

from infoblox.helpers.decorators.TriggerBase import TriggerBase

from infoblox.models.Infoblox.Asset.Trigger import Trigger

from infoblox.helpers.Log import Log


class TriggerIpv4s(TriggerBase):
    def __init__(self, wrappedMethod: callable, *args, **kwargs) -> None:
        super().__init__(wrappedMethod)

        self.wrappedMethod = wrappedMethod
        self.triggerMethod = "POST"
        self.triggerName = "trigger_ipv4s"
        self.triggerAction = self.getTriggerAction()



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def triggerBuildRequests(self):
        requestsList = list()

        try:
            ipAddressList = self.__prResponseParser(self.responsePrimary)

            for assetId in self.drAssetIds:
                triggerFilter = {
                    "trigger_name": self.triggerName,
                    "src_asset_id": self.primaryAssetId,
                    "dst_asset_id": assetId
                }

                networkCondition = [el["trigger_condition"] for el in Trigger.list(filter=triggerFilter)]
                for ip in ipAddressList:
                    if any(ipaddress.ip_address(ip) in ipaddress.ip_network(net) for net in networkCondition):
                        triggerPath = '/api/v1/infoblox/' + str(assetId) + "/ipv4s/"
                        triggerPayload = {
                            "data": {
                                "ipv4addr": ip,
                                "number": 1,
                                "mac": [
                                    "00:00:00:00:00:00"
                                ]
                            }
                        }

                        requestsList.append({
                            "request":  self.triggerActionRequest(
                                requestPr=self.requestPrimary, triggerPath=triggerPath, triggerMethod=self.triggerMethod, triggerPayload=triggerPayload, additionalQueryParams={"__concertoDrReplicaFlow": self.relationUuid}
                            ),
                            "assetId": assetId
                        })

            return requestsList
        except Exception as e:
            raise e



    def getTriggerAction(self) -> callable:
        return self.wrappedMethod # same controller of the first call, same method, different params.



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
            # responsePr example:
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
