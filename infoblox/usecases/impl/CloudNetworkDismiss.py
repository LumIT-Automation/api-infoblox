from abc import ABCMeta, abstractmethod


class CloudNetworkDismiss(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, assetId: int, provider: str, user: dict, *args, **kwargs):
        pass



    @abstractmethod
    def dismissNetworks(self, data: dict, *args, **kwargs) -> dict:
        pass
