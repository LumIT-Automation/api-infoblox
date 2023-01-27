from typing import Dict

from infoblox.models.Infoblox.connectors.NetworkContainer import NetworkContainer as Connector


Value: Dict[str, str] = {"value": ""}

class NetworkContainer:
    def __init__(self, assetId: int, container: str, *args, **kwargs):
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



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def info(self, filter: dict = None) -> dict:
        filter = {} if filter is None else filter

        try:
            o = Connector.get(self.asset_id, self.network_container, filter)
            if o:
                o[0]["asset_id"] = self.asset_id
        except Exception as e:
            raise e

        return o[0]



    def networks(self, filter: dict = None) -> dict:
        filter = {} if filter is None else filter

        try:
            # Quick list, do not using composition.
            return Connector.networks(self.asset_id, self.network_container, filter)
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
    def list(assetId: int) -> dict:
        try:
            return Connector.list(assetId)
        except Exception as e:
            raise e
