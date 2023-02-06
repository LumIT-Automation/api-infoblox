from typing import Dict

from infoblox.helpers.Exception import CustomException

from infoblox.models.Infoblox.connectors.VlanView import VlanView as Connector


class VlanView:
    def __init__(self, assetId: int, _ref: str, id: int, filter: dict = None, *args, **kwargs):
        filter = filter or {}

        super().__init__(*args, **kwargs)

        self.asset_id: int = int(assetId)
        self._ref: str = _ref
        self.id: int = id

        self.__load(filter=filter)



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def info(self, silent = True) -> dict:
        try:
            return Connector.get(_ref=self._ref, id=self.id, silent=silent)
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
    def listData(assetId: int, filters: dict = None) -> dict:
        filters = filters or {}

        try:
            o = Connector.list(assetId, filters)
            for i, v in enumerate(o):
                o[i]["asset_id"] = assetId # add assetId information.
        except Exception as e:
            raise e

        return o


    """
    @staticmethod
    def add(assetId: int, data) -> dict:
        try:
            return Connector.add(assetId, data)
        except Exception as e:
            raise e
    """


    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __load(self) -> None:
        try:
            data = Connector.get(self.asset_id, self._ref, self.id, silent=True)
            if data:
                for k, v in data.items():
                    setattr(self, k, v)
            else:
                raise CustomException(status=404)
        except Exception as e:
            raise e
