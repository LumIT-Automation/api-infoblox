from typing import Dict

from infoblox.helpers.Exception import CustomException

from infoblox.models.Infoblox.connectors.Vlan import Vlan as Connector


Value: Dict[str, str] = {"value": ""}

class Vlan:
    def __init__(self, assetId: int, id: int = 0, name: str = "", *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.asset_id: int = int(assetId)
        self._ref: str = ""
        self.id: int = int(id)
        self.name: str = str(name)
        self.reserved: bool = False
        self.status: str = ""
        self.extattrs: Dict[str, Dict[str, str]] = {}
        self.parent: Dict[str, str] = {}
        self.assigned_to: list = []

        self.__load()



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
    def listData(assetId: int, filters: dict = None) -> dict:
        filters = filters or {}

        try:
            o = Connector.list(assetId, filters)
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
            data = Connector.get(self.asset_id, self.id, silent=True)
            if data:
                for k, v in data.items():
                    setattr(self, k, v)
            else:
                raise CustomException(status=404)
        except Exception as e:
            raise e
