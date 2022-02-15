from typing import List, Dict

from infoblox.models.Infoblox.connectors.Ipv4 import Ipv4 as Connector

from infoblox.helpers.Exception import CustomException
from infoblox.helpers.Log import Log


class Ipv4:
    def __init__(self, assetId: int, address: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.asset_id: int = int(assetId)
        self.ip_address: str = address
        self.ipv4Addr: str = address # alternative in Infoblox model.

        self._ref: str = ""
        self.network: str = ""
        self.network_view: str = ""
        self.mac_address: str = ""
        self.mac: str = "" # alternative in Infoblox model.
        self.status: str = ""
        self.is_conflict: bool = False
        self.names: List[str] = []
        self.objects: List[str] = []
        self.types: List[str] = []
        self.usage: List[str] = []
        self.extattrs: Dict[str, Dict[str, str]] = {
            "Gateway": { "value": "" },
            "Mask": { "value": "" },
            "Reference": { "value": "" },
            "Name Server": { "value": "" }
        }



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
            ipv4 = self.info()

            # No PATCH API available: delete and reserve needed.
            # Delete the IPv4 (fixedaddressOnly).
            self.release(fixedaddressOnly=True)

            try:
                # Re-add with union data (data values overwrite ye olde ones).
                if "extattrs" in ipv4:
                    for k, v in ipv4["extattrs"].items():
                        extraAttributes[k] = v["value"]

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
            # @todo: atomicity?

            try:
                # If address is already reserved (but usable -> "DNS"), a fixedaddress information is present.
                # Delete the address' information regarding the fixedaddress value, if available.
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
