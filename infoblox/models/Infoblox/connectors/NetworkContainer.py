from infoblox.models.Infoblox.Asset.Asset import Asset

from infoblox.helpers.ApiSupplicant import ApiSupplicant
from infoblox.helpers.Log import Log


class NetworkContainer:

    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def get(assetId: int, container: str, filter: dict = {}) -> dict:
        apiParams = {
            "network": container
        }

        returnFields = ["network", "network_container", "extattrs"]

        fields = ','.join(returnFields)
        apiParams["_return_fields+"] = fields

        if filter:
            apiParams = {**apiParams, **filter} # merge dicts.

        try:
            infoblox = Asset(assetId)
            api = ApiSupplicant(
                endpoint=infoblox.baseurl+"/networkcontainer",
                params=apiParams,
                auth=(infoblox.username, infoblox.password),
                tlsVerify=infoblox.tlsverify
            )

            return api.get()
        except Exception as e:
            raise e



    @staticmethod
    def networks(assetId: int, container: str, filter: dict = {}) -> dict:
        apiParams = {
            "network_container": container
        }

        returnFields = ["network", "network_container", "extattrs"]

        fields = ','.join(returnFields)
        apiParams["_return_fields+"] = fields

        if filter:
            apiParams = {**apiParams, **filter} # merge dicts.

        try:
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



    @staticmethod
    def list(assetId: int) -> dict:
        try:
            apiParams = {
                "_max_results": 65535
            }

            returnFields = ["network", "network_container", "extattrs"]

            fields = ','.join(returnFields)
            apiParams["_return_fields+"] = fields

            infoblox = Asset(assetId)
            api = ApiSupplicant(
                endpoint=infoblox.baseurl+"/networkcontainer",
                params=apiParams,
                auth=(infoblox.username, infoblox.password),
                tlsVerify=infoblox.tlsverify
            )

            return api.get()
        except Exception as e:
            raise e
