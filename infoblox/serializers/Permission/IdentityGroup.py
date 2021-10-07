from rest_framework import serializers
from infoblox.models.Permission.Role import Role


class IdentityGroupsAssestRolesSubItems(serializers.Serializer):
    assetId = serializers.IntegerField(required=True)
    network = serializers.CharField(max_length=64, required=True)

class IdentityGroupsAssestRolesItems(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Adding dynamic fields as taken from the Roles model.
        additionalFields = []
        r = Role.list()["items"]
        for additionalField in r:
            if "role" in additionalField:
                additionalFields.append(additionalField["role"])

        for af in additionalFields:
            self.fields[af] = IdentityGroupsAssestRolesSubItems(many=True, required=False)

class IdentityGroupSerializer(serializers.Serializer):
    class IdentityGroupAssestItems(serializers.Serializer):
        name = serializers.CharField(max_length=64, required=True)
        identity_group_identifier = serializers.CharField(max_length=255, required=True)
        roles_network = IdentityGroupsAssestRolesItems(required=False)

    data = IdentityGroupAssestItems(required=True)
