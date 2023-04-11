from rest_framework.request import Request
from rest_framework.response import Response
from infoblox.helpers.decorators.TriggerBase import TriggerBase

from infoblox.helpers.Log import Log


# Trigget a GET ipv4 request for example and test.
class TriggerIpv4(TriggerBase):
    def __init__(self, wrappedMethod: callable, *args, **kwargs) -> None:
        super().__init__(wrappedMethod)
        self.triggerMethod = "GET"
        self.triggerAction = self.getTriggerAction()



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def triggerActionRequestParams(self) -> dict:
        try:
            # triggerAssetId = asset.get("id", 0)
            triggerAssetId = 1
            ipAddress = self.__prResponseParser(self.responsePr)[0]
            triggerPath = '/api/v1/infoblox/' + str(triggerAssetId) + "/ipv4/" + str(ipAddress)

            return {
                "request": self.triggerActionRequest(
                    requestPr=self.requestPr, triggerPath=triggerPath, triggerMethod=self.triggerMethod, triggerPayload=None, additionalQueryParams={"__concertoDrReplicaFlow": self.relationUuid}
                ),
                "assetId": triggerAssetId,
                "ipv4address": ipAddress
            }
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



    def triggerCondition(self, request: Request = None, response: Response = None):
        if response.status_code in (200, 201, 202, 204):  # trigger the action in dr only if it was successful.
            if "rep" in request.query_params and request.query_params["rep"]:  # trigger action in dr only if dr=1 param was passed.
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
