from django.db import connection

from infoblox.helpers.Exception import CustomException
from infoblox.helpers.Database import Database as DBHelper


class PermissionWorkflow:

    # IdentityGroupWorkflowNetwork

    # Tables: group_workflow_network, identity_group, workflow, network



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def get(permissionId: int) -> dict:
        c = connection.cursor()

        try:
            c.execute("SELECT * FROM group_workflow_network WHERE id=%s", [permissionId])

            return DBHelper.asDict(c)[0]
        except IndexError:
            raise CustomException(status=404, payload={"database": "Non existent permission"})
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def modify(permissionId: int, identityGroupId: int, workflowId: int, networkId: int) -> None:
        c = connection.cursor()

        try:
            c.execute("UPDATE group_workflow_network SET id_group=%s, id_workflow=%s, id_network=%s WHERE id=%s", [
                identityGroupId, # AD or RADIUS group.
                workflowId,
                networkId,
                permissionId
            ])
        except Exception as e:
            if e.__class__.__name__ == "IntegrityError" \
                    and e.args and e.args[0] and e.args[0] == 1062:
                raise CustomException(status=400, payload={"database": "Duplicated entry"})
            else:
                raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def delete(permissionId: int) -> None:
        c = connection.cursor()

        try:
            c.execute("DELETE FROM group_workflow_network WHERE id = %s", [
                permissionId
            ])
        except Exception as e:
            raise CustomException(status=400, payload={"database": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def list() -> list:
        c = connection.cursor()

        try:
            c.execute(
                "SELECT "
                    "group_workflow_network.id, "
                    "identity_group.name AS identity_group_name, "
                    "identity_group.identity_group_identifier AS identity_group_identifier, "
                    "workflow.workflow AS workflow, "
                    "`network`.id_asset AS network_asset, "
                    "`network`.`network` AS network_name "
                "FROM identity_group "
                "LEFT JOIN group_workflow_network ON group_workflow_network.id_group = identity_group.id "
                "LEFT JOIN workflow ON workflow.id = group_workflow_network.id_workflow "
                "LEFT JOIN `network` ON `network`.id = group_workflow_network.id_network "
                "WHERE workflow.workflow IS NOT NULL")
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



    @staticmethod
    def add(identityGroupId: int, workflowId: int, networkId: int) -> None:
        c = connection.cursor()

        try:
            c.execute("INSERT INTO group_workflow_network (id_group, id_workflow, id_network) VALUES (%s, %s, %s)", [
                identityGroupId, # AD or RADIUS group.
                workflowId,
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
