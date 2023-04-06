from typing import List, Dict

from infoblox.models.Infoblox.connectors.Ipv4 import Ipv4 as Connector

from infoblox.helpers.Exception import CustomException


Value: Dict[str, str] = {"value": ""}

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
        self.objects: List[dict] = [] # fixedaddress, record:host, ptr ...
        self.types: List[str] = []
        self.usage: List[str] = []
        self.extattrs: Dict[str, Dict[str, str]] = {
            "Gateway": Value,
            "Mask": Value,
            "Reference": Value,
            "Name Server": Value
        }

        self.__load()



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def modify(self, data: dict) -> None:
        extraAttributes = dict()

        try:
            # No PATCH API available: delete and reserve needed (@todo: ?).
            # Delete the IPv4 (fixedaddressOnly).
            self.release(fixedaddressOnly=True)

            try:
                # Re-add with union data (data values overwrite ye olde ones).
                for k, v in self.extattrs.items():
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
                    "mac": self.mac_address or "00:00:00:00:00:00",
                    "extattrs": self.extattrs
                })

                raise e

            self.__load()
        except Exception as e:
            raise e



    def release(self, fixedaddressOnly: bool = True) -> None:
        fixedaddress = ""

        try:
            # Reference to the IP "slot".
            ref = self._ref

            # Reference to IP data.
            for el in self.objects:
                if "_ref" in el:
                    if "fixedaddress" in el["_ref"]:
                        fixedaddress = el["_ref"]
                        break

            if not fixedaddress:
                raise CustomException(status=404, payload={})
            else:
                # Release ref (the "slot") or fixedaddress ("content").
                if fixedaddressOnly:
                    ref = fixedaddress # release only the fixedaddress data.

                Connector.deleteReferencedObject(self.asset_id, ref)

            self.__load()
        except Exception as e:
            raise e



    def repr(self) -> dict:
        try:
            return vars(self)
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def reserve(assetId, data: dict) -> dict:
        try:
            return Connector.reserveFixedAddress(assetId, data)
        except Exception as e:
            raise e



    @staticmethod
    def reserveNextAvailable(assetId: int, address: str, extattrs: dict, mac: str, options: list = None) -> dict:
        options = options or []
        try:
            # @todo: atomicity?

            try:
                # Delete the address' information regarding the fixedaddress value, if available.
                ipv4 = Ipv4(assetId, address)
                ipv4.release(fixedaddressOnly=True)
            except Exception:
                pass

            # Add the fixed address reservation with extensible attributes.
            return Ipv4.reserve(assetId, {
                "ipv4addr": address,
                "mac": mac,
                "extattrs": extattrs,
                "options": options
            })

        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __load(self) -> None:
        try:
            data = Connector.get(self.asset_id, self.ip_address)
            for k, v in data.items():
                setattr(self, k, v)
        except Exception as e:
            raise e
