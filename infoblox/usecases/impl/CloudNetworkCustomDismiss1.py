from infoblox.usecases.impl.CloudNetworkDismiss import CloudNetworkDismiss
from infoblox.models.Infoblox.Network import Network
from infoblox.models.History.History import History
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

                    if Permission.hasUserPermission(groups=self.user["groups"], action="dismiss_network", assetId=self.assetId, network=net["network"]) or self.user["authDisabled"]:
                        Network(self.assetId, net["network"]).delete()
                        status.append({net["network"]: "Deleted"})
                        self.__historyLog(net["network"], 'deleted')
                    else:
                        status.append({net["network"]: "Forbidden"})
                        self.__historyLog(net["network"], 'forbidden')
                except CustomException as e:
                    status.append({net["network"]: e.payload.get("Infoblox", e.payload)})
                    self.__historyLog(net["network"], e.payload.get("Infoblox", e.payload))
                except Exception as e:
                    status.append({net["network"]: e.__str__()})
                    self.__historyLog(net["network"], e.__str__())

            return status
        else:
            raise CustomException(status=400, payload={"Infoblox": "no network with specified parameters was found."})



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __getNetworks(self, data: dict) -> list:
        data = data or {}
        filter = {}

        if "network" in data:
            filter = {
                "network": data["network"]
            }
        else:
            if "Region" in data and data["Region"] != "any":
                filter.update({"*City": data["Region"]})
            if "Account ID" in data and data["Account ID"]:
                filter.update({"*Account ID": data["Account ID"]})
            if "Account Name" in data and data["Account Name"]:
                filter.update({"*Account Name": data["Account Name"]})

        if filter:
            filter.update({
                "*Environment": "Cloud",
                "*Country": "Cloud-" + self.provider
            })
        else:
            raise CustomException(status=400, payload={"Infoblox": "Missing parameters, you don't wanna delete all the cloud networks."})

        try:
            # Eligible networks.
            return Network.listData(self.assetId, filter)
        except Exception as e:
            raise e



    def __historyLog(self, network, status) -> int:
        historyId = 0

        try:
            data = {
                "log": {
                    "username": self.user["username"],
                    "action": "dismiss",
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
