from typing import Dict

from infoblox.models.Infoblox.connectors.Network import Network as Connector


Value: Dict[str, str] = {"value": ""}

class Network:
    def __init__(self, assetId: int, network: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.asset_id: int = int(assetId)
        self._ref: str = ""
        self.network: str = network
        self.network_container: str = ""
        self.network_view: str = ""
        self.extattrs: Dict[str, Dict[str, str]] = {
            "Gateway": Value,
            "Mask": Value,
            "Object Type": Value,
            "Real Network": Value,
        }

        self.__load()



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def info(self, filter: dict = None) -> dict:
        filter = {} if filter is None else filter

        try:
            data = Connector.get(self.asset_id, self.network, filter)
            if data:
                data["asset_id"] = self.asset_id
        except Exception as e:
            raise e

        return data



    def ipv4s(self, maxResults: int = 0, fromIp: str = "", toIp: str = "") -> dict:
        try:
            # Quick list, do not using composition.
            return Connector.addresses(self.asset_id, self.network, maxResults, fromIp, toIp)
        except Exception as e:
            raise e



    def repr(self) -> dict:
        try:
            return vars(self)
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(assetId: int) -> dict:
        try:
            o = Connector.list(assetId)

            for i, v in enumerate(o):
                o[i]["asset_id"] = assetId # add assetId information.
        except Exception as e:
            raise e

        return o



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __load(self) -> None:
        try:
            data = Connector.get(self.asset_id, self.network)
            for k, v in data.items():
                setattr(self, k, v)
        except Exception as e:
            raise e
