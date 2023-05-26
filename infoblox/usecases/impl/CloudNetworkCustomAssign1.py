import re
from django.conf import settings

from infoblox.usecases.impl.CloudNetworkAssign import CloudNetworkAssign
from infoblox.models.Infoblox.NetworkContainer import NetworkContainer
from infoblox.models.Infoblox.Network import Network
from infoblox.models.History.History import History
from infoblox.models.Permission.Permission import Permission

from infoblox.helpers.Exception import CustomException
from infoblox.helpers.Log import Log


class CloudNetworkCustomAssign1(CloudNetworkAssign):
    def __init__(self, assetId: int, provider: str, region: str, user: dict, *args, **kwargs):
        super().__init__(assetId, provider, region, user, *args, **kwargs)

        self.assetId: int = int(assetId)
        self.provider: str = provider
        self.region: str = region
        self.user = user



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def assignNetwork(self, data: dict, number: int = 1,  *args, **kwargs) -> dict:
        o = list()
        numForced = ""

        try:
            previousNetworks = self.__getAccountIdNetworks(data["extattrs"]["Account ID"]["value"])
            if previousNetworks:
                try:
                    # Check the given account name against the first entry in previousNetworks.
                    if previousNetworks[0]["extattrs"]["Account Name"]["value"] != data["extattrs"]["Account Name"]["value"]:
                        raise CustomException(status=400, payload={"Infoblox": "A network with the same Account ID but different Account Name exists: "+previousNetworks[0]["network"]})
                except KeyError:
                    raise CustomException(status=400, payload={"Infoblox": "Missing field in data given or in a previous assigned network."})
                except Exception as e:
                    raise e

            # CLOUD_ASSIGN_MAX_ACCOUNT_NETS is the maximum number of networks for Account ID in a region.
            if hasattr(settings, "CLOUD_ASSIGN_MAX_ACCOUNT_NETS"):
                max = settings.CLOUD_ASSIGN_MAX_ACCOUNT_NETS
            else:
                max = 5
            max = max - len([net for net in previousNetworks if net["extattrs"]["City"]["value"] == self.region]) # subtrack the existent networks.
            if max <= 0:
                raise CustomException(status=400, payload={"Infoblox": "Maximun number of networks for this Accoun ID in this region already reached."})

            if number > max:
                number = max
                numForced = " (forced by settings)."

            for n in range(number):
                try:
                    o.append({"Infoblox": self.assign(data)})
                except CustomException as c:
                    o.append(c.payload)
                    raise CustomException(status=c.status, payload={"Items": o})
                except Exception as e:
                    o.append( e.__str__())
                    raise CustomException(status=500, payload={"Items": o})

            return {
                "Number of networks requested": str(number) + numForced,
                "Networks": o
            }
        except Exception as e:
            raise e



    def assign(self, data: dict, *args, **kwargs) -> str:
        status = ""

        try:
            containers = self.__getContainers()
            if containers:
                for container in containers:
                    try:
                        Log.log(f"Trying {container}...")

                        if Permission.hasUserPermission(groups=self.user["groups"], action="assign_network", assetId=self.assetId, network=container) or self.user["authDisabled"]:
                            o = NetworkContainer(self.assetId, container["network"]).addNextAvailableNetwork(
                                subnetMaskCidr=24,
                                data=data
                            )

                            network = re.findall(r'network/[A-Za-z0-9]+:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/[0-9][0-9]?)/default$', o)[0]
                            hid = self.__historyLog(network, 'created')
                            from infoblox.controllers.CustomController import CustomController
                            CustomController.plugins(controller="assign-cloud-network_put", requestType="network.assign", requestStatus="success", network=network, user=self.user, historyId=hid)
                            return o
                        else:
                            status = "forbidden"
                    except CustomException as e:
                        status = e.payload.get("Infoblox", e.payload) # Infoblox error response, as full network.
                    except Exception as e:
                        status = e.__str__()

                if status == "forbidden":
                    raise CustomException(status=403)
                elif status != "":
                    raise CustomException(status=400, payload={"Infoblox": status})
            else:
                raise CustomException(status=400, payload={"Infoblox": "no container network available with specified parameters"})

        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __getContainers(self) -> list:
        try:
            # Eligible container networks.
            return NetworkContainer.listData(self.assetId, {
                "*Environment": "Cloud",
                "*Country": "Cloud-" + self.provider,
                "*City": self.region
            })
        except Exception as e:
            raise e



    def __getAccountIdNetworks(self, accountId: str):
        try:
            return Network.listData(self.assetId, {
                "*Account ID": accountId
            })

        except Exception as e:
            raise e



    def __historyLog(self, network, status) -> int:
        historyId = 0

        try:
            data = {
                "log": {
                    "username": self.user["username"],
                    "action": "assign",
                    "asset_id": self.assetId,
                    "status": status
                },
                "log_object": {
                    "type": "network",
                    "address": network.split('/')[0],
                    "network": network,
                    "mask": network.split('/')[1],
                    "gateway": ""
                }
            }
            historyId = History.add(data)

            return historyId
        except Exception:
            pass
