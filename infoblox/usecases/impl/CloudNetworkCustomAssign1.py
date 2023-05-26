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
        self.containers = None



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def assignNetworks(self, data: dict, number: int = 1,  *args, **kwargs) -> dict:
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
                    o.append({"network "+str(n+1): self.assignNetwork(data)})
                except CustomException as c:
                    o.append({"network "+str(n+1): c.payload.get("Infoblox", c.payload)})
                except Exception as e:
                    o.append({"network "+str(n+1): e.__str__()})

            return {
                "region": self.region,
                "Number of networks requested": str(number) + numForced,
                "Result": o
            }
        except Exception as e:
            raise e


    def assignNetwork(self, data: dict, *args, **kwargs) -> list:
        out = []

        try:
            if self.containers is None:
                self.containers = self.__getContainers()
        except Exception as e:
            raise e

        if self.containers:
            faliedContainers = []
            for container in self.containers:
                networkContainer = container["network"]
                try:
                    Log.log(f"Trying {networkContainer}...")
                    out.append({"container "+networkContainer: self.__assign(networkContainer, data)})
                except CustomException as c:
                    faliedContainers.append(container)
                    out.append({"container "+networkContainer: c.payload.get("Infoblox", str(c.payload))})
                except Exception as e:
                    faliedContainers.append(container)
                    out.append({"container "+networkContainer: e.__str__()})

            if faliedContainers:
                self.containers = [ c for c in self.containers if c not in faliedContainers] # do not try to reuse failed containers.
        else:
            raise CustomException(status=400, payload={"Infoblox": "no container network available with the specified parameters"})

        return out


    def __assign(self, container: str, data: dict):
        try:
            if Permission.hasUserPermission(groups=self.user["groups"], action="assign_network", assetId=self.assetId, network=container) or self.user["authDisabled"]:
                n = NetworkContainer(self.assetId, container).addNextAvailableNetwork(
                        subnetMaskCidr=24,
                        data=data
                    )

                network = re.findall(r'network/[A-Za-z0-9]+:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/[0-9][0-9]?)/default$', n)[0]
                hid = self.__historyLog(network, 'created')
                from infoblox.controllers.CustomController import CustomController
                CustomController.plugins(controller="assign-cloud-network_put", requestType="network.assign", requestStatus="success", network=network, user=self.user, historyId=hid)
                return n
            else:
                raise CustomException(status=403, payload={"Infoblox": "Forbidden."})

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
