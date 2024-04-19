from typing import Dict, List

from abc import ABCMeta, abstractmethod


class Ipv4PatchData(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass



    @abstractmethod
    def isIpv4Unused(ipAddressData: dict, scope: str) -> bool:
        pass



    @abstractmethod
    def patchInfoData(data: dict) -> dict:
        pass