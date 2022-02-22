from typing import Dict, List
from ipaddress import IPv4Network
import re

from infoblox.models.Infoblox.Ipv4 import Ipv4
from infoblox.models.Infoblox.Network import Network
from infoblox.models.History import History

from infoblox.helpers.Log import Log


class Ipv4UseCase:
    def __init__(self, assetId: int, request: str, userData: dict, username: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.assetId: int = int(assetId)
        if "next-available" in request:
            self.request: str = "next-available"
        else:
            self.request: str = "user-specified"

        self.data = userData
        self.username = username
        self.permissionCheckNetwork: str = ""
        self.networkLogic: str = ""
        self.targetNetwork: str = ""
        self.networkContainer: str = ""
        self.gateway: str = ""
        self.mask: str = ""

        self.__init(self.data)



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def reserve(self) -> Dict[str, List]:
        if self.request == "next-available":
            response, actualNetwork = self.__reserveNextAvail()
            self.__historyLog(response, network=actualNetwork)
        else:
            response = self.__reserveProvided()
            self.__historyLog(response, network=self.targetNetwork)

        return response



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __init(self, userData: dict):
        try:
            if self.request == "next-available":
                # Find out the network belonging to the IPv4 address provided by the user in order to check user's permissions against (network or direct-father-container) and logic information.
                userNetworkObj = Network.discriminateUserNetwork(self.assetId, userData["network"])

                if "network_container" in userNetworkObj:
                    # On container logic, networkContainer is the network for permissions' check.
                    self.networkLogic = "container"
                    self.permissionCheckNetwork = self.networkContainer = userNetworkObj["network_container"]
                else:
                    # On network logic.
                    self.networkLogic = "network"
                    self.permissionCheckNetwork = self.targetNetwork = userNetworkObj["targetNetwork"]

                self.gateway = userNetworkObj["gateway"]
                self.mask = userNetworkObj["mask"]

            else:
                ipv4 = Ipv4(self.assetId, userData["ipv4addr"])
                self.permissionCheckNetwork = targetNetwork = ipv4.network
                self.targetNetwork = targetNetwork.split("/")

                try:
                    info = Network(self.assetId, targetNetwork)
                    self.mask = info.extattrs["Mask"]["value"]
                    self.gateway = info.extattrs["Gateway"]["value"]
                except Exception:
                    self.mask = IPv4Network(targetNetwork).netmask

        except Exception as e:
            raise e



    def __reserveNextAvail(self) -> tuple:
        j = 0
        objectType = ""
        number = 1
        response = list()

        if "object_type" in self.data:
            objectType = self.data["object_type"]
        if "number" in self.data:
            number = int(self.data["number"])
            if number > 10:
                number = 10 # limited to 10.

        actualNetwork, addresses = Network.getNextAvailableIpv4Addresses(
            self.assetId,
            self.networkLogic,
            self.targetNetwork,
            self.networkContainer,
            number,
            objectType
        )

        for address in addresses:
            try:
                mac = self.data["mac"][j]
            except Exception:
                mac = "00:00:00:00:00:00"

            try:
                extattrs = self.data["extattrs"][j]
            except Exception:
                extattrs = self.data["extattrs"][0]

            response.append(Ipv4.reserveNextAvailable(self.assetId, address, extattrs, mac))
            j += 1

        return response, actualNetwork



    def __reserveProvided(self) -> list:
        if "number" in self.data:
            del (self.data["number"])

        if "extattrs" in self.data:
            self.data["extattrs"] = self.data["extattrs"][0]

        self.data["mac"] = "00:00:00:00:00:00"

        return [
            Ipv4.reserve(self.assetId, self.data)
        ]



    def __historyLog(self, response, network) -> None:
        try:
            for createdObject in response:
                ipv4 = re.findall(r'[0-9]+(?:\.[0-9]+){3}', createdObject["result"])[0]

                try:
                    network = network[0]+"/"+network[1]
                except Exception:
                    network = ""

                oId = History.addByType({
                    "type": "ipv4",
                    "address": ipv4,
                    "network": network,
                    "mask": self.mask,
                    "gateway": self.gateway
                }, "object")

                History.addByType({
                    "username": self.username,
                    "action": self.request,
                    "asset_id": self.assetId,
                    "object_id": oId,
                    "status": "created"
                }, "log")
        except Exception:
            pass
