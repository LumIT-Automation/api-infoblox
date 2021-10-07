from infoblox.models.Permission.Role import Role
from infoblox.models.Permission.Network import Network

from django.db import connection
from django.conf import settings

from infoblox.helpers.Log import Log
from infoblox.helpers.Exception import CustomException
from infoblox.helpers.Database import Database as DBHelper



class Permission:
    def __init__(self, permissionId: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.permissionId = permissionId



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def modify(self, identityGroupId: int, role: str, assetId: int, networkName: str) -> None:
        c = connection.cursor()

        if self.permissionId:
            try:
                if role == "admin":
                    networkName = "any" # if admin: "any" is the only valid choice (on selected assetId).

                # RoleId.
                r = Role(roleName=role)
                roleId = r.info()["id"]

                # Network id. If network does not exist, create it.
                p = Network(assetId=assetId, networkName=networkName)
                if p.exists():
                    networkId = p.info()["id"]
                else:
                    networkId = p.add(assetId, networkName)

                c.execute("UPDATE group_role_network SET id_group=%s, id_role=%s, id_network=%s WHERE id=%s", [
                    identityGroupId, # AD or RADIUS group.
                    roleId,
                    networkId,
                    self.permissionId
                ])

            except Exception as e:
                raise CustomException(status=400, payload={"database": {"message": e.__str__()}})
            finally:
                c.close()



    def delete(self) -> None:
        c = connection.cursor()

        if self.permissionId:
            try:
                c.execute("DELETE FROM group_role_network WHERE id = %s", [
                    self.permissionId
                ])

            except Exception as e:
                raise CustomException(status=400, payload={"database": {"message": e.__str__()}})
            finally:
                c.close()



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def hasUserPermission(groups: list, action: str, assetId: int = 0, networkName: str = "") -> bool:
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
                q = DBHelper.asDict(c)[0]["count"]
                if q:
                    return bool(q)

            except Exception as e:
                raise CustomException(status=400, payload={"database": {"message": e.__str__()}})
            finally:
                c.close()

        return False



    @staticmethod
    def list() -> dict:
        c = connection.cursor()

        try:
            c.execute("SELECT "
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

            return {
                "items": l
            }

        except Exception as e:
            raise CustomException(status=400, payload={"database": {"message": e.__str__()}})
        finally:
            c.close()



    @staticmethod
    def add(identityGroupId: int, role: str, assetId: int, networkName: str) -> None:
        c = connection.cursor()

        try:
            if role == "admin":
                networkName = "any" # if admin: "any" is the only valid choice (on selected assetId).

            # RoleId.
            r = Role(roleName=role)
            roleId = r.info()["id"]

            # Network id. If network does not exist, create it.
            p = Network(assetId=assetId, networkName=networkName)
            if p.exists():
                networkId = p.info()["id"]
            else:
                networkId = p.add(assetId, networkName)

            c.execute("INSERT INTO group_role_network (id_group, id_role, id_network) VALUES (%s, %s, %s)", [
                identityGroupId, # AD or RADIUS group.
                roleId,
                networkId
            ])

        except Exception as e:
            raise CustomException(status=400, payload={"database": {"message": e.__str__()}})
        finally:
            c.close()



    @staticmethod
    def cleanup(identityGroupId: int) -> None:
        c = connection.cursor()

        try:
            c.execute("DELETE FROM group_role_network WHERE id_group = %s", [
                identityGroupId,
            ])

        except Exception as e:
            raise CustomException(status=400, payload={"database": {"message": e.__str__()}})
        finally:
            c.close()
