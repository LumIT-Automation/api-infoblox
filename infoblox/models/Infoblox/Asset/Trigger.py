from infoblox.models.Infoblox.Asset.repository.Trigger import Trigger as Repository

from infoblox.helpers.Misc import Misc


class Trigger:
    def __init__(self, id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id = int(id)
        self.trigger_name = ""
        self.src_asset_id = ""
        self.dst_asset_id = ""
        self.trigger_condition = ""
        self.enabled = ""

        self.__load()



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def modify(self, enabled: bool) -> None:
        try:
            Repository.modify(self.id, enabled)

            for k, v in Misc.toDict(enabled).items():
                setattr(self, k, v)
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
    def list() -> list:
        try:
            return Repository.list()
        except Exception as e:
            raise e



    @staticmethod
    def add(data: dict) -> int:
        try:
            return Repository.add(data)
        except Exception as e:
            raise e



    @staticmethod
    def condition(triggerName, srcAssetId) -> list:
        try:
            return Repository.condition(triggerName=triggerName, srcAssetId=srcAssetId)
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
