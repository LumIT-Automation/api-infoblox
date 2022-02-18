import re
import socket
import ipaddress
from typing import Dict

from infoblox.models.Infoblox.NetworkContainer import NetworkContainer
from infoblox.models.Infoblox.connectors.Network import Network as Connector

from infoblox.helpers.Exception import CustomException
from infoblox.helpers.Log import Log


Value: Dict[str, str] = {"value": ""}

class Network:
    def __init__(self, assetId: int, network: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.asset_id: int = int(assetId)
        self._ref: str = ""
        self.network: str = network
        self.network_container: str = ""
        self.network_view: str = ""
        self.extattrs: Dict[str, Dict[str, str]] = {
            "Gateway": Value,
            "Mask": Value,
            "Object Type": Value,
            "Real Network": Value,
        }

        self.__load()



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def getOnlyRealNetworkWithExtattrs(self, attrs: dict) -> dict:
        try:
            data = Connector.get(self.asset_id, self.network, attrs)
            if data:
                data["asset_id"] = self.asset_id
        except Exception as e:
            raise e

        return data



    def ipv4Addresses(self, maxResults: int = 0, fromIp: str = "", toIp: str = "") -> dict:
        # Please note: composition is not so valuable here.
        try:
            return Connector.addresses(self.asset_id, self.network, maxResults, fromIp, toIp)
        except Exception as e:
            raise e



    def findFirstIpByAttrs(self, number: int, attrs: dict = None, operator: str = "or") -> list:
        j = 0
        cleanAddresses = list()
        checkAttrs = None
        condition = '"ip_address" in address'

        if attrs is None:
            attrs = {
                "status": "UNUSED",
                "usage": ["DNS"]
            }
            # Supported attrs: "status": str, "usage": [], type: []
            # Supported operators: and, or.

        if "status" in attrs:
            checkAttrs = ' ("status" in address and attrs["status"] == address["status"]) '
        if "usage" in attrs:
            if checkAttrs:
                checkAttrs += operator
            checkAttrs += ' ("usage" in address and attrs["usage"] == address["usage"]) ' # lists must be identical (order matters).
        if "type" in attrs:
            if checkAttrs:
                checkAttrs += operator
            checkAttrs += ' ("type" in address and attrs["type"] == address["type"])' # lists must be identical (order matters)

        if checkAttrs:
            condition = condition+" and "+checkAttrs

        try:
            networkCidr = self.network
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

                addresses = self.ipv4Addresses(maxResults=100, fromIp=startIp, toIp=endIp)

                # [{'_ref': 'ipv4address/Li5pcHY0X2FkZHJlc3MkMTAuOC4zLjAvMA:10.8.3.0','ip_address': '10.8.3.0', 'status': 'USED', 'usage': []}, {}, ...]

                if isinstance(addresses, list):
                    # For all addresses in the subnet.
                    for address in addresses:
                        # Until <number> suitable addresses is found.
                        if j < number:
                            if eval(condition):
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



    def repr(self) -> dict:
        try:
            return vars(self)
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(assetId: int) -> dict:
        try:
            o = Connector.list(assetId)

            for i, v in enumerate(o):
                o[i]["asset_id"] = assetId # add assetId information.
        except Exception as e:
            raise e

        return o



    @staticmethod
    def discriminateUserNetwork(assetId: int, userNetwork: str) -> dict:
        try:
            # For userNetwork ["AAAA"], find network information (as in comments below).
            # userNetwork is the direct target network or a network belonging to a container.

            # If the "Real Network" extensible attribute == "yes" for this network ["AAAA/M"] --> networkLogic: "network".
            # If (otherwise)
            #    network_container != "/"
            #    and "Real Network" = "yes" for the network --> networkLogic: "container".
            #    (If "Real Network" = "yes" in a container, we are within a "container logic" scheme).

            # "Real Network" = "yes" extensible attribute must be previously set within Infoblox.

            # Get userNetwork's information.
            networkInformation = Network(assetId, userNetwork)

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

            ####################################
            # Try networkLogic: "network" first.
            ####################################

            networkInfo = Network(assetId, networkInformation.network).getOnlyRealNetworkWithExtattrs(
                attrs={
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

            if "network" in networkInfo and networkInfo["network"]:
                try:
                    m = networkInfo["extattrs"]["Mask"]["value"]
                except Exception:
                    raise CustomException(status=400, payload={"message": "Mask value not set in the Infoblox network's extensible attributes."})

                try:
                    g = networkInfo["extattrs"]["Gateway"]["value"]
                except Exception:
                    g = ""

                o = {
                    "networkLogic": "network",
                    "targetNetwork": networkInfo["network"],
                    "mask": m,
                    "gateway": g
                }

                Log.log("Network information: "+str(o))
                return o

            ################################
            # Try networkLogic: "container".
            ################################

            else:
                # Is container logic?
                if networkInformation.network_container != "/":
                    if "/" in networkInformation.network_container:
                        n, m = networkInformation.network_container.split("/")

                        networkContainerInfo = NetworkContainer(assetId, n+"/"+m).getOnlyRealNetworkWithExtattrs(
                            filter={
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

                        if "network" in networkContainerInfo and networkContainerInfo["network"]:
                            try:
                                m = networkContainerInfo["extattrs"]["Mask"]["value"]
                            except Exception:
                                raise CustomException(status=400, payload={"message": "Mask value not set in the Infoblox's network's extensible attributes."})

                            try:
                                g = networkContainerInfo["extattrs"]["Gateway"]["value"]
                            except Exception:
                                g = ""

                            o = {
                                "networkLogic": "container",
                                "mask": m,
                                "gateway": g,
                                "network_container": networkInformation.network_container
                            }

                            Log.log("Network information: "+str(o))
                            return o

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
                    # Get all innerNetworks in the network container.
                    n, m = networkContainer.split('/')

                    netContainer = NetworkContainer(assetId, n+"/"+m)
                    subnetworks = netContainer.innerNetworks(
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

                    allSubnetworks = sorted(allSubnetworks, key=lambda item: socket.inet_aton(item))  # order subnetworks.

        except Exception:
            raise CustomException(status=400, payload={"message": "No network found."})

        if not allSubnetworks:
            raise CustomException(status=400, payload={"message": "No network found: make sure that Object Type is valid, if required."})
        else:
            Log.log("All subnetworks: "+str(allSubnetworks))

        return allSubnetworks



    @staticmethod
    def getNextAvailableIpv4Addresses(assetId: int, networkLogic: str, targetNetwork: str, networkContainer: str, number, objectType) -> tuple:
        # Get the next available IP address within allSubnetworks.
        # Select the first IPv4 among them which is:
        # * unused or used but with usage == "DNS" (only "DNS")
        # * not ending in 0 or 255.
        allSubnetworks = Network.getTargetSubnetworks(assetId, networkLogic, targetNetwork, networkContainer, objectType)

        try:
            for n in allSubnetworks:
                # Find the first <number> free IPv4(s) in the subnet.
                netObj = Network(assetId, n)
                addresses = netObj.findFirstIpByAttrs(number)

                if len(addresses) == number:
                    return n, addresses
        except Exception as e:
            raise CustomException(status=400, payload={"message": "Cannot get next available IPv4 address: "+e.payload})

        raise CustomException(status=400, payload={"message": "No available IPv4 addresses found."})



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __load(self) -> None:
        try:
            data = Connector.get(self.asset_id, self.network)
            for k, v in data.items():
                setattr(self, k, v)
        except Exception as e:
            raise e
