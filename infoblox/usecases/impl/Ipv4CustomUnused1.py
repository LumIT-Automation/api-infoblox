import re
from django.conf import settings

from infoblox.usecases.impl.Ipv4Unused import Ipv4Unused


from infoblox.helpers.Exception import CustomException
from infoblox.helpers.Log import Log


class  Ipv4CustomUnused1(Ipv4Unused):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def isUnused(ipAddressData: dict, ipOnARange: bool = False, scope: str = "status") -> bool:
        unused = False

        try:
            if "ip_address" and "status" in ipAddressData:
                if ipOnARange and ipAddressData["status"] == "UNUSED" and "types" in ipAddressData and  ipAddressData["types"] == ["RESERVED_RANGE"]:
                    unused = True
                elif (ipAddressData["status"] == "UNUSED" or ("usage" in ipAddressData and ipAddressData["usage"] == ["DNS"])):
                    # For DNS usage the condition is on ipAddressData["types"]: at least one value from ["HOST", "A", "PTR"]
                    # and not any other value.
                    if ("types" not in ipAddressData or not ipAddressData["types"]) or \
                        "usage" in ipAddressData and ipAddressData["usage"] == ["DNS"] and ("types" in ipAddressData and (
                            any(addrType for addrType in ["HOST", "A", "PTR"] if addrType in ipAddressData["types"]) and
                            not [ addrType for addrType in ipAddressData["types"] if addrType not in ["HOST", "A", "PTR"] ]
                        )
                    ):
                        unused = True

                # addresses in a DHCP range can be "unused" but not suitable for a "next-available" scope.
                if scope == "status":
                    if "usage" in ipAddressData and "DHCP" in ipAddressData["usage"]:
                        if "types" in ipAddressData and "LEASE" in ipAddressData["types"] and "DHCP_RANGE" in ipAddressData["types"]:
                            unused = True

            return unused
        except Exception as e:
            raise e
