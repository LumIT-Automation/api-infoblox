from infoblox.models.Infoblox.connectors.NetworkContainer import NetworkContainer as Connector


class NetworkContainer:
    def __init__(self, assetId: int, container: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.asset_id = int(assetId)

        self._ref = ""
        self.network = ""
        self.network_container = container
        self.network_view = ""
        self.extattrs = dict()



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def get(self, filter: dict = {}) -> dict:
        try:
            o = Connector.get(self.asset_id, self.network_container, filter)

            if o:
                o[0]["asset_id"] = self.asset_id

            return o
        except Exception as e:
            raise e



    def innerNetworks(self, filter: dict = {}) -> dict:
        o = dict()

        try:
            o["data"] = Connector.networks(self.asset_id, self.network_container, filter)
        except Exception as e:
            raise e

        return o



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(assetId: int) -> dict:
        o = dict()

        try:
            o["data"] = Connector.list(assetId)
        except Exception as e:
            raise e

        return o
