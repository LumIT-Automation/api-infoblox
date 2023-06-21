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

    def assignNetwork(self, data: dict, *args, **kwargs) -> str:
        try:
            previousNetworks = self.__getAccountIdNetworks(data["extattrs"]["Account ID"]["value"])
            if previousNetworks:
                try:
                    # Check the given account name against the entries in previousNetworks.
                    for net in previousNetworks:
                        if net.get("extattrs", {}).get("Account Name", {}).get("value", "") != data.get("extattrs", {}).get("Account Name", {}).get("value", ""):
                            raise CustomException(status=400, payload={"Infoblox": "A network with the same Account ID but different Account Name exists: "+net["network"]})
                except KeyError:
                    raise CustomException(status=400, payload={"Infoblox": "Missing field in data given or in a previous assigned network."})
                except Exception as e:
                    raise e

                # CLOUD_ASSIGN_MAX_ACCOUNT_NETS is the maximum number of networks for Account ID in a region.
                if hasattr(settings, "CLOUD_ASSIGN_MAX_ACCOUNT_NETS"):
                    if settings.CLOUD_ASSIGN_MAX_ACCOUNT_NETS <= len([net for net in previousNetworks if net.get("extattrs", {}).get("City", {}).get("value", "") == self.region]):
                        raise CustomException(status=400, payload={"Infoblox": "Maximun number of networks for this Accoun ID in this region already reached."})


            return self.__pickContainer(data)
        except Exception as e:
            raise e


    def __pickContainer(self, data: dict, *args, **kwargs) -> str:
        out = ""

        try:
            if self.containers is None:
                self.containers = self.__getContainers()
        except Exception as e:
            raise e

        if self.containers:
            for container in self.containers:
                networkContainer = container["network"]
                try:
                    Log.log(f"Trying {networkContainer}...")
                    return self.__assign(networkContainer, data)
                except CustomException as c:
                    out = c.payload.get("Infoblox", str(c.payload)) # this message is overwritten if there are other containers to which ask for the network.
                except Exception as e:
                    out = e.__str__() # this message is overwritten if there are other containers to which ask for the network.
        else:
            raise CustomException(status=400, payload={"Infoblox": "No network container with the specified parameters found."})

        return out


    def __assign(self, container: str, data: dict) -> str:
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
            filter = {
                "*Environment": "Cloud",
                "*Country": "Cloud-" + self.provider
            }
            if self.region:
                filter.update({"*City": self.region})
                nc = NetworkContainer.listData(self.assetId, filter)
            else:
                l = NetworkContainer.listData(self.assetId, filter)
                nc = [container for container in l if not container.get("extattrs", {}).get("City", {}).get("value", "")]

            # Eligible container networks.
            return nc
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
