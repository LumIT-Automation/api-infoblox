from infoblox.models.History.repository.History import History as Repository
from infoblox.helpers.Log import Log


class History:
    def __init__(self, id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id = id
        self.username = ""
        self.action = ""
        self.asset_id = 0
        self.config_object_type = ""
        self.config_object = ""
        self.status = ""
        self.date = ""



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(username: str, allUsersHistory: bool) -> list:
        try:
            return Repository.list(username, allUsersHistory)
        except Exception as e:
            raise e



    @staticmethod
    def addByType(data: dict, logType: str) -> int:
        if logType in ["object", "log"]:
            table = "log"
            if logType == "object":
                table = "log_object"

            try:
                return Repository.add(data, table)
            except Exception as e:
                raise e
        else:
            return 0



    @staticmethod
    def add(data: dict) -> int:
        try:
            if data["log_object"]:
                data["log"]["object_id"] = Repository.add(data["log_object"], "log_object")
            return Repository.add(data["log"], "log")
        except Exception as e:
            raise e

