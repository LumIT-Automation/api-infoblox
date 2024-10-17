from django.db import connection

from infoblox.helpers.Exception import CustomException
from infoblox.helpers.Database import Database as DBHelper


class Permission:
    def __init__(self, permissionId: int = 0, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id: int = int(permissionId)
        self.permissionTable = "group_role_network"
        self.privilegesList = "role"

        # Tables: group_role_network, identity_group, role, network.



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def get(self) -> dict:
        c = connection.cursor()

        try:
            c.execute(f"SELECT * FROM {self.permissionTable} WHERE id=%s", [self.id])

            return DBHelper.asDict(c)[0]
        except IndexError:
            raise CustomException(status=404, payload={"database": "Non existent permission"})
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    def modify(self, identityGroupId: int, privilegesListId: int, networkId: int) -> None:
        c = connection.cursor()

        try:
            c.execute(f"UPDATE {self.permissionTable} SET id_group=%s, id_{self.privilegesList}=%s, id_network=%s WHERE id=%s", [
                identityGroupId, # AD or RADIUS group.
                privilegesListId,
                networkId,
                self.id
            ])
        except Exception as e:
            if e.__class__.__name__ == "IntegrityError" \
                    and e.args and e.args[0] and e.args[0] == 1062:
                        raise CustomException(status=400, payload={"database": "Duplicated entry"})
            else:
                raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    def delete(self) -> None:
        c = connection.cursor()

        try:
            c.execute(f"DELETE FROM {self.permissionTable} WHERE id = %s", [self.id])
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    """
    SELECT group_role_network.id, 
        identity_group.name AS identity_group_name, 
        identity_group.identity_group_identifier AS identity_group_identifier, 
        role.role AS role, 
        `network`.id_asset AS network_asset, 
        `network`.`network` AS network_name 
    FROM identity_group 
    LEFT JOIN group_role_network ON group_role_network.id_group = identity_group.id 
    LEFT JOIN role ON role.id = group_role_network.id_role 
    LEFT JOIN `network` ON `network`.id = group_role_network.id_network 
    WHERE role.role IS NOT NULL
    """
    def list(self) -> list:
        c = connection.cursor()

        try:
            c.execute(
                f"SELECT {self.permissionTable}.id, "
                    "identity_group.name AS identity_group_name, "
                    "identity_group.identity_group_identifier AS identity_group_identifier, "
                    f"{self.privilegesList}.{self.privilegesList}, " 
                    "`network`.id_asset AS network_asset, "
                    "`network`.`network` AS network_name "
                "FROM identity_group "
                f"LEFT JOIN {self.permissionTable} ON {self.permissionTable}.id_group = identity_group.id "
                f"LEFT JOIN {self.privilegesList} ON {self.privilegesList}.id = {self.permissionTable}.id_{self.privilegesList} "
                f"LEFT JOIN `network` ON `network`.id = {self.permissionTable}.id_network "
                f"WHERE {self.privilegesList}.{self.privilegesList} IS NOT NULL")
            l = DBHelper.asDict(c)

            for el in l:
                el["network"] = {
                    "id_asset": el["network_asset"],
                    "name": el["network_name"]
                }

                del(el["network_asset"])
                del(el["network_name"])

            return l
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    def add(self, identityGroupId: int, privilegesListId: int, networkId: int) -> None:
        c = connection.cursor()

        try:
            c.execute(f"INSERT INTO {self.permissionTable} (id_group, id_{self.privilegesList}, id_network) VALUES (%s, %s, %s)", [
                identityGroupId, # AD or RADIUS group.
                privilegesListId,
                networkId
            ])
        except Exception as e:
            if e.__class__.__name__ == "IntegrityError" \
                    and e.args and e.args[0] and e.args[0] == 1062:
                        raise CustomException(status=400, payload={"database": "Duplicated entry"})
            else:
                raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()
