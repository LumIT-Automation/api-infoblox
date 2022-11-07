from rest_framework import serializers


class PermissionSerializer(serializers.Serializer):
    class PermissionPermissionSerializer(serializers.Serializer):
        id_asset = serializers.IntegerField(required=False)
        asset_id = serializers.IntegerField(required=False) # @todo: standardize: only id_asset.
        name = serializers.CharField(max_length=64, required=True)

    id = serializers.IntegerField(required=False)
    identity_group_name = serializers.CharField(max_length=64, required=False)
    identity_group_identifier = serializers.CharField(max_length=255, required=True)
    role = serializers.CharField(max_length=64, required=True)
    network = PermissionPermissionSerializer(required=True)
