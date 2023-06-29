from abc import ABCMeta, abstractmethod


class CloudNetworkModify(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, assetId: int, network: str, provider: str, region: str, user: dict, *args, **kwargs):
        pass



    @abstractmethod
    def modifyNetwork(self, data: dict, *args, **kwargs) -> dict:
        return {}
