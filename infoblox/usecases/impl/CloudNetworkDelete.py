from abc import ABCMeta, abstractmethod


class CloudNetworkDelete(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, assetId: int, networkAddress: str, user: dict, *args, **kwargs):
        pass



    @abstractmethod
    def delete(self, *args, **kwargs) -> dict:
        pass
