import json

from infoblox.models.Infoblox.Asset.Asset import Asset

from infoblox.helpers.ApiSupplicant import ApiSupplicant
from infoblox.helpers.Log import Log


class VlanView:

    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def get(assetId, _ref: str, id: int, silent: bool = False) -> dict:

        try:
            apiParams = {
                "_max_results": 65535,
                "_return_fields+": "start_vlan_id,end_vlan_id,name,vlan_view"
            }

            infoblox = Asset(assetId)
            api = ApiSupplicant(
                endpoint=infoblox.baseurl+"/vlanview",
                params=apiParams,
                auth=(infoblox.username, infoblox.password),
                tlsVerify=infoblox.tlsverify,
                silent=silent
            )

            return api.get()
        except Exception as e:
            raise e



    @staticmethod
    def list(assetId: int, filter: dict = None, silent: bool = False) -> dict:
        filter = filter or {}

        try:
            apiParams = {
                "_max_results": 65535,
                "_return_fields+": "start_vlan_id,end_vlan_id,name,vlan_view"
            }

            if filter:
                apiParams.update(filter)

            infoblox = Asset(assetId)
            api = ApiSupplicant(
                endpoint=infoblox.baseurl+"/vlanview",
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