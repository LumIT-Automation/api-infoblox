from typing import List, Dict, Union

from infoblox.models.Infoblox.Asset.repository.Trigger import Trigger as Repository


Condition: Dict[str, Union[str, int]] = {
    "src_asset_id": 0,
    "condition": ""
}

class Trigger:
    def __init__(self, id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id: int = int(id)
        self.name: str = ""
        self.dst_asset_id: str = ""
        self.action: str = ""
        self.enabled: bool = False

        self.conditions: List[Condition] = []

        self.__load()



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def repr(self) -> dict:
        try:
            return vars(self)
        except Exception as e:
            raise e



    def enable(self, enabled: bool) -> None:
        try:
            Repository.enable(self.id, enabled)
            setattr(self, "enabled", enabled)
        except Exception as e:
            raise e



    def delete(self) -> None:
        try:
            Repository.delete(self.id)
            del self
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(filter: dict = None) -> list:
        filter = filter or {}

        return Repository.list(filter)



    @staticmethod
    def add(data: dict) -> int:
        try:
            return Repository.add(data)
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __load(self) -> None:
        try:
            for k, v in Repository.get(self.id).items():
                setattr(self, k, v)
        except Exception as e:
            raise e
