from importlib import import_module

from django.conf import settings

from infoblox.helpers.Exception import CustomException


class Ipv4PatchDataFactory:
    def __call__(self, *args, **kwargs):
        try:
            module = import_module(settings.IPV4_PATCH_DATA_IMPLEMENTATION[0])
            Implementation = eval(
                "module."+settings.IPV4_PATCH_DATA_IMPLEMENTATION[1]
            )

            return Implementation()
        except CustomException as c:
            raise c
        except Exception:
            raise NotImplementedError
