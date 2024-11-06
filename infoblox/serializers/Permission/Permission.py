from rest_framework import serializers


class PermissionSerializer(serializers.Serializer):
    # Not using composition here, for simpler data structure exposed to consumer.

    class PermissionPermissionSerializer(serializers.Serializer):
        id_asset = serializers.IntegerField(required=False)
        name = serializers.CharField(max_length=64, required=True)
        asset_name = serializers.CharField(max_length=256, required=False)

    id = serializers.IntegerField(required=False)
    identity_group_name = serializers.CharField(max_length=64, required=False)
    identity_group_identifier = serializers.CharField(max_length=255, required=True)
    role = serializers.CharField(max_length=64, required=True)
    network = PermissionPermissionSerializer(required=True)
