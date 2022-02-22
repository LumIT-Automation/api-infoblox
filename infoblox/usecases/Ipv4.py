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
            self.request: str = "specified-ip"

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
            response, actualNetwork = Ipv4UseCase.__reserveNextAvail(self.assetId, self.data, self.networkLogic, self.targetNetwork, self.networkContainer)
            Ipv4UseCase.__historyLog(self.assetId, self.username, "next-available", response, network=actualNetwork, gateway=self.gateway, mask=self.mask)
        else:
            response = Ipv4UseCase.__reserveProvided(self.assetId, self.data)
            Ipv4UseCase.__historyLog(self.assetId, self.username, "user-specified", response, network=self.targetNetwork, gateway=self.gateway, mask=self.mask)

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



    ####################################################################################################################
    # Private static methods
    ####################################################################################################################

    @staticmethod
    def __reserveNextAvail(assetId, data, networkLogic, targetNetwork, networkContainer) -> tuple:
        j = 0
        response = list()

        objectType = ""
        number = 1
        if "object_type" in data:
            objectType = data["object_type"]
        if "number" in data:
            number = int(data["number"])
            if number > 10:
                number = 10 # limited to 10.

        actualNetwork, addresses = Network.getNextAvailableIpv4Addresses(assetId, networkLogic, targetNetwork, networkContainer, number, objectType)
        for address in addresses:
            try:
                mac = data["mac"][j]
            except Exception:
                mac = "00:00:00:00:00:00"

            try:
                extattrs = data["extattrs"][j]
            except Exception:
                extattrs = data["extattrs"][0]

            response.append(Ipv4.reserveNextAvailable(assetId, address, extattrs, mac))
            j += 1

        return response, actualNetwork



    @staticmethod
    def __reserveProvided(assetId, data) -> list:
        response = list()

        if "number" in data:
            del (data["number"])
        data["mac"] = "00:00:00:00:00:00"

        if "extattrs" in data:
            data["extattrs"] = data["extattrs"][0]

        response.append(Ipv4.reserve(assetId, data))

        return response



    @staticmethod
    def __historyLog(assetId, user, action, response, network: str = "", gateway: str = "", mask: str = "") -> None:
        try:
            for createdObject in response["data"]:
                ipv4 = re.findall(r'[0-9]+(?:\.[0-9]+){3}', createdObject["result"])[0]

                oId = History.addByType({
                    "type": "ipv4Addresses",
                    "address": ipv4,
                    "network": network,
                    "mask": mask,
                    "gateway": gateway
                }, "object")

                History.addByType({
                    "username": user,
                    "action": action,
                    "asset_id": assetId,
                    "object_id": oId,
                    "status": "created"
                }, "log")
        except Exception:
            pass
