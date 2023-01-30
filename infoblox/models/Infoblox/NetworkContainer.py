from typing import Dict

from infoblox.helpers.Exception import CustomException

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
            # Data list, not using composition.
            return Connector.networks(self.asset_id, self.network, filter)
        except Exception as e:
            raise e



    def addNextAvailableNetwork(self, data: dict) -> dict:
        data = {
            "network": "func:nextavailablenetwork:" + self.network_container + ", " + data["subnetMask"],
        }

        try:
            return Connector.addNetwork(self.asset_id, data)
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def listData(assetId: int) -> dict:
        try:
            return Connector.list(assetId)
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
