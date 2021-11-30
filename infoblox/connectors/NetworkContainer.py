from infoblox.models.Infoblox.Asset.Asset import Asset

from infoblox.helpers.ApiSupplicant import ApiSupplicant
from infoblox.helpers.Log import Log


class NetworkContainer:

    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def get(assetId: int, container: str, additionalFields: dict = {}, returnFields: list = []) -> dict:
        apiParams = {
            "network": container
        }

        if additionalFields:
            apiParams = {**apiParams, **additionalFields} # merge dicts.

        if returnFields:
            fields = ','.join(returnFields)
            apiParams["_return_fields+"] = fields

        try:
            infoblox = Asset(assetId)
            infoblox.load()

            api = ApiSupplicant(
                endpoint=infoblox.baseurl + "/networkcontainer",
                params=apiParams,
                auth=(infoblox.username, infoblox.password),
                tlsVerify=infoblox.tlsverify
            )

            return api.get()
        except Exception as e:
            raise e



    @staticmethod
    def networks(assetId: int, container: str, additionalFields: dict = {}, returnFields: list = []) -> dict:
        apiParams = {
            "network_container": container
        }

        if additionalFields:
            apiParams = {**apiParams, **additionalFields} # merge dicts.

        if returnFields:
            fields = ','.join(returnFields)
            apiParams["_return_fields+"] = fields

        try:
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
                endpoint=infoblox.baseurl+"/networkcontainer",
                params=apiParams,
                auth=(infoblox.username, infoblox.password),
                tlsVerify=infoblox.tlsverify
            )

            return api.get()
        except Exception as e:
            raise e
