from infoblox.repository.Asset import Asset as Repository


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]



class Asset(metaclass=Singleton):
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

        self.__load()



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
        try:
            aid = Repository.add(data)

            # When inserting an asset, add the "any" network (Permission).
            from infoblox.models.Permission.Network import Network as PermissionNetwork
            PermissionNetwork.add(aid, "any")
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
