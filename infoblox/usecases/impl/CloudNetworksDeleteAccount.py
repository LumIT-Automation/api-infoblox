from abc import ABCMeta, abstractmethod


class DeleteAccountCloudNetworks(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, assetId: int, provider: str, user: dict, *args, **kwargs):
        pass



    @abstractmethod
    def deleteNetworks(self, data: dict, *args, **kwargs) -> dict:
        pass
