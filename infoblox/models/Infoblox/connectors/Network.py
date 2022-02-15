from infoblox.models.Infoblox.Asset.Asset import Asset

from infoblox.helpers.ApiSupplicant import ApiSupplicant
from infoblox.helpers.Log import Log


class Network:

    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def get(assetId, network, filter: dict = None, silent: bool = False) -> dict:
        filter = {} if filter is None else filter

        try:
            apiParams = {
                "network": network,
                "_max_results": 65535,
                "_return_fields+": "network,network_container,extattrs"
            }

            if filter:
                apiParams.update(filter)

            infoblox = Asset(assetId)
            api = ApiSupplicant(
                endpoint=infoblox.baseurl+"/network",
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
    def addresses(assetId, network, maxResults, fromIp, toIp) -> dict:
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



    @staticmethod
    def list(assetId: int) -> dict:
        try:
            apiParams = {
                "_max_results": 65535,
                "_return_fields+": "network,network_container,extattrs"
            }

            infoblox = Asset(assetId)
            api = ApiSupplicant(
                endpoint=infoblox.baseurl+"/network",
                params=apiParams,
                auth=(infoblox.username, infoblox.password),
                tlsVerify=infoblox.tlsverify
            )

            return api.get()
        except Exception as e:
            raise e
