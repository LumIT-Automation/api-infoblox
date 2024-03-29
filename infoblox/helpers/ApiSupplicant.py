from typing import Callable, Union
from base64 import b64encode
import requests

from django.conf import settings

from infoblox.helpers.Log import Log
from infoblox.helpers.Exception import CustomException


class ApiSupplicant:
    def __init__(self, endpoint: str, auth: tuple, tlsVerify: bool = True, params: dict = None, silent: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.endpoint = endpoint
        self.params = params
        self.tlsVerify = tlsVerify
        self.httpProxy = settings.API_SUPPLICANT_HTTP_PROXY
        self.authorization = "Basic "+b64encode((auth[0]+":"+auth[1]).encode()).decode("ascii")
        self.silent = silent

        self.responseStatus = 500
        self.responsePayload = dict()
        self.responseHeaders = dict()



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def get(self) -> Union[dict, list]:
        try:
            Log.actionLog(
                "[API Supplicant] Fetching remote: GET "+str(self.endpoint)+" with params: "+str(self.params)
            )

            return self.__request(requests.get, params=self.params)
        except Exception as e:
            raise e



    def post(self, data: str, additionalHeaders: dict = None) -> dict:
        additionalHeaders = {} if additionalHeaders is None else additionalHeaders

        try:
            Log.actionLog("[API Supplicant] Posting to remote: "+str(self.endpoint))
            Log.actionLog("[API Supplicant] Posting data: "+str(data))

            return self.__request(requests.post, additionalHeaders=additionalHeaders, data=data)
        except Exception as e:
            raise e



    def put(self, data: str, additionalHeaders: dict = None) -> dict:
        additionalHeaders = {} if additionalHeaders is None else additionalHeaders

        try:
            Log.actionLog("[API Supplicant] Putting to remote: "+str(self.endpoint))
            Log.actionLog("[API Supplicant] Putting data: " + str(data))

            return self.__request(requests.put, additionalHeaders=additionalHeaders, data=data)
        except Exception as e:
            raise e



    def patch(self, data: str, additionalHeaders: dict = None) -> dict:
        additionalHeaders = {} if additionalHeaders is None else additionalHeaders

        try:
            Log.actionLog(
                "[API Supplicant] Patching remote: "+str(self.endpoint)
            )

            return self.__request(requests.patch, additionalHeaders=additionalHeaders, data=data)
        except Exception as e:
            raise e



    def delete(self) -> dict:
        try:
            Log.actionLog(
                "[API Supplicant] Deleting remote: "+str(self.endpoint)
            )

            return self.__request(requests.delete)
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __request(self, request: Callable, additionalHeaders: dict = None, params: dict = None, data: str = ""):
        params = {} if params is None else params
        additionalHeaders = {} if additionalHeaders is None else additionalHeaders

        # In the event of a network problem (e.g. DNS failure, refused connection, etc), Requests will raise a ConnectionError exception.
        # If a request times out, a Timeout exception is raised.
        # If a request exceeds the configured number of maximum redirections, a TooManyRedirects exception is raised.
        # SSLError on SSL/TLS error.

        # On KO status codes, a CustomException is raised, with response status and body.

        headers = {
            "Authorization": self.authorization
        }

        headers.update(additionalHeaders)

        try:
            response = request(self.endpoint,
                proxies=self.httpProxy,
                verify=self.tlsVerify,
                timeout=settings.API_SUPPLICANT_NETWORK_TIMEOUT,
                headers=headers,
                params=params, # GET parameters.
                data=data
            )

            self.responseStatus = response.status_code
            self.responseHeaders = response.headers

            try:
                self.responsePayload = response.json()
            except Exception:
                self.responsePayload = {}

            if not self.silent:
                for j in (("status", self.responseStatus), ("headers", self.responseHeaders), ("payload", self.responsePayload)):
                    Log.actionLog("[API Supplicant] Remote response "+j[0]+": "+str(j[1]))

            # CustomException errors on connection ok but ko status code.
            if self.responseStatus == 200 or self.responseStatus == 201: # ok / ok on POST.
                pass
            elif self.responseStatus == 401:
                raise CustomException(status=400, payload={"Infoblox": "Wrong credentials for the asset."})
            else:
                if "text" in self.responsePayload:
                    err = self.responsePayload["text"] # technology dependant.
                else:
                    err = self.responsePayload

                raise CustomException(status=self.responseStatus, payload={"Infoblox": err})
        except Exception as e:
            raise e

        return self.responsePayload
