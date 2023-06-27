import json

from infoblox.models.Asset.Asset import Asset

from infoblox.helpers.ApiSupplicant import ApiSupplicant


class Network:

    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def get(assetId: int, network: str, filter: dict = None, silent: bool = False) -> dict:
        filter = {} if filter is None else filter

        try:
            apiParams = {
                "network": network,
                "_max_results": 65535,
                "_return_fields+": "network,network_container,vlans,options,extattrs"
            }

            if filter:
                apiParams.update(filter)

            infoblox = Asset(assetId)
            api = ApiSupplicant(
                endpoint=infoblox.baseurl+"network",
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
                tlsVerify=infoblox.tlsverify,
                silent=silent
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
                silent=silent
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
                endpoint=infoblox.baseurl+"ipv4address",
                params=apiParams,
                auth=(infoblox.username, infoblox.password),
                tlsVerify=infoblox.tlsverify
            )

            return api.get()
        except Exception as e:
            raise e



    @staticmethod
    def list(assetId: int, filter: dict = None, silent: bool = False) -> list:
        filter = filter or {}

        apiParams = {
            "_max_results": 65535,
            "_return_fields+": "network,network_container,vlans,extattrs"
        }

        if filter:
            apiParams.update(filter)

        try:
            infoblox = Asset(assetId)
            api = ApiSupplicant(
                endpoint=infoblox.baseurl+"network",
                params=apiParams,
                auth=(infoblox.username, infoblox.password),
                tlsVerify=infoblox.tlsverify,
                silent=silent
            )

            return api.get()
        except Exception as e:
            raise e



    @staticmethod
    def add(assetId: int, data: dict, silent: bool = False) -> str:

        try:
            infoblox = Asset(assetId)
            api = ApiSupplicant(
                endpoint=infoblox.baseurl+"network",
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
