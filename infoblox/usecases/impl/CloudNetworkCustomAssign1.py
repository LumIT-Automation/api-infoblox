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
            # Get networks assigned to the given Account ID (extattr).
            accountIdNetworks = Network.listData(self.assetId, {
                "*Account ID": data.get("extattrs", {}).get("Account ID", {}).get("value", "-")
            })

            # Get networks assigned to the given Account Name (extattr).
            accountNameNetworks = Network.listData(self.assetId, {
                "*Account Name": data.get("extattrs", {}).get("Account Name", {}).get("value", "-")
            })

            if accountIdNetworks:
                try:
                    # Forbid Account ID with different Account Name.
                    for net in accountIdNetworks:
                        if net.get("extattrs", {}).get("Account Name", {}).get("value", "") != data.get("extattrs", {}).get("Account Name", {}).get("value", ""):
                            raise CustomException(status=400, payload={"Infoblox": "A network with the Account ID "+data.get("extattrs", {}).get("Account ID", {}).get("value", "" )+" but different Account Name exists: "+net["network"]})
                        if net.get("extattrs", {}).get("Reference", {}).get("value", "") != data.get("extattrs", {}).get("Reference", {}).get("value", ""):
                            raise CustomException(status=400, payload={"Infoblox": "A network with the Account ID "+data.get("extattrs", {}).get("Account ID", {}).get("value", "" )+" but different Reference exists: "+net["network"]})
                except Exception as e:
                    raise e

            if accountNameNetworks:
                try:
                    for net in accountNameNetworks:
                        if net.get("extattrs", {}).get("Account ID", {}).get("value", "") != data.get("extattrs", {}).get("Account ID", {}).get("value", ""):
                            raise CustomException(status=400, payload={"Infoblox": "A network with the Account Name "+data.get("extattrs", {}).get("Account Name", {}).get("value", "" )+" but different Account ID exists: "+net["network"]})
                except Exception as e:
                    raise e

                # CLOUD_MAX_ACCOUNT_REGION is the maximum number of regions for Account ID.
                if hasattr(settings, "CLOUD_MAX_ACCOUNT_REGION"):
                    if settings.CLOUD_MAX_ACCOUNT_REGION < len(set( [ net.get("extattrs", {}).get("City", {}).get("value", "") for net in accountIdNetworks ] )):
                        raise CustomException(status=400, payload={"Infoblox": "The maximum number of regions for this Account ID has been reached: " + str(settings.CLOUD_MAX_ACCOUNT_REGION)})

                # CLOUD_MAX_ACCOUNT_REGION_NETS is the maximum number of networks for Account ID in a region.
                if hasattr(settings, "CLOUD_MAX_ACCOUNT_REGION_NETS"):
                    if settings.CLOUD_MAX_ACCOUNT_REGION_NETS <= len([net for net in accountIdNetworks if net.get("extattrs", {}).get("City", {}).get("value", "") == self.region]):
                        raise CustomException(status=400, payload={"Infoblox": "The maximum number of networks for this Account ID in this region has been reached: " + str(settings.CLOUD_MAX_ACCOUNT_REGION_NETS)})

            return self.__pickContainer(data)
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __getEligibleContainers(self) -> list:
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



    def __pickContainer(self, data: dict) -> str:
        out = ""
        status = 0

        if "subnetMaskCidr" in data:
            if data["subnetMaskCidr"] == 24 or data["subnetMaskCidr"] == 23:
                subnetMaskCidr = data["subnetMaskCidr"]
                del data["subnetMaskCidr"]
            else:
                raise CustomException(status=400, payload={"Infoblox": "Bad subnet mask given: can be 23 or 24."})
        else:
            subnetMaskCidr = 24

        try:
            containers = self.__getEligibleContainers()
            if containers:
                for container in containers:
                    networkContainer = container["network"]
                    try:
                        Log.log(f"Trying {networkContainer}...")
                        return self.__assign(networkContainer, data, subnetMaskCidr)
                    except CustomException as c:
                        out = c.payload.get("Infoblox", str(c.payload)) # this message is overwritten if there are other containers to which ask for the network.
                        status = c.status
                    except Exception as e:
                        out = e.__str__() # this message is overwritten if there are other containers to which ask for the network.
                        status = 500
            else:
                raise CustomException(status=400, payload={"Infoblox": "No network container with the specified parameters found."})
        except Exception as e:
            raise e

        if status:
            raise CustomException(status=status, payload={"Infoblox": out})
        return out



    def __assign(self, container: str, data: dict, subnetMaskCidr: int) -> str:
        try:
            if Permission.hasUserPermission(groups=self.user["groups"], action="cloud_network_assign_put", assetId=self.assetId, container=container) or self.user["authDisabled"]:
                n = NetworkContainer(self.assetId, container).addNextAvailableNetwork(
                        subnetMaskCidr=subnetMaskCidr,
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



    def __historyLog(self, network, status) -> int:
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
