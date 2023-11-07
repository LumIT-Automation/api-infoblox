from importlib import import_module

from django.conf import settings

from infoblox.helpers.Exception import CustomException


class ModifyCloudNetworkFactory:
    def __init__(self, assetId: int, network: str, provider: str, region: str, user: dict):
        self.assetId: int = int(assetId)
        self.network: str = network
        self.provider: str = provider
        self.region: str = region
        self.user = user



    def __call__(self, *args, **kwargs):
        try:
            module = import_module(settings.CLOUD_MODIFY_IMPLEMENTATION[0])
            Implementation = eval(
                "module."+settings.CLOUD_MODIFY_IMPLEMENTATION[1]
            )

            return Implementation(self.assetId, self.network, self.provider, self.region, self.user)
        except CustomException as c:
            raise c
        except Exception:
            raise NotImplementedError
