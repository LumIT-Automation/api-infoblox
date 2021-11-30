from infoblox.models.Infoblox.Network import Network
from infoblox.models.Infoblox.NetworkContainer import NetworkContainer


class Tree:

    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def tree(assetId: int) -> dict:
        containers = dict()
        tree = dict()
        o = {
            "/": {
                "title": "/",
                "key": "networkcontainer/",
                "children": list()
            }
        }

        # Get a containers' key/values structure.
        l = NetworkContainer.list(assetId)
        for container in l["data"]:
            # {
            #      "_ref": "networkcontainer/ZG5zLm5ldHdvcmtfY29udGFpbmVyJDEwLjguMTAuMC8yNC8w:10.8.10.0/24/default",
            #      "network": "10.8.10.0/24",
            #      "network_container": "10.8.0.0/17",
            #      "network_view": "default"
            # },
            # {
            #      "_ref": "networkcontainer/ZG5zLm5ldHdvcmtfY29udGFpbmVyJDEwLjguMC4wLzE3LzA:10.8.0.0/17/default",
            #      "network": "10.8.0.0/17",
            #      "network_container": "/"
            # },

            if container["network_container"] not in containers:
                containers[container["network_container"]] = list()

            containers[container["network_container"]].append({
                "_ref": container["_ref"],
                "key": container["_ref"],
                "network": container["network"],
                "title": container["network"],
                "extattrs": container["extattrs"],
                "type": "container"
            })

            # {
            #     "/": [
            #         {
            #             "_ref": "networkcontainer/ZG5zLm5ldHdvcmtfY29udGFpbmVyJDEwLjkuMC4wLzE2LzA:10.9.0.0/16/default",
            #             "network": "10.9.0.0/16"
            #         },
            #         {
            #             "_ref": "networkcontainer/ZG5zLm5ldHdvcmtfY29udGFpbmVyJDEwLjEwLjAuMC8xNi8w:10.10.0.0/16/default",
            #             "network": "10.10.0.0/16"
            #         },
            #         {
            #             "_ref": "networkcontainer/ZG5zLm5ldHdvcmtfY29udGFpbmVyJDEwLjguMC4wLzE3LzA:10.8.0.0/17/default",
            #             "network": "10.8.0.0/17"
            #         }
            #     ],
            #     "10.8.0.0/17": [
            #         {
            #             "_ref": "networkcontainer/ZG5zLm5ldHdvcmtfY29udGFpbmVyJDEwLjguMTAuMC8yNC8w:10.8.10.0/24/default",
            #             "network": "10.8.10.0/24"
            #         }
            #     ],
            #     "10.10.0.0/16": [
            #         {
            #             "_ref": "networkcontainer/ZG5zLm5ldHdvcmtfY29udGFpbmVyJDEwLjEwLjAuMC8xOS8w:10.10.0.0/19/default",
            #             "network": "10.10.0.0/19"
            #         }
            #     ],
            #     "10.8.10.0/24": [
            #         {
            #             "_ref": "networkcontainer/ZG5zLm5ldHdvcmtfY29udGFpbmVyJDEwLjguMTAuMC8yOC8w:10.8.10.0/28/default",
            #             "network": "10.8.10.0/28"
            #         }
            #     ],
            #     "10.8.10.0/28": [
            #         {
            #             "_ref": "networkcontainer/ZG5zLm5ldHdvcmtfY29udGFpbmVyJDEwLjguMTAuMC8yOS8w:10.8.10.0/29/default",
            #             "network": "10.8.10.0/29"
            #         },
            #         {
            #             "_ref": "networkcontainer/ZG5zLm5ldHdvcmtfY29udGFpbmVyJDEwLjguMTAuOC8yOS8w:10.8.10.8/29/default",
            #             "network": "10.8.10.8/29"
            #         }
            #     ]
            # }

        # Add networks information to the containers' data structure.
        l = Network.list(assetId)
        for network in l["data"]:
            c = network["network_container"]

            del (network["network_view"])
            del (network["network_container"])

            # Just remove some useless info here.
            for ck, cv in network["extattrs"].items():
                if "inheritance_source" in cv:
                    del network["extattrs"][ck]["inheritance_source"]

            network["type"] = "network"
            network["title"] = network["network"]
            network["key"] = network["_ref"]

            if str(c) in containers:
                # Networks in branch containers.
                containers[c].append(network)
            else:
                # Networks in leaf containers: container must become a branch container.
                containers[c] = list()
                containers[c].append(network)

        Tree.__treeSort(containers, { "network": "/" }, "", tree)

        o["/"]["children"] = tree["/"]
        o["/"]["network"] = "/"

        containersTree = o

        # "/": {
        #     "children": [
        #         {
        #             "_ref": "networkcontainer/ZG5zLm5ldHdvcmtfY29udGFpbmVyJDEwLjkuMC4wLzE2LzA:10.9.0.0/16/default",
        #             "network": "10.9.0.0/16",
        #             "children": []
        #         },
        #         {
        #             "network": "10.10.0.0/16",
        #             "_ref": "networkcontainer/ZG5zLm5ldHdvcmtfY29udGFpbmVyJDEwLjEwLjAuMC8xNi8w:10.10.0.0/16/default",
        #             "children": [
        #                 {
        #                     "_ref": "networkcontainer/ZG5zLm5ldHdvcmtfY29udGFpbmVyJDEwLjEwLjAuMC8xOS8w:10.10.0.0/19/default",
        #                     "network": "10.10.0.0/19",
        #                     "children": []
        #                 }
        #             ]
        #         },
        #         {
        #             "network": "10.8.0.0/17",
        #             "_ref": "networkcontainer/ZG5zLm5ldHdvcmtfY29udGFpbmVyJDEwLjguMC4wLzE3LzA:10.8.0.0/17/default",
        #             "children": [
        #                 {
        #                     "network": "10.8.10.0/24",
        #                     "_ref": "networkcontainer/ZG5zLm5ldHdvcmtfY29udGFpbmVyJDEwLjguMTAuMC8yNC8w:10.8.10.0/24/default",
        #                     "children": [
        #                         {
        #                             "network": "10.8.10.0/28",
        #                             "_ref": "networkcontainer/ZG5zLm5ldHdvcmtfY29udGFpbmVyJDEwLjguMTAuMC8yOC8w:10.8.10.0/28/default",
        #                             "children": [
        #                                 {
        #                                     "_ref": "networkcontainer/ZG5zLm5ldHdvcmtfY29udGFpbmVyJDEwLjguMTAuMC8yOS8w:10.8.10.0/29/default",
        #                                     "network": "10.8.10.0/29",
        #                                     "children": []
        #                                 },
        #                                 {
        #                                     "_ref": "networkcontainer/ZG5zLm5ldHdvcmtfY29udGFpbmVyJDEwLjguMTAuOC8yOS8w:10.8.10.8/29/default",
        #                                     "network": "10.8.10.8/29",
        #                                     "children": []
        #                                 }
        #                             ]
        #                         }
        #                     ]
        #                 }
        #             ]
        #         }
        #     ]
        # }

        return containersTree



    ####################################################################################################################
    # Private static methods
    ####################################################################################################################

    @staticmethod
    def __treeSort(containers: dict, el: dict, father: str, tree: dict) -> None: # -> tree.
        if el["network"] not in containers: # not a dict key: leaf.
            el["children"] = []
            tree[father].append(el)
        else:
            if str(el["network"]) not in tree:
                tree[el["network"]] = list()

            for son in containers[el["network"]]:
                if father:
                    if father not in tree:
                        tree[father] = list()

                Tree.__treeSort(containers, son, el["network"], tree) # recurse.

                if father:
                    nc = {
                        "_ref": el["_ref"],
                        "network": el["network"],
                        "title": el["network"],
                        "key": el["_ref"],
                        "type": "container",
                        "extattrs": el["extattrs"],
                        "children": tree[el["network"]]
                    }

                    if nc not in tree[father]:
                        tree[father].append(nc)
