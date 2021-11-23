from infoblox.repository.History import History as Repository


class History:

    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(username: str, allUsersHistory: bool) -> dict:
        try:
            return dict({
                "data": {
                    "items": Repository.list(username, allUsersHistory)
                }
            })
        except Exception as e:
            raise e



    @staticmethod
    def add(data: dict, logType: str) -> int:
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
