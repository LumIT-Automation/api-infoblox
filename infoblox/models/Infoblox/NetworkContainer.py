from typing import Dict

from infoblox.models.Infoblox.connectors.NetworkContainer import NetworkContainer as Connector


class NetworkContainer:
    def __init__(self, assetId: int, container: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.asset_id: int = int(assetId)

        self._ref: str = ""
        self.network: str = ""
        self.network_container: str = container
        self.extattrs: Dict[str, Dict[str, str]] = {
            "Gateway": { "value": "" },
            "Mask": { "value": "" },
            "Object Type": { "value": "" },
            "Real Network": { "value": "" },
        }



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def get(self, filter: dict = None) -> dict:
        filter = {} if filter is None else filter

        try:
            o = Connector.get(self.asset_id, self.network_container, filter)

            if o:
                o[0]["asset_id"] = self.asset_id

            return o
        except Exception as e:
            raise e



    def innerNetworks(self, filter: dict = None) -> dict:
        filter = {} if filter is None else filter

        try:
            return Connector.networks(self.asset_id, self.network_container, filter)
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
