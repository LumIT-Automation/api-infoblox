import hashlib

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from infoblox.models.Infoblox.Tree import Tree
from infoblox.models.Infoblox.Network import Network
from infoblox.models.Infoblox.NetworkContainer import NetworkContainer
from infoblox.models.Permission.Permission import Permission

from infoblox.controllers.CustomController import CustomController

from infoblox.helpers.Lock import Lock
from infoblox.helpers.Conditional import Conditional
from infoblox.helpers.Log import Log


class InfobloxNetworksTreeController(CustomController):
    @staticmethod
    def get(request: Request, assetId: int) -> Response:
        data = dict()
        tree = dict()
        o = {
            "/": {
                "title": "/",
                "key": "networkcontainer/",
                "children": list()
            }
        }
        etagCondition = { "responseEtag": "" }
        user = CustomController.loggedUser(request)

        def __allowedTree(el: dict, father: str, tree: dict, networkList: list, networkContainterList: list) -> None: # -> tree.
            if not el["children"]:
                # Leaf, container or network.
                if "networkcontainer" in el["_ref"]:
                    action = "network_containers_get"
                    nList = []
                else:
                    action = "networks_get"
                    nList = networkList.copy()

                # Add only allowed leaves to the tree data structure.
                if Permission.checkPermissionInList(groups=user["groups"], action=action, assetId=assetId, networkName=el["network"], netContainerList=networkContainterList, netList=nList) or user["authDisabled"] :
                    el["key"] = hashlib.sha256(el["_ref"].encode('utf-8')).hexdigest()
                    el["children"] = []

                    del(el["_ref"])
                    del(el["network"])

                    tree[father].append(el)
            else:
                # Branch, container.
                if str(el["network"]) not in tree:
                    tree[el["network"]] = list()

                for son in el["children"]:
                    __allowedTree(son, el["network"], tree, networkList, networkContainterList) # recurse.

                    try:
                        if father:
                            nc = {
                                "title": el["network"],
                                "key": hashlib.sha256(el["_ref"].encode('utf-8')).hexdigest(),
                                "type": "container",
                                "extattrs": el["extattrs"],
                                "children": tree[el["network"]]
                            }

                            # If not branch allowed, clear information but maintain structure.
                            if not (Permission.checkPermissionInList(groups=user["groups"], action="network_containers_get", assetId=assetId, networkName=el["network"], netContainerList=networkContainterList)  or user["authDisabled"] or el["network"] == "/"):
                                nc["title"] = ""
                                nc["extattrs"] = dict()

                            if nc not in tree[father]:
                                tree[father].append(nc)
                    except Exception:
                        pass

        def __cleanupTree(el: dict, father: str, tree: dict) -> None: # -> tree.
            if not el["children"]:
                if el["title"]:
                    el["children"] = []
                    tree[father].append(el)
                else:
                    tree["clean"] = False
            else:
                # Branch, container.
                if str(el["key"]) not in tree:
                    tree[el["key"]] = list()

                for son in el["children"]:
                    __cleanupTree(son, el["key"], tree) # recurse.

                    try:
                        if father:
                            nc = {
                                "title": el["title"],
                                "key": el["key"],
                                "type": "container",
                                "extattrs": el["extattrs"],
                                "children": tree[el["key"]]
                            }

                            if nc not in tree[father]:
                                tree[father].append(nc)
                    except Exception:
                        pass

        try:
            if (Permission.hasUserPermission(groups=user["groups"], action="network_containers_get", assetId=assetId) and Permission.hasUserPermission(groups=user["groups"], action="networks_get", assetId=assetId)) or user["authDisabled"]:
                Log.actionLog("Tree", user)

                lock = Lock("tree", locals())
                if lock.isUnlocked():
                    lock.lock()

                    # Get the tree and check here user's permissions.
                    networkList = Network.listData(assetId)
                    networkContainerList = NetworkContainer.listData(assetId)

                    itemData = Tree.tree(assetId)
                    __allowedTree(itemData["/"], "", tree, networkList, networkContainerList) # tree modified: by reference.

                    o["/"]["children"] = tree["/"]

                    # Cleanup tree: remove empty leaves, one level per run.
                    while True:
                        tree = {
                            "clean": True
                        }
                        __cleanupTree(o["/"], "", tree)

                        o = {
                            "/": {
                                "title": "/",
                                "key": "networkcontainer/",
                                "children": list()
                            }
                        }
                        o["/"]["children"] = tree["networkcontainer/"]

                        if tree["clean"]:
                            break

                    data["data"] = o
                    data["href"] = request.get_full_path()

                    # Check the response's ETag validity (against client request).
                    conditional = Conditional(request)
                    etagCondition = conditional.responseEtagFreshnessAgainstRequest(data["data"])
                    if etagCondition["state"] == "fresh":
                        data = None
                        httpStatus = status.HTTP_304_NOT_MODIFIED
                    else:
                        httpStatus = status.HTTP_200_OK

                    lock.release()

                    CustomController.plugins("network_containers_get", locals())
                else:
                    data = None
                    httpStatus = status.HTTP_423_LOCKED
            else:
                data = None
                httpStatus = status.HTTP_403_FORBIDDEN
        except Exception as e:
            Lock("tree", locals()).release()

            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "ETag": etagCondition["responseEtag"],
            "Cache-Control": "must-revalidate"
        })
