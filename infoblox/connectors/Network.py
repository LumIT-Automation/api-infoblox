from infoblox.models.Infoblox.Asset.Asset import Asset

from infoblox.helpers.ApiSupplicant import ApiSupplicant


class Network:

    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def get(assetId, network, filter: dict = {}, silent: bool = False) -> dict:
        try:
            apiParams = {
                "network": network,
                "_max_results": 65535
            }

            returnFields = ["network", "network_container", "extattrs"]

            fields = ','.join(returnFields)
            apiParams["_return_fields+"] = fields

            if filter:
                apiParams = {**apiParams, **filter} # merge dicts.

            infoblox = Asset(assetId)
            infoblox.load()

            api = ApiSupplicant(
                endpoint=infoblox.baseurl+"/network",
                params=apiParams,
                auth=(infoblox.username, infoblox.password),
                tlsVerify=infoblox.tlsverify,
                silent=silent
            )

            return api.get()
        except Exception as e:
            raise e



    @staticmethod
    def addresses(assetId, network, additionalFields: dict = {}, returnFields: list = [], silent: bool = False) -> dict:
        try:
            apiParams = {
                "network": network
            }

            if additionalFields:
                apiParams = {**apiParams, **additionalFields} # merge dicts.

            if returnFields:
                fields = ','.join(returnFields)
                apiParams["_return_fields+"] = "ip_address,status,usage," + fields 

            infoblox = Asset(assetId)
            infoblox.load()

            api = ApiSupplicant(
                endpoint=infoblox.baseurl+"/ipv4address",
                params=apiParams,
                auth=(infoblox.username, infoblox.password),
                tlsVerify=infoblox.tlsverify,
                silent=silent
            )

            return api.get()
        except Exception as e:
            raise e



    @staticmethod
    def list(assetId: int, additionalFields: dict = {}, returnFields: list = []) -> dict:
        try:
            apiParams = {
                "_max_results": 65535
            }

            if additionalFields:
                apiParams = {**apiParams, **additionalFields} # merge dicts.

            if returnFields:
                fields = ','.join(returnFields)
                apiParams["_return_fields+"] = fields 

            infoblox = Asset(assetId)
            infoblox.load()

            api = ApiSupplicant(
                endpoint=infoblox.baseurl+"/network",
                params=apiParams,
                auth=(infoblox.username, infoblox.password),
                tlsVerify=infoblox.tlsverify
            )

            return api.get()
        except Exception as e:
            raise e
