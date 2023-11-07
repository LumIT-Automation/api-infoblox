from importlib import import_module

from django.conf import settings

from infoblox.helpers.Exception import CustomException


class ModifyCloudNetworkAccountFactory:
    def __init__(self, assetId: int, accountId: str, user: dict):
        self.assetId: int = int(assetId)
        self.accountId: str = accountId
        self.user = user



    def __call__(self, *args, **kwargs):
        try:
            module = import_module(settings.CLOUD_MODIFY_ACCOUNT_IMPLEMENTATION[0])
            Implementation = eval(
                "module."+settings.CLOUD_MODIFY_ACCOUNT_IMPLEMENTATION[1]
            )

            return Implementation(self.assetId, self.accountId, self.user)
        except CustomException as c:
            raise c
        except Exception:
            raise NotImplementedError
