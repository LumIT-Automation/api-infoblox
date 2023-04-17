import uuid
import functools

from django.http import HttpRequest, QueryDict
from rest_framework.request import Request
from rest_framework.response import Response

from infoblox.helpers.Log import Log


class TriggerBase:
    def __init__(self, wrappedMethod: callable, *args, **kwargs) -> None:
        self.wrappedMethod = wrappedMethod
        self.triggerMethod = "UNDEFINED" # GET, POST, PUT, PATCH, DELETE
        self.triggerAction = self.getTriggerAction()
        self.triggerName = "trigger_base"
        self.requestPrimary = None
        self.responsePrimary = None
        self.primaryAssetId: int = 0
        self.drAssetIds = set() # secondary/dr assetIds.
        self.relationUuid = uuid.uuid4().hex
        self.assets = list() # dr asset ids list.



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def __call__(self, request: Request, **kwargs):
        @functools.wraps(request)
        def wrapped():
            try:
                self.primaryAssetId = int(kwargs["assetId"])
                self.requestPrimary = request

                self.responsePrimary = self.wrappedMethod(request, **kwargs)

                # Whatever a particular condition is met, perform found triggers.
                if self.triggerCondition():
                    self.drAssetIds = self.__triggerAssetList()
                    try:
                        for req in self.triggerBuildRequests():
                            r = self.triggerAction(**req)
                            # Todo: history.
                    except Exception:
                        # Todo: Log and continue
                        pass

                return self.responsePrimary
            except Exception as e:
                raise e

        return wrapped()



    def triggerBuildRequests(self) -> list:
        raise NotImplementedError



    def triggerCondition(self) -> bool:
        # Checks whatever a condition is met.
        raise NotImplementedError



    def getTriggerAction(self) -> callable:
        # Return the controller's method called by the trigger.
        raise NotImplementedError



    def triggerActionRequest(self, requestPr: Request, triggerPath: str, triggerMethod: str, triggerPayload: dict = None, additionalQueryParams: dict = None) -> Request:
        triggerPayload = triggerPayload or {}
        additionalQueryParams = additionalQueryParams or {}

        djangoHttpRequest = HttpRequest()
        setattr(djangoHttpRequest, "auth", getattr(requestPr, "auth"))
        djangoHttpRequest.META["HTTP_AUTHORIZATION"] = requestPr.META["HTTP_AUTHORIZATION"]

        djangoHttpRequest.path = triggerPath
        djangoHttpRequest.method = triggerMethod

        req = Request(djangoHttpRequest)
        setattr(req, "authenticators", getattr(requestPr, "authenticators"))
        if triggerPayload:
            if isinstance(req.data, QueryDict):  # optional
                req.data._mutable = True
            req.data.update(triggerPayload)

        if additionalQueryParams:
            req.query_params.update(additionalQueryParams)

        return req



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __triggerAssetList(self) -> set:
        s = set()

        try:
            if self.primaryAssetId:
                from infoblox.models.Infoblox.Asset.Trigger import Trigger
                for el in Trigger.list({"trigger_name": self.triggerName, "src_asset_id": self.primaryAssetId}):
                    s.add( el["dst_asset_id"] )

            return s
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private static methods
    ####################################################################################################################
