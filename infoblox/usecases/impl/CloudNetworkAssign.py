from abc import ABCMeta, abstractmethod


class CloudNetworkAssign(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, assetId: int, provider: str, region: str, user: dict, *args, **kwargs):
        pass



    @abstractmethod
    def assignNetworks(self, data: dict, number: int = 1, *args, **kwargs) -> dict:
        return {}
