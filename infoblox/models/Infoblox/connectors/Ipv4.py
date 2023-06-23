import json

from infoblox.models.Asset.Asset import Asset

from infoblox.helpers.ApiSupplicant import ApiSupplicant


class Ipv4:

    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def get(assetId, address) -> dict:
        objects = list()

        try:
            infoblox = Asset(assetId)
            api = ApiSupplicant(
                endpoint=infoblox.baseurl+"ipv4address",
                params={
                    "ip_address": address,
                    "_return_fields+": "network,extattrs"
                },
                auth=(infoblox.username, infoblox.password),
                tlsVerify=infoblox.tlsverify
            )
            ipv4AddressInfo = api.get()[0]

            # Get children objects (ipv4, host, dns records ...)
            for objRef in ipv4AddressInfo["objects"]:
                endpoint = infoblox.baseurl + "/" + objRef
                returnFields = "extattrs"
                if "fixedaddress" in objRef:
                    returnFields = "network,network_view,extattrs,options,name,mac,comment,ipv4addr,use_options"

                api = ApiSupplicant(
                    endpoint=endpoint,
                    params={
                        "ip_address": address,
                        "_return_fields+": returnFields
                    },
                    auth=(infoblox.username, infoblox.password),
                    tlsVerify=infoblox.tlsverify
                )
                objects.append(api.get())

            ipv4AddressInfo["objects"] = objects

            return ipv4AddressInfo
        except Exception as e:
            raise e



    @staticmethod
    def deleteReferencedObject(assetId, ref) -> None:
        try:
            infoblox = Asset(assetId)
            api = ApiSupplicant(
                endpoint=infoblox.baseurl+""+ref,
                auth=(infoblox.username, infoblox.password),
                params={
                    "_return_as_object": 1
                },
                tlsVerify=infoblox.tlsverify
            )

            api.delete()
        except Exception as e:
            raise e



    @staticmethod
    def reserveFixedAddress(assetId, data: dict) -> dict:
        try:
            infoblox = Asset(assetId)
            api = ApiSupplicant(
                endpoint=infoblox.baseurl+"fixedaddress?_return_fields=mac,extattrs",
                auth=(infoblox.username, infoblox.password),
                tlsVerify=infoblox.tlsverify
            )

            o = api.post(
                additionalHeaders={
                    "Content-Type": "application/json",
                },
                data=json.dumps(data)
            )

            o["result"] = o["_ref"]
            del(o["_ref"])
        except Exception as e:
            raise e

        return o
