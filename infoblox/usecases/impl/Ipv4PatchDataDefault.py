from infoblox.usecases.impl.Ipv4PatchData import Ipv4PatchData


class  Ipv4PatchDataDefault(Ipv4PatchData):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def isIpv4Unused(ipAddressData: dict, scope: str = "status") -> bool:
        try:
            if "status" in ipAddressData and ipAddressData["status"] == "UNUSED":
                return True
            else:
                return False
        except Exception as e:
            raise e



    @staticmethod
    def patchInfoData(data: dict) -> dict:
        try:
            return data
        except Exception as e:
            raise e
