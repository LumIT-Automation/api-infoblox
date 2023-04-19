from typing import Dict

from infoblox.helpers.Exception import CustomException

from infoblox.models.Infoblox.connectors.Range import Range as Connector


Value: Dict[str, str] = {"value": ""}

class Range:
    def __init__(self, assetId: int, start_addr: str, end_addr: str, filter: dict = None, *args, **kwargs):
        filter = filter or {}

        super().__init__(*args, **kwargs)

        self.asset_id: int = int(assetId)
        self._ref: str = ""
        self.network: str = ""
        self.network_view: str = ""
        self.start_addr: str = start_addr
        self.end_addr: str = end_addr
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

    def repr(self) -> dict:
        try:
            return vars(self)
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def listData(assetId: int, filters: dict = None, silent: bool = False) -> list:
        filters = filters or {}

        try:
            o = Connector.list(assetId, filters, silent)
            for i, v in enumerate(o):
                o[i]["asset_id"] = assetId # add assetId information.
        except Exception as e:
            raise e

        return o



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __load(self, filter: dict) -> None:
        try:
            data = Connector.get(self.asset_id, self.start_addr, self.end_addr, filter=filter)
            if data:
                for k, v in data.items():
                    setattr(self, k, v)
            else:
                raise CustomException(status=404)
        except Exception as e:
            raise e
