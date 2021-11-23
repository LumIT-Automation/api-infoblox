from infoblox.repository.Asset import Asset as Repository


class Asset:
    def __init__(self, assetId: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.assetId = int(assetId)



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def info(self) -> dict:
        try:
            info = Repository.get(self.assetId)
            return info
        except Exception as e:
            raise e



    def modify(self, data: dict) -> None:
        try:
            Repository.modify(self.assetId, data)
        except Exception as e:
            raise e



    def delete(self) -> None:
        try:
            Repository.delete(self.assetId)
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
        try:
            aid = Repository.add(data)

            # When inserting an asset, add the "any" network (Permission).
            from infoblox.models.Permission.Network import Network as PermissionNetwork
            PermissionNetwork.add(aid, "any")
        except Exception as e:
            raise e
