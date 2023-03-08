import json
from typing import Dict
from django.core.cache import cache

from infoblox.helpers.Exception import CustomException

from infoblox.models.Infoblox.Network import Network
from infoblox.models.Infoblox.connectors.NetworkContainer import NetworkContainer as Connector


Value: Dict[str, str] = {"value": ""}

class NetworkContainer:
    def __init__(self, assetId: int, container: str, filter: dict = None, *args, **kwargs):
        filter = filter or {}

        super().__init__(*args, **kwargs)

        self.asset_id: int = int(assetId)
        self._ref: str = ""
        self.network: str = ""
        self.network_container: str = container
        self.network_view: str = ""
        self.extattrs: Dict[str, Dict[str, str]] = {
            "Gateway": Value,
            "Mask": Value,
            "Object Type": Value,
            "Real Network": Value,
        }

        self.__load(filter=filter)



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def networksData(self, filter: dict = None) -> dict:
        filter = filter or {}

        try:
            # Data list.
            # Not using composition because of filtering capabilities.
            return Connector.networks(self.asset_id, self.network, filter)
        except Exception as e:
            raise e



    def addNextAvailableNetwork(self, subnetMaskCidr: int, data: dict) -> dict:
        try:
            # Next available network in this container.
            data["network"] = "func:nextavailablenetwork:" + self.network + ", " + str(subnetMaskCidr)

            return Network.add(assetId=self.asset_id, data=data)
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def listData(assetId: int, filters: dict = None, silent: bool = False) -> list:
        filters = filters or {}

        try:
            return Connector.list(assetId, filters, silent)
        except Exception as e:
            raise e



    @staticmethod
    def genealogy(network: str, networkContainerList: list) -> list:
        try:
            networkContainer = ""
            f = list()
            struct = dict()

            try:
                def __fathers(son: str):
                    f.append(son)
                    if son in struct:
                        __fathers(struct[son])

                # Pre-process structure.
                for container in networkContainerList:
                    struct[container["network"]] = container["network_container"]

                    # Get container of given network.
                    if container["network"] == network:
                        networkContainer = container["network_container"]

                __fathers(networkContainer)
            except Exception as e:
                raise e

            return f
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __load(self, filter: dict) -> None:
        try:
            data = Connector.get(self.asset_id, self.network_container, filter)
            if data:
                for k, v in data[0].items(): # a list is returned for one only object.
                    setattr(self, k, v)
            else:
                raise CustomException(status=404)
        except Exception as e:
            raise e
