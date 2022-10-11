from infoblox.models.Permission.Role import Role
from infoblox.models.Permission.Network import Network

from infoblox.repository.Permission import Permission as Repository


class Permission:

    # IdentityGroupRoleNetwork

    def __init__(self, id: int, groupId: int = 0, roleId: int = 0, partitionId: int = 0, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id = id

        self.id_group = groupId
        self.id_role = roleId
        self.id_partition = partitionId



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def modify(self, identityGroupId: int, role: str, assetId: int, networkName: str) -> None:
        try:
            if role == "admin":
                networkName = "any" # if admin: "any" is the only valid choice (on selected assetId).

            # RoleId.
            r = Role(roleName=role)
            roleId = r.info()["id"]

            # Network id.
            networkId = Permission.__getNetwork(assetId, networkName)

            Repository.modify(identityGroupId, roleId, networkId, self.id)
        except Exception as e:
            raise e



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
                Repository.countUserPermissions(groups, action, assetId, networkName)
            )
        except Exception as e:
            raise e



    @staticmethod
    def listIdentityGroupsRolesPartitions() -> list:
        try:
            return Repository.list()
        except Exception as e:
            raise e



    @staticmethod
    def add(identityGroupId: int, role: str, assetId: int, networkName: str) -> None:
        try:
            if role == "admin" or role == "workflow":
                networkName = "any" # if admin: "any" is the only valid choice (on selected assetId).

            # RoleId.
            r = Role(roleName=role)
            roleId = r.info()["id"]

            # Network id.
            networkId = Permission.__getNetwork(assetId, networkName)

            Repository.add(identityGroupId, roleId, networkId)
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    @staticmethod
    def __getNetwork(assetId: int, networkName: str):
        p = Network(assetId=assetId, networkName=networkName)
        if p.exists():
            networkId = p.info()["id"]
        else:
            # If partition does not exist, create it (on Permissions database, not F5 endpoint).
            networkId = p.add(assetId, networkName)

        return networkId
