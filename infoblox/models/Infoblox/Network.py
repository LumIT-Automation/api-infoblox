import re
import socket
import ipaddress

from infoblox.models.Infoblox.NetworkContainer import NetworkContainer
from infoblox.models.Infoblox.Asset.Asset import Asset

from infoblox.helpers.ApiSupplicant import ApiSupplicant
from infoblox.helpers.Exception import CustomException
from infoblox.helpers.Log import Log


class Network:
    def __init__(self, assetId: int, userNetwork: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.assetId = int(assetId)
        self.userNetwork = userNetwork



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def info(self, additionalFields: dict = {}, returnFields: list = [], silent: bool = False) -> dict:
        o = dict()

        try:
            apiParams = {
                "network": self.userNetwork,
                "_max_results": 65535
            }

            if additionalFields:
                apiParams = {**apiParams, **additionalFields} # merge dicts.

            if returnFields:
                fields = ','.join(returnFields)
                apiParams["_return_fields+"] = fields 

            infoblox = Asset(self.assetId)
            infoblox.load()

            api = ApiSupplicant(
                endpoint=infoblox.baseurl+"/network",
                params=apiParams,
                auth=(infoblox.username, infoblox.password),
                tlsVerify=infoblox.tlsverify,
                silent=silent
            )
            o["data"] = api.get()
        except Exception as e:
            raise e

        return o



    def ipv4(self, additionalFields: dict = {}, returnFields: list = [], silent: bool = False) -> dict:
        o = dict()

        try:
            apiParams = {
                "network": self.userNetwork
            }

            if additionalFields:
                apiParams = {**apiParams, **additionalFields}  # merge dicts.

            if returnFields:
                fields = ','.join(returnFields)
                apiParams["_return_fields+"] = "ip_address,status,usage," + fields 

            infoblox = Asset(self.assetId)
            infoblox.load()

            api = ApiSupplicant(
                endpoint=infoblox.baseurl+"/ipv4address",
                params=apiParams,
                auth=(infoblox.username, infoblox.password),
                tlsVerify=infoblox.tlsverify,
                silent=silent
            )

            o["data"] = api.get()
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
            networkInformation = Network(assetId, userNetwork).info(
                returnFields=["network_container"]
            )["data"]

            if isinstance(networkInformation, list):
                networkInformation = networkInformation[0]

                if "network" not in networkInformation \
                        or "network_container" not in networkInformation:
                    raise CustomException(status=400, payload={"message": "Cannot read network information."})

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

                networkInfoList = Network(assetId, networkInformation["network"]).info(
                    additionalFields={
                      "*Real Network": "yes"
                    },
                    returnFields=["extattrs"]
                )["data"]

                if isinstance(networkInfoList, list) and len(networkInfoList) > 0 and "network" in networkInfoList[0]:
                    networkInfo = networkInfoList[0]

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

                    if networkInfo["network"]:
                        try:
                            m = networkInfo["extattrs"]["Mask"]["value"]
                        except Exception:
                            raise CustomException(status=400, payload={"message": "Mask value not set in the Infoblox's network's extensible attributes."})

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
                    if networkInformation["network_container"] != "/":
                        if "/" in networkInformation["network_container"]:
                            n, m = networkInformation["network_container"].split("/")

                            networkContainerInfoList = NetworkContainer(assetId, n, m).info(
                                additionalFields={
                                    "*Real Network": "yes"
                                },
                                returnFields=[
                                    "network_container",
                                    "extattrs"
                                ]
                            )["data"]

                            if isinstance(networkContainerInfoList, list) and len(networkContainerInfoList) > 0 and "extattrs" in networkContainerInfoList[0]:
                                networkContainerInfo = networkContainerInfoList[0]

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

                                if networkContainerInfo["network"]:
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
                                        "network_container": networkInformation["network_container"]
                                    }

                                    Log.log("Network information: "+str(o))
                                    return o

            raise CustomException(status=400, payload={"message": "Cannot discriminate network."})

        except Exception as e:
            raise CustomException(status=400, payload={"message": "Cannot discriminate network: "+str(e.payload)})



    @staticmethod
    def getTargetSubnetworks(assetId: int, networkLogic: str, targetNetwork: str, networkContainer: str, objectType: str = "") -> list:
        allSubnetworks = list()

        # If networkLogic == "network" -> targetNetworkInformation["targetNetwork"]
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

                    netContainer = NetworkContainer(assetId, n, m)
                    subnetworks = netContainer.innerNetworks(
                        additionalFields={
                            "*Object Type": objectType,
                            "_return_as_object": 1
                        }
                    )["data"]["result"]
                    
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
            Log.log("All subnetworks: " + str(allSubnetworks))

        return allSubnetworks



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
            condition = condition + " and " + checkAttrs

        try:
            networkCidr = self.info()["data"][0]["network"]
            n, mask = networkCidr.split('/')

            # There can be many IP addresses here.
            # Use ipaddress library to split the ip list in ranges of max 100 in order to make smaller calls.
            ipaddressNetworkObj = ipaddress.ip_network(networkCidr)
            ipList = list(ipaddressNetworkObj.hosts())

            if int(mask) > 22:
                ipListChunks = [ipList[x:x+100] for x in range(0, len(ipList), 100)]
            else:
                ipListChunks = [ipList[x:x + 500] for x in range(0, len(ipList), 500)]

            for chunk in ipListChunks:
                startIp = chunk[0]
                endIp = chunk[-1]

                addresses = self.ipv4(
                    additionalFields={
                        "_max_results": 100,
                        "ip_address>": startIp,
                        "ip_address<": endIp
                    },
                    silent=True
                )["data"]

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



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(assetId: int, additionalFields: dict = {}, returnFields: list = [], silent: bool = False) -> dict:
        o = dict()

        try:
            apiParams = {
                "_max_results": 65535
            }

            if additionalFields:
                apiParams = {**apiParams, **additionalFields}  # merge dicts.

            if returnFields:
                fields = ','.join(returnFields)
                apiParams["_return_fields+"] = fields 

            infoblox = Asset(assetId)
            infoblox.load()

            api = ApiSupplicant(
                endpoint=infoblox.baseurl+"/network",
                params=apiParams,
                auth=(infoblox.username, infoblox.password),
                tlsVerify=infoblox.tlsverify
            )

            o["data"] = api.get()
        except Exception as e:
            raise e

        return o
