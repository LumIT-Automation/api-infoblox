from importlib import import_module

from django.conf import settings


class ReserveFactory:
    def __init__(self, assetId, reqType, data, username):
        self.assetId = assetId
        self.reqType = reqType
        self.data = data
        self.username = username



    def __call__(self, *args, **kwargs):
        try:
            module = import_module(settings.IP_RESERVE_IMPLEMENTATION[0])
            Implementation = eval(
                "module."+settings.IP_RESERVE_IMPLEMENTATION[1]
            )

            return Implementation(self.assetId, self.reqType, self.data, self.username)
        except Exception:
            raise NotImplementedError
