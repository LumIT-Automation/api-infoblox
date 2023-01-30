import json

from infoblox.models.Infoblox.Asset.Asset import Asset

from infoblox.helpers.ApiSupplicant import ApiSupplicant
from infoblox.helpers.Log import Log


class NetworkContainer:

    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def get(assetId: int, container: str, filter: dict = None) -> dict:
        filter = {} if filter is None else filter

        apiParams = {
            "network": container,
            "_return_fields+": "network,network_container,extattrs"
        }

        if filter:
            apiParams.update(filter)

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
    def networks(assetId: int, container: str, filter: dict = None) -> dict:
        filter = {} if filter is None else filter

        apiParams = {
            "network_container": container,
            "_return_fields+": "network,network_container,extattrs"
        }

        if filter:
            apiParams.update(filter)

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
            infoblox = Asset(assetId)
            api = ApiSupplicant(
                endpoint=infoblox.baseurl+"/networkcontainer",
                params={
                    "_max_results": 65535,
                    "_return_fields+": "network,network_container,extattrs"
                },
                auth=(infoblox.username, infoblox.password),
                tlsVerify=infoblox.tlsverify
            )

            return api.get()
        except Exception as e:
            raise e



    @staticmethod
    def addNetwork(assetId, data: dict, silent: bool = False) -> dict:

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
