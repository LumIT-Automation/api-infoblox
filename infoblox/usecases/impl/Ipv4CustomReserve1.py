import socket
import re
import ipaddress
from datetime import datetime

from infoblox.usecases.impl.Ipv4Reserve import Ipv4Reserve

from infoblox.models.Infoblox.Ipv4 import Ipv4
from infoblox.models.Infoblox.Network import Network
from infoblox.models.Infoblox.NetworkContainer import NetworkContainer
from infoblox.models.History.History import History

from infoblox.helpers.Exception import CustomException
from infoblox.helpers.Log import Log


class Ipv4CustomReserve1(Ipv4Reserve):
    def __init__(self, assetId: int, request: str, userData: dict, username: str, *args, **kwargs):
        super().__init__(assetId, request, userData, username, *args, **kwargs)

        self.assetId: int = int(assetId)
        if "next-available" in request:
            self.request: str = "next-available"
        else:
            self.request: str = "user-specified"

        self.data = userData
        # "ipv4addr": "10.8.1.100", --> only for user-specified.
        # "network": "10.8.128.0", --> only next-available.
        # "object_type": "Server", --> only for next-available container and next-available heartbeat.
        # "number": 1,
        # "mac": [
        #     "00:00:00:00:00:00"
        # ],
        # "extattrs": [
        #     {
        #         "Name Server": {
        #             "value": "Service"
        #         },
        #         "Reference": {
        #             "value": "Reference"
        #         }
        #     }
        # ]

        self.username = username
        self.permissionCheckNetwork: str = ""
        self.networkLogic: str = ""
        self.targetNetwork: str = ""
        self.networkContainer: str = ""
        self.gateway: str = ""
        self.mask: str = ""

        self.__init()



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def reserve(self):
        actualNetwork = ""

        if self.request == "next-available":
            response, actualNetwork = self.__reserveNextAvail()
            historyId = self.__historyLog(response, network=actualNetwork)

            # Example.
            # Container:
            #     actualNetwork = 10.8.0.0
            #     response = [{'result': 'fixedaddress/ZG5zLmZpeGVkX2FkZHJlc3MkMTAuOC4wLjE1OC4wLi4:10.8.0.158/default', ...}]
            # Network:
            #     actualNetwork = 10.8.128.0
            #     response = [{'result': 'fixedaddress/ZG5zLmZpeGVkX2FkZHJlc3MkMTAuOC4xMzIuMy4wLi4:10.8.132.3/default', ...}]
            # HB:
            #     actualNetwork = 10.8.128.0
            #     response = [
            #         {'result': 'fixedaddress/ZG5zLmZpeGVkX2FkZHJlc3MkMTAuOC4xMC4xLjAuLg:10.8.10.1/default', ...},
            #         {'result': 'fixedaddress/ZG5zLmZpeGVkX2FkZHJlc3MkMTAuOC4xMC4yLjAuLg:10.8.10.2/default', ...}
            #     ]
        else:
            response = self.__reserveProvided()
            historyId = self.__historyLog(response, network=self.targetNetwork)

        return response, actualNetwork, self.mask, self.gateway, historyId



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __init(self):
        try:
            if self.request == "next-available":
                # Find out the network belonging to the IPv4 address provided by the user in order to check user's permissions against
                # (network or direct-father-container) and logic information.
                userNetworkObj = self.discriminateUserNetwork()

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
                ipv4 = Ipv4(self.assetId, self.data["ipv4addr"])
                self.permissionCheckNetwork = targetNetwork = ipv4.network
                self.targetNetwork = targetNetwork.split("/")

                try:
                    info = Network(self.assetId, targetNetwork)
                    self.mask = info.extattrs["Mask"]["value"]
                    self.gateway = info.extattrs["Gateway"]["value"]
                except Exception:
                    self.mask = ipaddress.IPv4Network(targetNetwork).netmask
        except Exception as e:
            raise e



    def discriminateUserNetwork(self) -> dict:
        try:
            # For self.data["network"] ["AAAA"], find network information (as in comments below).
            # self.data["network"] is the direct target network or a network belonging to a container.

            # If the "Real Network" extensible attribute == "yes" for this network ["AAAA/M"] --> networkLogic: "network".
            # If (otherwise)
            #    network_container != "/"
            #    and "Real Network" = "yes" for the network --> networkLogic: "container".
            #    (If "Real Network" = "yes" in a container, we are within a "container logic" scheme).

            # "Real Network" = "yes" extensible attribute must be previously set within Infoblox.

            networkInformation = Network(self.assetId, self.data["network"])

            # Example for a network container logic.
            # {
            #     '_ref': 'network/ZG5zLm5ldHdvcmskMTAuOC4xLjAvMjQvMA:10.8.1.0/24/default',
            #     'network': '10.8.1.0/24',
            #     'network_container': '10.8.0.0/17',
            #     'network_view': 'default'
            # }

            # Example for a network logic.
            # {
            #     '_ref': 'network/ZG5zLm5ldHdvcmskMTAuOC4xMjguMC8xNy8w:10.8.128.0/17/default',
            #     'network': '10.8.128.0/17',
            #     'network_container': '/',
            #     'network_view': 'default'
            # }

            # Try networkLogic: "network" first.
            ####################################

            try:
                oNetwork = Network(self.assetId, networkInformation.network, filter={
                    "*Real Network": "yes"
                })

                # {
                # '_ref': 'network/ZG5zLm5ldHdvcmskMTAuOC4xMjguMC8xNy8w:10.8.128.0/17/default',
                # 'extattrs': {
                #     'Gateway': {'value': '10.8.128.1'},
                #     'Mask': {'value': '255.255.128.0'},
                #     'Real Network': {'value': 'yes'}
                #     },
                # 'network': '10.8.128.0/17',
                # 'network_view': 'default'
                # }

                if oNetwork.network:
                    try:
                        m = oNetwork.extattrs["Mask"]["value"]
                    except Exception:
                        raise CustomException(status=400, payload={"message": "Mask value not set in the Infoblox network's extensible attributes."})

                    try:
                        g = oNetwork.extattrs["Gateway"]["value"]
                    except KeyError:
                        g = ""

                    o = {
                        "networkLogic": "network",
                        "targetNetwork": oNetwork.network,
                        "mask": m,
                        "gateway": g
                    }

                    Log.log("Network information: "+str(o))
                    return o
            except CustomException as e:
                if e.status == 404:
                    pass
                else:
                    raise e

            # Try networkLogic: "container".
            ################################

            # Is container logic?
            if networkInformation.network_container != "/":
                if "/" in networkInformation.network_container:
                    n, m = networkInformation.network_container.split("/")

                    try:
                        oNetworkContainer = NetworkContainer(self.assetId, n+"/"+m, filter={
                            "*Real Network": "yes"
                        })

                        # {
                        #     '_ref': 'networkcontainer/ZG5zLm5ldHdvcmtfY29udGFpbmVyJDEwLjguMC4wLzE3LzA:10.8.0.0/17/default',
                        #     'extattrs': {
                        #         'Gateway': {'value': '10.8.1.1'},
                        #         'Mask': {'value': '255.255.128.0'},
                        #         'Real Network': {'value': 'yes'}
                        #         },
                        #     'network': '10.8.0.0/17',
                        #     'network_container': '/',
                        #     'network_view': 'default'
                        # ]

                        if oNetworkContainer.network:
                            try:
                                m = oNetworkContainer.extattrs["Mask"]["value"]
                            except Exception:
                                raise CustomException(status=400, payload={"message": "Mask value not set in the Infoblox network's extensible attributes."})

                            try:
                                g = oNetworkContainer.extattrs["Gateway"]["value"]
                            except KeyError:
                                g = ""

                            o = {
                                "networkLogic": "container",
                                "mask": m,
                                "gateway": g,
                                "network_container": networkInformation.network_container
                            }

                            Log.log("Network information: "+str(o))
                            return o
                    except CustomException as e:
                        if e.status == 404:
                            pass
                        else:
                            raise e

            raise CustomException(status=400, payload={"message": "Cannot discriminate network."})
        except Exception as e:
            raise CustomException(status=400, payload={"message": "Cannot discriminate network: "+str(e.payload)})



    @staticmethod
    def getTargetSubnetworks(assetId: int, networkLogic: str, targetNetwork: str, networkContainer: str, objectType: str = "") -> list:
        allSubnetworks = list()

        # If networkLogic == "network" -> targetNetworkInformation.targetNetwork
        # If networkLogic == "container" -> find the networks which match the __objectType within the targetNetwork container.

        # targetNetworkInformation = {
        #    "networkLogic": "container",
        #    "targetNetwork": "10.8.0.0/17",
        #    "mask": "255.255.128.0",
        #    "gateway": "10.8.1.1"
        # }

        try:
            if networkLogic == "network":
                sn, sm = targetNetwork.split("/")
                allSubnetworks.append(sn)

            if networkLogic == "container":
                if objectType:

                    # Get all networks in the network container.
                    n, m = networkContainer.split('/')
                    subnetworks = NetworkContainer(assetId, n+"/"+m).networksData(
                        filter={
                            "*Object Type": objectType
                        }
                    )

                    # [
                    #     {
                    #         '_ref': 'network/ZG5zLm5ldHdvcmskMTAuOC4zLjAvMjQvMA:10.8.3.0/24/default',
                    #         'network': '10.8.3.0/24',
                    #         'network_container': '10.8.0.0/17',
                    #         'network_view': 'default'
                    #     },
                    #     {
                    #         ...
                    #         'network': '10.8.0.0/24',
                    #         ...
                    #     },
                    #     ...
                    # ]

                    for s in subnetworks:
                        sn, sm = s["network"].split("/")
                        allSubnetworks.append(sn)

                    allSubnetworks = sorted(allSubnetworks, key=lambda item: socket.inet_aton(item)) # order subnetworks.
        except Exception:
            raise CustomException(status=400, payload={"message": "No network found."})

        if not allSubnetworks:
            raise CustomException(status=400, payload={"message": "No network found: make sure that Object Type is valid, if required."})
        else:
            Log.log("All subnetworks: "+str(allSubnetworks))

        return allSubnetworks



    @staticmethod
    def findFirstIpByAttrs(assetId: int, network: str, number: int) -> list:
        j = 0
        cleanAddresses = list()

        try:
            networkCidr = network
            n, mask = networkCidr.split('/')

            # There can be many IP addresses here.
            # Use ipaddress library to split the ip list in ranges of max 100 in order to make smaller calls.
            ipaddressNetworkObj = ipaddress.ip_network(networkCidr)
            ipList = list(ipaddressNetworkObj.hosts())

            if int(mask) > 22:
                ipListChunks = [ipList[x:x + 100] for x in range(0, len(ipList), 100)]
            else:
                ipListChunks = [ipList[x:x + 500] for x in range(0, len(ipList), 500)]

            for chunk in ipListChunks:
                startIp = chunk[0]
                endIp = chunk[-1]

                addresses = Network(assetId, network).ipv4sData(maxResults=100, fromIp=startIp, toIp=endIp)

                # [{'_ref': 'ipv4address/Li5pcHY0X2FkZHJlc3MkMTAuOC4zLjAvMA:10.8.3.0','ip_address': '10.8.3.0', 'status': 'USED', 'usage': []}, {}, ...]

                if isinstance(addresses, list):
                    # For all addresses in the subnet.
                    for address in addresses:
                        # Until <number> suitable addresses is found.
                        if j < number:
                            if "ip_address" in address and ("status" in address and address["status"] == "UNUSED") or ("usage" in address and address["usage"] == ["DNS"]):
                                # Addresses not ending in 0 or 255.
                                matches = re.search(r"^((?!(^\d+.\d+.\d+.(0+|255)$)).)*$", address["ip_address"])
                                if matches:
                                    cleanAddress = str(matches.group(0)).strip()
                                    cleanAddresses.append(cleanAddress)

                                    j += 1

                if len(cleanAddresses) == number:
                    return cleanAddresses
        except Exception as e:
            raise e

        return []



    @staticmethod
    def getNextAvailableIpv4Addresses(assetId: int, networkLogic: str, targetNetwork: str, networkContainer: str, number, objectType) -> tuple:
        # Get the next available IP address within allSubnetworks.
        # Select the first IPv4 among them which is:
        # * unused or used but with usage == "DNS" (only "DNS")
        # * not ending in 0 or 255.
        allSubnetworks = Ipv4CustomReserve1.getTargetSubnetworks(assetId, networkLogic, targetNetwork, networkContainer, objectType)

        try:
            for n in allSubnetworks:
                # Find the first <number> free IPv4(s) in the subnet.
                addresses = Ipv4CustomReserve1.findFirstIpByAttrs(
                    assetId,
                    Network(assetId, n).network,
                    number
                )

                if len(addresses) == number:
                    return n, addresses
        except Exception as e:
            raise CustomException(status=400, payload={"message": "Cannot get next available IPv4 address: "+e.payload})

        raise CustomException(status=400, payload={"message": "No available IPv4 addresses found."})



    def __reserveNextAvail(self) -> tuple:
        j = 0
        objectType = ""
        number = 1
        response = list()
        reservedIps = list()

        if "object_type" in self.data:
            objectType = self.data["object_type"]
        if "number" in self.data:
            number = int(self.data["number"])
            if number > 10:
                number = 10 # limited to 10.

        actualNetwork, addresses = Ipv4CustomReserve1.getNextAvailableIpv4Addresses(
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

            # Override Reference extattr.
            extattrs["Reference"] = {
                "value": self.username + ", " + str(datetime.today().strftime("%Y-%m-%d %H:%M:%S"))
            }

            try:
                r = Ipv4.reserveNextAvailable(self.assetId, address, extattrs, mac) # {'result': 'fixedaddress/ZG5zLmZpeGVkX2FkZHJlc3MkMTAuOC4wLjE1OC4wLi4:10.8.0.158/default'}
                if isinstance(r, dict):
                    r["mask"] = self.mask
                    r["gateway"] = self.gateway

                response.append(r)
                reservedIps.append(address)
            except Exception as e:
                if self.data["object_type"] == "Heartbeat":
                    # If an error occurs in a Heartbeat creation, clean all the other created addresses.
                    for i in reservedIps:
                        Ipv4(self.assetId, i).release(fixedaddressOnly=True)

                raise e
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



    def __historyLog(self, response, network) -> int:
        historyId = 0

        try:
            network = network+"/"+str(ipaddress.IPv4Network(f"0.0.0.0/{self.mask}").prefixlen)

            for o in response:
                ipv4 = re.findall(r'[0-9]+(?:\.[0-9]+){3}', o["result"])[0]

                data = {
                    "log": {
                        "username": self.username,
                        "action": self.request,
                        "asset_id": self.assetId,
                        "status": "created"
                    },
                    "log_object": {
                        "type": "ipv4",
                        "address": ipv4,
                        "network": network,
                        "mask": self.mask,
                        "gateway": self.gateway
                    }
                }
                historyId = History.add(data)

            return historyId
        except Exception:
            pass
