from infoblox.models.Permission.Permission import Permission
from infoblox.models.Permission.PermissionWorkflow import PermissionWorkflow


class CheckPermissionFacade:



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def hasUserPermission(groups: list, action: str, assetId: int = 0, network: str = "", isWorkflow: bool = False) -> bool:
        try:
            if isWorkflow:
                return bool(
                    PermissionWorkflow.hasUserPermission(groups=groups, action=action, assetId=assetId, network=network)
                )
            else:
                return bool(
                    Permission.hasUserPermission(groups=groups, action=action, assetId=assetId, network=network)
                )
        except Exception as e:
            raise e
