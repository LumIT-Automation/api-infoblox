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
            Log.log("Sending Spark notice failed: "+str(e.__str__()))



def run(controller: str, o: dict):
    action = ""
    data = dict()

    if controller in ["ipv4s_post", "ipv4_delete", "ipv4_patch"]:
        Log.log("Running CiscoSpark plugin")

        if "POST" in str(o["request"]):
            action = "created"
        if "PATCH" in str(o["request"]):
            action = "modified"
        if "DELETE" in str(o["request"]):
            action = "deleted"

        if "data" in o:
            data = o["data"]

        if action == "modified" or action == "deleted":
            message = "IPv4 address "+o["ipv4address"]+" has been "+action+" by "+o["user"]["username"]+".\n"

            if "mac" in data:
                mac = data["mac"]
                message += "MAC: "+mac+"\n"
            if "extattrs" in data:
                if "Mask" in data["extattrs"]:
                    mask = data["extattrs"]["Mask"]["value"]
                    message += "Mask: "+mask+"\n"
                if "Gateway" in data["extattrs"]:
                    gw = data["extattrs"]["Gateway"]["value"]
                    message += "Gateway: "+gw+"\n"
                if "Name Server" in data["extattrs"]:
                    ns = data["extattrs"]["Name Server"]["value"]
                    message += "Hostname: "+ns+"\n"
                if "Reference" in data["extattrs"]:
                    ref = data["extattrs"]["Reference"]["value"]
                    message += "Reference: "+ref+"\n"
            if "historyId" in o:
                message += "Unique operation ID: "+str(o["historyId"])+"\n"

            CiscoSpark.send(o["user"], message)

        if action == "created":
            if o["reqType"] == "post.next-available":
                j = 0

                for createdObject in o["response"]["data"]:
                    ip = re.findall(r'[0-9]+(?:\.[0-9]+){3}', createdObject["result"])[0]
                    message = "IPv4 address "+ip+" has been "+action+" by "+o["user"]["username"]+".\n"

                    if "mac" in o["userValidatedData"]:
                        message += "MAC: "+o["userValidatedData"]["mac"][j]+"\n"
                    if "actualNetwork" in o and o["actualNetwork"]:
                        message += "Network: "+o["actualNetwork"]+"\n"
                    if "gateway" in o and o["gateway"]:
                        message += "Gateway: "+o["gateway"]+"\n"
                    if "mask" in o and o["mask"]:
                        message += "Mask: "+o["mask"]+"\n"

                    if "object_type" in o["userValidatedData"]:
                        if o["userValidatedData"]["object_type"] != "undefined":
                            message += "Type: "+o["userValidatedData"]["object_type"]+"\n"
                    if "extattrs" in o["userValidatedData"]:
                        if "Name Server" in o["userValidatedData"]["extattrs"][j]:
                            message += "Hostname: "+o["userValidatedData"]["extattrs"][j]["Name Server"]["value"]+"\n"
                        if "Reference" in o["userValidatedData"]["extattrs"][j]:
                            message += "Reference: "+o["userValidatedData"]["extattrs"][j]["Reference"]["value"]+"\n"
                    if "historyId" in o:
                        message += "Unique operation ID: "+str(o["historyId"])+"\n"
                    j += 1

                    CiscoSpark.send(o["user"], message)
