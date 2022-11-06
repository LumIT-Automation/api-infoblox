from infoblox.models.Infoblox.Network import Network as InfobloxNetwork
from infoblox.models.Infoblox.NetworkContainer import NetworkContainer as InfobloxNetworkContainer

from infoblox.models.Permission.repository.Network import Network as Repository


class Network:
    def __init__(self, id: int = 0, assetId: int = 0, network: str = "", *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id: int = int(id)
        self.id_asset: int = int(assetId) # simple property, not composition.
        self.network: str = network
        self.description: str = ""

        self.__load()



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
            return Repository.get(self.id, self.id_asset, self.network)
        except Exception as e:
            raise e



    def delete(self) -> None:
        try:
            Repository.delete(self.id_asset, self.network)
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def add(assetId, network) -> int:
        if network == "any":
            try:
                return Repository.add(assetId, network)
            except Exception as e:
                raise e
        else:
            # Check if assetId/networkName is a valid Infoblox network (at the time of the insertion).
            infobloxNetworks = InfobloxNetwork.list(assetId) + InfobloxNetworkContainer.list(assetId)
            for v in infobloxNetworks:
                if v["network"] == network:
                    try:
                        return Repository.add(assetId, network)
                    except Exception as e:
                        raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __load(self) -> None:
        try:
            info = Repository.get(self.id, self.id_asset, self.network)

            # Set attributes.
            for k, v in info.items():
                setattr(self, k, v)
        except Exception as e:
            raise e
