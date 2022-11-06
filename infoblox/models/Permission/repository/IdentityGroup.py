from django.db import connection

from django.utils.html import strip_tags
from django.db import transaction

from infoblox.helpers.Log import Log
from infoblox.helpers.Exception import CustomException
from infoblox.helpers.Database import Database as DBHelper


class IdentityGroup:

    # Table: identity_group

    #   `id` int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    #   `name` varchar(64) NOT NULL KEY,
    #   `identity_group_identifier` varchar(255) DEFAULT NULL UNIQUE KEY



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def get(identityGroupIdentifier: str) -> dict:
        c = connection.cursor()

        try:
            c.execute("SELECT * FROM identity_group WHERE identity_group_identifier = %s", [
                identityGroupIdentifier
            ])

            return DBHelper.asDict(c)[0]
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def modify(identityGroupIdentifier: str, data: dict) -> None:
        sql = ""
        values = []
        c = connection.cursor()

        if IdentityGroup.__exists(identityGroupIdentifier):
            # %s placeholders and values for SET.
            for k, v in data.items():
                sql += k + "=%s,"
                values.append(strip_tags(v))  # no HTML allowed.

            # Condition for WHERE.
            values.append(identityGroupIdentifier)

            try:
                c.execute("UPDATE identity_group SET "+sql[:-1]+" WHERE identity_group_identifier = %s",
                    values
                )
            except Exception as e:
                raise CustomException(status=400, payload={"database": e.__str__()})
            finally:
                c.close()

        else:
            raise CustomException(status=404, payload={"database": "Non existent identity group"})



    @staticmethod
    def delete(identityGroupIdentifier: str) -> None:
        c = connection.cursor()

        if IdentityGroup.__exists(identityGroupIdentifier):
            try:
                c.execute("DELETE FROM identity_group WHERE identity_group_identifier = %s", [
                    identityGroupIdentifier
                ])

                # Foreign keys' on cascade rules will clean the linked items on db.
            except Exception as e:
                raise CustomException(status=400, payload={"database": e.__str__()})
            finally:
                c.close()

        else:
            raise CustomException(status=404, payload={"database": "Non existent identity group"})



    @staticmethod
    def list() -> list:
        # List identity groups with related information regarding the associated roles on networks
        # and optionally detailed privileges' descriptions.
        c = connection.cursor()

        try:
            c.execute("SELECT "
                "identity_group.*, " 

                "IFNULL(GROUP_CONCAT( "
                    "DISTINCT CONCAT(role.role,'::',CONCAT(network.id_asset,'::',network.network)) " 
                    "ORDER BY role.id "
                    "SEPARATOR ',' "
                "), '') AS roles_network, "

                "IFNULL(GROUP_CONCAT( "
                    "DISTINCT CONCAT(privilege.privilege,'::',network.id_asset,'::',network.network,'::',privilege.privilege_type) " 
                    "ORDER BY privilege.id "
                    "SEPARATOR ',' "
                "), '') AS privileges_network "

                "FROM identity_group "
                "LEFT JOIN group_role_network ON group_role_network.id_group = identity_group.id "
                "LEFT JOIN role ON role.id = group_role_network.id_role "
                "LEFT JOIN `network` ON `network`.id = group_role_network.id_network "
                "LEFT JOIN role_privilege ON role_privilege.id_role = role.id "
                "LEFT JOIN privilege ON privilege.id = role_privilege.id_privilege "
                "GROUP BY identity_group.id"
            )

            # Simple start query:
            # SELECT identity_group.*, role.role, privilege.privilege, `network`.network
            # FROM identity_group
            # LEFT JOIN group_role_network ON group_role_network.id_group = identity_group.id
            # LEFT JOIN role ON role.id = group_role_network.id_role
            # LEFT JOIN `network` ON `network`.id = group_role_network.id_network
            # LEFT JOIN role_privilege ON role_privilege.id_role = role.id
            # LEFT JOIN privilege ON privilege.id = role_privilege.id_privilege
            # GROUP BY identity_group.id

            return DBHelper.asDict(c)
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def add(data: dict) -> int:
        s = ""
        keys = "("
        values = []

        c = connection.cursor()

        # Build SQL query according to dict fields (only whitelisted fields pass).
        for k, v in data.items():
            s += "%s,"
            keys += k + ","
            values.append(strip_tags(v))  # no HTML allowed.

        keys = keys[:-1]+")"

        try:
            with transaction.atomic():
                c.execute("INSERT INTO identity_group "+keys+" VALUES ("+s[:-1]+")",
                    values
                )

                return c.lastrowid
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    ####################################################################################################################
    # Private static methods
    ####################################################################################################################

    @staticmethod
    def __exists(identityGroupIdentifier: str) -> int:
        c = connection.cursor()
        try:
            c.execute("SELECT COUNT(*) AS c FROM identity_group WHERE identity_group_identifier = %s", [
                identityGroupIdentifier
            ])
            o = DBHelper.asDict(c)

            return int(o[0]['c'])
        except Exception:
            return 0
        finally:
            c.close()
