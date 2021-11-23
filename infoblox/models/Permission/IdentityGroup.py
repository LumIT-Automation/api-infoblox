from django.utils.html import strip_tags
from django.db import transaction

from infoblox.models.Permission.Permission import Permission

from infoblox.helpers.Log import Log
from infoblox.helpers.Exception import CustomException
from infoblox.helpers.Database import Database as DBHelper
from django.db import connection



class IdentityGroup:
    def __init__(self, identityGroupIdentifier: str,  *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.identityGroupIdentifier = identityGroupIdentifier



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def info(self) -> dict:
        c = connection.cursor()

        try:
            c.execute("SELECT * FROM identity_group WHERE identity_group_identifier = %s", [
                self.identityGroupIdentifier
            ])

            return DBHelper.asDict(c)[0]

        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    def modify(self, data: dict) -> None:
        sql = ""
        values = []
        roles = dict()

        c = connection.cursor()
        if self.__exists():
            for k, v in data.items():
                if any(exc in k for exc in (
                        "roles_network",
                )):
                    # "roles_network": {
                    #     "staff": [
                    #         {
                    #             "assetId": 1,
                    #             "network": "any"
                    #         }
                    #     ],
                    #  "nonExistent": []
                    # }

                    if isinstance(v, dict):
                        for rk, rv in v.items():
                            roles[rk] = rv
                else:
                    sql += k + "=%s,"
                    values.append(strip_tags(v))  # no HTML allowed.

            try:
                with transaction.atomic():
                    identityGroupId = self.info()["id"]

                    # Patch identity group.
                    c.execute("UPDATE identity_group SET "+sql[:-1]+" WHERE id = "+str(identityGroupId),
                        values
                    )

                    # Replace associated roles with roles[]' elements.
                    try:
                        # Empty existent roles.
                        Permission.cleanup(identityGroupId)
                    except Exception:
                        pass

                    for roleName, networksAssetsList in roles.items():
                        for networksAssetDict in networksAssetsList:
                            try:
                                Permission.add(identityGroupId, roleName, networksAssetDict["assetId"], networksAssetDict["network"])
                            except Exception:
                                pass

            except Exception as e:
                raise CustomException(status=400, payload={"database": e.__str__()})
            finally:
                c.close()

        else:
            raise CustomException(status=404, payload={"database": {"message": "Non existent identity group"}})



    def delete(self) -> None:
        c = connection.cursor()

        if self.__exists():
            try:
                c.execute("DELETE FROM identity_group WHERE identity_group_identifier = %s", [
                    self.identityGroupIdentifier
                ])

                # Foreign keys' on cascade rules will clean the linked items on db.

            except Exception as e:
                raise CustomException(status=400, payload={"database": e.__str__()})
            finally:
                c.close()

        else:
            raise CustomException(status=404, payload={"database": {"message": "Non existent identity group"}})



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(showPrivileges: bool = False) -> dict:
        # List identity groups with related information regarding the associated roles on networks
        # and optionally detailed privileges' descriptions.

        j = 0
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

            items = DBHelper.asDict(c)

            # "items": [
            # ...,
            # {
            #    "id": 2,
            #    "name": "groupStaff",
            #    "identity_group_identifier": "cn=groupStaff,cn=users,dc=lab,dc=local",
            #    "roles_network": "staff::1::Common",
            #    "privileges_network": "certificates_post::1::Common::1::0,poolMember_get::1::Common::0::0,poolMember_patch::1::Common::0::0,poolMembers_get::1::Common::0::0,poolMemberStats_get::1::Common::0::0,pools_get::1::Common::0::0,networks_get::1::Common::1::1"
            # },
            # ...
            # ]

            for ln in items:
                if "roles_network" in items[j]:
                    if "," in ln["roles_network"]:
                        items[j]["roles_network"] = ln["roles_network"].split(",") # "staff::1::network,...,readonly::2::network" string to list value: replace into original data structure.
                    else:
                        items[j]["roles_network"] = [ ln["roles_network"] ] # simple string to list.

                    # "roles_network": [
                    #    "admin::1::any",
                    #    "staff::1::PARTITION1",
                    #    "staff::2::PARTITION2"
                    # ]

                    rolesStructure = dict()
                    for rls in items[j]["roles_network"]:
                        if "::" in rls:
                            rlsList = rls.split("::")
                            if not str(rlsList[0]) in rolesStructure:
                                # Initialize list if not already done.
                                rolesStructure[rlsList[0]] = list()

                            rolesStructure[rlsList[0]].append({
                                "assetId": rlsList[1],
                                "network": rlsList[2]
                            })

                    items[j]["roles_network"] = rolesStructure

                    #"roles_network": {
                    #    "staff": [
                    #        {
                    #            "assetId": 1
                    #            "network": "PARTITION1"
                    #        },
                    #        {
                    #            "assetId": 2
                    #            "network": "PARTITION2"
                    #        },
                    #    ],
                    #    "admin": [
                    #        {
                    #            "assetId": 1
                    #            "network": "any"
                    #        },
                    #    ]
                    #}

                if showPrivileges:
                    # Add detailed privileges' descriptions to the output.
                    if "privileges_network" in items[j]:
                        if "," in ln["privileges_network"]:
                            items[j]["privileges_network"] = ln["privileges_network"].split(",")
                        else:
                            items[j]["privileges_network"] = [ ln["privileges_network"] ]

                        ppStructure = dict()
                        for pls in items[j]["privileges_network"]:
                            if "::" in pls:
                                pList = pls.split("::")
                                if not str(pList[0]) in ppStructure:
                                    ppStructure[pList[0]] = list()

                                # Differentiate permission type:
                                # global:
                                #     a privilege does not require the asset to be specified <--> it's valid for all assets;
                                #     set "any" for assets value.

                                # asset:
                                #    a privilege does not require the networks to be specified <--> it's valid for all networks within the asset;
                                #    set "any" for networks value.
                                #
                                # object:
                                #     standard.

                                if pList[3]:
                                    if pList[3] == "global":
                                        pList[1] = 0
                                        pList[2] = "any"
                                    if pList[3] == "asset":
                                        pList[2] = "any"

                                if not any(v['assetId'] == 0 for v in ppStructure[pList[0]]): # insert value only if not already present (applied to assetId "0").
                                    ppStructure[pList[0]].append({
                                        "assetId": pList[1],
                                        "network": pList[2],
                                    })

                        items[j]["privileges_network"] = ppStructure
                else:
                    del items[j]["privileges_network"]

                j = j+1

            return dict({
                "items": items
            })

        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def add(data: dict) -> None:
        s = ""
        keys = "("
        values = []
        roles = dict()

        c = connection.cursor()

        # Build SQL query according to dict fields (only whitelisted fields pass).
        for k, v in data.items():
            # roles is a dictionary of related roles/networks, which is POSTed together with the main identity group item.
            if any(exc in k for exc in (
                    "roles_network",
            )):
                # "roles_network": {
                #     "staff": [
                #         {
                #             "assetId": 1,
                #             "network": "any"
                #         }
                #     ],
                #  "nonExistent": []
                # }

                if isinstance(v, dict):
                    for rk, rv in v.items():
                        roles[rk] = rv
            else:
                s += "%s,"
                keys += k + ","
                values.append(strip_tags(v))  # no HTML allowed.

        keys = keys[:-1]+")"

        try:
            with transaction.atomic():
                # Insert identity group.
                c.execute("INSERT INTO identity_group "+keys+" VALUES ("+s[:-1]+")",
                    values
                )
                igId = c.lastrowid

                # Add associated roles (no error on non-existent role).
                for roleName, networksAssetsList in roles.items():
                    for networksAssetDict in networksAssetsList:
                        try:
                            Permission.add(igId, roleName, networksAssetDict["assetId"], networksAssetDict["network"])
                        except Exception:
                            pass

        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __exists(self) -> int:
        c = connection.cursor()
        try:
            c.execute("SELECT COUNT(*) AS c FROM identity_group WHERE identity_group_identifier = %s", [
                self.identityGroupIdentifier
            ])
            o = DBHelper.asDict(c)

            return int(o[0]['c'])

        except Exception:
            return 0
        finally:
            c.close()
