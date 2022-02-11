import json

from infoblox.models.Infoblox.Asset.Asset import Asset

from infoblox.helpers.ApiSupplicant import ApiSupplicant
from infoblox.helpers.Log import Log


class Ipv4:

    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def get(assetId, address) -> dict:
        try:
            apiParams = {
                "ip_address": address
            }

            returnFields = ["network", "extattrs"]

            fields = ','.join(returnFields)
            apiParams["_return_fields+"] = fields

            infoblox = Asset(assetId)
            api = ApiSupplicant(
                endpoint=infoblox.baseurl+"/ipv4address",
                params=apiParams,
                auth=(infoblox.username, infoblox.password),
                tlsVerify=infoblox.tlsverify
            )

            return api.get()[0]
        except Exception as e:
            raise e



    @staticmethod
    def delete(assetId, ref) -> None:
        try:
            apiParams = {
                "_return_as_object": 1
            }

            infoblox = Asset(assetId)
            api = ApiSupplicant(
                endpoint=infoblox.baseurl+"/"+ref,
                auth=(infoblox.username, infoblox.password),
                params=apiParams,
                tlsVerify=infoblox.tlsverify
            )

            api.delete()
        except Exception as e:
            raise e



    @staticmethod
    def reserve(assetId, data: dict) -> dict:
        try:
            infoblox = Asset(assetId)
            api = ApiSupplicant(
                endpoint=infoblox.baseurl+"/fixedaddress?_return_as_object=1",
                auth=(infoblox.username, infoblox.password),
                tlsVerify=infoblox.tlsverify
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
