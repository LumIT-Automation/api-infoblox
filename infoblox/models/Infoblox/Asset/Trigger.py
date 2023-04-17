from infoblox.models.Infoblox.Asset.repository.Trigger import Trigger as Repository

from infoblox.helpers.Log import Log


class Trigger:
    def __init__(self, id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id: int = int(id)
        self.trigger_name: str = ""
        self.src_asset_id: str = ""
        self.dst_asset_id: str = ""
        self.trigger_condition: str = ""
        self.enabled: bool = False

        self.__load()



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def modify(self, enabled: bool) -> None:
        try:
            Repository.modify(self.id, enabled)
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
            data = Repository.get(self.id)
            for k, v in data.items():
                setattr(self, k, v)
        except Exception as e:
            raise e
