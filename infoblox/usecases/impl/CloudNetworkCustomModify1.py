import re
from django.conf import settings

from infoblox.usecases.impl.CloudNetworkModify import CloudNetworkModify
from infoblox.models.Infoblox.Network import Network
from infoblox.models.History.History import History

from infoblox.helpers.Exception import CustomException
from infoblox.helpers.Log import Log


class CloudNetworkCustomModify1(CloudNetworkModify):
    def __init__(self, assetId: int, network: str, provider: str, region: str, user: str, *args, **kwargs):
        super().__init__(assetId, network, provider, region, user, *args, **kwargs)

        self.assetId = assetId
        self.network = Network(assetId=self.assetId, network=network)
        self.provider: str = provider
        self.region: str = region
        self.user = user

        self.networkData = self.network.repr()
        self.__checkNetwork()



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def modifyNetwork(self, data: dict, *args, **kwargs) -> dict:
        try:
            data = self.__formatData(data)
            o = self.network.modify(data)
            hid = self.__historyLog(self.network.network, 'modified')
            return o
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __checkNetwork(self):
        try:
            if not self.networkData.get("extattrs", {}).get("Environment", {}).get("value", "") == "Cloud":
                raise CustomException(status=400, payload={"Infoblox": "This network do not belong to the Cloud Enviroment."})
        except Exception as e:
            raise e



    def __formatData(self, data):
        try:
            extattrs = data.get("extattrs", {})

            if self.provider:
                extattrs.update({"Country": {"value": "Cloud-" + self.provider}})
            if self.region:
                extattrs.update({"City": {"value": self.region}})

            if extattrs:
                accountId = extattrs.get("Account ID", {}).get("value", "")
                if accountId:
                    previousNetworks = self.__getAccountNetworks(accountId=accountId)
                    if previousNetworks:
                        # Get the Account Name from the first occurrence.
                        accountName = previousNetworks[0].get("extattrs", {}).get("Account Name", {}).get("value", "")
                        if accountName:
                            extattrs.update({"Account Name": {"value": accountName}})
                        # Get the Reference from the first occurrence.
                        reference = previousNetworks[0].get("extattrs", {}).get("Reference", {}).get("value", "")
                        if reference:
                            extattrs.update({"Reference": {"value": reference}})
                else:
                    accountName = extattrs.get("Account Name", {}).get("value", "")
                    if accountName:
                        previousNetworks = self.__getAccountNetworks(accountName=accountName)
                        # Get the Account ID from the first occurrence.
                        accountId = previousNetworks[0].get("extattrs", {}).get("Account ID", {}).get("value", "")
                        if accountId:
                            extattrs.update({"Account ID": {"value": accountId}})
                        # Get the Reference from the first occurrence.
                        reference = previousNetworks[0].get("extattrs", {}).get("Reference", {}).get("value", "")
                        if reference:
                            extattrs.update({"Reference": {"value": reference}})

            # Add existing extattrs fields of the network that are missing in the input data.
            for k, v in self.networkData["extattrs"].items():
                if k not in extattrs:
                    extattrs[k] = v

            if extattrs:
                data["extattrs"] = extattrs

            return data
        except Exception as e:
            raise e



    def __getAccountNetworks(self, accountId: str = "", accountName: str = ""):
        try:
            if accountId:
                return Network.listData(self.assetId, {
                    "*Account ID": accountId
                })
            if accountName:
                return Network.listData(self.assetId, {
                    "*Account Name": accountName
                })

        except Exception as e:
            raise e



    def __historyLog(self, network, status) -> int:
        historyId = 0

        try:
            data = {
                "log": {
                    "username": self.user["username"],
                    "action": "modify",
                    "asset_id": self.assetId,
                    "status": status
                },
                "log_object": {
                    "type": "network",
                    "address": network.split('/')[0],
                    "network": network,
                    "mask": network.split('/')[1],
                    "gateway": ""
                }
            }
            historyId = History.add(data)

            return historyId
        except Exception:
            pass
