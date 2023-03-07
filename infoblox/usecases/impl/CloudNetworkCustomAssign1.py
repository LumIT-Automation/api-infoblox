from infoblox.usecases.impl.CloudNetworkAssign import CloudNetworkAssign
from infoblox.models.Infoblox.NetworkContainer import NetworkContainer
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

    def assignNetwork(self, data: dict, *args, **kwargs) -> dict:
        status = ""

        containers = self.__getContainers()
        if containers:
            for container in containers:
                try:
                    Log.log(f"Trying {container}...")

                    if Permission.hasUserPermission(groups=self.user["groups"], action="assign_network", assetId=self.assetId, network=container) or self.user["authDisabled"]:
                        return NetworkContainer(self.assetId, container["network"]).addNextAvailableNetwork(
                            subnetMaskCidr=24,
                            data=data
                        )
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
