from infoblox.models.Infoblox.Asset.repository.Trigger import Trigger as Repository

from infoblox.helpers.Log import Log


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
    def runConditionList(triggerName: str, srcAssetId: int, dstAssetId: int = None) -> list:

        filter = {
            "trigger_name": triggerName,
            "src_asset_id": srcAssetId
        }
        if dstAssetId:
            filter["dst_asset_id"] = dstAssetId

        try:
            l = Repository.list(filter=filter)
            Log.log(l, 'LLLLLLLLLLLLLLLLLLLLLLLLLLLL')
            return l
            #return Repository.runConditionList(triggerName=triggerName, srcAssetId=srcAssetId, dstAssetId=dstAssetId)
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
