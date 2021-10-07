import ipaddress
import json

from infoblox.models.Infoblox.Asset.Asset import Asset
from infoblox.helpers.ApiSupplicant import ApiSupplicant

from infoblox.models.Infoblox.Network import Network
from infoblox.models.Infoblox.NetworkContainer import NetworkContainer

from infoblox.helpers.Exception import CustomException
from infoblox.helpers.Log import Log


class Ipv4:
    def __init__(self, assetId: int, address: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.assetId = int(assetId)
        self.address = address



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def info(self, additionalFields: dict = {}, returnFields: list = [], silent: bool = False) -> dict:
        o = dict()

        try:
            apiParams = {
                "ip_address": self.address
            }

            if additionalFields:
                apiParams = {**apiParams, **additionalFields} # merge dicts.

            if returnFields:
                fields = ','.join(returnFields)
                apiParams["_return_fields+"] = fields

            infoblox = Asset(self.assetId)
            asset = infoblox.info()

            api = ApiSupplicant(
                endpoint=asset["baseurl"]+"/ipv4address",
                params=apiParams,
                auth=asset["auth"],
                tlsVerify=asset["tlsverify"],
                silent=silent
            )

            o["data"] = api.get()[0]
        except Exception as e:
            raise e

        return o



    def modify(self, data: dict) -> None:
        extraAttributes = dict()

        try:
            # Read IPv4 address' extra attributes from Infoblox.
            ipInformation = self.info(
                returnFields=["network", "extattrs"]
            )["data"]

            if "extattrs" in ipInformation:
                for k, v in ipInformation["extattrs"].items():
                    extraAttributes[k] = v["value"]

            # Delete the IPv4 (fixedaddressOnly).
            self.release(fixedaddressOnly=True)

            # Re-add with union data.
            for k, v in extraAttributes.items():
                if k not in data["extattrs"]:
                    data["extattrs"][k] = {
                        "value": v
                    }

            data["ipv4addr"] = self.address
            data["mac"] = "00:00:00:00:00:00"

            Ipv4.reserve(self.assetId, data)

            # @todo: if re-add fails...

        except Exception as e:
            raise e



    def release(self, fixedaddressOnly: bool = False) -> None:
        ref = ""
        fixedaddress = ""

        try:
            ipv4Data = self.info()["data"]

            # Reference to "IP slot".
            if "_ref" in ipv4Data: # _ref as dict key.
                ref = ipv4Data["_ref"]

            # Reference to IP data.
            if "objects" in ipv4Data and isinstance(ipv4Data["objects"], list):
                for el in ipv4Data["objects"]:
                    if "fixedaddress" in el:
                        fixedaddress = el

            if not fixedaddress:
                raise CustomException(status=404, payload={})
            else:
                # Release ref (by default) or fixedaddress.
                if fixedaddressOnly:
                    ref = fixedaddress # release only the fixedaddress data.

                infoblox = Asset(self.assetId)
                asset = infoblox.info()

                apiParams = {
                    "_return_as_object": 1
                }

                api = ApiSupplicant(
                    endpoint=asset["baseurl"]+"/"+ref,
                    auth=asset["auth"],
                    params=apiParams,
                    tlsVerify=asset["tlsverify"]
                )

                api.delete()
        except Exception as e:
            raise e



    def network(self) -> str:
        try:
            # First check if the ip address belongs to a network container. If so, check in the child networks.
            netContainer = Ipv4.__getNetwork(self.address, NetworkContainer.list(self.assetId)["data"])

            if netContainer:
                # Now look into the network container to find the right network.
                netC, netCMask = netContainer.split("/")
                nC = NetworkContainer(self.assetId, netC, netCMask)
                netList = nC.subnetsList()["data"]
                network = Ipv4.__getNetwork(self.address, netList)
            else:
                # If the ip don't belong to any network container maybe is in a standalone network.
                # Unfortunately the network_container filter breaks if when using the root network container ("/"). The call below currently does't work.
                # (https://community.infoblox.com/t5/API-Integration/List-of-Top-Level-Networks-using-Rest-API/m-p/1417/highlight/true#M41)
                # netList = Network.list(self.assetId, additionalFields=["network_container"], attrsFilter={"network_container": "/"})
                # So we are forced to search in all networks
                netList = Network.list(self.assetId)["data"]
                network = Ipv4.__getNetwork(self.address, netList)
        except Exception:
            raise CustomException(status=500, payload={"message": "Error on find the network of the ip address."})

        return network



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def reserve(assetId, data: dict) -> dict:
        try:
            infoblox = Asset(assetId)
            asset = infoblox.info()

            api = ApiSupplicant(
                endpoint=asset["baseurl"]+"/fixedaddress?_return_as_object=1",
                auth=asset["auth"],
                tlsVerify=asset["tlsverify"]
            )

            o = api.post(
                additionalHeaders={
                    "Content-Type": "application/json",
                },
                data=json.dumps(data)
            )
        except Exception as e:
            raise e

        return o



    @staticmethod
    def reserveNextAvailable(assetId: int, address: str, data: dict, mac: str) -> object:
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
                "extattrs": data["extattrs"]
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
