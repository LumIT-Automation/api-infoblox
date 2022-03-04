from typing import Dict, List

from abc import ABCMeta, abstractmethod


class Ipv4Reserve(metaclass=ABCMeta):
    @abstractmethod
    def reserve(self) -> Dict[str, List]:
        pass
