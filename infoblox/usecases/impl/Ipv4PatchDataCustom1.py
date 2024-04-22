from infoblox.usecases.impl.Ipv4PatchData import Ipv4PatchData



class  Ipv4PatchDataCustom1(Ipv4PatchData):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def isIpv4Unused(ipAddressData: dict, scope: str = "status") -> bool:
        unused = False

        try:
            # Both "status" and "next-available" scope.
            if "ip_address" and "status" in ipAddressData:
                if ipAddressData["status"] == "UNUSED" and "types" in ipAddressData and  ipAddressData["types"] == ["RESERVED_RANGE"]: # range condition.
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



    @staticmethod
    def patchInfoData(data: dict) -> dict:
        data = data

        try:
            if  Ipv4PatchDataCustom1.isIpv4Unused(ipAddressData=data, scope="status"):
                data["status"] = "UNUSED"

            if "RESERVED_RANGE" in data.get("types", []):
                objects = data.get("objects", [])
                for obj in objects:
                    if "fixedaddress" in obj.get("_ref", ""):
                        referenceList = obj.get("extattrs", {}).get("Reference", {}).get("value", "").split(", ")
                        if len(referenceList) >= 3:
                            data["extattrs"]["Reference"]["value"] = data["extattrs"]["Reference"]["value"] + ", " + referenceList[0]
                            obj["extattrs"]["Reference"]["value"] = ", ".join(referenceList[1:])
            else:
                if "Reference" in data.get("extattrs", {}):
                    data["extattrs"]["Reference"] = {"value": ""}

            return data
        except Exception as e:
            raise e



