import json
import requests

from django.conf import settings

from infoblox.helpers.Log import Log
from infoblox.helpers.Exception import CustomException


class CiscoSpark:

    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def send(user: dict, message: str) -> None:
        responseObject = {}

        # In the event of a network problem (e.g. DNS failure, refused connection, etc), Requests will raise a ConnectionError exception.
        # If a request times out, a Timeout exception is raised.
        # If a request exceeds the configured number of maximum redirections, a TooManyRedirects exception is raised.
        # SSLError on SSL/TLS error.

        # On KO status codes, a CustomException is raised, with response status and body.
        try:
            Log.actionLog("Sending Spark notice", user)

            response = requests.post(
                settings.CISCO_SPARK_URL+"/messages",
                proxies=settings.API_SUPPLICANT_HTTP_PROXY,
                verify=True,
                timeout=settings.API_SUPPLICANT_NETWORK_TIMEOUT,

                headers={
                    "Authorization": "Bearer "+settings.CISCO_SPARK_TOKEN,
                    "Content-Type": "application/json"
                },
                params=None,
                data=json.dumps({
                    "roomId": settings.CISCO_SPARK_ROOM_ID,
                    "text": "[Automation, Infoblox]\n" + str(message)
                })
            )

            try:
                responseObject = response.json()
            except Exception:
                pass

            responseStatus = response.status_code
            if responseStatus != 201 and responseStatus != 200:
                raise CustomException(status=responseStatus, payload={"Cisco Spark": str(responseStatus)+", "+str(responseObject)})
        except Exception as e:
            Log.log("Sending Spark notice failed: "+str(e.__str__()))
