from rest_framework import serializers


class InfobloxVlanSerializer(serializers.Serializer):
    class InfobloxVlanParentSerializer(serializers.Serializer):
        _ref = serializers.CharField(max_length=255, required=False)

    asset_id = serializers.IntegerField(required=False)
    _ref = serializers.CharField(max_length=255, required=False, allow_blank=True)
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(max_length=255, required=False)
    assigned_to = serializers.ListField(
        child=serializers.CharField(max_length=255, required=False),
        required=False
    )
    reserved = serializers.BooleanField(required=False)
    status = serializers.CharField(max_length=15, required=False)
    parent = InfobloxVlanParentSerializer(required=False)
    extattrs = serializers.JSONField(required=False)
