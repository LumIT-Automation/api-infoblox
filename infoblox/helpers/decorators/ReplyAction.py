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
        self.primaryAssetId: int = 0
        self.assets = list() # dr asset ids list.



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def __call__(self, request: Request, **kwargs):
        @functools.wraps(request)
        def wrapped():
            try:
                relationUuid = uuid.uuid4().hex
                self.primaryAssetId = int(kwargs["assetId"])

                # Modify the request injecting the __concertoDrReplicaFlow query parameter,
                # then perform the request to the primary asset.
                responsePr = self.wrappedMethod(
                    ReplyAction.__forgeRequest(
                        request=request,
                        additionalQueryParams={"__concertoDrReplicaFlow": relationUuid}
                    ),
                    **kwargs
                )

                if responsePr.status_code in (200, 201, 202, 204): # reply the action in dr only if it was successful.
                    if "rep" in request.query_params and request.query_params["rep"]: # reply action in dr only if dr=1 param was passed.
                        for asset in self.__listAssetsDr():
                            try:
                                # Modify the request injecting the dr asset and the __concertoDrReplicaFlow query parameter,
                                # then re-run the decorated method.
                                #replyAssetId = asset.get("id", 0)
                                replyAssetId = 1

                                o = self.replyAction(
                                    self.replyActionequest(
                                        requestPr=request, responsePr=responsePr, replyAssetId=replyAssetId, replyMethod='GET', additionalQueryParams={"__concertoDrReplicaFlow": relationUuid}
                                    ),
                                    assetId=replyAssetId,
                                    ipv4address=self.prResponseParser(responsePr)[0]
                                )
                            except Exception as e:
                                raise e

                return responsePr
            except Exception as e:
                raise e

        return wrapped()



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



    def replyActionequest(self, requestPr: Request, responsePr: Response, replyAssetId: int, replyMethod: str, additionalQueryParams: dict = None) -> Request:
        additionalQueryParams = additionalQueryParams or {}

        djangoHttpRequest = HttpRequest()

        for attr in ("auth", "META"):
            setattr(djangoHttpRequest, attr, getattr(requestPr, attr))
        djangoHttpRequest.META["QUERY_STRING"] = ""
        djangoHttpRequest.META["REQUEST_URI"] = ""

        ip = self.prResponseParser(responsePr)[0]
        djangoHttpRequest.path = '/api/v1/infoblox/' + str(replyAssetId) + "/ipv4/" + str(ip)
        djangoHttpRequest.method = replyMethod

        req = Request(djangoHttpRequest)

        setattr(req, "authenticators", getattr(requestPr, "authenticators"))

        for p in req.query_params.items():
            req.query_params.pop(p)
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
