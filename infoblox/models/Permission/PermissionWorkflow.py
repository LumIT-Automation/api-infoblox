from typing import Union

from django.conf import settings

from infoblox.models.Permission.IdentityGroup import IdentityGroup
from infoblox.models.Permission.Workflow import Workflow
from infoblox.models.Permission.Network import Network

from infoblox.models.Infoblox.NetworkContainer import NetworkContainer as NetworkContainerModel
from infoblox.models.Infoblox.Network import Network as NetworkModel

from infoblox.models.Permission.repository.PermissionWorkflow import PermissionWorkflow as Repository
from infoblox.models.Permission.repository.PermissionWorkflowPrivilege import PermissionWorkflowPrivilege as PermissionPrivilegeRepository
from infoblox.models.Permission.Privilege import Privilege

from infoblox.helpers.Exception import CustomException


class PermissionWorkflow:

    # IdentityGroupWorkflowNetwork

    def __init__(self, permissionId: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id: int = int(permissionId)
        self.identityGroup: IdentityGroup
        self.workflow: Workflow
        self.network: Network

        self.__load()



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def delete(self) -> None:
        try:
            Repository.delete(self.id)
            del self
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################


    @staticmethod
    def hasUserPermission(groups: list, action: str, assetId: int = 0, container: str = "", network: Union[str, NetworkModel] = None, containers: list = None, networks: list = None) -> bool:
        networks = networks or []
        containers = containers or []
        permissionNetworks = []

        # Authorizations' list allowed for any (authenticated) user.
        if action == "authorizations_get":
            return True

        try:
            for gr in groups:
                if gr.lower() == "automation.local":
                    # Check if the given action exists.
                    if action in [ p["privilege"] for p in Privilege.listQuick()]:
                        return True
                    else:
                        return False

            if network or container:
                if network:
                    if isinstance(network, NetworkModel):
                        permissionNetworks.append(network.network)
                        container = network.network_container

                    if isinstance(network, str):
                        if "/" not in network: # if not already in CIDR notation.
                            network = NetworkModel(assetId, network).network

                        if not networks:
                            n = NetworkModel(assetId, network)
                            permissionNetworks.append(n.network)
                            container = n.network_container
                        else:
                            permissionNetworks.append(network)
                            container = [net for net in networks if net["network"] == network][0]["network_container"]

                permissionNetworks.append(container) # [network, container] if network // [container] if container.

                if settings.INHERIT_GRANDPARENTS_PERMISSIONS:
                    if not containers:
                        containers = NetworkContainerModel.listData(assetId, silent=True)

                    permissionNetworks.extend(NetworkContainerModel.genealogy(network=container, networkContainerList=containers))

            return bool(
                PermissionPrivilegeRepository.countUserWorkflowPermissions(groups, action, assetId, permissionNetworks) # check in all permissionNetworks.
            )

        except Exception as e:
                raise e



    @staticmethod
    def workflowPermissionsDataList() -> list:
        try:
            return Repository.list()
        except Exception as e:
            raise e



    @staticmethod
    def workflowAuthorizationsList(groups: list, workflow: str = "") -> dict:

        # Superadmin's group.
        for gr in groups:
            if gr.lower() == "automation.local":
                return  {
                    "assetId": 0,
                    "network": "any"
                }

        try:
            return PermissionPrivilegeRepository.workflowAuthorizationsList(groups=groups, workflow=workflow)
        except Exception as e:
            raise e



    @staticmethod
    def addFacade(identityGroupId: str, workflow: str, networkInfo: dict) -> None:
        networkAssetId = int(networkInfo.get("assetId", ""))
        networkName = networkInfo.get("name", "")

        try:
            try:
                # Try retrieving network.
                network = Network(assetId=networkAssetId, network=networkName)
            except CustomException as e:
                if e.status == 404:
                    try:
                        # If network does not exist, create it (permissions database).
                        network = Network(
                            id=Network.add(networkAssetId, networkName)
                        )
                    except Exception:
                        raise e
                else:
                    raise e

            PermissionWorkflow.__add(
                identityGroup=IdentityGroup(identityGroupIdentifier=identityGroupId),
                workflow=Workflow(workflow=workflow),
                network=network
            )
        except Exception as e:
            raise e



    @staticmethod
    def modifyFacade(permissionId: int, identityGroupId: str, workflow: str, networkInfo: dict) -> None:
        networkAssetId = int(networkInfo.get("assetId", ""))
        networkName = networkInfo.get("name", "")

        try:
            try:
                # Try retrieving network.
                network = Network(assetId=networkAssetId, network=networkName)
            except CustomException as e:
                if e.status == 404:
                    try:
                        # If network does not exist, create it (permissions database).
                        network = Network(
                            id=Network.add(networkAssetId, networkName)
                        )
                    except Exception:
                        raise e
                else:
                    raise e

            PermissionWorkflow(permissionId).__modify(
                identityGroup=IdentityGroup(identityGroupIdentifier=identityGroupId),
                workflow=Workflow(workflow=workflow),
                network=network
            )
        except Exception as e:
            raise e

    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __load(self) -> None:
        try:
            info = Repository.get(self.id)

            self.identityGroup = IdentityGroup(id=info["id_group"])
            self.workflow = Workflow(id=info["id_workflow"])
            self.network = Network(id=info["id_network"])
        except Exception as e:
            raise e



    def __modify(self, identityGroup: IdentityGroup, workflow: Workflow, network: Network) -> None:
        try:
            Repository.modify(
                self.id,
                identityGroupId=identityGroup.id,
                workflowId=workflow.id,
                networkId=network.id
            )

            self.__load()
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private static methods
    ####################################################################################################################

    @staticmethod
    def __add(identityGroup: IdentityGroup, workflow: Workflow, network: Network) -> None:
        try:
            Repository.add(
                identityGroupId=identityGroup.id,
                workflowId=workflow.id,
                networkId=network.id
            )
        except Exception as e:
            raise e
