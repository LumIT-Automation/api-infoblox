from typing import Dict

from infoblox.helpers.Exception import CustomException

from infoblox.models.Infoblox.connectors.Network import Network as Connector


Value: Dict[str, str] = {"value": ""}

class Network:
    def __init__(self, assetId: int, network: str, filter: dict = None, *args, **kwargs):
        filter = filter or {}

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

        self.__load(filter=filter)



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def ipv4sData(self, maxResults: int = 0, fromIp: str = "", toIp: str = "") -> dict:
        try:
            # Data list.
            # Not using composition for possible huge dataset.
            return Connector.addresses(self.asset_id, self.network, maxResults, fromIp, toIp)
        except Exception as e:
            raise e



    def repr(self) -> dict:
        try:
            return vars(self)
        except Exception as e:
            raise e




    def modify(self, data: dict) -> dict:
        try:
            data["network"] = self.network
            return Connector.modify(assetId=self.asset_id, _ref=self._ref, data=data, silent=False)
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def listData(assetId: int, filters: dict = None) -> list:
        filters = filters or {}

        try:
            o = Connector.list(assetId, filters)
            for i, v in enumerate(o):
                o[i]["asset_id"] = assetId # add assetId information.
        except Exception as e:
            raise e

        return o



    @staticmethod
    def add(assetId: int, data) -> dict:
        try:
            return Connector.add(assetId, data)
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __load(self, filter: dict) -> None:
        try:
            data = Connector.get(self.asset_id, self.network, filter=filter)
            if data:
                for k, v in data.items():
                    setattr(self, k, v)
            else:
                raise CustomException(status=404)
        except Exception as e:
            raise e
