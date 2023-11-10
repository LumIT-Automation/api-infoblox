from typing import List, Dict

from django.conf import settings

from infoblox.usecases.impl.CloudNetworkModifyAccount import CloudNetworkModifyAccount
from infoblox.models.Infoblox.Network import Network
from infoblox.models.History.History import History
from infoblox.helpers.Exception import CustomException


class CloudNetworkCustomModifyAccount1(CloudNetworkModifyAccount):
    def __init__(self, assetId: int, accountId: str, user: dict, *args, **kwargs):
        super().__init__(assetId, accountId, user, *args, **kwargs)

        self.assetId = assetId
        self.accountId = accountId
        self.user = user
        self.oldAccountIdNetworks = self.__getAccountCloudNetworks(accountId=self.accountId) # network to which the Account ID, Account Name, Reference extattrs should be changed.



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def modifyAccount(self, data: dict, *args, **kwargs) -> List[Dict]:
        l= list()

        try:
            self.__checkNetworkCountLimits(extrattrs=data, oldAccountIdNetworks=self.oldAccountIdNetworks)

            for net in self.oldAccountIdNetworks:
                formattedData = self.__formatData(net["extattrs"], data)
                l.append(Network(assetId=self.assetId, network=net["network"]).modify(formattedData))
                hid = self.__historyLog(net["network"], 'modified')

            return l
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __getAccountCloudNetworks(self, accountId: str = "", accountName: str = "") -> List[Dict]:
        try:
            if accountId:
                return Network.listData(self.assetId, {
                    "*Account ID": accountId,
                    "*Environment": "Cloud"
                })
            if accountName:
                return Network.listData(self.assetId, {
                    "*Account Name": accountName,
                    "*Environment": "Cloud"
                })

        except Exception as e:
            raise e



    def __formatData(self, extattrs: dict, data: dict) -> dict:
        try:
            for key, val in extattrs.items():
                if key in data:
                    extattrs[key] = data[key]

            return {
                "extattrs": extattrs
            }
        except Exception as e:
            raise e



    def __checkNetworkCountLimits(self, extrattrs: dict, oldAccountIdNetworks: list):
        totalNetworks = []

        try:
            newAccountIdNetworks = self.__getAccountCloudNetworks(accountId=extrattrs.get("Account ID", {}).get("value", ""))

            if newAccountIdNetworks:
                for net in newAccountIdNetworks: # check if the Account ID was already used with a different Account Name or Reference.
                    if net.get("extattrs", {}).get("Account Name", {}).get("value", "") != extrattrs.get("Account Name", {}).get("value", ""):
                        raise CustomException(
                            status=400,
                            payload={
                                "Infoblox": "A network with the Account ID " + extrattrs.get("Account ID", {}).get("value", "") +
                                            " but different Account Name exists: " + net["network"]
                            }
                        )
                    if net.get("extattrs", {}).get("Reference", {}).get("value", "") != extrattrs.get("Reference", {}).get("value", ""):
                        raise CustomException(
                            status=400,
                            payload={
                                "Infoblox": "A network with the Account ID " + extrattrs.get("Account ID", {}).get("value", "") +
                                            " but different Reference exists: " + net["network"]
                            }
                        )

                totalNetworks.extend(newAccountIdNetworks) # the total number of networks for the changed account must respect the configured limits after the change.

            newAccountNameNetworks = self.__getAccountCloudNetworks(accountName=extrattrs.get("Account Name", {}).get("value", ""))
            if newAccountNameNetworks:
                for net in newAccountNameNetworks: # also check if the Account Name was already used with a different Account ID.
                    if net.get("extattrs", {}).get("Account ID", {}).get("value", "") != extrattrs.get("Account ID", {}).get("value", ""):
                        raise CustomException(
                            status=400,
                            payload={
                                "Infoblox": "A network with the Account Name " + extrattrs.get("Account Name", {}).get("value", "") +
                                            " but different Account ID exists: " + net["network"]
                            }
                        )

            if totalNetworks:
                totalNetworks.extend(oldAccountIdNetworks)

                # CLOUD_MAX_ACCOUNT_REGION is the maximum number of regions for Account ID.
                if hasattr(settings, "CLOUD_MAX_ACCOUNT_REGION"):
                    if settings.CLOUD_MAX_ACCOUNT_REGION < len(set([net.get("extattrs", {}).get("City", {}).get("value", "") for net in totalNetworks])):
                        raise CustomException(
                            status=400,
                            payload={
                                "Infoblox": "Cannot change the account: others networks exists for this account and the maximum number of regions for account should not be exceed: " + str(settings.CLOUD_MAX_ACCOUNT_REGION)
                            }
                        )

                # CLOUD_MAX_ACCOUNT_REGION_NETS is the maximum number of networks for Account ID in a region.
                if hasattr(settings, "CLOUD_MAX_ACCOUNT_REGION_NETS"):
                    regionsNetworks = [ net.get("extattrs", {}).get("City", {}).get("value", "") for net in totalNetworks ]
                    for region in set(regionsNetworks):
                        if settings.CLOUD_MAX_ACCOUNT_REGION_NETS < regionsNetworks.count(region):
                            raise CustomException(
                                status=400,
                                payload={
                                    "Infoblox": "Cannot change the account: others networks exists for this account and the maximum number of networks for region for account should not be exceed: " + str(settings.CLOUD_MAX_ACCOUNT_REGION_NETS)}
                            )

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
