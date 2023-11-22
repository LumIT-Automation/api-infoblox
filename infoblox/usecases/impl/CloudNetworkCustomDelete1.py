from infoblox.usecases.impl.CloudNetworkDelete import CloudNetworkDelete
from infoblox.models.Infoblox.Network import Network
from infoblox.models.History.History import History
from infoblox.models.Permission.Permission import Permission

from infoblox.helpers.Exception import CustomException
from infoblox.helpers.Mail import Mail
from infoblox.helpers.Log import Log


class CloudNetworkCustomDelete1(CloudNetworkDelete):
    def __init__(self, assetId: int, networkAddress: str, user: dict, *args, **kwargs):
        super().__init__(assetId, networkAddress, user, *args, **kwargs)

        self.assetId: int = int(assetId)
        self.networkAddress = networkAddress
        self.user = user



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def delete(self, *args, **kwargs) -> None:
        try:
            network = Network(self.assetId, self.networkAddress)
            if not network.repr().get("extattrs", {}).get("Environment", {}).get("value", "") == "Cloud":
                raise CustomException(status=400, payload={"Infoblox": "This is not a Cloud Network."})

            if Permission.hasUserPermission(groups=self.user["groups"], action="cloud_network_delete", assetId=self.assetId, network=network) or self.user["authDisabled"]:
                from infoblox.controllers.CustomController import CustomController
                accountId = network.repr().get("extattrs", {}).get("Account ID", {}).get("value", "")
                accountName = network.repr().get("extattrs", {}).get("Account Name", {}).get("value", "")

                network.delete()
                hid = self.__historyLog(network.network, 'deleted')
                CustomController.plugins(controller="delete-cloud-networks_delete", requestType="network.delete", requestStatus="success", network=network.network, user=self.user, historyId=hid)

                # If there are no networks left for this Account ID, email the admin group.
                if not self.__getAccountIdNetworks(accountId):
                    Mail.send(self.user, "ALERT_JSM", "Account ID " + accountId + " with name " + accountName + " has been deleted by " + self.user["username"] + "." + "\r\nGroup: IT Network Management.")
            else:
                raise CustomException(status=403, payload={"Infoblox": "Forbidden."})

        except Exception as e:
            raise e

    ####################################################################################################################
    # Private methods
    ####################################################################################################################

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
                    "action": "delete",
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
