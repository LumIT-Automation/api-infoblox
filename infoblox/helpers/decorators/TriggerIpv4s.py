from rest_framework.response import Response
from infoblox.helpers.decorators.TriggerBase import TriggerBase

from infoblox.helpers.Log import Log


class TriggerIpv4s(TriggerBase):
    def __init__(self, wrappedMethod: callable, *args, **kwargs) -> None:
        super().__init__(wrappedMethod)
        self.wrappedMethod = wrappedMethod
        self.triggerMethod = "POST"
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
            triggerPayload =  {
                "data": {
                    "ipv4addr": ipAddress,
                    "number": 1,
                    "mac": [
                        "00:00:00:00:00:00"
                    ]
                }
            }

            return {
                "request": self.triggerActionRequest(
                    requestPr=self.requestPr, triggerPath=triggerPath, triggerMethod=self.triggerMethod, triggerPayload=triggerPayload, additionalQueryParams={"__concertoDrReplicaFlow": self.relationUuid}
                ),
                "assetId": triggerAssetId
            }
        except Exception as e:
            raise e



    def getTriggerAction(self) -> callable:
        return self.wrappedMethod # same controller of the first call, same method, different params.



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
