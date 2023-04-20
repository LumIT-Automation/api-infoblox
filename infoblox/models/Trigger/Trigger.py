from typing import List, Dict, Union

from infoblox.models.Trigger.repository.Trigger import Trigger as Repository

from infoblox.helpers.Misc import Misc


Condition: Dict[str, Union[str, int]] = {
    "condition_id": 0,
    "src_asset_id": 0,
    "condition": ""
}

class Trigger:
    def __init__(self, id: int, loadConditions: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id: int = int(id)
        self.name: str = ""
        self.dst_asset_id: str = ""
        self.action: str = ""
        self.enabled: bool = False

        self.conditions: List[Condition] = []

        self.__load(loadConditions=loadConditions)



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def repr(self) -> dict:
        try:
            return vars(self)
        except Exception as e:
            raise e



    def modify(self, data: dict) -> None:
        try:
            Repository.modify(self.id, data)

            for k, v in Misc.toDict(data).items():
                setattr(self, k, v)
        except Exception as e:
            raise e



    def delete(self) -> None:
        try:
            Repository.delete(self.id)
            del self
        except Exception as e:
            raise e



    def addCondition(self, data: dict) -> None:
        try:
            Repository.addCondition(triggerId=self.id, srcAssetId=data["src_asset_id"], condition=data["condition"])
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def dataList(filter: dict = None, loadConditions: bool = False) -> list:
        filter = filter or {}

        return Repository.list(filter=filter, loadConditions=loadConditions)



    @staticmethod
    def add(data: dict) -> int:
        try:
            return Repository.add(data)
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __load(self, loadConditions: bool = False) -> None:
        try:
            for k, v in Repository.get(self.id, loadConditions).items():
                setattr(self, k, v)

            if not loadConditions:
                del self.conditions
        except Exception as e:
            raise e
