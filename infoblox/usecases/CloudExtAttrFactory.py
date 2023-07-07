from importlib import import_module

from django.conf import settings

from infoblox.helpers.Exception import CustomException


class CloudExtAttrFactory:
    def __init__(self, assetId: int, user: dict):
        self.assetId: int = int(assetId)
        self.user = user



    def __call__(self, *args, **kwargs):
        try:
            module = import_module(settings.CLOUD_EXTATTR_IMPLEMENTATION[0])
            Implementation = eval(
                "module."+settings.CLOUD_EXTATTR_IMPLEMENTATION[1]
            )

            return Implementation(self.assetId, self.user)
        except CustomException as c:
            raise c
        except Exception:
            raise NotImplementedError
