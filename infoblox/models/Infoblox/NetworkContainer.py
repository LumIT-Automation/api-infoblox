from typing import Dict

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

    def networks(self, filter: dict = None) -> dict:
        filter = filter or {}

        try:
            # Data list.
            # Not using composition because of filtering capabilities.
            return Connector.networks(self.asset_id, self.network, filter)
        except Exception as e:
            raise e



    def addNextAvailableNetwork(self, subnetMask: str) -> dict:
        try:
            return Network.add(assetId=self.asset_id, data={
                "network": "func:nextavailablenetwork:" + self.network + ", " + str(subnetMask),
            })
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(assetId: int, filters: dict = None) -> dict:
        filters = filters or {}

        try:
            return Connector.list(assetId, filters)
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
