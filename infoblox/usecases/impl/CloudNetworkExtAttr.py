from abc import ABCMeta, abstractmethod


class CloudNetworkExtAttr(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, assetId: int, user: dict, *args, **kwargs):
        pass



    @abstractmethod
    def listProviders(self, filter: dict = None, *args, **kwargs) -> set:
        return set()



    @abstractmethod
    def listAccountsProviders(self, filter: dict = None, *args, **kwargs) -> set:
        return set()
