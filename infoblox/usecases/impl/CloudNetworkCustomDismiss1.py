from infoblox.usecases.impl.CloudNetworkDismiss import CloudNetworkDismiss
from infoblox.models.Infoblox.Network import Network
from infoblox.models.Permission.Permission import Permission

from infoblox.helpers.Exception import CustomException
from infoblox.helpers.Log import Log


class CloudNetworkCustomDismiss1(CloudNetworkDismiss):
    def __init__(self, assetId: int, provider: str, user: dict, *args, **kwargs):
        super().__init__(assetId, provider, user, *args, **kwargs)

        self.assetId: int = int(assetId)
        self.provider: str = provider
        self.user = user



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def dismissNetworks(self, data: dict, *args, **kwargs) -> list:
        status = []

        networks = self.__getNetworks(data)
        if networks:
            for net in networks:
                try:
                    Log.log(f"Trying {net}...")

                    if Permission.hasUserPermission(groups=self.user["groups"], action="dismiss_network", assetId=self.assetId, network=net) or self.user["authDisabled"]:
                        Network(self.assetId, net).delete()
                        status.append({net: 200})
                    else:
                        status.append({net: 403})
                except CustomException as e:
                    status.append({net: e.payload.get("Infoblox", e.payload)}) # Infoblox error response, as full network.
                except Exception as e:
                    status.append({net: e.__str__()})

            return status
        else:
            raise CustomException(status=400, payload={"Infoblox": "no network with specified parameters was found."})



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __getNetworks(self, data: dict) -> list:
        data = data or {}
        filter = {
            "*Environment": "Cloud",
            "*Country": "Cloud-" + self.provider
        }


        if "network" in data:
            filter.update({"network": data["network"]})
        elif data["extattrs"]:
            if "Region" in data["extattrs"] and data["extattrs"]["Region"] == "any":
                del data["extattrs"]["region"]
            filter.update(data["extattrs"])
        else:
            raise CustomException(status=400, payload={"Infoblox": "Missing parameters, you don't wanna delete all the cloud networks."})

        try:
            # Eligible networks.
            return Network.listData(self.assetId, filter)
        except Exception as e:
            raise e
