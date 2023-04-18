import json

from infoblox.models.Infoblox.Asset.Asset import Asset

from infoblox.helpers.ApiSupplicant import ApiSupplicant
from infoblox.helpers.Log import Log


class Range:

    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def get(assetId: int, start_addr: str, end_addr: str, filter: dict = None, silent: bool = False) -> dict:
        filter = filter or {}

        try:
            apiParams = {
                "start_addr": start_addr,
                "end_addr": end_addr,
                "_max_results": 65535,
                "_return_fields+": "network,options,extattrs"
            }

            if filter:
                apiParams.update(filter)

            infoblox = Asset(assetId)
            api = ApiSupplicant(
                endpoint=infoblox.baseurl+"/range",
                params=apiParams,
                auth=(infoblox.username, infoblox.password),
                tlsVerify=infoblox.tlsverify,
                silent=silent
            )

            n = api.get()
            if isinstance(n, list) and len(n) > 0:
                return n[0]
            else:
                return n
        except Exception as e:
            raise e


    """
    @staticmethod
    def modify(assetId: int, _ref: str, data: dict, silent: bool = False) -> dict:
        apiParams = {
            "_max_results": 65535,
            "_return_fields+": "network,network_container,vlans,options,extattrs"
        }

        try:
            infoblox = Asset(assetId)
            api = ApiSupplicant(
                endpoint=infoblox.baseurl + "/" + _ref,
                params=apiParams,
                auth=(infoblox.username, infoblox.password),
                tlsVerify = infoblox.tlsverify,
                silent = silent
            )

            return api.put(
                additionalHeaders={
                    "Content-Type": "application/json",
                },
                data=json.dumps(data)
            )
        except Exception as e:
            raise e



    @staticmethod
    def delete(assetId: int, _ref: str, silent: bool = False):
        try:
            infoblox = Asset(assetId)
            api = ApiSupplicant(
                endpoint=infoblox.baseurl + "/" + _ref,
                auth=(infoblox.username, infoblox.password),
                tlsVerify=infoblox.tlsverify,
                silent = silent
            )

            api.delete()
        except Exception as e:
            raise e



    @staticmethod
    def addresses(assetId: int, network: str, maxResults: int, fromIp: str, toIp: str) -> dict:
        try:
            apiParams = {
                "network": network
            }

            if maxResults and fromIp and toIp:
                additionalFields = {
                    "_max_results": maxResults,
                    "ip_address>": fromIp,
                    "ip_address<": toIp
                }

                apiParams.update(additionalFields)

            infoblox = Asset(assetId)
            api = ApiSupplicant(
                endpoint=infoblox.baseurl+"/ipv4address",
                params=apiParams,
                auth=(infoblox.username, infoblox.password),
                tlsVerify=infoblox.tlsverify
            )

            return api.get()
        except Exception as e:
            raise e
    """


    @staticmethod
    def list(assetId: int, filter: dict = None, silent: bool = False) -> list:
        filter = filter or {}
        # Example: get only ranges in network 10.8.1.0/24":
        # filter = {"network": "10.8.1.0/24"}

        apiParams = {
            "_max_results": 65535,
            "_return_fields+": "network,extattrs"
        }

        if filter:
            apiParams.update(filter)

        try:
            infoblox = Asset(assetId)
            api = ApiSupplicant(
                endpoint=infoblox.baseurl+"/range",
                params=apiParams,
                auth=(infoblox.username, infoblox.password),
                tlsVerify=infoblox.tlsverify,
                silent = silent
            )

            return api.get()
        except Exception as e:
            raise e


    """
    @staticmethod
    def add(assetId: int, data: dict, silent: bool = False) -> dict:

        try:
            infoblox = Asset(assetId)
            api = ApiSupplicant(
                endpoint=infoblox.baseurl+"/network",
                params={
                    "_max_results": 65535,
                    "_return_fields+": "network,network_container,extattrs"
                },
                auth=(infoblox.username, infoblox.password),
                tlsVerify=infoblox.tlsverify,
                silent=silent
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
    """