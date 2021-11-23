from infoblox.models.Permission.Role import Role
from infoblox.models.Permission.Network import Network

from infoblox.repository.Permission import Permission as Repository


class Permission:
    def __init__(self, permissionId: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.permissionId = permissionId



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

            # Network id. If network does not exist, create it.
            p = Network(assetId=assetId, networkName=networkName)
            if p.exists():
                networkId = p.info()["id"]
            else:
                networkId = p.add(assetId, networkName)

            Repository.modify(identityGroupId, roleId, networkId, self.permissionId)
        except Exception as e:
            raise e



    def delete(self) -> None:
        try:
            Repository.delete(self.permissionId)
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
    def list() -> dict:
        try:
            return {
                "items": Repository.list()
            }
        except Exception as e:
            raise e



    @staticmethod
    def add(identityGroupId: int, role: str, assetId: int, networkName: str) -> None:
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

            Repository.add(identityGroupId, roleId, networkId)
        except Exception as e:
            raise e



    @staticmethod
    def cleanup(identityGroupId: int) -> None:
        try:
            Repository.cleanup(identityGroupId)
        except Exception as e:
            raise e
