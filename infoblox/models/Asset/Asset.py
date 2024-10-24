from infoblox.models.Asset.repository.Asset import Asset as Repository

from infoblox.helpers.Misc import Misc


class Asset:
    def __init__(self, assetId: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

        self.__load(showPassword=True)



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def modify(self, data: dict) -> None:
        try:
            Repository.modify(self.id, data)

            for k, v in Misc.toDict(data).items():
                setattr(self, k, v)
        except Exception as e:
            raise e



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
    def list(showPassword: bool) -> list:
        try:
            return Repository.list(showPassword=showPassword)
        except Exception as e:
            raise e



    @staticmethod
    def add(data: dict) -> None:
        from infoblox.models.Permission.Network import Network as PermissionNetwork

        try:
            aid = Repository.add(data)

            # When inserting an asset, add the "any" network (Permission).
            PermissionNetwork.add(aid, "any")

        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __load(self, showPassword: bool) -> None:
        try:
            data = Repository.get(self.id, showPassword=showPassword)
            for k, v in data.items():
                setattr(self, k, v)
        except Exception as e:
            raise e
