from infoblox.usecases.impl.CloudNetworkModifyAccount import CloudNetworkModifyAccount
from infoblox.models.Infoblox.Network import Network
from infoblox.models.History.History import History


class CloudNetworkCustomModifyAccount1(CloudNetworkModifyAccount):
    def __init__(self, assetId: int, accountId: str, user: dict, *args, **kwargs):
        super().__init__(assetId, accountId, user, *args, **kwargs)

        self.assetId = assetId
        self.accountId = accountId
        self.user = user



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def modifyAccount(self, data: dict, *args, **kwargs) -> list:
        l= list()

        try:
            for net in self.__getAccountCloudNetworks():
                extattrs = net["extattrs"]
                formattedData = self.__formatData(extattrs, data)
                l.append(Network(assetId=self.assetId, network=net["network"]).modify(formattedData))
                hid = self.__historyLog(net["network"], 'modified')

            return l
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __getAccountCloudNetworks(self):
        try:
            return Network.listData(self.assetId, {
                "*Account ID": self.accountId,
                "*Environment": "Cloud"
            })

        except Exception as e:
            raise e



    def __formatData(self, extattrs: dict, data: dict):
        try:
            for key, val in extattrs.items():
                if key in data:
                    extattrs[key] = data[key]

            return {
                "extattrs": extattrs
            }
        except Exception as e:
            raise e



    def __historyLog(self, network, status) -> int:
        historyId = 0

        try:
            data = {
                "log": {
                    "username": self.user["username"],
                    "action": "modify",
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
