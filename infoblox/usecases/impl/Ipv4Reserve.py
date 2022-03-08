from typing import Dict, List

from abc import ABCMeta, abstractmethod


class Ipv4Reserve(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, assetId: int, request: str, userData: dict, username: str, *args, **kwargs):
        pass



    @abstractmethod
    def reserve(self) -> Dict[str, List]:
        pass
