import json

from infoblox.models.Infoblox.Asset.Asset import Asset

from infoblox.helpers.ApiSupplicant import ApiSupplicant
from infoblox.helpers.Log import Log


class Vlan:

    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def get(assetId, id: int, silent: bool = False) -> dict:
        try:
            return Vlan.list(assetId=assetId, filter={"id": id}, silent=silent)[0]
        except Exception as e:
            raise e



    @staticmethod
    def list(assetId: int, filter: dict = None, silent: bool = False) -> dict:
        filter = filter or {}

        try:
            apiParams = {
                "_max_results": 65535,
                "_return_fields+": "id,assigned_to,name,parent,reserved,status,description,comment,department,extattrs"
            }

            if filter:
                apiParams.update(filter)

            infoblox = Asset(assetId)
            api = ApiSupplicant(
                endpoint=infoblox.baseurl+"/vlan",
                params=apiParams,
                auth=(infoblox.username, infoblox.password),
                tlsVerify=infoblox.tlsverify,
                silent=silent
            )

            return api.get()
        except Exception as e:
            raise e


    """
    @staticmethod
    def add(assetId, data: dict, silent: bool = False) -> dict:

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