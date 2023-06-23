from infoblox.models.Asset.Asset import Asset

from infoblox.helpers.ApiSupplicant import ApiSupplicant


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
                endpoint=infoblox.baseurl+"range",
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
                endpoint=infoblox.baseurl+"range",
                params=apiParams,
                auth=(infoblox.username, infoblox.password),
                tlsVerify=infoblox.tlsverify,
                silent=silent
            )

            return api.get()
        except Exception as e:
            raise e
