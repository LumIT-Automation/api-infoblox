from infoblox.repository.IdentityGroup import IdentityGroup as Repository


class IdentityGroup:
    def __init__(self, identityGroupIdentifier: str,  *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.identityGroupIdentifier = identityGroupIdentifier



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def info(self) -> dict:
        try:
            return Repository.get(self.identityGroupIdentifier)
        except Exception as e:
            raise e



    def modify(self, data: dict) -> None:
        try:
            Repository.modify(self.identityGroupIdentifier, data)
        except Exception as e:
            raise e



    def delete(self) -> None:
        try:
            Repository.delete(self.identityGroupIdentifier)
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(showPrivileges: bool = False) -> dict:
        # List identity groups with related information regarding the associated roles on networks
        # and optionally detailed privileges' descriptions.
        j = 0

        try:
            items = Repository.list()

            # "items": [
            # ...,
            # {
            #    "id": 2,
            #    "name": "groupStaff",
            #    "identity_group_identifier": "cn=groupStaff,cn=users,dc=lab,dc=local",
            #    "roles_network": "staff::1::Common",
            #    "privileges_network": "certificates_post::1::Common::1::0,poolMember_get::1::Common::0::0,poolMember_patch::1::Common::0::0,poolMembers_get::1::Common::0::0,poolMemberStats_get::1::Common::0::0,pools_get::1::Common::0::0,networks_get::1::Common::1::1"
            # },
            # ...
            # ]

            for ln in items:
                if "roles_network" in items[j]:
                    if "," in ln["roles_network"]:
                        items[j]["roles_network"] = ln["roles_network"].split(",") # "staff::1::network,...,readonly::2::network" string to list value: replace into original data structure.
                    else:
                        items[j]["roles_network"] = [ ln["roles_network"] ] # simple string to list.

                    # "roles_network": [
                    #    "admin::1::any",
                    #    "staff::1::PARTITION1",
                    #    "staff::2::PARTITION2"
                    # ]

                    rolesStructure = dict()
                    for rls in items[j]["roles_network"]:
                        if "::" in rls:
                            rlsList = rls.split("::")
                            if not str(rlsList[0]) in rolesStructure:
                                # Initialize list if not already done.
                                rolesStructure[rlsList[0]] = list()

                            rolesStructure[rlsList[0]].append({
                                "assetId": rlsList[1],
                                "network": rlsList[2]
                            })

                    items[j]["roles_network"] = rolesStructure

                    #"roles_network": {
                    #    "staff": [
                    #        {
                    #            "assetId": 1
                    #            "network": "PARTITION1"
                    #        },
                    #        {
                    #            "assetId": 2
                    #            "network": "PARTITION2"
                    #        },
                    #    ],
                    #    "admin": [
                    #        {
                    #            "assetId": 1
                    #            "network": "any"
                    #        },
                    #    ]
                    #}

                if showPrivileges:
                    # Add detailed privileges' descriptions to the output.
                    if "privileges_network" in items[j]:
                        if "," in ln["privileges_network"]:
                            items[j]["privileges_network"] = ln["privileges_network"].split(",")
                        else:
                            items[j]["privileges_network"] = [ ln["privileges_network"] ]

                        ppStructure = dict()
                        for pls in items[j]["privileges_network"]:
                            if "::" in pls:
                                pList = pls.split("::")
                                if not str(pList[0]) in ppStructure:
                                    ppStructure[pList[0]] = list()

                                # Differentiate permission type:
                                # global:
                                #     a privilege does not require the asset to be specified <--> it's valid for all assets;
                                #     set "any" for assets value.

                                # asset:
                                #    a privilege does not require the networks to be specified <--> it's valid for all networks within the asset;
                                #    set "any" for networks value.
                                #
                                # object:
                                #     standard.

                                if pList[3]:
                                    if pList[3] == "global":
                                        pList[1] = 0
                                        pList[2] = "any"
                                    if pList[3] == "asset":
                                        pList[2] = "any"

                                if not any(v['assetId'] == 0 for v in ppStructure[pList[0]]): # insert value only if not already present (applied to assetId "0").
                                    ppStructure[pList[0]].append({
                                        "assetId": pList[1],
                                        "network": pList[2],
                                    })

                        items[j]["privileges_network"] = ppStructure
                else:
                    del items[j]["privileges_network"]

                j = j+1

            return dict({
                "items": items
            })
        except Exception as e:
            raise e



    @staticmethod
    def add(data: dict) -> None:
        try:
            Repository.add(data)
        except Exception as e:
            raise e
