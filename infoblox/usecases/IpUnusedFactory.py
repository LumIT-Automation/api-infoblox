from importlib import import_module

from django.conf import settings

from infoblox.helpers.Exception import CustomException


class Ipv4UnusedFactory:
    def __call__(self, *args, **kwargs):
        try:
            module = import_module(settings.IP_UNUSED_IMPLEMENTATION[0])
            Implementation = eval(
                "module."+settings.IP_UNUSED_IMPLEMENTATION[1]
            )

            return Implementation()
        except CustomException as c:
            raise c
        except Exception:
            raise NotImplementedError
