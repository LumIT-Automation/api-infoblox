import uuid
import functools

from django.http import HttpRequest
from rest_framework.request import Request
from rest_framework.response import Response

from infoblox.models.Infoblox.Asset.Asset import Asset

from infoblox.helpers.Log import Log



class ReplyAction:
    def __init__(self, wrappedMethod: callable, *args, **kwargs) -> None:
        self.wrappedMethod = wrappedMethod
        self.replyAction = self.getReplyAction()
        self.replyMethod = 'GET'
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
                    ReplyAction.__forgeRequest(
                        request=self.requestPr,
                        additionalQueryParams={"__concertoDrReplicaFlow": self.relationUuid}
                    ),
                    **kwargs
                )

                if self.responsePr.status_code in (200, 201, 202, 204): # reply the action in dr only if it was successful.
                    if "rep" in self.requestPr.query_params and self.requestPr.query_params["rep"]: # reply action in dr only if dr=1 param was passed.
                        for asset in self.__listAssetsDr():
                            try:
                                o = self.replyAction(
                                    **self.replyActionRequestParams()
                                )
                            except Exception as e:
                                raise e

                return self.responsePr
            except Exception as e:
                raise e

        return wrapped()



    def replyActionRequestParams(self) -> dict:
        try:
            # replyAssetId = asset.get("id", 0)
            replyAssetId = 1
            ipAddress = self.prResponseParser(self.responsePr)[0]
            replyPath = '/api/v1/infoblox/' + str(replyAssetId) + "/ipv4/" + str(ipAddress)

            return {
                "request": self.replyActionRequest(
                    requestPr=self.requestPr, replyPath=replyPath, replyMethod=self.replyMethod, additionalQueryParams={"__concertoDrReplicaFlow": self.relationUuid}
                ),
                "assetId": replyAssetId,
                "ipv4address": ipAddress
            }
        except Exception as e:
            raise e



    def getReplyAction(self) -> callable:
        try:
            from infoblox.controllers.Infoblox.Ipv4 import InfobloxIpv4Controller as action
        except ImportError:
            class action:
                def get(self):
                    pass

        return action.get



    def prResponseParser(self, response: Response) -> list:
        import re
        ipList = []

        try:
            """
            # responsePr example:
            {
                "data": [
                    {
                        "result": "fixedaddress/ZG5zLmZpeGVkX2FkZHJlc3MkMTAuOC4wLjIzMS4wLi4:10.8.0.231/default",
                        "mask": "255.255.128.0",
                        "gateway": "10.8.1.1"
                    }
                ]
            }
            """

            if hasattr(response, "data"):
                if "data" in response.data and response.data["data"]:
                    for el in response.data["data"]:
                        if "result" in el:
                            ipList.extend(
                                re.findall(
                                    r'fixedaddress/[A-Za-z0-9]+:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})/[A-Za-z]+$',
                                    el["result"]
                                )
                            )

            return ipList
        except Exception as e:
            raise e



    def replyActionRequest(self, requestPr: Request, replyPath: str, replyMethod: str, additionalQueryParams: dict = None) -> Request:
        additionalQueryParams = additionalQueryParams or {}

        djangoHttpRequest = HttpRequest()
        setattr(djangoHttpRequest, "auth", getattr(requestPr, "auth"))
        djangoHttpRequest.META["HTTP_AUTHORIZATION"] = requestPr.META["HTTP_AUTHORIZATION"]

        djangoHttpRequest.path = replyPath
        djangoHttpRequest.method = replyMethod

        req = Request(djangoHttpRequest)
        setattr(req, "authenticators", getattr(requestPr, "authenticators"))

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
