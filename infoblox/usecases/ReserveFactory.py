from infoblox.usecases.impl.Ipv4CustomReserve1 import Ipv4CustomReserve1


class ReserveFactory:
    def __init__(self, assetId, reqType, data, username):
        self.assetId = assetId
        self.reqType = reqType
        self.data = data
        self.username = username



    def __call__(self, *args, **kwargs):
        return Ipv4CustomReserve1(self.assetId, self.reqType, self.data, self.username)
