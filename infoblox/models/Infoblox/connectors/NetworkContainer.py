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
        filter = filter or {}

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
    def parentList(assetId: int, container: str, maxNumRequests: int = 7) -> list:
        parentList = []
        n = 0

        try:
            while container != "/" and n < maxNumRequests:
                container = NetworkContainer.get(assetId, container, filter = {"_return_fields+": "network,network_container"})[0]["network_container"]
                parentList.append(container)
                n += 1

            return parentList
        except Exception as e:
            raise e




    @staticmethod
    def networks(assetId: int, container: str, filter: dict = None) -> dict:
        filter = filter or {}

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
    def list(assetId: int, filter: dict = None) -> list:
        filter = filter or {}

        apiParams = {
            "_max_results": 65535,
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
