from abc import ABCMeta, abstractmethod


class CloudNetworkModifyAccount(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, assetId: int, accountId: str, user: dict, *args, **kwargs):
        pass



    @abstractmethod
    def modifyAccount(self, data: dict, *args, **kwargs) -> dict:
        return {}
