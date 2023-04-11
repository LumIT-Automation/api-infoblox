import uuid
import functools
from typing import List

from django.http import HttpRequest, QueryDict
from rest_framework.request import Request
from rest_framework.response import Response


from infoblox.models.Infoblox.Asset.Asset import Asset
from infoblox.helpers.Log import Log


class TriggerBase:
    def __init__(self, wrappedMethod: callable, *args, **kwargs) -> None:
        self.wrappedMethod = wrappedMethod
        self.triggerMethod = "UNDEFINED" # GET, POST, PUT, PATCH, DELETE
        self.triggerAction = self.getTriggerAction()
        self.triggerName = "trigger_base"
        self.requestPr = None
        self.responsePr = None
        self.primaryAssetId: int = 0
        self.drAssetIds: List[int] = [] # secondary/dr assetIds.
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
                self.requestPr = request

                # Modify the request injecting the __concertoDrReplicaFlow query parameter,
                # then perform the request to the primary asset.
                self.responsePr = self.wrappedMethod(
                    TriggerBase.__forgeRequest(
                        request=self.requestPr,
                        additionalQueryParams={"__concertoDrReplicaFlow": self.relationUuid}
                    ),
                    **kwargs
                )

                if self.triggerCondition(request=self.requestPr, response=self.responsePr):
                    self.drAssetIds = self.__triggerAssetList()
                    try:
                        for req in self.triggerBuildRequests():
                            r = self.triggerAction(**req)
                            # Todo: history.

                    except Exception:
                        # Todo: Log and continue
                        pass

                return self.responsePr
            except Exception as e:
                raise e

        return wrapped()



    def triggerBuildRequests(self) -> list:
        raise NotImplementedError



    def triggerCondition(self, request: Request, response: Response) -> bool:
        raise NotImplementedError



    # Returns the method of the controller called by the trigger (triggerAction).
    def getTriggerAction(self) -> callable:
        raise NotImplementedError

        """
        Example:
        try:
            from infoblox.controllers.Infoblox.Ipv4 import InfobloxIpv4Controller as action

            m = self.triggerMethod.lower()
            if hasattr(action, m) and callable(getattr(action, m)):
                return getattr(action, m)
        except ImportError as e:
            raise e
        """



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

    def __triggerAssetList(self) -> list:
        l = list()

        try:
            if self.primaryAssetId:
                #from infoblox.models.Infoblox.Asset.Trigger import Trigger
                #dataList = Trigger.condition(triggerName=self.triggerName, srcAssetId=self.primaryAssetId)

                pass
                #l = Asset(self.primaryAssetId).drDataList(onlyEnabled=True)

            return [1]
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private static methods
    ####################################################################################################################

    @staticmethod
    def __forgeRequest(request: Request, additionalQueryParams: dict = None) -> Request:
        additionalQueryParams = additionalQueryParams or {}

        try:
            djangoHttpRequest = HttpRequest()
            djangoHttpRequest.path = request.path[:]
            djangoHttpRequest.method = request.method
            query_params = request.query_params.copy()
            if "dr" in query_params:
                del query_params["dr"]

            if additionalQueryParams:
                query_params.update(additionalQueryParams)

            for attr in ("POST", "data", "FILES", "auth", "META"):
                setattr(djangoHttpRequest, attr, getattr(request, attr))

            req = Request(djangoHttpRequest)
            for attr in ("authenticators", "accepted_media_type", "accepted_renderer", "version", "versioning_scheme"):
                setattr(req, attr, getattr(request, attr))

            if additionalQueryParams:
                req.query_params.update(query_params)

            return req
        except Exception as e:
            raise e
