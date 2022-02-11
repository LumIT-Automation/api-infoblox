import ipaddress

from infoblox.models.Infoblox.Network import Network
from infoblox.models.Infoblox.NetworkContainer import NetworkContainer

from infoblox.helpers.Exception import CustomException
from infoblox.helpers.Log import Log

from infoblox.models.Infoblox.connectors.Ipv4 import Ipv4 as Connector


class Ipv4:
    def __init__(self, assetId: int, address: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.asset_id = int(assetId)
        self.ip_address = address

        self._ref = ""
        self.network = ""
        self.network_view = ""
        self.mac_address = ""
        self.status = ""
        self.is_conflict = False
        self.names = list()
        self.objects = list()
        self.types = list()
        self.usage = list()
        self.extattrs = dict()



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def info(self) -> dict:
        try:
            return Connector.get(self.asset_id, self.ip_address)
        except Exception as e:
            raise e



    def modify(self, data: dict) -> None:
        extraAttributes = dict()

        try:
            # Read IPv4 address' extra attributes from Infoblox.
            ipv4 = self.info()
            if "extattrs" in ipv4:
                for k, v in ipv4["extattrs"].items():
                    extraAttributes[k] = v["value"]

            # No PATCH API available: delete and reserve.
            # Delete the IPv4 (fixedaddressOnly).
            self.release(fixedaddressOnly=True)

            try:
                # Re-add with union data (data values overwrite ye olde ones).
                data["ipv4addr"] = self.ip_address
                for k, v in extraAttributes.items():
                    if k not in data["extattrs"]:
                        data["extattrs"][k] = {
                            "value": v
                        }

                Ipv4.reserve(self.asset_id, data)
            except Exception as e:
                # Restore the old one.
                Ipv4.reserve(self.asset_id, {
                    "ipv4addr": self.ip_address,
                    "mac": ipv4["mac_address"] or "00:00:00:00:00:00",
                    "extattrs": ipv4["extattrs"]
                })

                raise e
        except Exception as e:
            raise e



    def release(self, fixedaddressOnly: bool = False) -> None:
        ref = ""
        fixedaddress = ""

        try:
            ipv4 = self.info()

            # Reference to the IP "slot".
            if "_ref" in ipv4:
                ref = ipv4["_ref"]

            # Reference to IP data.
            if "objects" in ipv4 and isinstance(ipv4["objects"], list):
                for el in ipv4["objects"]:
                    if "fixedaddress" in el:
                        fixedaddress = el
                        break

            if not fixedaddress:
                raise CustomException(status=404, payload={})
            else:
                # Release ref (the "slot") or fixedaddress ("content").
                if fixedaddressOnly:
                    ref = fixedaddress # release only the fixedaddress data.

                Connector.delete(self.asset_id, ref)
        except Exception as e:
            raise e



    def getNetwork(self) -> str:
        try:
            # First check if the ip address belongs to a network container. If so, check in the child networks.
            netContainer = Ipv4.__getNetwork(self.ip_address, NetworkContainer.list(self.asset_id)["data"])

            if netContainer:
                # Now look into the network container to find the right network.
                netC, netCMask = netContainer.split("/")
                nC = NetworkContainer(self.asset_id, netC + "/" + netCMask)
                netList = nC.innerNetworks()["data"]
                network = Ipv4.__getNetwork(self.ip_address, netList)
            else:
                # If the ip does not belong to any network container maybe is in a standalone network.
                # Unfortunately the network_container filter breaks when using the root network container ("/"). The call below currently doesn't work.
                # (https://community.infoblox.com/t5/API-Integration/List-of-Top-Level-Networks-using-Rest-API/m-p/1417/highlight/true#M41)
                # netList = Network.list(self.assetId, additionalFields=["network_container"], attrsFilter={"network_container": "/"})
                # So we are forced to search in all networks.
                netList = Network.list(self.asset_id)["data"]
                network = Ipv4.__getNetwork(self.ip_address, netList)
        except Exception:
            raise CustomException(status=500, payload={"message": "Error on find the network of the ip address."})

        return network



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def reserve(assetId, data: dict) -> dict:
        try:
            return Connector.reserve(assetId, data)
        except Exception as e:
            raise e



    @staticmethod
    def reserveNextAvailable(assetId: int, address: str, extattrs: dict, mac: str) -> object:
        try:
            # If address is already reserved (but usable -> "DNS"), a fixedaddress information is present.
            # Delete the address' information regarding the fixedaddress value, if available.

            # @todo: atomicity is a dream here. Do something...
            try:
                ipv4 = Ipv4(assetId, address)
                ipv4.release(fixedaddressOnly=True)
            except Exception:
                pass

            # Add the fixed address reservation with extensible attributes.
            return Ipv4.reserve(assetId, {
                "ipv4addr": address,
                "mac": mac,
                "extattrs": extattrs
            })

        except Exception as e:
            raise e



    @staticmethod
    def ipv4InNetwork(address: str, network_cidr: str) -> bool:
        return ipaddress.ip_address(address) in ipaddress.ip_network(network_cidr)



    @staticmethod
    def subnetInNetwork(subnet_cidr: str, network_cidr: str) -> bool:
        return ipaddress.ip_network(subnet_cidr).subnet_of(ipaddress.ip_network(network_cidr))



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
    # Private static methods
    ####################################################################################################################

    @staticmethod
    def __getNetwork(address: str, networks: list) -> str:
        network = ""
        for net in networks:
            if "network" in net:
                if Ipv4.ipv4InNetwork(address, net["network"]):
                    network = net["network"]

                    Log.log("Ip address "+str(address)+" belongs to network or network container "+str(network), "Ipv4 method: __isAddressInNetworkList")
                    break

        return network
