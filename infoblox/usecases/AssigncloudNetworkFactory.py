from importlib import import_module

from django.conf import settings


class AssignCloudNetworkFactory:
    def __init__(self, assetId: int, provider: str, region: str, user: dict):
        self.assetId: int = int(assetId)
        self.provider: str = provider
        self.region: str = region
        self.user = user



    def __call__(self, *args, **kwargs):
        try:
            module = import_module(settings.CLOUD_ASSIGN_IMPLEMENTATION[0])
            Implementation = eval(
                "module."+settings.CLOUD_ASSIGN_IMPLEMENTATION[1]
            )

            return Implementation(self.assetId, self.provider, self.region, self.user)
        except Exception:
            raise NotImplementedError
