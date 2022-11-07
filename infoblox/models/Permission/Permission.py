from infoblox.models.Permission.IdentityGroup import IdentityGroup
from infoblox.models.Permission.Role import Role
from infoblox.models.Permission.Network import Network

from infoblox.models.Permission.repository.Permission import Permission as Repository
from infoblox.models.Permission.repository.PermissionPrivilege import PermissionPrivilege as PermissionPrivilegeRepository

from infoblox.helpers.Exception import CustomException


class Permission:

    # IdentityGroupRoleNetwork

    def __init__(self, permissionId: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id: int = int(permissionId)
        self.identityGroup: IdentityGroup
        self.role: Role
        self.network: Network

        self.__load()



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def delete(self) -> None:
        try:
            Repository.delete(self.id)
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def hasUserPermission(groups: list, action: str, assetId: int = 0, networkName: str = "") -> bool:
        # Superadmin's group.
        for gr in groups:
            if gr.lower() == "automation.local":
                return True

        try:
            return bool(
                PermissionPrivilegeRepository.countUserPermissions(groups, action, assetId, networkName)
            )
        except Exception as e:
            raise e



    @staticmethod
    def permissionsDataList() -> list:
        try:
            return Repository.list()
        except Exception as e:
            raise e



    @staticmethod
    def addFacade(identityGroupIdentifier: str, role: str, networkInfo: dict) -> None:
        networkAssetId = networkInfo.get("assetId", "")
        networkName = networkInfo.get("name", "")

        try:
            # Get existent or new network (permissions database).
            if role == "admin" or role == "workflow":
                # Role admin -> "any" network, which always exists.
                network = Network(assetId=networkAssetId, network="any")
            else:
                try:
                    # Try retrieving network.
                    network = Network(assetId=networkAssetId, network=networkName)
                except CustomException as e:
                    if e.status == 404:
                        try:
                            # If domain does not exist, create it (permissions database).
                            network = Network(
                                id=Network.add(networkAssetId, networkName)
                            )
                        except Exception:
                            raise e
                    else:
                        raise e

            Permission.__add(
                identityGroup=IdentityGroup(identityGroupIdentifier=identityGroupIdentifier),
                role=Role(role=role),
                network=network
            )
        except Exception as e:
            raise e



    @staticmethod
    def modifyFacade(permissionId: int, identityGroupIdentifier: str, role: str, networkInfo: dict) -> None:
        networkAssetId = networkInfo.get("assetId", "")
        networkName = networkInfo.get("name", "")

        try:
            # Get existent or new network (permissions database).
            if role == "admin" or role == "workflow":
                # Role admin -> "any" network, which always exists.
                network = Network(assetId=networkAssetId, network="any")
            else:
                try:
                    # Try retrieving network.
                    network = Network(assetId=networkAssetId, network=networkName)
                except CustomException as e:
                    if e.status == 404:
                        try:
                            # If domain does not exist, create it (permissions database).
                            network = Network(
                                id=Network.add(networkAssetId, networkName)
                            )
                        except Exception:
                            raise e
                    else:
                        raise e

            Permission(permissionId).__modify(
                identityGroup=IdentityGroup(identityGroupIdentifier=identityGroupIdentifier),
                role=Role(role=role),
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
            self.role = Role(id=info["id_role"])
            self.network = Network(id=info["id_network"])
        except Exception as e:
            raise e



    def __modify(self, identityGroup: IdentityGroup, role: Role, network: Network) -> None:
        try:
            Repository.modify(
                self.id,
                identityGroupId=identityGroup.id,
                roleId=role.id,
                networkId=network.id
            )
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private static methods
    ####################################################################################################################

    @staticmethod
    def __add(identityGroup: IdentityGroup, role: Role, network: Network) -> None:
        try:
            Repository.add(
                identityGroupId=identityGroup.id,
                roleId=role.id,
                networkId=network.id
            )
        except Exception as e:
            raise e
