from infoblox.repository.Role import Role as Repository

from infoblox.helpers.Log import Log


class Role:
    def __init__(self, roleId: int = 0, roleName: str = "", *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id = roleId
        self.role = roleName
        self.description = ""



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def info(self) -> dict:
        try:
            return Repository.get(roleName=self.role)
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
    def listWithPrivileges() -> list:
        j = 0

        try:
            items = Repository.list(True)

            for ln in items:
                if "privileges" in items[j]:
                    if "," in ln["privileges"]:
                        items[j]["privileges"] = ln["privileges"].split(",")
                    else:
                        if ln["privileges"]:
                            items[j]["privileges"] = [ ln["privileges"] ]
                j = j+1

            return items
        except Exception as e:
            raise e
