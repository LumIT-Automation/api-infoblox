import ipaddress


class Network:
    @staticmethod
    def isSubnetInNetwork(subnetCidr: str, networkCidr: str) -> bool:
        return ipaddress.ip_network(subnetCidr).subnet_of(ipaddress.ip_network(networkCidr))



    @staticmethod
    def isIpv4InNetwork(address: str, networkCidr: str) -> bool:
        return ipaddress.ip_address(address) in ipaddress.ip_network(networkCidr)
