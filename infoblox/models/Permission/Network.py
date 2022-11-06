from infoblox.models.Infoblox.Network import Network as InfobloxNetwork
from infoblox.models.Infoblox.NetworkContainer import NetworkContainer as InfobloxNetworkContainer

from infoblox.models.Permission.repository.Network import Network as Repository


class Network:
    def __init__(self, assetId: int, networkName: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.assetId = assetId
        self.networkName = networkName
        self.description = ""



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def exists(self) -> bool:
        try:
            pid = self.info()["id"] # just a probe.
            return True
        except Exception:
            return False



    def info(self) -> dict:
        try:
            return Repository.get(self.assetId, self.networkName)
        except Exception as e:
            raise e



    def delete(self) -> None:
        try:
            Repository.delete(self.assetId, self.networkName)
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def add(assetId, networkName) -> int:
        if networkName == "any":
            try:
                return Repository.add(assetId, networkName)
            except Exception as e:
                raise e

        else:
            # Check if assetId/networkName is a valid Infoblox network (at the time of the insertion).
            infobloxNetworks = InfobloxNetwork.list(assetId) + InfobloxNetworkContainer.list(assetId)

            for v in infobloxNetworks:
                if v["network"] == networkName:
                    try:
                        return Repository.add(assetId, networkName)
                    except Exception as e:
                        raise e
