from importlib import import_module

from django.conf import settings

from infoblox.helpers.Exception import CustomException


class DismissCloudNetworksFactory:
    def __init__(self, assetId: int, provider: str, user: dict):
        self.assetId: int = int(assetId)
        self.provider: str = provider
        self.user = user



    def __call__(self, *args, **kwargs):
        try:
            module = import_module(settings.CLOUD_DISMISS_IMPLEMENTATION[0])
            Implementation = eval(
                "module."+settings.CLOUD_DISMISS_IMPLEMENTATION[1]
            )

            return Implementation(self.assetId, self.provider, self.user)
        except CustomException as c:
            raise c
        except Exception:
            raise NotImplementedError
