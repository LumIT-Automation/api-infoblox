from infoblox.models.Infoblox.Asset.repository.Asset import Asset as Repository


class Asset:
    # A custom pseudo-singleton (avoids initialization but uses different objects).
    instances = {}

    def __init__(self, assetId: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if assetId in Asset.instances:
            # Use saved properties.
            for k, v in vars(Asset.instances[assetId]).items():
                setattr(self, k, v)
        else:
            self.id = int(assetId)
            self.address = ""
            self.fqdn = ""
            self.baseurl = ""
            self.tlsverify = ""
            self.datacenter = ""
            self.environment = ""
            self.position = ""

            self.username = ""
            self.password = ""

            self.__load()

            Asset.instances[assetId] = self # save class instance in class variable.



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def modify(self, data: dict) -> None:
        try:
            Repository.modify(self.id, data)
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
    def list() -> list:
        try:
            return Repository.list()
        except Exception as e:
            raise e



    @staticmethod
    def add(data: dict) -> None:
        from infoblox.models.Permission.Network import Network as PermissionNetwork
        from infoblox.models.Permission.Permission import Permission
        from infoblox.models.Permission.IdentityGroup import IdentityGroup

        try:
            aid = Repository.add(data)

            # When inserting an asset, add the "any" network (Permission).
            PermissionNetwork.add(aid, "any")

            # Also, add a "*" permission for the workflow.local system user.
            Permission.add(
                identityGroupId=IdentityGroup("workflow.local").info()["id"], # get the identityGroupId of the workflow system user.
                role="workflow",
                assetId=aid,
                networkName="any"
            )
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __load(self) -> None:
        try:
            data = Repository.get(self.id)
            for k, v in data.items():
                setattr(self, k, v)
        except Exception as e:
            raise e
