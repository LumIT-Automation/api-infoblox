import re
import json
import requests

from django.conf import settings

from infoblox.helpers.Log import Log
from infoblox.helpers.Exception import CustomException

# Register this plugin in settings.py, first.
# Configure in settings_spark.py.


class CiscoSpark:
    @staticmethod
    def send(user: dict, message: str) -> None:
        responseObject = {}

        try:
            concertoEnvironment = settings.CONCERTO_ENVIRONMENT
        except Exception:
            concertoEnvironment = "Development"

        # In the event of a network problem (e.g. DNS failure, refused connection, etc), Requests will raise a ConnectionError exception.
        # If a request times out, a Timeout exception is raised.
        # If a request exceeds the configured number of maximum redirections, a TooManyRedirects exception is raised.
        # SSLError on SSL/TLS error.

        # On KO status codes, a CustomException is raised, with response status and body.
        try:
            Log.actionLog("[Plugins] Sending Spark notice", user)

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
                    "text": f"[Concerto Orchestration, Infoblox][{concertoEnvironment}]\n"+str(message)
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
            Log.log("[Plugins] Sending Spark notice failed: "+str(e.__str__()))



def run(controller: str, requestType: str = "", requestStatus: str = "", data: dict = None, response: dict = None, ipv4Address: str = "", network: str = "", gateway: str = "", mask: str = "", user: dict = None, historyId: int = 0):
    data = data or {}
    user = user or {}
    response = response or {}

    action = ""

    if controller in ("ipv4s_post", "ipv4_get", "ipv4_delete", "ipv4_patch"):
        Log.log("[Plugins] Running CiscoSpark plugin")

        if controller == "ipv4s_post":
            action = "created"
        if controller == "ipv4_get":
            action = "read"
        if controller == "ipv4_patch":
            action = "modified"
        if controller == "ipv4_delete":
            action = "released"

        if action in ("read", "modified", "released"):
            message = "IPv4 address "+ipv4Address+" has been "+action+" by "+user.get("username", "--")+".\n"

            if "mac" in data:
                mac = data["mac"]
                message += "MAC: "+mac+"\n"
            if "extattrs" in data:
                extAttrsData = data["extattrs"]
                if "Mask" in extAttrsData:
                    mask = extAttrsData["Mask"]["value"]
                    message += "Mask: "+mask+"\n"
                if "Gateway" in extAttrsData:
                    gw = extAttrsData["Gateway"]["value"]
                    message += "Gateway: "+gw+"\n"
                if "Name Server" in extAttrsData:
                    ns = extAttrsData["Name Server"]["value"]
                    message += "Hostname: "+ns+"\n"
                if "Reference" in extAttrsData:
                    ref = extAttrsData["Reference"]["value"]
                    message += "Reference: "+ref+"\n"
            if historyId:
                message += "Unique operation ID: "+str(historyId)+"\n"

            CiscoSpark.send(user, message)

        if action == "created":
            if requestType == "post.next-available":
                j = 0

                for createdObject in response.get("data", {}):
                    ip = re.findall(r'[0-9]+(?:\.[0-9]+){3}', createdObject["result"])[0]
                    message = "IPv4 address "+ip+" has been "+action+" by "+user.get("username", "--")+".\n"

                    if "mac" in data:
                        message += "MAC: "+data["mac"][j]+"\n"
                    if network:
                        message += "Network: "+network+"\n"
                    if gateway:
                        message += "Gateway: "+gateway+"\n"
                    if mask:
                        message += "Mask: "+mask+"\n"

                    if "object_type" in data:
                        if data["object_type"] != "undefined":
                            message += "Type: "+data["object_type"]+"\n"
                    if "extattrs" in data:
                        extAttrsData = data["extattrs"]
                        if "Name Server" in extAttrsData[j]:
                            message += "Hostname: "+extAttrsData[j]["Name Server"]["value"]+"\n"
                        if "Reference" in extAttrsData[j]:
                            message += "Reference: "+extAttrsData[j]["Reference"]["value"]+"\n"
                    if historyId:
                        message += "Unique operation ID: "+str(historyId)+"\n"
                    j += 1

                    CiscoSpark.send(user, message)

            if requestType == "replica.specified-ip":
                if requestStatus == "success":
                    message = "IPv4 address "+ipv4Address+" has been "+action+".\n"
                else:
                    message = "Error replicating IPv4 address "+ipv4Address+" on disaster recovery asset.\n"

                CiscoSpark.send(user, message)

    elif controller == "dismiss-cloud-network_put":
        Log.log("[Plugins] Running CiscoSpark plugin")

        if requestStatus == "success" or requestStatus == "forbidden":
            message = f"Network {network}: action {requestType} was requested from user "+user.get("username", "--")+f": {requestStatus}."
        else:
            message = f"Network {network}: action {requestType}"
            pass
        if historyId:
            message += "Unique operation ID: " + str(historyId) + "\n"
        CiscoSpark.send(user, message)

    elif controller == "assign-cloud-network_put":
        Log.log("[Plugins] Running CiscoSpark plugin")