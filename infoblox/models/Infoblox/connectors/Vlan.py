from infoblox.models.Asset.Asset import Asset

from infoblox.helpers.ApiSupplicant import ApiSupplicant


class Vlan:

    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def get(assetId, id: int, silent: bool = False) -> dict:
        try:
            infoblox = Asset(assetId)
            api = ApiSupplicant(
                endpoint=infoblox.baseurl+"vlan",
                params={
                    "id": id,
                    "_max_results": 65535,
                    "_return_fields+": "id,assigned_to,name,parent,reserved,status,description,comment,department,extattrs"
                },
                auth=(infoblox.username, infoblox.password),
                tlsVerify=infoblox.tlsverify,
                silent=silent
            )

            v = api.get()
            if isinstance(v, list) and len(v) > 0:
                return v[0]
            else:
                return v
        except Exception as e:
            raise e



    @staticmethod
    def list(assetId: int, filter: dict = None, silent: bool = False) -> list:
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
                endpoint=infoblox.baseurl+"vlan",
                params=apiParams,
                auth=(infoblox.username, infoblox.password),
                tlsVerify=infoblox.tlsverify,
                silent=silent
            )

            return api.get()
        except Exception as e:
            raise e
