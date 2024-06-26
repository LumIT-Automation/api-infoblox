from typing import Union

from infoblox.models.Permission.Permission import Permission
from infoblox.models.Permission.PermissionWorkflow import PermissionWorkflow

from infoblox.models.Infoblox.Network import Network as NetworkModel


class CheckPermissionFacade:



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def hasUserPermission(groups: list, action: str, assetId: int = 0, container: str = "", network: Union[str, NetworkModel] = None, containers: list = None, networks: list = None, isWorkflow: bool = False) -> bool:
        try:
            if isWorkflow:
                return bool(
                    PermissionWorkflow.hasUserPermission(groups=groups, action=action, assetId=assetId, container=container, network=network, containers=containers, networks=networks)
                )
            else:
                return bool(
                    Permission.hasUserPermission(groups=groups, action=action, assetId=assetId, container=container, network=network, containers=containers, networks=networks)
                )
        except Exception as e:
            raise e
