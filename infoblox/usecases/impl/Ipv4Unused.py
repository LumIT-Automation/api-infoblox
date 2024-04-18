from typing import Dict, List

from abc import ABCMeta, abstractmethod


class Ipv4Unused(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass



    @abstractmethod
    def isUnused(ipAddressData: dict, ipOnARange: bool, scope: str) -> bool:
        pass



    @abstractmethod
    def patchData(data: dict) -> dict:
        pass