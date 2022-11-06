from django.db import connection

from infoblox.helpers.Log import Log
from infoblox.helpers.Exception import CustomException
from infoblox.helpers.Database import Database as DBHelper


class Permission:

    # IdentityGroupRoleNetwork

    # Table: group_role_network

    #   `id` int(255) NOT NULL AUTO_INCREMENT,
    #   `id_group` int(11) NOT NULL KEY,
    #   `id_role` int(11) NOT NULL KEY,
    #   `id_network` int(11) NOT NULL KEY
    #
    #   PRIMARY KEY (`id_group`,`id_role`,`id_network`)
    #
    #   CONSTRAINT `grp_group` FOREIGN KEY (`id_group`) REFERENCES `identity_group` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    #   CONSTRAINT `grp_network` FOREIGN KEY (`id_network`) REFERENCES `network` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    #   CONSTRAINT `grp_role` FOREIGN KEY (`id_role`) REFERENCES `role` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def modify(identityGroupId: int, roleId: int, networkId: int, permissionId: int) -> None:
        c = connection.cursor()

        if permissionId:
            try:
                c.execute("UPDATE group_role_network SET id_group=%s, id_role=%s, id_network=%s WHERE id=%s", [
                    identityGroupId, # AD or RADIUS group.
                    roleId,
                    networkId,
                    permissionId
                ])

            except Exception as e:
                raise CustomException(status=400, payload={"database": e.__str__()})
            finally:
                c.close()



    @staticmethod
    def delete(permissionId) -> None:
        c = connection.cursor()

        try:
            c.execute("DELETE FROM group_role_network WHERE id = %s", [
                permissionId
            ])

        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def countUserPermissions(groups: list, action: str, assetId: int = 0, networkName: str = "") -> int:
        if action and groups:
            args = groups.copy()
            assetWhere = ""
            networkWhere = ""
            c = connection.cursor()

            # Superadmin's group.
            for gr in groups:
                if gr.lower() == "automation.local":
                    return True

            try:
                # Build the first half of the where condition of the query.
                # Obtain: WHERE (identity_group.identity_group_identifier = %s || identity_group.identity_group_identifier = %s || identity_group.identity_group_identifier = %s || ....)
                groupWhere = ''
                for g in groups:
                    groupWhere += 'identity_group.identity_group_identifier = %s || '

                # Put all the args of the query in a list.
                if assetId:
                    args.append(assetId)
                    assetWhere = "AND `network`.id_asset = %s "

                if networkName:
                    args.append(networkName)
                    networkWhere = "AND (`network`.`network` = %s OR `network`.`network` = 'any') " # if "any" appears in the query results so far -> pass.

                args.append(action)

                c.execute("SELECT COUNT(*) AS count "
                    "FROM identity_group "
                    "LEFT JOIN group_role_network ON group_role_network.id_group = identity_group.id "
                    "LEFT JOIN role ON role.id = group_role_network.id_role "
                    "LEFT JOIN role_privilege ON role_privilege.id_role = role.id "
                    "LEFT JOIN `network` ON `network`.id = group_role_network.id_network "                      
                    "LEFT JOIN privilege ON privilege.id = role_privilege.id_privilege "
                    "WHERE ("+groupWhere[:-4]+") " +
                    assetWhere +
                    networkWhere +
                    "AND privilege.privilege = %s ",
                        args
                )

                return DBHelper.asDict(c)[0]["count"]
            except Exception as e:
                raise CustomException(status=400, payload={"database": e.__str__()})
            finally:
                c.close()

        return False



    @staticmethod
    def list() -> list:
        c = connection.cursor()

        try:
            c.execute(
                "SELECT "
                    "group_role_network.id, "
                    "identity_group.name AS identity_group_name, "
                    "identity_group.identity_group_identifier AS identity_group_identifier, "
                    "role.role AS role, "
                    "`network`.id_asset AS network_asset, "
                    "`network`.`network` AS network_name "
                "FROM identity_group "
                "LEFT JOIN group_role_network ON group_role_network.id_group = identity_group.id "
                "LEFT JOIN role ON role.id = group_role_network.id_role "
                "LEFT JOIN `network` ON `network`.id = group_role_network.id_network "
                "WHERE role.role IS NOT NULL")
            l = DBHelper.asDict(c)

            for el in l:
                el["network"] = {
                    "asset_id": el["network_asset"],
                    "name": el["network_name"]
                }

                del(el["network_asset"])
                del(el["network_name"])

            return l
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def add(identityGroupId: int, roleId: int, networkId: int) -> None:
        c = connection.cursor()

        try:
            c.execute("INSERT INTO group_role_network (id_group, id_role, id_network) VALUES (%s, %s, %s)", [
                identityGroupId, # AD or RADIUS group.
                roleId,
                networkId
            ])

        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()
