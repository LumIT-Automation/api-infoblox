import re
from django.conf import settings

from infoblox.usecases.impl.CloudNetworkExtAttr import CloudNetworkExtAttr
from infoblox.models.Infoblox.NetworkContainer import NetworkContainer
from infoblox.models.Infoblox.Network import Network

from infoblox.helpers.Exception import CustomException
from infoblox.helpers.Log import Log


class CloudNetworkCustomExtAttr1(CloudNetworkExtAttr):
    def __init__(self, assetId: int, user: dict, *args, **kwargs):
        super().__init__(assetId, user, *args, **kwargs)

        self.assetId: int = int(assetId)



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def listProviders(self, filter: dict = None, *args, **kwargs) -> set:
        filter = filter or {}

        try:
            if not filter:
                containers = self.__getContainers() # optimization.
                return set(
                    [ container.get("extattrs", {}).get("Country", {}).get("value", "")[6:] for container in containers ]
                )
            else:
                networks = self.__getNetworks(filter) # can't optimize.
                return set(
                    [ network.get("extattrs", {}).get("Country", {}).get("value", "")[6:] for network in networks ]
                )

        except Exception as e:
            raise e



    def listAccountsProviders(self, filter: dict = None, *args, **kwargs) -> set:
        filter = filter or {}

        try:
            networks = self.__getNetworks(filter)
            return set([
                network.get("extattrs", {}).get("Account ID", {}).get("value", "") + "::" + \
                network.get("extattrs", {}).get("Account Name", {}).get("value", "") + "::" + \
                network.get("extattrs", {}).get("Country", {}).get("value", "")[6:] \
                for network in networks
            ])
        except Exception as e:
            raise e

    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __getContainers(self, filter: dict = None) -> list:
        filter = filter or {}

        try:
            filter.update({
                "*Environment": "Cloud"
            })
            l = NetworkContainer.listData(self.assetId, filter)

            # The provider is the "Country" extattr and must have the "Cloud-" prefix.
            if not "Country" in filter or not filter["Country"]:
                return [container for container in l if container.get("extattrs", {}).get("Country", {}).get("value", "")[0:6] == "Cloud-"]
            else:
                return l
        except Exception as e:
            raise e



    def __getNetworks(self, filter: dict = None) -> list:
        filter = filter or {}

        try:
            filter.update({
                "*Environment": "Cloud"
            })
            l = Network.listData(self.assetId, filter)

            # The provider is the "Country" extattr and must have the "Cloud-" prefix.
            if not "Country" in filter or not filter["Country"]:
                return [network for network in l if network.get("extattrs", {}).get("Country", {}).get("value", "")[0:6] == "Cloud-"]
            else:
                return l
        except Exception as e:
            raise e
