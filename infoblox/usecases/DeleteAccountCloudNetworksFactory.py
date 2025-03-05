from importlib import import_module

from django.conf import settings

from infoblox.helpers.Exception import CustomException


class DeleteAccountCloudNetworksFactory:
    def __init__(self, assetId: int, provider: str, user: dict, workflowId: str = "", isWorkflow: bool = False):
        self.assetId: int = int(assetId)
        self.provider: str = provider
        self.user = user
        self.workflowId = workflowId
        self.isWorkflow = isWorkflow



    def __call__(self, *args, **kwargs):
        try:
            module = import_module(settings.CLOUD_NETWORK_ACCOUNT_DELETE_IMPLEMENTATION[0])
            Implementation = eval(
                "module."+settings.CLOUD_NETWORK_ACCOUNT_DELETE_IMPLEMENTATION[1]
            )

            return Implementation(self.assetId, self.provider, self.user, self.workflowId, self.isWorkflow)
        except CustomException as c:
            raise c
        except Exception:
            raise NotImplementedError
