import uuid
import functools

from django.http import HttpRequest, QueryDict
from rest_framework.request import Request

from infoblox.models.Infoblox.Asset.Asset import Asset
from infoblox.helpers.Log import Log


class TriggerBase:
    def __init__(self, wrappedMethod: callable, *args, **kwargs) -> None:
        self.wrappedMethod = wrappedMethod
        self.triggerMethod = "UNDEFINED" # GET, POST, PUT, PATCH, DELETE
        self.triggerAction = self.getTriggerAction()
        self.requestPr = None
        self.responsePr = None
        self.primaryAssetId: int = 0
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

                if self.responsePr.status_code in (200, 201, 202, 204): # trigger the action in dr only if it was successful.
                    if "rep" in self.requestPr.query_params and self.requestPr.query_params["rep"]: # trigger action in dr only if dr=1 param was passed.
                        for asset in self.__listAssetsDr():
                            try:
                                o = self.triggerAction(
                                    **self.triggerActionRequestParams()
                                )
                            except Exception as e:
                                raise e

                return self.responsePr
            except Exception as e:
                raise e

        return wrapped()


    # Forge the dict with the params for the triggerAction.
    def triggerActionRequestParams(self) -> dict:
        raise NotImplementedError

        """
        Example:
              return {
                "request": self.triggerActionRequest(
                    requestPr=self.requestPr, triggerPath=triggerPath, triggerMethod=self.triggerMethod, triggerPayload=triggerPayload, additionalQueryParams={"__concertoDrReplicaFlow": self.relationUuid}
                ),
                "assetId": triggerAssetId,
                "ipv4address": ipAddress
            }
        """



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

    def __listAssetsDr(self) -> list:
        l = list()

        try:
            if self.primaryAssetId:
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
