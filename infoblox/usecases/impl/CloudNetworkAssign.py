from abc import ABCMeta, abstractmethod


class CloudNetworkAssign(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, assetId: int, provider: str, region: str, user: dict, isWorkflow: bool = False, *args, **kwargs):
        pass

    @abstractmethod
    def assignNetwork(self, data: dict, *args, **kwargs) -> dict:
        return {}
