from typing import List, Dict

from django.db import connection

from infoblox.helpers.Exception import CustomException
from infoblox.helpers.Database import Database as DBHelper
from infoblox.helpers.Log import Log


class PermissionPrivilege:

    # (IdentityGroupRoleNetworkPrivilege)

    # Tables: group_role_network, identity_group, role, network, privilege, role_privilege.



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(filterGroups: list = None, showPrivileges: bool = False) -> list:
        # List identity groups with related information regarding the associated roles on networks,
        # and optionally detailed privileges' descriptions.
        filterGroups = filterGroups or []
        groupWhere = ""
        j = 0

        c = connection.cursor()

        try:
            # Build WHERE clause when filterGroups is specified.
            if filterGroups:
                groupWhere = "WHERE ("
                for _ in filterGroups:
                    groupWhere += "identity_group.identity_group_identifier = %s || "
                groupWhere = groupWhere[:-4] + ") "

            c.execute(
                "SELECT identity_group.*, " 

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
                + groupWhere +
                "GROUP BY identity_group.id",
                      filterGroups
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

            items: List[Dict] = DBHelper.asDict(c)

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

            return items
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def authorizationsList(groups: list) -> dict:
        permissions = list()
        combinedPermissions = dict()

        try:
            o = PermissionPrivilege.list(filterGroups=groups, showPrivileges=True)

            # [
            #   {
            #     "id": 3,
            #     "name": "groupStaff",
            #     "identity_group_identifier": "cn=groupstaff,cn=users,dc=lab,dc=local",
            #     "roles_network": { ... },
            #     "privileges_network": { ... }
            #   },
            #   ...
            # ]

            # Collect every permission related to the group in groups.
            for identityGroup in groups:
                for el in o:
                    if "identity_group_identifier" in el:
                        if el["identity_group_identifier"].lower() == identityGroup.lower():
                            permissions.append(el["privileges_network"])

            # [
            #    {
            #        "assets_get": [
            #            {
            #                "assetId": "1",
            #                "network": "any"
            #            }
            #        ],
            #        ...
            #    },
            #    {
            #        "assets_get": [
            #            {
            #                "assetId": "1",
            #                "network": "Common"
            #            }
            #        ],
            #        ...
            #    }
            # ]

            # Clean up structure.
            for el in permissions:
                for k, v in el.items():

                    # Initialize list if not already done.
                    if not str(k) in combinedPermissions:
                        combinedPermissions[k] = list()

                    for innerEl in v:
                        if innerEl not in combinedPermissions[k]:
                            combinedPermissions[k].append(innerEl)

            # {
            #    ...
            #    "assets_get": [
            #        {
            #            "assetId": "1",
            #            "network": "any"
            #        },
            #        {
            #            "assetId": "1",
            #            "network": "Common"
            #        },
            #        {
            #            "assetId": "2",
            #            "network": "Common"
            #        }
            #    ],
            #    ...
            # }

            # Clean up structure.
            for k, v in combinedPermissions.items():
                asset = 0
                for el in v:
                    if el["network"] == "any":
                        asset = el["assetId"] # assetId for network "any".

                if asset:
                    for j in range(len(v)):
                        try:
                            if v[j]["assetId"] == asset and v[j]["network"] != "any":
                                del v[j]
                        except Exception:
                            pass

            # {
            #    ...
            #    "assets_get": [
            #        {
            #            "assetId": "1",
            #            "network": "any"
            #        },
            #        {
            #            "assetId": "2",
            #            "network": "Common"
            #        }
            #    ],
            #    ...
            # }
        except Exception as e:
            raise e

        return combinedPermissions



    @staticmethod
    def countUserPermissions(groups: list, action: str, assetId: int = 0, networks: list = None) -> int:
        networks = networks or []
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
                for _ in groups:
                    groupWhere += 'identity_group.identity_group_identifier = %s || '

                # Put all the args of the query in a list.
                if assetId:
                    args.append(assetId)
                    assetWhere = "AND `network`.id_asset = %s "

                if networks and any(net != "" for net in networks):
                    orNets = ""
                    for n in networks:
                        if n:
                            orNets += 'OR `network`.`network` = %s '
                            args.append(n)

                    networkWhere = "AND (`network`.`network` = 'any' " + orNets + " ) " # if "any" appears in the query results so far -> pass.

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
    def countUserWorkflowPermissions(groups: list, workflow: str, assetId: int = 0, networks: list = None) -> int:
        if workflow and groups:
            assetWhere = ""
            networkWhere = ""

            c = connection.cursor()

            try:
                args = groups.copy()
                groupWhere = ""
                for g in groups:
                    groupWhere += "identity_group.identity_group_identifier = %s || "

                # Put all the args of the query in a list.
                if assetId:
                    args.append(assetId)
                    assetWhere = "AND `partition`.id_asset = %s "

                if networks and any(net != "" for net in networks):
                    orNets = ""
                    for n in networks:
                        if n:
                            orNets += 'OR `network`.`network` = %s '
                            args.append(n)

                    networkWhere = "AND (`network`.`network` = 'any' " + orNets + " ) " # if "any" appears in the query results so far -> pass.

                args.append(workflow)

                c.execute(
                    "SELECT COUNT(*) AS count "
                    "FROM identity_group "
                    "LEFT JOIN group_workflow_network ON group_workflow_network.id_group = identity_group.id "
                    "LEFT JOIN workflow ON workflow.id = group_workflow_network.id_workflow "
                    "LEFT JOIN workflow_privilege ON workflow_privilege.id_workflow = workflow.id "
                    "LEFT JOIN `network` ON `network`.id = group_workflow_network.id_network "                      
                    "LEFT JOIN privilege ON privilege.id = workflow_privilege.id_privilege "
                    "WHERE (" + groupWhere[:-4] + ") " +
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

        return 0



    @staticmethod
    def workflowAuthorizationsList(groups: list, workflow: str = "") -> dict:
        from infoblox.helpers.Log import Log
        o = dict()

        if groups:
            workflowWhere = ""
            c = connection.cursor()

            try:
                args = groups.copy()
                groupWhere = ""
                for g in groups:
                    groupWhere += "identity_group.identity_group_identifier = %s || "

                if workflow:
                    workflowWhere = "AND workflow.workflow = %s "
                    args.append(workflow)

                c.execute(
                    "SELECT IFNULL(workflow.workflow, '') AS workflow, "

                    "IFNULL(GROUP_CONCAT( "
                        "DISTINCT CONCAT(`network`.id_asset,'::',`network`.`network`) "
                        "ORDER BY `network`.id_asset "
                        "SEPARATOR ',' "
                    "), '') AS assetId_network "

                    "FROM identity_group "
                    "LEFT JOIN group_workflow_network ON group_workflow_network.id_group = identity_group.id "
                    "LEFT JOIN workflow ON workflow.id = group_workflow_network.id_workflow "
                    "LEFT JOIN `network` ON `network`.id = group_workflow_network.id_network "
                    "WHERE (" + groupWhere[:-4] + ") " +
                    workflowWhere +
                    "GROUP BY workflow.workflow",
                        args
                )

                items: List[Dict] = DBHelper.asDict(c)
                for item in items:
                    flow = item.get("workflow", "")
                    if flow:
                        o[flow] = []
                        el = item.get("assetId_network", "")
                        assetId_network = el.split(",")
                        for an in assetId_network:
                            [ a, n ] = an.split("::")
                            o[flow].append({
                                "asseId": a,
                                "network": n
                            })

                return o
            except Exception as e:
                raise CustomException(status=400, payload={"database": e.__str__()})
            finally:
                c.close()

        return {}



